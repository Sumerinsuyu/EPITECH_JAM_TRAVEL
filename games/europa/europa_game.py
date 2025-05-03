import arcade
import random
import os

from arcade.types import Color
from games.IGame import IGame

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
GLASS_IMG = os.path.join(ASSETS_DIR, "emptyglass.png")
BACKGROUND_IMG = os.path.join(ASSETS_DIR, "bar.jpg")

TOTAL_BEERS = 5
FILL_RATE_RANGE = (150, 300)
TARGET_LINE_RANGE = (0.3, 0.9)
TOLERANCE = 15
LINE_THICKNESS = 8
BEER_WIDTH_RATIO = 0.35
BOTTOM_MARGIN_RATIO = 0.02 # Lowered from 0.2
TOP_MARGIN_RATIO = 0.33


class EuropaGame(IGame, arcade.View):
    def __init__(self):
        super().__init__(window=None)
        self._init_state()
        self._load_assets()

    def _init_state(self):
        self.score = 0
        self.round_score = 0
        self.current_beer_index = 0
        self.game_state = "IDLE"
        self.beer_level = 0
        self.beer_fill_rate = 0
        self.result_text = arcade.Text("", 0, 0, arcade.color.WHITE, 24, anchor_x="center")

    def _load_assets(self):
        self.background_sprite = arcade.Sprite(BACKGROUND_IMG) if os.path.exists(BACKGROUND_IMG) else None
        self.glass_sprite = arcade.Sprite(GLASS_IMG, scale=1.0) if os.path.exists(GLASS_IMG) else None
        self.background_list = arcade.SpriteList()
        self.glass_list = arcade.SpriteList()
        if self.background_sprite: self.background_list.append(self.background_sprite)
        if self.glass_sprite: self.glass_list.append(self.glass_sprite)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self._setup_positions()
        self._reset_beer()

    def _setup_positions(self):
        if not self.window or not self.glass_sprite: return
        self.background_sprite.center_x = self.window.width / 2
        self.background_sprite.center_y = self.window.height / 2
        self.background_sprite.width = self.window.width
        self.background_sprite.height = self.window.height

        self.glass_sprite.center_x = self.window.width / 2
        self.glass_sprite.bottom = self.window.height / 5
        self.beer_max_level = self.glass_sprite.height * (1 - BOTTOM_MARGIN_RATIO - TOP_MARGIN_RATIO)

        self.result_text.x = self.window.width / 2
        self.result_text.y = self.glass_sprite.top + 30

    def _randomize_target_line(self):
        # Calculate the absolute Y coordinate of the bottom of the fillable area
        beer_bottom_y = self.glass_sprite.bottom + self.glass_sprite.height * BOTTOM_MARGIN_RATIO
        # Get a random ratio within the defined range for the target line height
        # This ratio is relative to the maximum fillable height (beer_max_level)
        ratio = random.uniform(*TARGET_LINE_RANGE)
        # Calculate the target line's absolute Y coordinate based on the fillable area
        self.target_line_y = beer_bottom_y + ratio * self.beer_max_level
        # Return the ratio just in case it's needed elsewhere, though it's not currently used
        return ratio

    def _reset_beer(self):
        self.beer_level = 0
        self.beer_fill_rate = 0
        self.game_state = "IDLE"
        self._randomize_target_line()
        self.result_text.text = f"Beer {self.current_beer_index + 1}/{TOTAL_BEERS}: Hold SPACE to fill"

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        if not self.glass_sprite: return
        self._draw_beer()
        self.glass_list.draw()
        self._draw_target_line()
        self.result_text.draw()

    def _draw_beer(self):
        if self.beer_level <= 0: return
        width = self.glass_sprite.width * BEER_WIDTH_RATIO
        x = self.glass_sprite.center_x - width / 2
        bottom = self.glass_sprite.bottom + self.glass_sprite.height * BOTTOM_MARGIN_RATIO
        arcade.draw_lrbt_rectangle_filled(
            left=x, right=x + width,
            top=bottom + self.beer_level,
            bottom=bottom,
            color=arcade.color.YELLOW
        )

    def _draw_target_line(self):
        width = self.glass_sprite.width * BEER_WIDTH_RATIO
        start_x = self.glass_sprite.center_x - width / 2
        end_x = self.glass_sprite.center_x + width / 2
        arcade.draw_line(start_x, self.target_line_y, end_x, self.target_line_y,
                         arcade.color.RED, LINE_THICKNESS)

    def on_update(self, delta_time):
        if self.game_state == "FILLING":
            self.beer_level += self.beer_fill_rate * delta_time
            if self.beer_level >= self.beer_max_level:
                self.beer_level = self.beer_max_level
                self._stop_filling()

    def _start_filling(self):
        if self.game_state != "IDLE": return
        self.beer_fill_rate = random.uniform(*FILL_RATE_RANGE)
        self.game_state = "FILLING"
        self.result_text.text = f"Beer {self.current_beer_index + 1}/{TOTAL_BEERS}: Release SPACE to stop"

    def _stop_filling(self):
        if self.game_state != "FILLING": return

        bottom = self.glass_sprite.bottom + self.glass_sprite.height * BOTTOM_MARGIN_RATIO
        top_y = bottom + self.beer_level
        min_y = self.target_line_y - LINE_THICKNESS / 2 - TOLERANCE
        max_y = self.target_line_y + LINE_THICKNESS / 2 + TOLERANCE

        success = min_y <= top_y <= max_y
        self.score = int(success)
        self.round_score += self.score
        result = "Perfect! +1 point." if success else "Missed! +0 points."

        self.current_beer_index += 1
        if self.current_beer_index < TOTAL_BEERS:
            self.game_state = "BETWEEN_BEERS"
            self.result_text.text = f"{result} Press SPACE for next beer."
        else:
            self.game_state = "ROUND_OVER"
            self.result_text.text = f"Round Over! Score: {self.round_score}/{TOTAL_BEERS}. Press SPACE to exit."

    def _return_to_menu(self):
        print(f"{self.get_name()} finished, score: {self.round_score}")
        self.window.last_game_score = self.round_score
        if hasattr(self.window, "game_menu_view_instance"):
            self.window.show_view(self.window.game_menu_view_instance)
        else:
            print("Error: menu view missing.")
        self.game_state = "DONE"

    def on_key_press(self, key, _):
        if self.game_state == "DONE": return
        if key == arcade.key.SPACE:
            if self.game_state == "IDLE": self._start_filling()
            elif self.game_state == "BETWEEN_BEERS": self._reset_beer()
            elif self.game_state == "ROUND_OVER": self._return_to_menu()
        elif key == arcade.key.ESCAPE:
            self._return_to_menu()

    def on_key_release(self, key, _):
        if self.game_state == "FILLING" and key == arcade.key.SPACE:
            self._stop_filling()

    def run(self, window):
        self.window = window
        self._setup_positions()
        window.show_view(self)

    def get_name(self):
        return "Europa Bar Challenge"

    def get_color(self):
        return Color(0, 0, 255)
