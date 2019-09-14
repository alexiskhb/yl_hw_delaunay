import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from typing import List, Optional


class PointSet:
    class PointDescriptor:
        radius = 5
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

    def __init__(self, points=None):
        self.points: List[List[int]] = []
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

    def draw(self, painter):
        if isinstance(painter, QPainter):
            for point in self:
                point.draw(painter)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('main.ui')
        self.ps = PointSet()
        self.moving = False
        self.current_point = None

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
