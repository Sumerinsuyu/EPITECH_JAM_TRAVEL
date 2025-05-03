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
        self.color_map_path = os.path.join(os.path.dirname(__file__), "assets", "backmap.jpg")
        try:
            self.color_pil_image = Image.open(self.color_map_path).convert("RGB")
        except FileNotFoundError:
            self.color_pil_image = None
        try:
            self.background_sprite = arcade.Sprite(self.display_map_path)
            self.background_list = arcade.SpriteList()
            self.background_list.append(self.background_sprite)
            if self.window:
                 self._resize_background()
        except FileNotFoundError:
            self.background_sprite = None
            self.background_list = arcade.SpriteList()
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
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.current_turn = 1
        self.max_turns = 6
        self.score_text_object = arcade.Text(
            "",
            10, self.window.height - 30 if self.window else 700,
            arcade.color.WHITE, font_size=16
        )

    def _create_color_map(self) -> dict[Tuple[int, int, int], IGame]:
        """Creates a dictionary mapping game colors (RGB tuples) to game instances."""
        color_map = {}
        for game in self.playable_games:
            color_tuple = game.get_color()
            if color_tuple:
                 if isinstance(color_tuple, list): color_tuple = tuple(color_tuple)
                 if len(color_tuple) == 4: color_tuple = color_tuple[:3]
                 color_map[color_tuple] = game
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
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.current_turn = 1
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

        self.score_text_object.text = (f"Turn: {self.current_turn}/{self.max_turns} | Player {self.current_player}'s Turn\n"
                                       f"Player 1 Score: {self.player1_score}\n"
                                       f"Player 2 Score: {self.player2_score}")
        self.score_text_object.position = (10, self.window.height - 50)
        self.score_text_object.draw()

        if self.state == "selecting":
            self._draw_horizontal_bar()
            self._draw_vertical_bar()
        if self.hit_point and self.state != "game_over":
            arcade.draw_circle_outline(self.hit_point[0], self.hit_point[1], 15, arcade.color.RED, 3)
            arcade.draw_circle_filled(self.hit_point[0], self.hit_point[1], 5, arcade.color.RED)
        if self.result_message:
            self.result_text_object.position = (self.window.width / 2, self.window.height / 2)
            self.result_text_object.text = self.result_message
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
        """Gets the color at the hit point, looks up the game, updates score, and advances turn."""
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

                if selected_game:
                    score = selected_game.run(self.window)

                    if self.current_player == 1:
                        self.player1_score += score
                    else:
                        self.player2_score += score

                    if self.current_turn >= self.max_turns:
                        self.state = "game_over"
                        final_message = f"Game Over!\nPlayer 1 Score: {self.player1_score}\nPlayer 2 Score: {self.player2_score}\n"
                        if self.player1_score > self.player2_score:
                            final_message += "Player 1 Wins!"
                        elif self.player2_score > self.player1_score:
                            final_message += "Player 2 Wins!"
                        else:
                            final_message += "It's a Tie!"
                        final_message += "\nPress SPACE to play again."
                        self.result_message = final_message
                    else:
                        self.current_turn += 1
                        self.current_player = 2 if self.current_player == 1 else 1
                        self.result_message = (f"Player {3 - self.current_player} scored {score}!\n"
                                               f"Player {self.current_player}'s turn ({self.current_turn}/{self.max_turns}).\n"
                                               f"Press SPACE to continue selecting.")
                        self.state = "result_displayed"

                else:
                    self.result_message = (f"Hit color {hit_color_rgb}.\nNo game is mapped here.\n"
                                           f"Player {self.current_player} throws again.\nPress SPACE to try again.")
                    self.state = "result_displayed"

            except IndexError:
                 self.result_message = "Error: Hit point outside map bounds.\nPress SPACE to try again."
                 self.state = "result_displayed"
            except Exception as e:
                 self.result_message = f"An error occurred: {e}\nPress SPACE to try again."
                 self.state = "result_displayed"
        else:
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

    def on_key_press(self, key, modifiers):
        """Handle key presses based on state."""
        if key == arcade.key.SPACE:
            if self.state == "selecting":
                self._handle_selecting_press()
            elif self.state == "displaying_hit":
                 self._perform_throw()
            elif self.state == "result_displayed":
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
            elif self.state == "game_over":
                 self.reset_state()
        elif key == arcade.key.ESCAPE:
             self.reset_state()

if __name__ == "__main__":
    class DummyGame(IGame):
        def get_name(self): return "Dummy Blue Game"
        def get_color(self): return (0, 0, 255)
        def run(self, window):
            return random.choice([0, 5])

    test_width = 1024
    test_height = 768
    window = arcade.Window(test_width, test_height, "Game Menu Test")
    dummy_games = [DummyGame()]
    menu_view = GameMenu(dummy_games, window)
    window.game_menu_view_instance = menu_view
    window.show_view(menu_view)
    arcade.run()
