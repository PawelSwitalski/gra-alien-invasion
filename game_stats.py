class GameStats:
    """Monitorowanie danych statystycznych w grze """

    def __init__(self, ai_settings):
        """Inicjalizacja danych statystycznych."""
        self.ai_settings = ai_settings
        self.reset_stats()

        # Uruchomienie gry "alien_invasion" w stanie nieaktywnym.
        self.game_active = False

        # Najlepszy wynik
        self.high_score = 0

    def reset_stats(self):
        """
        Inicjalizacja danych statycznych, które
        mogą zmienić się w trakcie gry.
        """
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 1
