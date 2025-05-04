import arcade

from arcade.types import Color
from games.IGame import IGame
from games.IstanbulCat.player import Player, JUMP, RUN, FALL
from arcade.types import LBWH, LRBT, XYWH, Color, Point2List, Rect, RGBOrA255

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 600
FLOOR           = 90
BG_SPEED        = -2

def create_rect(x, y, width, height):
    return Rect(x, width, height, y, width, height, width / 2, height / 2)

class IstanbulCat(IGame, arcade.View):

    def __init__(self):
        super().__init__()
        self.player = Player("WIWIWI", (200, FLOOR))
        self.player_pos_jump = FLOOR
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
        self.update_player()
        self.draw_player()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and self.player.state == RUN:
            self.player.state = JUMP

    def draw_moving_background(self):
        self.background_rect = self.background_rect.move(BG_SPEED, 0)
        self.background_rect2 = self.background_rect2.move(BG_SPEED, 0)

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

        arcade.draw_texture_rect(self.background_texture, self.background_rect)
        arcade.draw_texture_rect(self.background_texture, self.background_rect2)

    def draw_player(self):
        arcade.draw_lbwh_rectangle_filled(
            self.player.position[0],
            self.player.position[1],
            self.player.size[0],
            self.player.size[1],
            self.player.color
        )

    def update_player(self):
        if self.player.state == JUMP:
            position = list(self.player.position)
            position[1] += 2
            self.player.position = tuple(position)
            if self.player.position[1] >= FLOOR + 100:
                self.player.state = FALL
        if self.player.state == FALL:
            position = list(self.player.position)
            position[1] -= 2
            self.player.position = tuple(position)
            if self.player.position[1] <= FLOOR:
                self.player.state = RUN
