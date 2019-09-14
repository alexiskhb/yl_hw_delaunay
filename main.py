import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from color import Color
from point_set import PointSet


class Window(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
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
        if event.button() == Qt.RightButton:
            removee = self.ps.get_point(event.x(), event.y())
            if removee is not None and len(self.ps.points) > 3:
                Color.pop(removee.idx)
                self.ps.points.pop(removee.idx)

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
