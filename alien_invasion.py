import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
import game_functions as gf


def run_game():
    # inicjalizacja Pygame, ustawień i obiektu ekranu
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Inwazja obcych")

    # Utworzenie przycisku Play.
    play_button = Button(ai_settings, screen, "Play")

    # Utworzenie egzemplarza przeznaczonego do przechowywania danych
    # statystycznych gry oraz utworzenie egzemplarza klasy Scoreboard.
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)

    # Utworzenie statku kosmicznego, grupy pocisków oraz grupy obcych.
    ship = Ship(ai_settings, screen)
    bullets = Group()
    aliens = Group()

    # Wszystkie obiekty gry
    kwargs = {'ai_settings': ai_settings, 'screen': screen, 'ship': ship,
              'aliens': aliens, 'stats': stats, 'sb': sb,
              'play_button': play_button, 'bullets': bullets}

    # Utworzenie floty obcych.
    gf.create_fleet(**kwargs)

    # Rozpoczęcie pętli głównej gry
    while True:
        gf.check_events(**kwargs)
        if stats.game_active:
            ship.update()
            gf.update_bullets(**kwargs)
            gf.update_aliens(**kwargs)

        gf.update_screen(**kwargs)


run_game()
