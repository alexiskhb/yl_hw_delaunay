from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPolygon, QPen
from typing import List, Optional, Tuple
from scipy.spatial import Voronoi, ConvexHull
from scipy.spatial.qhull import QhullError
from settings import Settings
import numpy as np
from color import Color


class PointSet:
    class PointDescriptor:
        def __init__(self, ps, idx: int):
            self.ps: PointSet = ps
            self.idx = idx

        def draw(self, painter):
            if isinstance(painter, QPainter):
                try:
                    color = Color.get(self.idx) if not self.ps.region(self.idx).is_closed() else Settings.default_brush
                except IndexError:
                    color = Settings.default_brush
                painter.setBrush(color)
                painter.drawEllipse(self.x - Settings.point_size, self.y - Settings.point_size, 2 * Settings.point_size,
                                    2 * Settings.point_size)

        @property
        def xy(self) -> List[int]:
            return self.ps.points[self.idx]

        @property
        def x(self) -> int:
            return self.xy[0]

        @property
        def y(self) -> int:
            return self.xy[1]

        def set(self, x=None, y=None):
            if isinstance(x, (int, float)):
                self.xy[0] = x
            if isinstance(y, (int, float)):
                self.xy[1] = y

    class RegionDescriptor:
        def __init__(self, ps, prr: Tuple[int, List[Tuple[int, List[float]]]]):
            self.ps: PointSet = ps
            self.idx = prr[0]
            self.ngbrs = [p for p, _ in prr[1]]
            self.ridges = [((int(x1), int(y1)), (int(x2), int(y2))) for _, ((x1, y1), (x2, y2)) in prr[1]]
            self.points = []
            for ridge in self.ridges:
                self.points.extend(ridge)
            try:
                self.hull = ConvexHull(self.points)
            except QhullError:
                self.hull = None

        def draw(self, painter, draw_polygon=False):
            if isinstance(painter, QPainter):
                if Settings.show_voronoi:
                    pen = QPen(Settings.default_pen)
                    if Settings.show_delaunay:
                        pen.setStyle(Qt.DashLine)
                    painter.setPen(pen)
                    if draw_polygon and self.is_closed() and self.hull:
                        painter.setBrush(Color.get(self.idx))
                        painter.drawPolygon(QPolygon(QPoint(*p) for p in self.hull.points[self.hull.vertices]))
                        return
                    for i, ((x1, y1), (x2, y2)) in enumerate(self.ridges):
                        if self.idx > self.ngbrs[i]:
                            painter.drawLine(x1, y1, x2, y2)
                if Settings.show_delaunay:
                    pen = QPen(Settings.default_pen)
                    painter.setPen(pen)
                    for nbr in self.ngbrs:
                        if self.idx > nbr:
                            (x1, y1), (x2, y2) = self.ps.points[self.idx], self.ps.points[nbr]
                            painter.drawLine(x1, y1, x2, y2)

        def is_closed(self):
            return all(idx >= 0 for idx in self.ps.vor.regions[self.ps.vor.point_region[self.idx]])

    def __init__(self, points=None):
        self.points: List[List[int]] = []
        self._regions = []
        self.vor: Optional[Voronoi] = None
        try:
            self.points.extend(points)
        except TypeError:
            pass

    def __getitem__(self, idx: int):
        return PointSet.PointDescriptor(self, idx)

    def __iter__(self):
        yield from map(lambda i: self[i], range(len((self.points))))

    def add(self, x: int, y: int):
        self.points.append([x, y])

    def get_point(self, x: int, y: int) -> Optional[PointDescriptor]:
        # Разворачиваем, чтобы хватать верхнюю точку в стопке (более интуитивно)
        for i, (x0, y0) in list(enumerate(self.points))[::-1]:
            if (x - x0) ** 2 + (y - y0) ** 2 <= Settings.point_size ** 2:
                return self[i]
        return None

    @property
    def regions(self):
        try:
            self.vor = Voronoi(self.points)
        except QhullError:
            pass
        prrs = get_segments(self.vor)
        self._regions = list(map(lambda prr: PointSet.RegionDescriptor(self, prr), sorted(prrs.items())))
        return self._regions

    def region(self, idx) -> RegionDescriptor:
        return self._regions[idx]

    def draw(self, painter):
        for region in self.regions:
            region.draw(painter, draw_polygon=True)
        for region in self.regions:
            region.draw(painter)
        for point in self:
            point.draw(painter)


# Копипаста из scipy.spatial.voronoi_plot_2d
def get_segments(vor):
    center = vor.points.mean(axis=0)
    ptp_bound = vor.points.ptp(axis=0)
    point_region_ridges = {}
    segments = []
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
        simplex = np.asarray(simplex)
        if np.all(simplex >= 0):
            segments.append(vor.vertices[simplex])
        else:
            i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[i] + direction * ptp_bound.max()

            segments.append([vor.vertices[i], far_point])
        for p1, p2 in pointidx, reversed(pointidx):
            if p1 not in point_region_ridges:
                point_region_ridges[p1] = []
            point_region_ridges[p1].append((p2, segments[-1]))
    return point_region_ridges
