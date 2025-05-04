import arcade

from games.IGame import IGame
from games.europa.europa_game import EuropaGame
from games.japan_game.japan_game import JapanGame
from games.usa_game.usa_game import USAGame
from games.menu.game_menu import GameMenu
from games.Antartica.antartica_game import AntarticaGame
from games.Africa.africa_game import AfricaGame

class GameWindow(arcade.Window):
    def __init__(self):

        screen_width, screen_height = arcade.get_display_size()
        super().__init__(screen_width, screen_height, "EPITECH JAM TRAVEL", fullscreen=True)
        self.playable_games = [
            EuropaGame(),
            JapanGame(),
            USAGame(),
            AntarticaGame(),
            AfricaGame(),
        ]
        self.game_menu_view = GameMenu(self.playable_games, self)
        self.game_menu_view_instance = self.game_menu_view
        self.show_view(self.game_menu_view)


if __name__ == "__main__":
    window = GameWindow()
    arcade.run()
