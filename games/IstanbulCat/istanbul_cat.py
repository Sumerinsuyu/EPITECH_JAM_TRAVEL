import arcade

from arcade.types import Color
from games.IGame import IGame
from games.IstanbulCat.player import Player

class IstanbulCat(IGame, arcade.View):

    def __init__(self):
        super().__init__()
        self.player = Player("WIWIWI", (200, 300))

    def run(self, window):
        window.show_view(self)

    def get_name(self):
        return "Istanbul Cat"

    def get_color(self):
        return Color(255, 0, 0)

    def on_draw(self):
        self.clear()
        arcade.draw_lbwh_rectangle_filled(
            self.player.position[0],
            self.player.position[1],
            self.player.size[0],
            self.player.size[1],
            self.player.color
        )
