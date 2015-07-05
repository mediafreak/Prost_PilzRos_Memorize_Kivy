#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from kivy.animation import Animation

__author__ = 'Natalia Prost'
__author__ = 'Jenny Pilz-Rosenthal'

from screenwidgets import *

from functools import partial

from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen


# Create all screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.

#########################################################################
#
# Screens
#
#########################################################################
class PlayScreens(Screen):
    """
    Oberklasse für MemorizeScreen und RememberScreen, enthält die Aktualisierung des ScoreHeaders und Playgrounds
    """
    # class variable shared by all instances
    playgroundGrid = ObjectProperty(None)
    layout = ObjectProperty(None)
    labellayout = ObjectProperty(None)
    header = ObjectProperty(None)
    level = NumericProperty(1)
    mempoints = NumericProperty(0)
    progresspoints = NumericProperty(0)
    progressmax = NumericProperty(0)
    levelpoint_limits = []

    def on_enter(self, *args):
        """
        Setzt bei Betreten des Screens  Werte für Progressbar sowie das PlaygroundGrid
        """
        self.levelpoint_limits = self.player.get_levelpoints_min_max()
        self.progressmax = self.player.get_pointdifference_to_next_level()
        self.progresspoints = self.calculate_progresspoints()

        self.remove_element(self.playgroundGrid)
        self.playgroundGrid = PlaygroundGrid()
        self.playgroundGrid.set_game_and_config(self.player, self.gameConfig)

        self.add_element(self.layout, self.playgroundGrid)

    def calculate_progresspoints(self, dt=0):
        """
        fuer Anzeige des Fortschrittbalkens bis zum naechsten Level
        """
        # print "LEVELPOINT LIMITS", self.levelpoint_limits
        # print "PUUUNKTE", self.player.points
        return self.player.points - self.levelpoint_limits['lowerBound']

    def finished_screen(self):
        # Loeschen des PlaygroundGrid bei Verlassen des Screens
        Clock.schedule_once(partial(self.remove_element, self.playgroundGrid), 0.3)

    def update_progressbar(self):
        """
        Anzeige des Fortschrittbalkens bis zum naechsten Level
        """
        self.progresspoints = self.calculate_progresspoints()

        if self.progresspoints is self.progressmax:
            Clock.schedule_once(self.update_progessbar_for_levelchange, .2)
            # print "update_progressbar",self.progressmax, self.progresspoints, self.levelpoint_limits

    def update_labels(self, dt=0):
        """
        Anzeige der aktuellen Punkte und des aktuellen Levels
        """
        # print "update_labels", self.player
        self.level = self.player.level
        self.mempoints = self.player.points
        # self.header.levelUpLabel.opacity = 1

    def remove_element(self, element, dt=0):
        # print("AbstractScreen remove_element()")
        self.layout.remove_widget(element)

    @staticmethod
    def add_element(layout, element):
        layout.add_widget(element)


class MainScreen(Screen):
    @staticmethod
    def exit():
        App.get_running_app().stop()


class SettingsScreen(Screen):
    """
    Anzeige der bisherigen Spielstaende, Auswahl einer GameConfig, Zuruecksetzen der bisherigen Spielstaende
    """
    level = NumericProperty(1)
    points = NumericProperty(0)
    mode = NumericProperty(0)

    def __init__(self, settings, gameConfig, name):
        # print "ResultScreen init()"
        self.name = name
        self.settings = settings
        self.gameConfig = gameConfig
        super(SettingsScreen, self).__init__()

    def on_pre_enter(self, *args):
        self.level = self.settings.level
        self.points = self.settings.points
        # print "SettingsScreen: ",self, self.level, self.points

    def update_settings(self, config):
        # print "SettingScreen update_settings() with config:", config
        try:
            self.gameConfig.set_config_in_store(self.settings, int(config))

            App.get_running_app().set_game_config(int(config))

            self.gameConfig.get_level_and_points_from_store(self.settings)
            # print "Level: ", self.settings.level, "Points: ", self.settings.points, "Mode: ", self.settings.initMode

            self.update_screen_informations()
        except:
            pass

    def update_screen_informations(self):
        # print "Level: ", self.settings.level, "Points: ", self.settings.points, "Mode: ", self.settings.initMode
        self.level = self.settings.level
        self.points = self.settings.points
        self.mode = self.settings.initMode

    def reset_game(self):
        """
        Loest Zuruecksetzen des SettingsScore aus und setzt die GameConfig auf Default-Werte
        """
        self.gameConfig.reset_score(self.settings)

        App.get_running_app().set_game_config(self.settings.initConfig)

        self.update_screen_informations()
        pass


