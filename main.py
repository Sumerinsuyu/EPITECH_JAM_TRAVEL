import arcade
from games.IGame import IGame
from games.small_game import SmallGame
from games.europa.europa_game import EuropaGame # Corrected import path
from games.menu.game_menu import GameMenu

class GameWindow(arcade.Window):
    def __init__(self):
        # Get screen dimensions for fullscreen
        screen_width, screen_height = arcade.get_display_size()
        super().__init__(screen_width, screen_height, "EPITECH JAM TRAVEL", fullscreen=True)

        # Define the list of actual playable games
        self.playable_games = [
            SmallGame(),
            EuropaGame() # Add the new Europa game instance
        ]

        # Instantiate the GameMenu, passing the list of games and the window
        self.game_menu_view = GameMenu(self.playable_games, self)
        # Store the menu view instance on the window for games to access
        # This is crucial for games to be able to return to the menu
        self.game_menu_view_instance = self.game_menu_view

        # Show the GameMenu view immediately
        self.show_view(self.game_menu_view)


if __name__ == "__main__":
    window = GameWindow()
    arcade.run()
