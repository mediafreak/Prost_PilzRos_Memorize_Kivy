#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Natalia Prost'
__author__ = 'Jenny Pilz-Rosenthal'

from screens import *

from kivy.config import Config
from kivy.lang import Builder


Builder.load_file('symbol.kv')

#########################################################################
#
# MainClass of Game
#
#########################################################################
class MemorizeApp(App):
    gameConfig = GameConfig()
    #gameConfig = None
    sm = ObjectProperty(None)

    def build(self):
        """
        Holt aus geladenem JsonStore die zuletzt gespielte Schwierigkeitsstufe und setzt entsprechende GameConfig
        :return: Screenmanager - verwaltet Screens und deren Wechsel (Transitions)
        """
        print "MemorizeApp build()"

        self.configure_kivy_app()
        self.settings = SettingsJsonStore()
        self.soundMachine = SoundMachine()

        try:
            self.set_game_config( self.settings.get_config_from_store_and_set() )
            self.set_game_mode() # fuer geplanten Time-Mode
            self.sm = self.gameConfig.sm
            self.init_game()
            #Clock.schedule_once(self.init_game,.1)
        except:
            pass

        return self.sm


    def set_game_config(self, gameConfig):
        #print "set_gameConfig BEFORE", self.gameConfig
        self.gameConfig = CONFIG_CLASS_NAME[gameConfig]


    # für geplanten Wechsel zwischen Zen- und Time-Mode
    def set_game_mode(self):
        self.gameConfig.initMode = self.settings.load_mode_from_store()
        #print "initmode",self.settings.load_mode_from_store()


    def init_game(self):
        """
        Holt Punkte- und Levelstand aus JsonStore und erzeugt MainScreen und SettingsScreen
        """
        try:
            self.gameConfig.get_level_and_points_from_store(self.settings)
            self.gameConfig.get_mode_from_store(self.settings) # fuer geplanten Time-Mode
        except:
            pass

        self.sm.add_widget(MainScreen(name=self.gameConfig.MAIN_NAME))  # 0
        self.sm.add_widget(SettingsScreen(self.settings, self.gameConfig, name=self.gameConfig.SETTINGS_NAME)) # 1


    def start_game(self):
        """
        Player wird mit aktueller GameConfig und aktuellen Settings initialisiert.
        Erzeugt Screens für Memorize, Remember und Result mit notwendigen Parametern fuer Settings, Player bzw. GameConfig
        """
        self.player = Player(self.gameConfig, self.settings)
        #self.leftTime = self.gameConfig.get_default_time() # fuer geplanten Time-Mode
        #Clock.schedule_interval(self.decrease_time, 1)

        #print "start_game", self.gameConfig

        memScreen = MemorizeScreen(self.player, self.gameConfig)
        remScreen = RememberScreen(self.settings, self.player, self.gameConfig)

        self.sm.add_widget(memScreen)  # 2
        self.sm.add_widget(remScreen)  # 3
        self.sm.add_widget(ResultScreen(self.settings, self.player, name=self.gameConfig.RESULT_NAME))  # 4
        self.view = self.sm.screens[2]  # entry screen


    def restart_game(self):
        #print "reset game", sm.screens[3]
        self.gameConfig.get_level_and_points_from_store(self.settings)
        Clock.schedule_once(self.clear_screen, .5)


    def clear_screen(self, dt=0):
        """
        Loescht Memorize-, Remember- und ResultScreen fuer restart
        """
        self.sm.screens[4].clear_widgets()
        self.sm.remove_widget(self.sm.screens[4])
        self.sm.screens[3].clear_widgets()
        self.sm.remove_widget(self.sm.screens[3])
        self.sm.screens[2].clear_widgets()
        self.sm.remove_widget(self.sm.screens[2])


    # für geplanten Time-Mode
    def decrease_time(self, dt=0):
        self.leftTime -= 1


    @staticmethod
    def configure_kivy_app():
        """
        Konfiguration fuer das Kivy-Window, http://kivy.org/docs/api-kivy.player.html
        """
        Config.set('kivy', 'exit_on_escape', 1)
        Config.set('graphics', 'resizable', 0)
        Config.write()


#########################################################################
#
# Main Methode
#
#########################################################################
if __name__ == '__main__':
    MemorizeApp().run()