#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Natalia Prost'
__author__ = 'Jenny Pilz-Rosenthal'

from symbols import *

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget


#########################################################################
#
# Widgets into the Screens
#
#########################################################################
class ScreenWidgets(Widget):
    """
    Oberklasse fuer Playgroundgrid und TileBarGrid.
    Beinhaltet gemeinsame Funktionen für Symbole (Farben/Figuren)
    """
    def __del__(self):
        print "geloescht", self


    def set_game_and_config(self, player, gameConfig):
        #print "AbstractPlayBar set_game_and_config()"
        self.player = player
        self.gameConfig = gameConfig


    def show_tile_in_grid(self, figure):
        #print "AbstractPlayBar show_tile_in_grid()"

        symbol = None

        # abbrechen bei leerem Feld
        if figure is None:
            self.show_empty_element()
            return symbol

        symbol = self.get_symbol_from_figure(figure)
        self.add_widget(symbol)

        symbol.check_answer_status(figure.get_origin_copy())

        return symbol


    def get_symbol_from_figure(self, figure):
        """
        Erzeugt für jede Figur ein Symbol
        """
        #print "AbstractPlayBar get_symbol_from_figure()"

        colorOfSymbolRGB = self.get_color_from_index(figure.color)

        symbol = None

        with self.canvas:

            if figure.form == 1:
                #print("show Circle")
                symbol = Circle(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 2:
                #print("show Square")
                symbol = Square(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 3:
                #print("show EquilateralTriangle")
                symbol = EquilateralTriangle(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 4:
                #print("show RightAngledTriangle")
                symbol = RightAngledTriangle(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 5:
                #print("show CircleOutline")
                symbol = CircleOutline(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 6:
                #print("show SquareOutline")
                symbol = SquareOutline(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 7:
                #print("show EquilateralTriangleOutline")
                symbol = EquilateralTriangleOutline(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 8:
                #print("show RightTriangleOutline")
                symbol = RightAngledTriangleOutline(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 9:
                #print("show Mund")
                symbol = MouthOutline(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 10:
                #print("show Ring")
                symbol = Ring(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 11:
                #print("show PacmanOutline")
                symbol = PacmanOutline(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 12:
                #print("show Cross")
                symbol = Cross(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == 0:
                # kein None, aber Figur die als Hidden markiert wurde
                symbol = HiddenTile(colorOfSymbolRGB, figure, size_hint=(1, 1))
            elif figure.form == -1:
                #print("show QuestionTile")
                symbol = QuestionTile(colorOfSymbolRGB, figure, size_hint=(1, 1))

        return symbol


    def remove_tile_in_grid(self):
        #print "AbstractPlayBar remove_tile_in_grid()"
        self.clear_widgets() # fuer Aufdecken/Platzieren der abgefragten Karten


    def get_color_from_index(self, nr):
        #print "AbstractPlayBar get_color_from_index()"

        colorRGB = 0

        if nr == 1:
            colorRGB = RED_COLOR
        elif nr == 2:
            colorRGB = GREEN_COLOR
        elif nr == 3:
            colorRGB = BLUE_COLOR
        elif nr == 4:
            colorRGB = CYAN_COLOR
        elif nr == 5:
            colorRGB = MAGENTA_COLOR
        elif nr == 6:
            colorRGB = YELLOW_COLOR
        elif nr == 7:
            colorRGB = PURPLE_COLOR
        elif nr == 8:
            colorRGB = ORANGE_COLOR
        elif nr == 9:
            colorRGB = BABY_BLUE_COLOR
        elif nr == 10:
            colorRGB = LIGHT_GREEN_COLOR
        elif nr == 11:
            colorRGB = BABY_PINK_COLOR
        elif nr == 12:
            colorRGB = RED_WINE_COLOR
        elif nr == 0:
            colorRGB = BLACK_COLOR
        elif nr == -1:
            colorRGB = WHITE_COLOR

        return colorRGB


class PlaygroundGrid(GridLayout, ScreenWidgets):
    """
    Erzeugt das PlaygroundGrid für Memorize- und RememberScreen
    """
    def show_all_tiles(self):
        #print "PlaygroundGrid show_all_tiles()"

        for x in range(0, self.gameConfig.get_max_number_of_cards()):
            self.show_tile_in_grid(self.player.arrayToShow[x])


    def set_hidden_tiles(self):
        """
        markiert im gesamten arrayToShow zufällige Karten als "hidden"
        """
        #print "PlaygroundGrid set_hidden_tiles() of", self.gameConfig.arrayToShow

        tilesToSkip = []
        skippedFigures = []
        skippedIndices = []

        self.numberOfHiddenCards = self.gameConfig.get_number_of_hidden_cards()

        for number in range(0, self.gameConfig.get_max_number_of_cards()):
            tilesToSkip.append(number)  # [0, 1, 2, 3, 4, ... ]
        random.shuffle(tilesToSkip)  # [10, 5, 2, 4, 1, 0 ... ]
        #print("indizes of tiles to be hidden", tilesToSkip)
        #print("so many tiles will be hidden:", hideSoMany)

        for b in range(0, self.gameConfig.get_max_number_of_cards()):
            if not self.player.arrayToShow[tilesToSkip[b]] is None \
                    and skippedFigures.__len__() < self.player.numberOfHiddenCards:
                # nur verdecken, wenn sich an dieser Indexstelle ein Symbol befindet und
                # solange die notwendige Anzahl von hidden Cards noch nicht erreicht ist
                self.player.arrayToShow[tilesToSkip[b]].mark_as_hidden()
                skippedFigures.append(self.player.arrayToShow[tilesToSkip[b]])
                skippedIndices.append(tilesToSkip[b])
        #print "diese Symbole werden verdeckt:", skippedFigures
        return skippedIndices

    def show_empty_element(self):
        #print "PlaygroundGrid show_empty_element()"
        with self.canvas:
            self.add_widget(Nothing(size_hint=(1, 1)))


class TileBarGrid(BoxLayout, ScreenWidgets):
    """
    Enthaelt TileBar fuer auszuwaehlende bzw. zuzuordnende Symbole/Karten
    """
    def __init__(self, **kwargs):
        #print "TileBarGrid init()"
        super(TileBarGrid, self).__init__(**kwargs)


    def show_tiles_to_choose(self, figure):
        #print "TileBarGrid show_tiles_to_choose()"
        self.create_random_array(figure)
        self.remove_tile_in_grid()
        self.show_choose_tiles()


    def create_random_array(self, figure):
        """
        Erzeugt Array mit gesuchtem Symbol/Kachel und weiteren per Zufall zur Auswahl stehenden Symbole/Karten
        :param figure:
        """
        self.randomSymbols = []
        self.randomSymbols.append(figure.get_origin_copy())  # fehlendes Symbol einfügen

        while not self.randomSymbols.__len__() == self.player.numberOfTilebarCards:

            randomForm = random.randint(1, self.player.numberOfForms)
            randomColor = random.randint(1, self.player.numberOfColors)
            newFigure = Figure(randomForm, randomColor)

            # gegen doppelte Symbole
            if str(newFigure) in str(self.randomSymbols):
                #print "Schon drin"
                continue
            else:
                self.randomSymbols.append(newFigure)
            #print newFigure

        self.chooseSymbols = self.randomSymbols
        random.shuffle(self.chooseSymbols)
        #print "chooseSymbols:", self.chooseSymbols


    def show_choose_tiles(self):
        #print "TileBarGrid show_choose_tiles() of", self.chooseSymbols
        for x in range(0, self.player.numberOfTilebarCards):
            self.show_tile_in_grid(self.chooseSymbols[x].get_origin_copy())