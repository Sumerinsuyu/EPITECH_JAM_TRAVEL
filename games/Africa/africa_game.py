import arcade
import os
import random
from games.IGame import IGame
from PIL import Image
from arcade import Rect

class AfricaGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()
        self.title = "Africa Fruit Catcher"
        self.fruit_count = 0
        self.game_over = False
        self.score = 5  # Score starts at 5
        self.time_since_decrement = 0  # Track time for score decrement
        self.window = arcade.get_window()
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        # Load and resize background
        bg_path = os.path.join(self.assets_dir, "savanaBG.png")
        pil_bg = Image.open(bg_path).convert("RGBA").resize((self.window.width, self.window.height))
        self.bg_texture = arcade.Texture.create_empty("bg_resized", (self.window.width, self.window.height))
        self.bg_texture.image = pil_bg
        # Load zebra
        self.zebra_sprite = arcade.Sprite(os.path.join(self.assets_dir, "zebraS.png"), scale=0.3)
        self.zebra_sprite.center_x = self.window.width // 2
        self.zebra_sprite.center_y = 60
        self.zebra_speed = 8
        self.zebra_list = arcade.SpriteList()
        self.zebra_list.append(self.zebra_sprite)
        # Load fruit spritesheet info (3 rows x 3 cols)
        self.fruit_image, self.fruit_w, self.fruit_h, self.fruit_rows, self.fruit_cols = self.load_fruit_info(os.path.join(self.assets_dir, "fruit.png"))
        self.fruit_list = arcade.SpriteList()
        self.fruit_spawn_timer = 0
        self.fruit_spawn_interval = 0.8
        self.held_keys = set()
        self.score_text = arcade.Text(f"Fruit Count: {self.fruit_count}", 20, self.window.height - 40, arcade.color.BLACK, 28)
        self.score_display = arcade.Text(f"Score: {self.score}", self.window.width // 2, self.window.height - 40, arcade.color.BLACK, 28, anchor_x="center")
        self.game_over_text = arcade.Text(
            "Game Over!",
            self.window.width // 2,
            self.window.height // 2,
            arcade.color.RED,
            48,
            anchor_x="center"
        )

    def get_name(self):
        return self.title

    def run(self, window):
        window.show_view(self)
        return self.score

    def on_draw(self):
        self.clear()
        # Draw background using draw_texture_rect with all required Rect arguments
        rect = Rect(
            0,  # left
            self.window.width,  # right
            0,  # bottom
            self.window.height,  # top
            self.window.width,  # width
            self.window.height,  # height
            self.window.width // 2,  # x (center)
            self.window.height // 2  # y (center)
        )
        arcade.draw_texture_rect(self.bg_texture, rect)
        # Draw zebra
        self.zebra_list.draw()
        # Draw fruits
        self.fruit_list.draw()
        # Draw score
        self.score_text.text = f"Fruit Count: {self.fruit_count}"
        self.score_text.position = (20, self.window.height - 40)
        self.score_text.draw()
        # Draw score at the top center
        self.score_display.text = f"Score: {self.score}"
        self.score_display.position = (self.window.width // 2, self.window.height - 40)
        self.score_display.draw()
        if self.game_over:
            self.game_over_text.draw()

    def on_update(self, delta_time):
        if self.game_over:
            return
        self.time_since_decrement += delta_time
        if self.time_since_decrement >= 10:
            self.time_since_decrement = 0
            if self.score > 0:
                self.score -= 1
        self.handle_input()
        self.spawn_fruit(delta_time)
        self.fruit_list.update()
        self.check_catch()
        self.remove_missed_fruit()

    def handle_input(self):
        if arcade.key.LEFT in self.held_keys:
            self.zebra_sprite.center_x -= self.zebra_speed
            self.zebra_sprite.scale_x = 0.3
            if self.zebra_sprite.left < 0:
                self.zebra_sprite.left = 0
        if arcade.key.RIGHT in self.held_keys:
            self.zebra_sprite.center_x += self.zebra_speed
            self.zebra_sprite.scale_x = -0.3
            if self.zebra_sprite.right > self.window.width:
                self.zebra_sprite.right = self.window.width

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.held_keys.add(key)
        if key == arcade.key.ESCAPE:
            if hasattr(self.window, 'menu_view'):
                self.window.show_view(self.window.menu_view)

    def on_key_release(self, key, modifiers):
        if key in self.held_keys:
            self.held_keys.remove(key)

    def spawn_fruit(self, delta_time):
        self.fruit_spawn_timer += delta_time
        if self.fruit_spawn_timer >= self.fruit_spawn_interval:
            self.fruit_spawn_timer = 0
            row = random.randint(0, self.fruit_rows - 1)
            col = random.randint(0, self.fruit_cols - 1)
            left = col * self.fruit_w
            upper = row * self.fruit_h
            right = left + self.fruit_w
            lower = upper + self.fruit_h
            frame_img = self.fruit_image.crop((left, upper, right, lower))
            texture = arcade.Texture.create_empty(f"fruit_{row}_{col}", (self.fruit_w, self.fruit_h))
            texture.image = frame_img
            fruit = arcade.Sprite()
            fruit.texture = texture
            fruit.center_x = random.randint(40, self.window.width - 40)
            fruit.center_y = self.window.height + 30
            fruit.change_y = -random.uniform(4, 7)
            fruit.scale = 0.6  # Increased scale for larger fruit
            self.fruit_list.append(fruit)

    def check_catch(self):
        caught = arcade.check_for_collision_with_list(self.zebra_sprite, self.fruit_list)
        for fruit in caught:
            self.fruit_count += 1
            fruit.remove_from_sprite_lists()
        if self.fruit_count >= 20:
            self.game_over = True

    def remove_missed_fruit(self):
        for fruit in self.fruit_list:
            if fruit.center_y < 0:
                fruit.remove_from_sprite_lists()

    def load_fruit_info(self, path):
        pil_image = Image.open(path).convert("RGBA")
        width, height = pil_image.size
        rows, cols = 3, 3
        frame_width = width // cols
        frame_height = height // rows
        return pil_image, frame_width, frame_height, rows, cols

    def get_color(self):
        return (255, 215, 0)  # Gold/yellow for Africa
