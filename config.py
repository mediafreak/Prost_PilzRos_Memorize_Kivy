#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Natalia Prost'
__author__ = 'Jenny Pilz-Rosenthal'

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager

import random
import os
from os.path import join


#########################################################################
#
# Color constants
# TODO Aenderung hier auch in screenwidgets.py > get_color_from_index() + config.py > __repr__
#
#########################################################################
WHITE_COLOR = 1, 1, 1
GREY_COLOR = .5, .5, .5
RED_COLOR = .8, 0, 0
GREEN_COLOR = 0, .8, 0
BLUE_COLOR = 0, 0, 1
CYAN_COLOR = 0, .8, .8
YELLOW_COLOR = 1, 1, 0
ORANGE_COLOR = 1, .5, .2
MAGENTA_COLOR = 1, 0, 1
PURPLE_COLOR = .5, 0, 1
BLACK_COLOR = 0, 0, 0
BABY_BLUE_COLOR = .4, .6, 1
LIGHT_GREEN_COLOR = .2, .9, .5
BABY_PINK_COLOR = 1, .6, .8
RED_WINE_COLOR = .4, 0, .2

# Hintergrund für richtige bzw. falsch gemerkte Symbole
WRONG_COLOR = 1, 0, 0
RIGHT_COLOR = 0, 1, 0

JSON_STORE_NAME = 'level_memorize.json'


class ScreenConfig(object):
    sm = ScreenManager()
    MAIN_NAME = 'main'
    MEMORIZE_NAME = 'memorize'
    REMEMBER_NAME = 'remember'
    RESULT_NAME = 'result'
    SETTINGS_NAME = 'settings'

    RESULT_STRING = ["Versuch’s weiter.", "Gut gemacht!", "Perfekt!"]


#########################################################################
#
# Settings from JsonStore
#
#########################################################################
class SettingsJsonStore(JsonStore):
    """
    beinhaltet Funktionen zum Speichern und Laden des Spielstands auf dem System des Spielers
    """

    DIFFICULTY_NAME = ["easy", "middle", "hard"]
    numberOfDifficulty = len(DIFFICULTY_NAME)

    DEFAULT_LEVEL = 1
    DEFAULT_POINTS = 0
    DEFAULT_CONFIG = 1
    DEFAULT_MODE = 0

    # defaultSettingsStoreData = None # fuer next Version siehe clear_store


    def __init__(self, filename, **kwargs):
        self.fileName = join(App.get_running_app().user_data_dir, filename)
        self.settingsStore = JsonStore(self.fileName)
        super(SettingsJsonStore, self).__init__(filename, **kwargs)
        print "geladener Spielstand:",self.settingsStore._data

    def get_config_from_store_and_set(self):
        storeExists = "config" in self.settingsStore
        # storeExists = self.settingsStore.store_exists("config") # alternative Schreibweise
        if storeExists is True:
            # Spieler kann mit zuletzt gespielter Schwierigkeitsstufe starten
            self.initConfig = self.settingsStore["config"]["difficulty"]
        else:
            self.set_default_store()

        return self.initConfig

    def set_default_store(self):
        """
        erzeugt neuen JsonStore mit initialen Werten
        """

        # initiale Werte für Anzeige in SettingScreen
        self.level = self.DEFAULT_LEVEL
        self.points = self.DEFAULT_POINTS
        self.initMode = self.DEFAULT_MODE
        self.initConfig = self.DEFAULT_CONFIG

        # nach reset des Spielstands müssen alle Werte zurückgesetzt werden
        for i in range(0, self.numberOfDifficulty):
            self.settingsStore.put(str(i), index=i,
                                   name=self.DIFFICULTY_NAME[i],
                                   points=self.DEFAULT_POINTS,
                                   level=self.DEFAULT_LEVEL,
                                   mode=self.DEFAULT_MODE)
        self.settingsStore.put("config", difficulty=self.DEFAULT_CONFIG)

        # self.defaultSettingsStoreData =  self.settingsStore._data # fuer next Version siehe clear_store

    def load_level_and_points_from_store(self):
        # print "load_level_from_store",self.initConfig, self.settingsStore, str(self.initConfig) in self.settingsStore
        storeId = str(self.initConfig)
        self.level = self.settingsStore[storeId]["level"]
        self.points = self.settingsStore[storeId]["points"]

        return {'level': self.level, 'points': self.points}

    def load_mode_from_store(self):
        # print "load_mode_from_store",self.initConfig
        storeId = str(self.initConfig)
        self.initMode = self.settingsStore[storeId]["mode"]

        return self.initMode

    def save_level_and_points_in_store(self, player):
        storeId = str(self.initConfig)
        storeExists = storeId in self.settingsStore
        # storeExists = self.settingsStore.store_exists(storeId) # alternative Schreibweise

        if storeExists is True:
            self.settingsStore.put(storeId, index=int(self.initConfig),
                                   name=self.DIFFICULTY_NAME[self.initConfig],
                                   points=player.points,
                                   level=player.level,
                                   mode=self.initMode)
            self.settingsStore.put("config", difficulty=self.initConfig)
            print "gesicherter Spielstand:",self.settingsStore._data

    def save_config_in_store(self, config):
        """
        speichert den zuletzt gewählten Schwierigkeitsgrad in den JsonStore
        """
        self.initConfig = config
        self.settingsStore.put("config", difficulty=self.initConfig)

    # TODO fuer next Version > ueberpruefe, ob zu loeschender Store == default Store > wenn ja, ist reset-button inaktiv
    def clear_store(self):
        # print self.settingsStore._is_changed
        # if not self.defaultSettingsStoreData is self.settingsStore._data:
        self.settingsStore.store_clear()


