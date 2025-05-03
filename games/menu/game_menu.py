import arcade
import os
from PIL import Image
import math
import random
from games.IGame import IGame
from typing import List, Tuple

class GameMenu(arcade.View):
    def __init__(self, playable_games: List[IGame], window: arcade.Window):
        super().__init__()
        self.window = window
        self.playable_games = playable_games
        self.game_color_map = self._create_color_map()
        self.state = "selecting"
        self.hit_point = None
        self.selected_x = None
        self.selected_y = None
        self.result_message = None
        self.horizontal_cursor_pos = 0.5
        self.horizontal_cursor_speed_base = 0.4
        self.horizontal_cursor_speed = self.horizontal_cursor_speed_base
        self.horizontal_cursor_direction = 1
        self.vertical_cursor_pos = 0.5
        self.vertical_cursor_speed_base = 0.4
        self.vertical_cursor_speed = self.vertical_cursor_speed_base
        self.vertical_cursor_direction = 1
        self.random_offset_std_dev = 30
        self.min_speed_factor = 0.9
        self.max_speed_factor = 1.5
        self.display_map_path = os.path.join(os.path.dirname(__file__), "assets", "earthmap.jpg")
        self.color_map_path = os.path.join(os.path.dirname(__file__), "assets", "testmap.jpg")
        try:
            self.color_pil_image = Image.open(self.color_map_path).convert("RGB")
        except FileNotFoundError:
            self.color_pil_image = None
            print(f"Error: Color map file not found at {self.color_map_path}")
        try:
            self.background_sprite = arcade.Sprite(self.display_map_path)
            self.background_list = arcade.SpriteList()
            self.background_list.append(self.background_sprite)
            if self.window:
                 self._resize_background()
        except FileNotFoundError:
            self.background_sprite = None
            self.background_list = arcade.SpriteList()
            print(f"Error: Display map file not found at {self.display_map_path}")
        self.result_text_object = arcade.Text(
            "",
            self.window.width / 2 if self.window else 500,
            self.window.height / 2 if self.window else 400,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=self.window.width - 100 if self.window else 800
        )

    def _create_color_map(self) -> dict[Tuple[int, int, int], IGame]:
        """Creates a dictionary mapping game colors (RGB tuples) to game instances."""
        color_map = {}
        print("Creating color map:")
        for game in self.playable_games:
            color_tuple = game.get_color()
            if color_tuple:
                 if isinstance(color_tuple, list): color_tuple = tuple(color_tuple)
                 if len(color_tuple) == 4: color_tuple = color_tuple[:3]
                 print(f"  Mapping color {color_tuple} to game {game.get_name()}")
                 color_map[color_tuple] = game
            else:
                 print(f"  Game {game.get_name()} has no color defined.")
        return color_map

    def _resize_background(self):
         """Resizes the background sprite to fit the window."""
         if self.background_sprite and self.window:
            self.background_sprite.width = self.window.width
            self.background_sprite.height = self.window.height
            self.background_sprite.center_x = self.window.width / 2
            self.background_sprite.center_y = self.window.height / 2

    def on_show_view(self):
        """Called when switching to this view."""
        arcade.set_background_color(arcade.color.BLACK)
        self._resize_background()
        self.reset_state()

    def reset_state(self):
        """Resets the game state to the beginning."""
        self.state = "selecting"
        self.hit_point = None
        self.selected_x = None
        self.selected_y = None
        self.result_message = None
        self.result_text_object.text = ""
        self.horizontal_cursor_pos = random.random()
        self.vertical_cursor_pos = random.random()
        self.horizontal_cursor_direction = random.choice([1, -1])
        self.vertical_cursor_direction = random.choice([1, -1])
        self.horizontal_cursor_speed = self.horizontal_cursor_speed_base * random.uniform(self.min_speed_factor, self.max_speed_factor)
        self.vertical_cursor_speed = self.vertical_cursor_speed_base * random.uniform(self.min_speed_factor, self.max_speed_factor)

    def _draw_horizontal_bar(self):
        """Draws the horizontal selection bar."""
        if not self.window: return
        screen_width = self.window.width
        bar_y = 30
        bar_height = 10
        bar_margin = 20
        arcade.draw_lrbt_rectangle_filled(bar_margin, screen_width - bar_margin,
                                          bar_y - bar_height / 2, bar_y + bar_height / 2,
                                          arcade.color.DARK_GRAY)
        cursor_x = bar_margin + self.horizontal_cursor_pos * (screen_width - 2 * bar_margin)
        cursor_width = 5
        arcade.draw_lrbt_rectangle_filled(cursor_x - cursor_width / 2, cursor_x + cursor_width / 2,
                                          bar_y - bar_height, bar_y + bar_height,
                                          arcade.color.YELLOW)

    def _draw_vertical_bar(self):
        """Draws the vertical selection bar."""
        if not self.window: return
        screen_height = self.window.height
        bar_x = 30
        bar_width = 10
        bar_margin = 20
        arcade.draw_lrbt_rectangle_filled(bar_x - bar_width / 2, bar_x + bar_width / 2,
                                          bar_margin, screen_height - bar_margin,
                                          arcade.color.DARK_GRAY)
        draw_pos = 1.0 - self.vertical_cursor_pos
        cursor_y = bar_margin + draw_pos * (screen_height - 2 * bar_margin)
        cursor_height = 5
        arcade.draw_lrbt_rectangle_filled(bar_x - bar_width, bar_x + bar_width,
                                          cursor_y - cursor_height / 2, cursor_y + cursor_height / 2,
                                          arcade.color.YELLOW)

    def on_draw(self):
        """Draw everything."""
        self.clear()
        if self.background_list:
            self.background_list.draw()
        if self.state == "selecting":
            self._draw_horizontal_bar()
            self._draw_vertical_bar()
        if self.hit_point:
            arcade.draw_circle_outline(self.hit_point[0], self.hit_point[1], 15, arcade.color.RED, 3)
            arcade.draw_circle_filled(self.hit_point[0], self.hit_point[1], 5, arcade.color.RED)
        if self.result_message:
            self.result_text_object.position = (self.window.width / 2, self.window.height / 2)
            self.result_text_object.text = self.result_message
            center_x = self.result_text_object.x
            center_y = self.result_text_object.y
            width = self.result_text_object.content_width + 40
            height = self.result_text_object.content_height + 40
            left = center_x - width / 2
            right = center_x + width / 2
            bottom = center_y - height / 2
            top = center_y + height / 2
            arcade.draw_lrbt_rectangle_filled(
                left=left,
                right=right,
                bottom=bottom,
                top=top,
                color=(0, 0, 0, 180)
            )
            self.result_text_object.draw()

    def _update_horizontal_cursor(self, delta_time):
        """Updates the horizontal cursor position."""
        self.horizontal_cursor_pos += self.horizontal_cursor_speed * self.horizontal_cursor_direction * delta_time
        if self.horizontal_cursor_pos > 1.0:
            self.horizontal_cursor_pos = 1.0
            self.horizontal_cursor_direction *= -1
        elif self.horizontal_cursor_pos < 0.0:
            self.horizontal_cursor_pos = 0.0
            self.horizontal_cursor_direction *= -1

    def _update_vertical_cursor(self, delta_time):
        """Updates the vertical cursor position."""
        self.vertical_cursor_pos += self.vertical_cursor_speed * self.vertical_cursor_direction * delta_time
        if self.vertical_cursor_pos > 1.0:
            self.vertical_cursor_pos = 1.0
            self.vertical_cursor_direction *= -1
        elif self.vertical_cursor_pos < 0.0:
            self.vertical_cursor_pos = 0.0
            self.vertical_cursor_direction *= -1

    def on_update(self, delta_time):
        """Update game state."""
        if self.state == "selecting":
            self._update_horizontal_cursor(delta_time)
            self._update_vertical_cursor(delta_time)

    def _calculate_hit_point(self):
        """Calculates the final hit point based on selections and randomness."""
        if not self.window or self.selected_x is None or self.selected_y is None:
            print("Warning: Cannot calculate hit point, selection missing.")
            return None
        screen_width = self.window.width
        screen_height = self.window.height
        base_target_x = self.selected_x
        base_target_y = self.selected_y
        final_target_x = random.gauss(base_target_x, self.random_offset_std_dev)
        final_target_y = random.gauss(base_target_y, self.random_offset_std_dev)
        final_target_x = max(0, min(screen_width - 1, final_target_x))
        final_target_y = max(0, min(screen_height - 1, final_target_y))
        return (final_target_x, final_target_y)

    def _perform_throw(self):
        """Gets the color at the hit point, looks up the game, and sets the result."""
        if not self.window or self.hit_point is None:
            self.result_message = "Error: Hit point not calculated."
            self.state = "result_displayed"
            return
        screen_width = self.window.width
        screen_height = self.window.height
        final_target_x, final_target_y = self.hit_point
        hit_color_rgb = None
        selected_game = None
        if self.color_pil_image:
            try:
                img_width, img_height = self.color_pil_image.size
                map_x = max(0, min(img_width - 1, int((final_target_x / screen_width) * img_width)))
                map_y = max(0, min(img_height - 1, int(((screen_height - final_target_y) / screen_height) * img_height)))
                hit_color_rgb = self.color_pil_image.getpixel((map_x, map_y))
                selected_game = self.game_color_map.get(hit_color_rgb)
                self.state = "result_displayed"
                if selected_game:
                    print(f"Color {hit_color_rgb} matched! Launching {selected_game.get_name()}...")
                    self.result_message = f"Hit color {hit_color_rgb}.\nLaunching {selected_game.get_name()}..."
                    if not hasattr(self.window, 'game_menu_view_instance'):
                         self.window.game_menu_view_instance = self
                    selected_game.run(self.window)
                else:
                    print(f"Hit color {hit_color_rgb}, but no game matches this color.")
                    self.result_message = f"Hit color {hit_color_rgb}.\nNo game is mapped to this location.\nPress SPACE to try again."
            except IndexError:
                 print("Error: Calculated hit point is outside color map bounds.")
                 self.result_message = "Error: Hit point outside map bounds.\nPress SPACE to try again."
                 self.state = "result_displayed"
            except Exception as e:
                 print(f"Error getting pixel color or looking up game: {e}")
                 self.result_message = f"An error occurred: {e}\nPress SPACE to try again."
                 self.state = "result_displayed"
        else:
            print("Cannot get pixel color: Color map image not loaded.")
            self.result_message = "Error: Color map image not loaded.\nCannot determine location.\nPress SPACE to try again."
            self.state = "result_displayed"

    def _handle_selecting_press(self):
        """Handles first space press: locks selection, calculates hit, changes state."""
        if not self.window: return
        screen_width = self.window.width
        screen_height = self.window.height
        bar_margin = 20
        self.selected_x = bar_margin + self.horizontal_cursor_pos * (screen_width - 2 * bar_margin)
        self.selected_y = bar_margin + (1.0 - self.vertical_cursor_pos) * (screen_height - 2 * bar_margin)
        self.hit_point = self._calculate_hit_point()
        self.state = "displaying_hit"
        self.result_message = None
        self.result_text_object.text = ""
        print("State changed to displaying_hit. Hit point calculated:", self.hit_point)

    def on_key_press(self, key, modifiers):
        """Handle key presses based on state."""
        if key == arcade.key.SPACE:
            if self.state == "selecting":
                self._handle_selecting_press()
            elif self.state == "displaying_hit":
                 print("Space pressed in displaying_hit state. Performing throw...")
                 self._perform_throw()
            elif self.state == "result_displayed":
                 print("Space pressed in result_displayed state. Resetting...")
                 self.reset_state()
        elif key == arcade.key.ESCAPE:
             print("Escape pressed. Resetting state.")
             self.reset_state()

if __name__ == "__main__":
    class DummyGame(IGame):
        def get_name(self): return "Dummy Blue Game"
        def get_color(self): return (0, 0, 255)
        def run(self, window):
            print(f"Running {self.get_name()}")
            view = arcade.View()
            label = arcade.Text(f"{self.get_name()} Running!\nPress ESC to return to menu.",
                                window.width / 2, window.height / 2,
                                arcade.color.WHITE, 20, anchor_x="center")
            @view.window.event
            def on_key_press(key, modifiers):
                if key == arcade.key.ESCAPE:
                    if hasattr(window, 'game_menu_view_instance'):
                         window.show_view(window.game_menu_view_instance)
                    else:
                         print("Cannot return to menu automatically in test.")
            @view.window.event
            def on_draw():
                view.clear()
                label.draw()
            window.show_view(view)
    test_width = 1024
    test_height = 768
    window = arcade.Window(test_width, test_height, "Game Menu Test")
    dummy_games = [DummyGame()]
    menu_view = GameMenu(dummy_games, window)
    window.game_menu_view_instance = menu_view
    window.show_view(menu_view)
    arcade.run()
