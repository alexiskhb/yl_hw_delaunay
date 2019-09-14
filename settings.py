from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QCheckBox, QSpinBox


class Settings:
    colors_on = True
    point_size = 10
    default_brush = Qt.white
    default_pen = Qt.black
    show_voronoi = True
    show_delaunay = False


class SettingsWindow(QWidget):
    def __init__(self, settings_changed_callback):
        super().__init__()
        uic.loadUi('settings.ui', self)
        self.update_ui = settings_changed_callback
        self.colorsOn: QCheckBox = self.colorsOn
        self.showVoronoi: QCheckBox = self.showVoronoi
        self.showDelaunay: QCheckBox = self.showDelaunay
        self.pointSize: QSpinBox = self.pointSize
        self.colorsOn.clicked.connect(self.colors_on_checked)
        self.showVoronoi.clicked.connect(self.show_voronoi_checked)
        self.showDelaunay.clicked.connect(self.show_delaunay_checked)
        self.pointSize.valueChanged.connect(self.point_size_changed)

    def colors_on_checked(self):
        Settings.colors_on = self.colorsOn.isChecked()
        self.update_ui()

    def show_voronoi_checked(self):
        Settings.show_voronoi = self.showVoronoi.isChecked()
        self.update_ui()

    def show_delaunay_checked(self):
        Settings.show_delaunay = self.showDelaunay.isChecked()
        self.update_ui()

    def point_size_changed(self):
        Settings.point_size = self.pointSize.value()
        self.update_ui()