#########################################################################
#
# Default GameConfig
#
#########################################################################
class GameConfig(ScreenConfig):
    """
    enthält die Konfigurationsdaten des Spiels in der mittleren Schwierigkeitsstufe
    """

    CONFIG_CLASS_NAME = "Normale Schwierigkeitsstufe"

    DEFAULT_COLUMNS = 5
    DEFAULT_ROWS = 3
    DEFAULT_MAX_CARDS = DEFAULT_COLUMNS * DEFAULT_ROWS
    DEFAULT_MAX_TILEBAR_CARDS = 7

    DEFAULT_MAX_FORMS = 12
    DEFAULT_MAX_COLORS = 12
    DEFAULT_FORMS = 3
    DEFAULT_COLORS = 3

    DEFAULT_NUMBER_CARDS = 3
    DEFAULT_FAKTOR_FOR_HIDDEN_CARDS = 2.0 / 3.0
    DEFAULT_NUMBER_HIDDEN_CARDS = int(DEFAULT_NUMBER_CARDS * DEFAULT_FAKTOR_FOR_HIDDEN_CARDS)
    DEFAULT_NUMBER_TILEBAR_CARDS = 3
    DEFAULT_MODULO = 5  # jedes zweite Level verändert sich etwas s. Player.increase_level()

    # Reihenfolge der zu befüllenden GridLayout Zellen (s. Player.create_actual_array)
    DEFAULT_CARDORDER = [6, 7, 8, 12, 2, 5, 9, 11, 3, 1, 13, 10, 14, 0, 4]

    DEFAULT_TIME = 200

    necessaryCorrectAnswers = 5

    arrayToShow = []

    def __init__(self):
        # print "GameConfig init()"
        super(GameConfig, self).__init__()

    # getter-Methoden ermöglichen Polymorphie
    def get_max_number_of_cards(self):
        return self.DEFAULT_COLUMNS * self.DEFAULT_ROWS

    def get_number_of_columns(self):
        return self.DEFAULT_COLUMNS

    def get_number_of_rows(self):
        return self.DEFAULT_ROWS

    def get_number_of_forms(self):
        return self.DEFAULT_FORMS

    def get_number_of_colors(self):
        return self.DEFAULT_COLORS

    def get_number_of_cards(self):
        return self.DEFAULT_NUMBER_CARDS

    def get_factor_for_hidden_cards(self):
        return self.DEFAULT_FAKTOR_FOR_HIDDEN_CARDS

    def get_number_of_hidden_cards(self):
        return self.DEFAULT_NUMBER_HIDDEN_CARDS

    def get_number_of_tilebar_cards(self):
        return self.DEFAULT_NUMBER_TILEBAR_CARDS

    def get_number_of_modulo(self):
        return self.DEFAULT_MODULO

    def get_cardorder(self):
        return self.DEFAULT_CARDORDER

    def get_default_time(self):
        return self.DEFAULT_TIME

    def get_necessary_correct_answers(self):
        return self.necessaryCorrectAnswers

    def __repr__(self):
        return  "{}: {}x{} mit {}".format(self.CONFIG_CLASS_NAME, self.DEFAULT_COLUMNS, self.DEFAULT_ROWS, self.DEFAULT_CARDORDER)


    ###############
    #
    # Settings
    #
    ###############
    def get_level_and_points_from_store(self, store):
        # print "get_level_from_store",store
        levelAndPointsFromStore = store.load_level_and_points_from_store()
        self.level = levelAndPointsFromStore['level']
        self.points = levelAndPointsFromStore['points']

    def get_mode_from_store(self, store):
        # print "get_mode_from_store",store
        self.initMode = store.load_mode_from_store()['mode']
        # print ">>>> mode", self.initMode

    @staticmethod
    def set_level_and_points_in_store(store, player):
        # print "set_level_and_points_in_store",store
        store.save_level_and_points_in_store(player)

    @staticmethod
    def set_config_in_store(store, config_id):
        # print "set_config_in_store",store, config_id
        store.save_config_in_store(config_id)

    @staticmethod
    def reset_score(store):
        # print "reset_score"
        store.clear_store()
        store.set_default_store()


