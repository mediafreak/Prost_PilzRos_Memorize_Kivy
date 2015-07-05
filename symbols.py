#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Natalia Prost'
__author__ = 'Jenny Pilz-Rosenthal'

from config import *

from kivy.graphics import Color
from kivy.uix.label import Label
from kivy.uix.widget import Widget

sizeOfFigures = 80


#########################################################################
#
# Figuren/Symbole
#
#########################################################################
class Symbol(Widget):
    """
    Oberklasse aller Symbole (wie Circle, Square usw.)
    """

    def __init__(self, color, figure, **kwargs):
        # print("Symbol init()")
        self.colorRGB = color
        self.colorOfBorder = figure.colorOfBackground
        self.color = figure.color
        self.form = figure.form
        super(Symbol, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        # print("Symbol on_touch_down()")
        if self.collide_point(touch.x, touch.y) and "TileBarGrid" in str(self.parent):
            gameConfig = self.parent.parent.parent.gameConfig
            sm = gameConfig.sm
            remScreen = sm.get_screen(gameConfig.REMEMBER_NAME)
            touchEnabled = remScreen.questionNumber < remScreen.missingIndices.__len__()

            if touchEnabled is True:
                remScreen.handle_touched_symbol(self)

    def check_answer_status(self, figure):
        # print("Symbol check_answer_status()")
        # return if status hasn't been set to true or false
        if figure.statusAnswer == 0:
            return

        if figure.statusAnswer is True:
            self.colorOfBorder = Color(RIGHT_COLOR)
        else:
            self.colorOfBorder = Color(WRONG_COLOR)


# Circle mit Ellipse in KV-Datei
class Circle(Symbol):
    pass


# Circle mit Line.Ellipse in KV-Datei
class CircleOutline(Symbol):
    pass


# Offener Circle mit Line.Ellipse in KV-Datei
class MouthOutline(Symbol):
    pass


# Offener Circle mit Line.Ellipse in KV-Datei
class PacmanOutline(Symbol):
    pass


# Offener Circle mit Line.Ellipse in KV-Datei
class Ring(Symbol):
    pass


# Square mit Rectangle in KV-Datei
class Square(Symbol):
    pass


# Square mit Linie > Rectanle in KV-Datei
class SquareOutline(Symbol):
    pass


# gleichseitiges Dreieck mit Vertices
class EquilateralTriangle(Symbol):
    pass


# gleichseitiges ungefuelltes Dreieck mit Vertices
class EquilateralTriangleOutline(Symbol):
    pass


# rechtwinkliges Dreieck mit Vertices
class RightAngledTriangle(Symbol):
    pass


# rechtwinkliges ungefuelltes Dreieck mit Vertices
class RightAngledTriangleOutline(Symbol):
    pass


# Kreuz mit Rectangles
class Cross(Symbol):
    pass


# Platzhalter für verdeckte Symbole
class HiddenTile(Symbol):
    def __init__(self, color, figure, **kwargs):
        self.colorOfBackground = BLACK_COLOR
        self.colorOfLine = GREY_COLOR
        super(HiddenTile, self).__init__(color, figure, **kwargs)


# Ersatz für gesuchte Symbole/Kacheln
class QuestionTile(Label):
    def __init__(self, color, figure, **kwargs):
        self.size = (sizeOfFigures, sizeOfFigures)
        self.colorOfBackground = BLACK_COLOR
        self.colorOfLine = WHITE_COLOR
        self.figure = figure.get_origin_copy()
        super(QuestionTile, self).__init__(**kwargs)
        # super(QuestionTile, self).__init__(color=color, figure=figure.get_origin_copy(), **kwargs)
        self.text = "?"
        self.font_size = "60sp"

    def check_answer_status(self, figure):
        # print("QuestionTile check_answer_status()")
        # return if status hasn't been set to true or false
        if figure.get_origin_copy().statusAnswer == 0:
            return
        if figure.get_origin_copy().statusAnswer is True:
            self.colorOfBorder = Color(RIGHT_COLOR)
        else:
            self.colorOfBorder = Color(WRONG_COLOR)


# Platzhalter fürs Gridlayout
class Nothing(Widget):  # nicht von Symbol erben wegen des Hintergrunds
    def __init__(self, **kwargs):
        super(Nothing, self).__init__(**kwargs)
        color = Color(WHITE_COLOR)
        with self.canvas:
            self.canvas.add(color)