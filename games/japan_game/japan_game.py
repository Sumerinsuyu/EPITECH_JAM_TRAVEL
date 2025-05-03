import arcade
import random
import os
from abc import ABC, abstractmethod
from typing import Tuple

class JapanGame(IGame):
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.title = "Japan - Sushi Rampage"
        self.sushi_list = arcade.SpriteList()
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        self.score = 0
        self.cut_sound = None
        self.cut_sprites = arcade.SpriteList()
        self.cut_timers = []
        self.rect_color = arcade.color.RED
        self.sushi_speed = 600
        self.sushi_health = 8
        self.game_over_text = "GAME OVER!"
        self.view = None
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")

    def get_name(self) -> str:
        return "Sushi Rampage"

    def get_color(self) -> Tuple[int, int, int]:
        return (255, 50, 50)  # Red color for Japan

    def run(self, window: arcade.Window) -> int:
        """Run the game and return the score."""
        self.view = JapanGameView(self)
        window.show_view(self.view)
        window.run()  # This will block until the game is done
        return self.score

    def setup(self):
        """Setup the game state."""
        self.sushi_list = arcade.SpriteList()
        self.spawn_timer = 0
        self.score = 0
        self.rect_color = arcade.color.RED
        self.sushi_speed = 600
        self.sushi_health = 8
        try:
            self.cut_sound = arcade.load_sound(os.path.join(self.assets_path, "cut.wav"))
        except Exception:
            self.cut_sound = None

class JapanGameView(arcade.View):
    def __init__(self, game: JapanGame):
        super().__init__()
        self.game = game
        self.window.set_mouse_visible(True)

    def on_draw(self):
        self.clear()
        if self.game.sushi_health <= 0:
            arcade.draw_text(self.game.game_over_text, 
                           self.game.screen_width / 2, 
                           self.game.screen_height / 2, 
                           arcade.color.WHITE, 24, 
                           anchor_x="center", anchor_y="center")
            return
        
        arcade.draw_text("Press space to be a sushi sensei", 
                        200, 550, arcade.color.WHITE, 16)
        arcade.draw_text(f"Score : {self.game.score}", 
                        10, 10, arcade.color.WHITE, 14)
        arcade.draw_lrbt_rectangle_outline(0, self.game.screen_width, 
                                          100, 150, 
                                          self.game.rect_color, 2)
        self.game.sushi_list.draw()
        self.game.cut_sprites.draw()

    def on_update(self, delta_time):
        self.game.rect_color = arcade.color.RED 

        if self.game.sushi_health > 0:
            self.game.spawn_timer += delta_time
            if self.game.spawn_timer >= self.game.spawn_interval:
                x = random.randint(50, self.game.screen_width - 50)
                sushi = Sushi(x, self.game.screen_height)
                sushi.speed = self.game.sushi_speed
                self.game.sushi_list.append(sushi)
                self.game.spawn_timer = 0
                
            for sushi in self.game.sushi_list:
                sushi.update(delta_time)
                
            for sushi in self.game.sushi_list:
                if sushi.center_y < 0:
                    self.game.sushi_list.remove(sushi)
                    self.game.sushi_health -= 1
                    
            for sprite in self.game.cut_sprites:
                sprite.center_x += sprite.change_x * delta_time
                sprite.center_y -= 50 * delta_time

            for i in range(len(self.game.cut_timers)):
                self.game.cut_timers[i] -= delta_time

            expired_indices = [i for i, t in enumerate(self.game.cut_timers) if t <= 0]
            for index in reversed(expired_indices):
                self.game.cut_sprites.pop(index)
                self.game.cut_timers.pop(index)
                
            for sushi in self.game.sushi_list:
                if sushi.is_in_cut_zone():
                    self.game.rect_color = arcade.color.WHITE
                    break

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            for sushi in self.game.sushi_list:
                if sushi.is_in_cut_zone():
                    self.game.sushi_list.remove(sushi)
                    self.game.score += 1
                    self.game.sushi_speed += 50

                    left = arcade.Sprite(os.path.join(self.game.assets_path, "sushi_half_left.png"), 
                                        scale=0.5)
                    left.center_x = sushi.center_x
                    left.center_y = sushi.center_y
                    left.change_x = -150

                    right = arcade.Sprite(os.path.join(self.game.assets_path, "sushi_half_right.png"), 
                                         scale=0.5)
                    right.center_x = sushi.center_x
                    right.center_y = sushi.center_y
                    right.change_x = 150

                    self.game.cut_sprites.append(left)
                    self.game.cut_sprites.append(right)
                    self.game.cut_timers.append(0.5)
                    self.game.cut_timers.append(0.5)

                    if self.game.cut_sound:
                        arcade.play_sound(self.game.cut_sound)
                    break
        elif key == arcade.key.ESCAPE:
            # Return to menu
            self.window.show_view(self.window.game_menu_view_instance)

class Sushi(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(os.path.join(os.path.dirname(__file__), "assets", "sushi.png"), 
                         scale=0.35)
        self.center_x = x
        self.center_y = y
        self.speed = 600  # pixels/sec

    def update(self, delta_time: float = 1/60):
        self.center_y -= self.speed * delta_time

    def is_in_cut_zone(self):
        return 100 < self.center_y < 150