class EasyConfig(GameConfig):
    """
    enthält die Konfigurationsdaten des Spiels in der einfachen Schwierigkeitsstufe
    """

    CONFIG_CLASS_NAME = "Einfache Schwierigkeitsstufe"

    DEFAULT_COLUMNS = 4
    DEFAULT_ROWS = 3

    # Reihenfolge angepasst auf 4x3 Feld
    DEFAULT_CARDORDER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    DEFAULT_MODULO = 6  # langsamer Schwierigkeitszuwachs s. Player.increase_level()


    # Überschreiben der normalen Konfigurations-Getter
    def get_number_of_columns(self):
        return self.DEFAULT_COLUMNS

    def get_number_of_rows(self):
        return self.DEFAULT_ROWS

    def get_number_of_forms(self):
        return self.DEFAULT_FORMS - 1

    def get_number_of_colors(self):
        return self.DEFAULT_COLORS - 1

    def get_number_of_cards(self):
        return self.DEFAULT_NUMBER_CARDS - 1

    def get_number_of_hidden_cards(self):
        return self.DEFAULT_NUMBER_HIDDEN_CARDS - 1

    def get_number_of_tilebar_cards(self):
        return self.DEFAULT_NUMBER_TILEBAR_CARDS - 1

    def get_cardorder(self):
        return self.DEFAULT_CARDORDER


class HardConfig(GameConfig):
    """
    enthält die Konfigurationsdaten des Spiels in der schwierigsten Spielstufe
    """

    CONFIG_CLASS_NAME = "Hohe Schwierigkeitsstufe"

    DEFAULT_COLUMNS = 7
    DEFAULT_ROWS = 4

    # Reihenfolge angepasst auf 7x4 Feld
    DEFAULT_CARDORDER = [10, 17, 9, 11, 16, 18, 8, 12, 15, 19, 1, 26, 2, 25, 22, 5, 23, 4, 3, 24, 7, 13, 14, 20, 0, 21,
                         6, 27]

    DEFAULT_MODULO = 4  # schneller Schwierigkeitszuwachs s. Player.increase_level()


    # Überschreiben der normalen Konfigurations-Getter
    def get_max_number_of_cards(self):
        return self.DEFAULT_COLUMNS * self.DEFAULT_ROWS

    def get_number_of_columns(self):
        return self.DEFAULT_COLUMNS

    def get_number_of_rows(self):
        return self.DEFAULT_ROWS

    def get_number_of_forms(self):
        return self.DEFAULT_FORMS + 2

    def get_number_of_colors(self):
        return self.DEFAULT_COLORS + 2

    def get_number_of_cards(self):
        return self.DEFAULT_NUMBER_CARDS + 1

    def get_number_of_hidden_cards(self):
        return self.DEFAULT_NUMBER_HIDDEN_CARDS + 1

    def get_number_of_tilebar_cards(self):
        return self.DEFAULT_NUMBER_TILEBAR_CARDS + 1

    def get_cardorder(self):
        return self.DEFAULT_CARDORDER


CONFIG_CLASS_NAME = [EasyConfig(), GameConfig(), HardConfig()]


