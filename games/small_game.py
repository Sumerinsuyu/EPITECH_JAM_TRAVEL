import arcade
from games.IGame import IGame

from arcade.types import Color

class SmallGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.running_text = arcade.Text("Small Game Running", 100, 300, arcade.color.WHITE, 24)

    def on_draw(self):
        self.clear()
        self.running_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Access the stored menu view instance to return
            if hasattr(self.window, 'game_menu_view_instance'):
                self.window.show_view(self.window.game_menu_view_instance)
            else:
                print("Error: Could not find game_menu_view_instance on window to return.")

    def run(self, window):
        window.show_view(self)

    def get_name(self):
        return "Small Game"

    def get_color(self):
        return Color(254, 0,  0)