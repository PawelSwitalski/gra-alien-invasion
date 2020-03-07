import sys
from time import sleep

import pygame

from bullet import Bullet
from alien import Alien


def check_keydown_events(event, **kwargs):
    """Reakcja na naciśnięcie klawisza"""
    ship = kwargs['ship']

    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(**kwargs)
    elif event.key == pygame.K_q:
        sys.exit()
    elif event.key == pygame.K_s:
        play_game(**kwargs)


def fire_bullet(ai_settings, screen, ship, bullets, **kwargs):
    """Wystrzelenie pocisku, jeśli nie przekroczono ustalonego limitu."""
    if len(bullets) < ai_settings.bullets_allowed:
        # Utworzenie pocisku i dodanie go do grupy pocisków
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keyup_events(event, ship):
    """Reakcja na zwolnienie klawisza"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(**kwargs):
    """Reakcja na zdarzenia generowane przez klawiaturę i mysz."""
    ship = kwargs['ship']

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, **kwargs)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(mouse_x, mouse_y, **kwargs)


def check_play_button(mouse_x, mouse_y, **kwargs):
    """Rozpoczęcie nowej gry po kliknięci przycisku Play przez urzytkownika."""
    button_clicked = kwargs['play_button'].rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and (not kwargs['stats'].game_active):
        play_game(**kwargs)


def play_game(ai_settings, aliens, bullets, sb, screen, ship, stats, **kwargs):
    """Rozpoczyna nową grę"""
    # Wyzerowanie ustawień dotyczących gry.
    ai_settings.initialize_dynamic_settings()
    # Ukrycue kursora myszy
    pygame.mouse.set_visible(False)
    # Wyzerowanie danych statystycznych gry
    stats.reset_stats()
    stats.game_active = True
    # Wyzerowanie obrazów tablicy wyników.
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_ships()
    # Usunięcie zawareiści list aliens i bullets
    aliens.empty()
    bullets.empty()
    # Utworzenie nowej floty i wyśrodkowanie statku
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()


def update_screen(**kwargs):
    """Uaktualnienie obrazów na ekranie i przejście do niwego ekranu."""
    ai_settings = kwargs['ai_settings']
    screen = kwargs['screen']
    stats = kwargs['stats']
    sb = kwargs['sb']
    ship = kwargs['ship']
    aliens = kwargs['aliens']
    bullets = kwargs['bullets']
    play_button = kwargs['play_button']

    # Odświeżanie ekranu w trakcie każdej iteracji pętli
    screen.fill(ai_settings.bg_color)

    # Ponowne wyświetlanie wszystkich pocisków pod warstwami
    # statku kosmicznego i obcych.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    # Wyświetlanie informacji o punktacji
    sb.show_score()

    # Wyświetlenie przycisku tylko wtedy, gdy gra jest nieaktywna.
    if not stats.game_active:
        play_button.draw_button()

    # Wyświetlani ostatnio zmodyfikowanego ekranu
    pygame.display.flip()


def update_bullets(**kwargs):
    """Uaktualnienie położenia pocisków i usunięcie tych niewidocznych na ekranie"""
    bullets = kwargs['bullets']

    # Uaktualnienie położenia pocisków.
    bullets.update()

    # Usuwanie pocisków, które znajdują się poza ekranem.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collision(**kwargs)


def check_bullet_alien_collision(ai_settings, screen, stats, sb, ship, aliens, bullets, **kwargs):
    """Reakcja na kolizję między pociskiem i obcym."""
    # Usuwanie wszystkich pocisków i obcych, między którymi doszło do kolizji.
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # Jeżeli cała flota zostaje zniszczona, gracz przechodzi na kolejny poziom.
        bullets.empty()
        ai_settings.increase_speed()

        # Inkrementacja numeru poziomu.
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)


def check_fleet_edges(ai_settings, aliens):
    """Odpowiednia reakcja, gdy obcy dotrze do krawędzi ekranu."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Przesunięcie całej floty w dół i zmiana kierunku, w którym się ona porusza"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Reakcja na uderzenie obcego w statek."""
    if stats.ships_left > 0:
        # Zmniejszenie wartości przechowywanej w ships_left.
        stats.ships_left -= 1

        # Uaktualnienie tablicy statków
        sb.prep_ships()

        # Usunięcie zawartości list aliens i bullets
        aliens.empty()
        bullets.empty()

        # Utworzenie nowej floty i wyśrodkowanie statku.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause.
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Sprawdzenie, czy którykolwiek obcy dotarł do dolnej krawędzi ekranu."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Tak samo jak w przypadku zderzenia statku z obcym.
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
            break


def update_aliens(ai_settings, stats, screen, sb, ship, aliens, bullets, **kwargs):
    """
    Sprawdzenie, czy flota znajduje się przy krawędzi ekranu,
    a następnie uaktualnienie położenia wszystkich obcych we flocie.
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Wykrywanie kolizji między obcym i statkiem.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)

    # Wyszukiwanie obcych docierających do dolnej krawędzi ekranu.
    check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)


def get_number_aliens_x(ai_settings, alien_width):
    """Ustawienie liczby obcych, którzy zmieszczą się w rzędzie"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """Ustalenie, ile rzędów obcych zmieści się na ekranie"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    alien_rows = int(available_space_y / (2 * alien_height))
    return alien_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Utworzenie obcego i umieszczenie go w rzędzie."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens, **kwargs):
    """Utworzenie pełnej floty obcych"""
    # Utworzenie obcego i ustalenie liczby obcych, którzy zmieszczą sie w rzędzie.
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    # Utworzenie  obcych.
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_high_score(stats, sb):
    """Sprawdzenie, czy mamy nowy najlepszy wynik osiągnięty dotąd w grze."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