class MemorizeScreen(PlayScreens):
    """
    Zeigt einzuspraegendes Spielfeld an
    """

    def __init__(self, player, gameConfig):
        # print("MemScreen init()")
        self.player = player
        self.gameConfig = gameConfig
        self.sm = self.gameConfig.sm

        super(MemorizeScreen, self).__init__()

        self.playgroundGrid.set_game_and_config(self.player, self.gameConfig)
        self.buttons = self.layout.children[0]
        self.update_labels()

    def on_enter(self, *args):
        # print("MemScreen on_enter()")

        super(MemorizeScreen, self).on_enter()

        self.remove_element(self.buttons)
        self.add_element(self.layout, self.buttons)
        self.header.opacity = 1

        self.player.create_actual_array()
        self.playgroundGrid.show_all_tiles()

    def finished_memorization(self):
        """
        beendet die Anzeige der Symbole und führt den Benutzer zum nächsten Screen
        """
        # print("MemScreen finished_memorization()")
        self.header.opacity = 0
        self.finished_screen()
        Clock.schedule_once(partial(self.remove_element, self.buttons), 0.3)
        self.sm.get_screen(self.gameConfig.REMEMBER_NAME).update_labels()
        self.sm.current = self.gameConfig.REMEMBER_NAME


class RememberScreen(PlayScreens):
    """
    Enthaelt Spielfeld mit zum Teil verdeckten Karten und eine TileBarGrid zum Zuordnen der Symbole
    """
    tilebarGrid = ObjectProperty(None)

    def __init__(self, settings, player, gameConfig):
        # print "remScreen init()"

        # instance variable unique to each instance
        self.player = player
        self.gameConfig = gameConfig
        self.settings = settings
        self.sm = self.gameConfig.sm
        self.app = App.get_running_app()

        super(RememberScreen, self).__init__()

    def on_enter(self, *args):
        # print self.gameConfig
        super(RememberScreen, self).on_enter()

        self.update_tilebar()

        self.header.opacity = 1

        self.init_questions()

        self.rightAnswers = 0
        self.wrongAnswers = 0

        self.playgroundGrid.show_all_tiles()
        self.show_tilebar()

    def init_questions(self):
        """
        Erzeugt Array fuer verdeckte Karten und aktuelle Karte, die abgefragt werden soll (Fragezeichen)
        """
        self.missingIndices = self.playgroundGrid.set_hidden_tiles()
        self.questionNumber = 0
        # print self.gameConfig.arrayToShow
        self.currentQuestion = self.player.arrayToShow[self.missingIndices[self.questionNumber]]
        self.currentQuestion.mark_as_question()

    def handle_touched_symbol(self, symbol):
        """
        Ueberprueft ausgewaehltes Symbol mit abgefragtem Symbol, akustischen/visuelles Feedback für falssch oder richtig
        :param symbol: ausgewaehltes Symbol aus Tilebar
        """

        # print("RemScreen handle_touched_symbol()")
        self.player.arrayToShow[self.missingIndices[self.questionNumber]].reset()

        print "gesuchtes Symbol: {} - ausgewaehltes Symbol: {}"\
            .format(self.currentQuestion, Figure(symbol.form, symbol.color))

        # check if same color and form as currentQuestion
        if symbol.color == self.currentQuestion.originColor and symbol.form == self.currentQuestion.originForm:
            rightSound = self.app.soundMachine.get_right_sound()
            self.app.soundMachine.play_the_sound(rightSound)
            self.player.arrayToShow[self.missingIndices[self.questionNumber]].mark_as_right()
            self.player.add_points()
            self.rightAnswers += 1
        else:
            wrongSound = self.app.soundMachine.get_wrong_sound()
            self.app.soundMachine.play_the_sound(wrongSound)
            self.player.arrayToShow[self.missingIndices[self.questionNumber]].mark_as_wrong()
            self.wrongAnswers += 1

        self.questionNumber += 1
        # if more Questions exist, move on
        if self.questionNumber < self.missingIndices.__len__():
            self.show_next_question()
        else:
            # print("RemScreen handle_touched_symbol() no questions left")
            Clock.schedule_once(self.show_resultscreen, 0.4)

        self.update_progressbar()  #
        self.update_labels()
        self.update_playground()

    def show_next_question(self):
        # print("RemScreen show_next_question()")
        self.currentQuestion = self.player.arrayToShow[self.missingIndices[self.questionNumber]]
        self.currentQuestion.mark_as_question()

        self.update_tilebar()
        self.show_tilebar()

    def update_progessbar_for_levelchange(self, dt=0):
        """
        Zuruecksetzen der Progressbar bei Levelaufstieg, akustischen/visuelles Feedback
        """
        self.levelpoint_limits = self.player.get_levelpoints_min_max()
        self.progressmax = self.player.get_pointdifference_to_next_level()
        self.progresspoints = 0
        self.animate_level_up_label()

        levelUpSound = App.get_running_app().soundMachine.get_level_up_sound()
        App.get_running_app().soundMachine.play_the_sound(levelUpSound)

        self.player.game.set_level_and_points_in_store(self.settings, self.player)

        # print "level up"
        # print "update_progessbar_for_levelchange",self.progressmax, self.progresspoints,self.levelpoint_limits

    def animate_level_up_label(self):
        """
        Ein- und Ausfaden des Next-Level-Labels
        """
        anim = Animation(opacity=1, duration=.2) + Animation(opacity=1, duration=.8) + Animation(opacity=0, duration=.5)
        anim.start(self.header.levelUpLabel)

    def update_playground(self):
        # print("RemScreen update_playground()")
        self.playgroundGrid.remove_tile_in_grid()
        self.playgroundGrid.show_all_tiles()

    def update_tilebar(self, dt=0):
        # print("RemScreen remove_tilebar()")
        self.remove_element(self.tilebarGrid)
        self.tilebarGrid = TileBarGrid()
        self.tilebarGrid.set_game_and_config(self.player, self.gameConfig)
        self.add_element(self.layout, self.tilebarGrid)

    def show_tilebar(self):
        # print("RemScreen show_tilebar()")
        print "{}. Fragezeichen: {}".format(self.questionNumber+1, self.player.arrayToShow[self.missingIndices[self.questionNumber]])

        self.tilebarGrid.show_tiles_to_choose(
            self.player.arrayToShow[self.missingIndices[self.questionNumber]])

    def show_resultscreen(self, dt=0):
        """
        Wenn Challange beendet ist, Weiterleitung auf ResultScreen
        """
        # print("RemScreen show_resultscreen()")
        self.sm.get_screen(self.gameConfig.MEMORIZE_NAME).update_labels()
        self.finished_screen()
        Clock.schedule_once(partial(self.remove_element, self.tilebarGrid), 0.3)
        Clock.schedule_once(self.set_result_screen, .1)

    def set_result_screen(self, dt=0):

        self.sm.get_screen(self.gameConfig.RESULT_NAME).set_result_text("suuuuper!\n Gedächtnisleistung:",
                                                                        self.rightAnswers, self.wrongAnswers)
        self.sm.current = self.gameConfig.RESULT_NAME
        self.header.opacity = 0


class ResultScreen(Screen):
    """
    Zeigt Ergebnis der abgefragten Spielkarten in Prozent
    """
    result_text = StringProperty("")
    result_percent = StringProperty("")

    def __init__(self, settings, player, name):
        # print "ResultScreen init()"
        self.player = player
        self.settings = settings
        super(ResultScreen, self).__init__()

    def set_result_text(self, text, right, wrong):
        if wrong > 0:
            percent = float(right) / float(wrong + right) * 100
        else:
            percent = 100

        if percent == 100:
            self.result_text = self.player.game.RESULT_STRING[2]
        elif percent >= 50:
            self.result_text = self.player.game.RESULT_STRING[1]
        elif percent < 50:
            self.result_text = self.player.game.RESULT_STRING[0]

        self.result_percent = "%8.2f" % percent

    def on_enter(self, *args):
        self.player.game.set_level_and_points_in_store(self.settings, self.player)