class Player(object):
    """
    beinhaltet Controller-Funktionen des Spiels in Abhängigkeit vom aktuellen Spielfortschritt
    """

    def __init__(self, config, settings):
        # print "Player init"
        self.game = config
        self.numberOfPlaygroundCards = config.get_number_of_cards()
        self.numberOfTilebarCards = config.get_number_of_tilebar_cards()
        self.increaseModulo = config.get_number_of_modulo()
        self.numberOfHiddenCards = config.get_number_of_hidden_cards()
        self.numberOfForms = config.get_number_of_forms()
        self.numberOfColors = config.get_number_of_colors()
        self.level_temp = settings.level
        self.level = settings.DEFAULT_LEVEL
        self.points = settings.points

        print self.game
        print "Spielstand: Level {} - {} Punkte".format(self.level, self.points)

        for x in range(0, self.level_temp - 1):
            self.increase_level()

    def initialize_game(self):
        self.create_actual_array()

    def create_actual_array(self):
        """
        erstellt Symbole mit zufälliger Form und Farbe und fügt sie in der Reihenfolge ihrer Erzeugung in ein Array ein
        """
        # print "Player create_actual_array() "

        self.actual = []

        while not self.actual.__len__() == self.numberOfPlaygroundCards:

            randomForm = random.randint(1, self.numberOfForms)
            randomColor = random.randint(1, self.numberOfColors)
            newFigure = Figure(randomForm, randomColor)

            if str(newFigure) in str(self.actual):
                # print "Schon drin, neuer Versuch"
                continue
            else:
                self.actual.append(newFigure)

        ##### Für DOKU: Array mit allen vorhandenen Formen füllen
        # self.actual = []
        # self.numberOfPlaygroundCards = self.game.DEFAULT_MAX_FORMS
        # for x in range(0, self.game.DEFAULT_MAX_FORMS):
        #     newFigure = Figure(x+1, 9)
        #     self.actual.append(newFigure)

        ##### Für DOKU: Array mit allen vorhandenen Farben füllen
        # self.actual = []
        # self.numberOfPlaygroundCards = self.game.DEFAULT_MAX_COLORS
        # for x in range(0, self.game.DEFAULT_MAX_COLORS):
        #     newFigure = Figure(1, x+1)
        #     self.actual.append(newFigure)

        self.create_array_with_cardorder()

    def create_array_with_cardorder(self):
        """
        sortiert die Symbole entsprechend der Reihenfolge zum Anzeigen im GridLayout von oben links nach unten rechts
        """
        # print "Player create_actual_array()"

        self.arrayToShow = []
        for x in range(0, self.game.get_max_number_of_cards()):
            self.arrayToShow.append(None)

        for x in range(0, self.numberOfPlaygroundCards):
            self.arrayToShow[self.game.DEFAULT_CARDORDER[x]] = self.actual[x]

        print "MemorizeApp Symbolfolge:", self.actual
        print "Array in Reihenfolge von links oben nach rechts unten:", self.arrayToShow

    def increase_level(self):
        # print "config increase_level()", self.numberOfPlaygroundCards

        self.level += 1

        if self.level % self.increaseModulo == 0 and \
                not self.numberOfPlaygroundCards == self.game.get_max_number_of_cards():
            self.numberOfPlaygroundCards += 1

        if self.level % self.increaseModulo == (self.game.get_number_of_modulo() - 1) and \
                not self.numberOfForms == self.game.DEFAULT_MAX_FORMS:
            self.numberOfForms += 1

        if self.level % self.increaseModulo == (self.game.get_number_of_modulo() - 2) and \
                not self.numberOfColors == self.game.DEFAULT_MAX_COLORS:
            self.numberOfColors += 1

        self.numberOfHiddenCards = int(self.numberOfPlaygroundCards * self.game.get_factor_for_hidden_cards())

        if self.level % self.increaseModulo == (self.game.get_number_of_modulo() - 3) and \
                not self.numberOfTilebarCards == self.game.DEFAULT_MAX_TILEBAR_CARDS:
            self.numberOfTilebarCards += 1

        print "Level erhöht: {} Karten, {} verdeckte Karten, {} mögliche Formen, {} mögliche Farben, {} Auswahlkarten"\
            .format(self.numberOfPlaygroundCards, self.numberOfHiddenCards,
                    self.numberOfForms, self.numberOfColors, self.numberOfTilebarCards)

    def add_points(self):
        # print "add_points"
        self.points += (self.level + 1)

        if self.points >= self.get_levelpoints_min_max()['upperBound']:
            self.increase_level()

    def get_pointdifference_to_next_level(self):
        """
        für Max-Wert der ProgressBar in KV-Datei
        """
        distance = (self.level + 1) * self.game.get_necessary_correct_answers()
        # print "get_pointdifference_to_next_level", distance
        return distance

    def get_levelpoints_min_max(self):
        """
        gibt untere und obere Punktegrenzen des aktuellen Levels als Array zurück; wichtig für ProgressBar
        """
        distance = (self.level + 1) * self.game.get_necessary_correct_answers()

        n = self.level - 1
        # 0,2,5,9,14,20,27...-Folge > (n+1)*(n+2)/2-1 oder (.5*n+1.5)*n
        lowerBound = int((.5 * n + 1.5) * n) * self.game.get_necessary_correct_answers()
        upperBound = lowerBound + distance
        return {'lowerBound': lowerBound, 'upperBound': upperBound}


