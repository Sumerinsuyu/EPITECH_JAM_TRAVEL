import arcade

from arcade.types import Color
from games.IGame import IGame
from games.IstanbulCat.player import Player, IDLE, JUMP, RUN
from arcade.types import LBWH, LRBT, XYWH, Color, Point2List, Rect, RGBOrA255

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FLOOR = 90

def create_rect(x, y, width, height):
    return Rect(x, width, height, y, width, height, width / 2, height / 2)

class IstanbulCat(IGame, arcade.View):

    def __init__(self):
        super().__init__()
        self.player = Player("WIWIWI", (200, FLOOR))
        self.isOver = False
        self.background_texture = arcade.load_texture("games/IstanbulCat/assets/istanbul_background.png")
        self.background_rect = create_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background_rect2 = Rect(
            SCREEN_WIDTH,
            SCREEN_WIDTH * 2,
            SCREEN_HEIGHT,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_WIDTH + SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2
        )

    def run(self, window):
        window.show_view(self)

    def get_name(self):
        return "Istanbul Cat"

    def get_color(self):
        return Color(254, 0, 0)

    def on_draw(self):
        self.clear()
        self.draw_moving_background()

        arcade.draw_lbwh_rectangle_filled(
            self.player.position[0],
            self.player.position[1],
            self.player.size[0],
            self.player.size[1],
            self.player.color
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.player.state = JUMP
            print("JUMPING")

    def draw_moving_background(self):
        # Move both background rectangles left
        self.background_rect = self.background_rect.move(-2, 0)
        self.background_rect2 = self.background_rect2.move(-2, 0)

        # If a background has moved completely off screen, reset it to the right
        if self.background_rect.right <= 0:
            self.background_rect = Rect(
            SCREEN_WIDTH,
            SCREEN_WIDTH * 2,
            SCREEN_HEIGHT,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_WIDTH + SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2
        )

        if self.background_rect2.right <= 0:
            self.background_rect2 = Rect(
            SCREEN_WIDTH,
            SCREEN_WIDTH * 2,
            SCREEN_HEIGHT,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_WIDTH + SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2
        )

        # Draw both background textures
        arcade.draw_texture_rect(self.background_texture, self.background_rect)
        arcade.draw_texture_rect(self.background_texture, self.background_rect2)