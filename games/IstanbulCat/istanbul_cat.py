import arcade

from arcade.types import Color
from games.IGame import IGame
from games.IstanbulCat.player import Player, JUMP, RUN, FALL
from games.IstanbulCat.ennemy import Ennemy
from arcade.types import LBWH, LRBT, XYWH, Color, Point2List, Rect, RGBOrA255
from random import randint

FLOOR           = 90
BG_SPEED        = -1

def create_rect(x, y, width, height):
    return Rect(x, width, height, y, width, height, width / 2, height / 2)

class IstanbulCat(IGame, arcade.View):

    def __init__(self):
        super().__init__()
        self.player = Player("WIWIWI", (200, FLOOR))
        self.player_pos_jump = FLOOR
        self.background_texture = arcade.load_texture("games/IstanbulCat/assets/istanbul_background.png")
        self.window_width = self.window.width
        self.window_height = self.window.height
        self.background_rect = create_rect(0, 0, self.window_width, self.window_height)
        self.background_rect2 = Rect(
            self.window_width,
            self.window_width * 2,
            self.window_height,
            0,
            self.window_width,
            self.window_height,
            self.window_width + self.window_width / 2,
            self.window_height / 2
        )
        self.ennemy = []
        self.is_ended = False
        self.score = 0
        for i in range(0, 5):
            self.ennemy.append(Ennemy("WIWIWI", (self.window_width + (i * randint(600, 900)), FLOOR)))

    def run(self, window):
        if self.check_end():
            self = self.__init__
            return 5
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
        self.update_ennemy()
        self.draw_ennemy()
        self.check_collision()
        self.check_end()
        if self.player.is_dead or self.is_ended:
            self.__init__()
            self._return_to_menu()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and self.player.state == RUN:
            self.player.state = JUMP
        if key == arcade.key.ESCAPE:
            self.__init__()
            self._return_to_menu()

    def draw_moving_background(self):
        self.background_rect = self.background_rect.move(BG_SPEED, 0)
        self.background_rect2 = self.background_rect2.move(BG_SPEED, 0)

        if self.background_rect.right <= 0:
            self.background_rect = Rect(
            self.window_width,
            self.window_width * 2,
            self.window_height,
            0,
            self.window_width,
            self.window_height,
            self.window_width + self.window_width / 2,
            self.window_height / 2
        )

        if self.background_rect2.right <= 0:
            self.background_rect2 = Rect(
            self.window_width,
            self.window_width * 2,
            self.window_height,
            0,
            self.window_width,
            self.window_height,
            self.window_width + self.window_width / 2,
            self.window_height / 2
        )

        arcade.draw_texture_rect(self.background_texture, self.background_rect)
        arcade.draw_texture_rect(self.background_texture, self.background_rect2)

    def update_player(self):
        if self.player.state == JUMP:
            position = list(self.player.position)
            position[1] += 4
            self.player.move(position[0], position[1])
            if self.player.position[1] >= FLOOR + 200:
                self.player.state = FALL
        if self.player.state == FALL:
            position = list(self.player.position)
            position[1] -= 4
            self.player.move(position[0], position[1])
            if self.player.position[1] <= FLOOR:
                self.player.state = RUN

    def draw_player(self):
        arcade.draw_texture_rect(self.player.texture, self.player.rect)

    def draw_ennemy(self):
        for dogs in self.ennemy:
            arcade.draw_texture_rect(dogs.texture, dogs.rect)

    def update_ennemy(self):
        for dogs in self.ennemy:
            position = list(dogs.position)
            position[0] -= 6
            dogs.move(position[0], position[1])

    def check_collision(self):
        for dog in self.ennemy:
            if (
                self.player.position[0] < dog.position[0] + dog.size[0] and
                self.player.position[0] + self.player.size[0] > dog.position[0] and
                self.player.position[1] < dog.position[1] + dog.size[1] and
                self.player.position[1] + self.player.size[1] > dog.position[1]
            ):
                self.player.is_dead = True

    def check_end(self):
        for dog in self.ennemy:
            if dog.position[0] > 0:
                return False
        self.is_ended = True
        self.score = 5
        return True

    def _return_to_menu(self, save_score: bool = False):
        """Return to the main game menu. Optionally save the score."""
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            print(f"{self.get_name()} finished. Score {'saved' if save_score else 'not saved'}: {self.score}")
            if save_score:
                # Use the calculated score based on fish count
                self.window.last_game_score = self.score
            else:
                 # Score is 0 if ESC is pressed or not saving
                 self.window.last_game_score = 0
            # Ensure the menu view instance exists before showing it
            menu_view = getattr(self.window, "game_menu_view_instance", None)
            if menu_view:
                self.window.show_view(menu_view)
            else:
                print("Error: game_menu_view_instance not found on window.")
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close() # Fallback: close window if menu is broken