#########################################################################
#
# Figuren/Symbole
#
#########################################################################
class Figure(object):
    colorOfBackground = BLACK_COLOR

    statusAnswer = 0

    def __init__(self, form, color):
        # print("Figure __init__()")
        self.form = form
        self.color = color
        self.originColor = color
        self.originForm = form

    def mark_as_hidden(self):
        # #print("Figure mark_as_hidden()", self)
        self.color = 0
        self.form = 0

    def mark_as_question(self):
        # #print("Figure mark_as_question()", self)
        self.color = -1
        self.form = -1

    def mark_as_right(self):
        # #print("Figure mark_as_right()", self)
        self.statusAnswer = True
        self.colorOfBackground = RIGHT_COLOR

    def mark_as_wrong(self):
        # #print("Figure mark_as_wrong()", self)
        self.statusAnswer = False
        self.colorOfBackground = WRONG_COLOR

    def reset(self):
        # #print("Figure reset()", self)
        self.color = self.originColor
        self.form = self.originForm

    def get_origin_copy(self):
        # #print("Figure get_origin_copy()", self)
        copy = Figure(self.originForm, self.originColor)
        return copy

    def __repr__(self):
        """
        Stringrepräsentation der Figuren mit Form und Farbe
        """

        formText = ""
        colorText = ""
        if self.originForm == 1:
            formText = "Kreis"
        elif self.originForm == 2:
            formText = "Quadrat"
        elif self.originForm == 3:
            formText = "gleichseitiges Dreieck"
        elif self.originForm == 4:
            formText = "rechtwinkliges Dreieck"
        elif self.originForm == 5:
            formText = "ungefuellter Kreis"
        elif self.originForm == 6:
            formText = "ungefuelltes Quadrat"
        elif self.originForm == 7:
            formText = "ungefuelltes gleichseitiges Dreieck"
        elif self.originForm == 8:
            formText = "ungefuelltes rechtwinkliges Dreieck"
        elif self.originForm == 9:
            formText = "leerer Mund"
        elif self.originForm == 10:
            formText = "Ring"
        elif self.originForm == 11:
            formText = "Pacman"
        elif self.originForm == 12:
            formText = "Kreuz"
        else:
            formText = "Form unbekannt"

        # if self.form == 0:
        #     formText = "Fragezeichen"
        #     return formText

        if self.originColor == 1:
            colorText = "rot"
        elif self.originColor == 2:
            colorText = "gruen"
        elif self.originColor == 3:
            colorText = "blau"
        elif self.originColor == 4:
            colorText = "cyan"
        elif self.originColor == 5:
            colorText = "magenta"
        elif self.originColor == 6:
            colorText = "gelb"
        elif self.originColor == 7:
            colorText = "lila"
        elif self.originColor == 8:
            colorText = "orange"
        elif self.originColor == 9:
            colorText = "babyblau"
        elif self.originColor == 10:
            colorText = "hellgruen"
        else:
            colorText = "Farbe unbekannt"

        return "{} ({})".format(formText, colorText)


class SoundMachine(object):
    """
    ermöglicht das Abspielen von Sound-Effekten
    """

    pathToSound = "sounds"

    # Sounds from http://soundbible.com
    rightSound = os.path.join(pathToSound, "right.wav")
    wrongSound = os.path.join(pathToSound, "wrong.wav")
    levelUpSound = os.path.join(pathToSound, "levelup.wav")

    def get_right_sound(self):
        # print "Soundmachine:",self.rightSound
        return self.load_the_sound(self.rightSound)

    def get_wrong_sound(self):
        return self.load_the_sound(self.wrongSound)

    def get_level_up_sound(self):
        return self.load_the_sound(self.levelUpSound)

    @staticmethod
    def load_the_sound(sound):
        # noinspection PyBroadException
        try:
            sound = SoundLoader.load(sound)
            return sound
        except:
            print "Soundmodul fehlt"

    @staticmethod
    def play_the_sound(sound):
        if sound:
            try:
                sound.play()
                pass
            except:
                print "Sound kann nicht abgespielt werden"
