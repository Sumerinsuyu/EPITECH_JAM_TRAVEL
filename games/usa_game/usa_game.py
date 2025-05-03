import arcade
import os
import random
from typing import Tuple
from games.IGame import IGame
from arcade.types import Rect

class USAGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()

        self.title = "USA - Duck Hunt"
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")
        self.score = 0
        self.duck_list = arcade.SpriteList()

        self.duck_spawn_interval = 2.0
        self.spawn_timer = 0
        self.max_ducks = 5
        self.ducks_spawned = 0
        self.bullets = 5
        self.game_over = False
        self.game_over_message = ""

        self.background_texture = None
        self.background_rect = None
        self.duck_texture_path = os.path.join(self.assets_path, "duck.png")
        self.shot_sound = None

        self._load_assets()

    def _load_assets(self):
        try:
            self.background_texture = arcade.load_texture(
                os.path.join(self.assets_path, "usabg.jpg")
            )
        except FileNotFoundError:
            print(f"Warning: Background file not found at {os.path.join(self.assets_path, 'usabg.jpg')}")
            self.background_texture = None
        try:
            self.shot_sound = arcade.load_sound(os.path.join(self.assets_path, "shot.wav"))
        except FileNotFoundError:
             print(f"Warning: Shot sound file not found at {os.path.join(self.assets_path, 'shot.wav')}")
             self.shot_sound = None
        except Exception as e:
            print(f"Error loading shot sound: {e}")
            self.shot_sound = None

    def get_name(self) -> str:
        return "Duck Hunt USA"

    def get_color(self) -> Tuple[int, int, int]:
        return (255, 255, 255)

    def run(self, window: arcade.Window):
        self.window = window
        self.setup()
        window.show_view(self)


    def setup(self):
        self.score = 0
        self.duck_list = arcade.SpriteList()
        self.spawn_timer = 0
        self.ducks_spawned = 0
        self.bullets = 10
        self.game_over = False
        self.game_over_message = ""
        if self.window:
            self.window.set_mouse_visible(True)
            self.window.set_exclusive_mouse(False)
            if self.background_texture:
                 self.background_rect = Rect(0, self.window.width, self.window.height, 0, self.window.width, self.window.height, self.window.width / 2, self.window.height / 2)
            else:
                 arcade.set_background_color(arcade.color.SKY_BLUE)
        else:
            print("Warning: setup() called without a window reference.")
    def on_show_view(self):
        """Called when switching to this view."""
        self.setup()

    def on_draw(self):
        self.clear()
        if self.background_texture and self.background_rect:
            arcade.draw_texture_rect(self.background_texture, self.background_rect)
        else:
            pass
        if self.window:
            arcade.draw_text(f"Score: {self.score}", 10, self.window.height - 70, arcade.color.WHITE, 50)
            self.duck_list.draw()
            if self.game_over:
                arcade.draw_text(
                    self.game_over_message,
                    self.window.width / 2,
                    self.window.height / 2,
                    arcade.color.WHITE,
                    font_size=40,
                    anchor_x="center",
                    anchor_y="center",
                    multiline=True,
                    width=self.window.width * 0.8
                )
        else:
             arcade.draw_text("Error: Window not available", 100, 100, arcade.color.RED, 20)

    def on_update(self, delta_time: float):
        if self.game_over or not self.window:
            return
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.duck_spawn_interval and self.ducks_spawned < self.max_ducks:
            duck = arcade.Sprite(self.duck_texture_path, scale=0.37)
            duck.center_x = 0
            duck.center_y = random.randint(200, self.window.height - 50)
            duck.change_x = random.randint(10, 30)
            self.duck_list.append(duck)
            self.spawn_timer = 0
            self.ducks_spawned += 1
        self.duck_list.update()
        ducks_to_remove = []
        for duck in self.duck_list:
            if duck.left > self.window.width:
                ducks_to_remove.append(duck)
        for duck in ducks_to_remove:
             self.duck_list.remove(duck)
        if self.ducks_spawned == self.max_ducks and len(self.duck_list) == 0:
            self.game_over = True
            self.game_over_message = f"Game Over! Score: {self.score}\nPress SPACE to return to menu"

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over or self.bullets <= 0:
            return
        self.bullets -= 1
        if self.shot_sound:
            arcade.play_sound(self.shot_sound)
        hit_duck = None
        for duck in self.duck_list:
            if duck.collides_with_point((x, y)):
                hit_duck = duck
                break
        if hit_duck:
            self.duck_list.remove(hit_duck)
            self.score += 1
        game_ended = False
        if self.bullets == 0 and not self.game_over:
            self.game_over = True
            self.game_over_message = f"Out of Bullets! Score: {self.score}\nPress SPACE to return to menu"
            game_ended = True
        if not game_ended and self.ducks_spawned == self.max_ducks and len(self.duck_list) == 0 and not self.game_over:
             self.game_over = True
             self.game_over_message = f"Game Over! Score: {self.score}\nPress SPACE to return to menu"

    def on_key_press(self, key, modifiers):
        """Handle keyboard input."""
        if self.game_over and key == arcade.key.SPACE:
            self._return_to_menu(save_score=True)
        elif key == arcade.key.ESCAPE:
             self._return_to_menu(save_score=False)
    def _return_to_menu(self, save_score: bool = False):
        """Return to the main game menu. Optionally save the score."""
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            print(f"{self.get_name()} finished. Score {'saved' if save_score else 'not saved'}: {self.score}")
            if save_score:
                self.window.last_game_score = self.score
            else:
                 self.window.last_game_score = 0
            self.window.show_view(self.window.game_menu_view_instance)
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close()
