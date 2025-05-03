import arcade

from games.IGame import IGame
from games.small_game import SmallGame
from games.IstanbulCat.istanbul_cat import IstanbulCat

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Game Menu"

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.games = [SmallGame(), IstanbulCat()]
        self.title_text = arcade.Text("Select a game:", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                                      arcade.color.WHITE, font_size=20, anchor_x="center")
        self.game_texts = [
            arcade.Text(f"{i + 1}. {game.get_name()}", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150 - i * 30,
                        arcade.color.WHITE, font_size=16, anchor_x="center")
            for i, game in enumerate(self.games)
        ]

    def on_draw(self):
        self.clear()
        self.title_text.draw()
        for game_text in self.game_texts:
            game_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1 and len(self.games) > 0:
            self.games[0].run(self.window)
        if key == arcade.key.KEY_2 and len(self.games) > 0:
            self.games[1].run(self.window)

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.menu_view = MenuView()
        self.menu_view.window = self
        self.show_view(self.menu_view)

if __name__ == "__main__":
    window = GameWindow()
    arcade.run()
