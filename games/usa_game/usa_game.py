import arcade
import os
import random
from typing import Tuple
from games.IGame import IGame  # Suppose que tu as une interface IGame
from arcade.types import Rect

class USAGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()
        self.window.set_mouse_visible(True)
        self.window.set_exclusive_mouse(False)
        self.title = "USA - Duck Hunt"
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")
        self.score = 0
        self.duck_list = arcade.SpriteList()
        self.duck_speed = 10
        self.duck_spawn_interval = 2.0
        self.spawn_timer = 0

        self.background_texture = arcade.load_texture(
            os.path.join(self.assets_path, "usabg.jpg")
        )
        self.background_rect = Rect(0, self.window.width, self.window.height, 0, self.window.width, self.window.height, self.window.width / 2, self.window.height / 2)
        self.duck_texture_path = os.path.join(self.assets_path, "duck.png")
        self.shot_sound = None

        self._load_assets()

    def _load_assets(self):
        try:
            self.shot_sound = arcade.load_sound(os.path.join(self.assets_path, "shot.wav"))
        except:
            pass

    def get_name(self) -> str:
        return "Duck Hunt USA"

    def get_color(self) -> Tuple[int, int, int]:
        return (255, 255, 255)

    def run(self, window: arcade.Window) -> int:
        window.show_view(self)
        self.setup()
        return self.score

    def setup(self):
        self.score = 0
        self.duck_list = arcade.SpriteList()
        self.spawn_timer = 0

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(self.background_texture, self.background_rect)
        arcade.draw_text(f"Score: {self.score}", 10, self.window.height - 70, arcade.color.WHITE, 50)

        self.duck_list.draw()

    def on_update(self, delta_time: float):
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.duck_spawn_interval:
            duck = arcade.Sprite(self.duck_texture_path, scale=0.37)
            duck.center_x = 0
            duck.center_y = random.randint(200, self.window.height - 50)
            duck.change_x = self.duck_speed
            self.duck_list.append(duck)
            self.spawn_timer = 0

        self.duck_list.update()

        # Remove ducks that leave the screen
        for duck in self.duck_list:
            if duck.center_x > self.window.width:
                self.duck_list.remove(duck)

    def on_mouse_press(self, x, y, button, modifiers):
        for duck in self.duck_list:
            if duck.collides_with_point((x, y)):
                self.duck_list.remove(duck)
                self.score += 1
                if self.shot_sound:
                    arcade.play_sound(self.shot_sound)
                break
