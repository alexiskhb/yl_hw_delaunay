from settings import Settings
from random import random
from PyQt5.QtGui import QColor


class Color:
    _idx2clr = []

    @staticmethod
    def get(idx):
        if idx >= len(Color._idx2clr):
            while len(Color._idx2clr) <= idx:
                h = 360 * random()
                s = 80 + 20 * random()
                l = 95 + 5 * random()
                Color._idx2clr.append(QColor.fromHsl(h, s, l))
        if not Settings.colors_on:
            return Settings.default_brush
        return Color._idx2clr[idx]

    @staticmethod
    def pop(idx):
        Color._idx2clr.pop(idx)
