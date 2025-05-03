import arcade
from games.IGame import IGame

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
            self.window.show_view(self.window.menu_view)

    def run(self, window):
        window.show_view(self)

    def get_name(self):
        return "Small Game"

    def get_color(self):
        return arcade.color.BLUE