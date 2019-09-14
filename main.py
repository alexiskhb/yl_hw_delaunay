import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from typing import List, Optional, Tuple
from scipy.spatial import Voronoi
from scipy.spatial.qhull import QhullError
import numpy as np


class PointSet:
    class PointDescriptor:
        radius = 8
        color = Qt.white

        def __init__(self, ps, idx: int):
            self.ps = ps
            self.idx = idx

        def draw(self, painter):
            if isinstance(painter, QPainter):
                painter.setBrush(self.color)
                painter.drawEllipse(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

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
            self.ps = ps
            self.idx = prr[0]
            self.ngbrs = [p for p, _ in prr[1]]
            self.ridges = [((int(x1), int(y1)), (int(x2), int(y2))) for _, ((x1, y1), (x2, y2)) in prr[1]]

        def draw(self, painter):
            if isinstance(painter, QPainter):
                for i, ((x1, y1), (x2, y2)) in enumerate(self.ridges):
                    if self.idx > self.ngbrs[i]:
                        painter.setPen(Qt.black)
                        painter.drawLine(x1, y1, x2, y2)

    def __init__(self, points=None):
        self.points: List[List[int]] = []
        self.vor = None
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
            if (x - x0)**2 + (y - y0)**2 <= PointSet.PointDescriptor.radius**2:
                return self[i]
        return None
    
    @property
    def regions(self):
        try:
            self.vor = Voronoi(self.points)
        except QhullError:
            pass
        prrs = get_segments(self.vor)
        return map(lambda prr: PointSet.RegionDescriptor(self, prr), prrs.items())

    def draw(self, painter):
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


class Window(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('main.ui')
        w0, h0 = self.width()//4, self.height()//4
        self.ps = PointSet([[w0, h0], [w0, h0*3], [w0*3, h0*3]])
        self.moving = False
        self.current_point = None
        self.repaint()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        self.ps.draw(painter)
        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.ps.get_point(event.x(), event.y()) is None:
                self.ps.add(event.x(), event.y())
            self.current_point = self.ps.get_point(event.x(), event.y())
            self.moving = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.moving = False
        self.repaint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.moving:
            self.current_point.set(x=event.x(), y=event.y())
            self.repaint()

    def in_ball(self, x, y):
        return (x - self.ball_x) ** 2 + (y - self.ball_y) ** 2 <= self.ball_r ** 2


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.exit(app.exec())
