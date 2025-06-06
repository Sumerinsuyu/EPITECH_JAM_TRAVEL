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
        self.color_map_path = os.path.join(os.path.dirname(__file__), "assets", "backmap2.jpg")
        try:
            self.color_pil_image = Image.open(self.color_map_path).convert("RGB")
        except FileNotFoundError:
            print(f"Error: Color map file not found at {self.color_map_path}")
            self.color_pil_image = None
        try:
            self.background_sprite = arcade.Sprite(self.display_map_path)
            self.background_list = arcade.SpriteList()
            self.background_list.append(self.background_sprite)
            if self.window:
                self._resize_assets()
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
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.current_turn = 1
        self.max_turns = 3
        self.score_text_object = arcade.Text(
            "",
            10, self.window.height - 30 if self.window else 700,
            arcade.color.WHITE, font_size=16
        )
        self.waiting_for_view_score = False
        self.current_game_instance = None

    def _create_color_map(self) -> dict[Tuple[int, int, int], IGame]:
        color_map = {}
        for game in self.playable_games:
            color_tuple = game.get_color()
            if color_tuple:
                if isinstance(color_tuple, list):
                    color_tuple = tuple(color_tuple)
                if len(color_tuple) == 4:
                    color_tuple = color_tuple[:3]
                rounded_color = tuple(int(round(c / 125) * 125) for c in color_tuple)
                color_map[rounded_color] = game
        return color_map

    def _resize_assets(self):
        """Resizes both the background display sprite and the color map PIL image."""
        if not self.window:
            print("Warning: _resize_assets called but window is not available.")
            return

        # Resize background sprite
        if self.background_sprite:
            self.background_sprite.width = self.window.width
            self.background_sprite.height = self.window.height
            self.background_sprite.center_x = self.window.width / 2
            self.background_sprite.center_y = self.window.height / 2
        else:
            print("Warning: Background sprite not loaded, cannot resize.")

        # Resize color map PIL image
        if self.color_pil_image:
            try:
                # Use NEAREST resampling to avoid color blending/aliasing which breaks exact matching
                self.resized_color_pil_image = self.color_pil_image.resize(
                    (self.window.width, self.window.height),
                    Image.Resampling.NEAREST # Crucial for keeping distinct color areas
                )
                # print(f"Resized color map to {self.window.width}x{self.window.height}") # Debug print
            except Exception as e:
                print(f"Error resizing color map image: {e}")
                self.resized_color_pil_image = None
        else:
             print("Warning: Original color map PIL image not loaded, cannot resize.")
             self.resized_color_pil_image = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self._resize_assets()
        if self.waiting_for_view_score:
            score = getattr(self.window, 'last_game_score', 0)
            if hasattr(self.window, 'last_game_score'):
                try:
                    delattr(self.window, 'last_game_score')
                except AttributeError:
                    pass
            else:
                print("Warning: Returned from View game but no 'last_game_score' found on window.")
            self._process_score_and_advance_turn(score, self.current_game_instance)
            self.waiting_for_view_score = False
            self.current_game_instance = None
        else:
            if self.current_turn == 1 and self.player1_score == 0 and self.player2_score == 0:
                self.reset_state()

    def reset_state(self):
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
        self.waiting_for_view_score = False
        self.current_game_instance = None

    def _draw_horizontal_bar(self):
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
        self.horizontal_cursor_pos += self.horizontal_cursor_speed * self.horizontal_cursor_direction * delta_time
        if self.horizontal_cursor_pos > 1.0:
            self.horizontal_cursor_pos = 1.0
            self.horizontal_cursor_direction *= -1
        elif self.horizontal_cursor_pos < 0.0:
            self.horizontal_cursor_pos = 0.0
            self.horizontal_cursor_direction *= -1

    def _update_vertical_cursor(self, delta_time):
        self.vertical_cursor_pos += self.vertical_cursor_speed * self.vertical_cursor_direction * delta_time
        if self.vertical_cursor_pos > 1.0:
            self.vertical_cursor_pos = 1.0
            self.vertical_cursor_direction *= -1
        elif self.vertical_cursor_pos < 0.0:
            self.vertical_cursor_pos = 0.0
            self.vertical_cursor_direction *= -1

    def on_update(self, delta_time):
        if self.state == "selecting" and not self.waiting_for_view_score:
            self._update_horizontal_cursor(delta_time)
            self._update_vertical_cursor(delta_time)

    def _calculate_hit_point(self):
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

    def _process_score_and_advance_turn(self, score, selected_game):
        game_name = selected_game.get_name() if selected_game else "Unknown Game"
        if self.current_player == 1:
            self.player1_score += score
        else:
            self.player2_score += score
        if self.current_turn >= self.max_turns and self.current_player == 2:
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
            if self.current_player == 2:
                self.current_turn += 1
            previous_player = self.current_player
            self.current_player = 2 if self.current_player == 1 else 1
            self.result_message = (f"Player {previous_player} played '{game_name}' and scored {score}!\n"
                                   f"Player {self.current_player}'s turn ({self.current_turn}/{self.max_turns}).\n"
                                   f"Press SPACE to continue selecting.")
            self.state = "result_displayed"

    def _perform_throw(self):
        """Gets the color at the hit point from the RESIZED color map, looks up the game, launches it."""
        if not self.window or self.hit_point is None:
            self.result_message = "Error: Cannot perform throw without window or hit point.\nPress SPACE to try again."
            self.state = "result_displayed"
            return

        # Use the resized PIL image for color lookup
        if self.resized_color_pil_image:
            try:
                img_width, img_height = self.resized_color_pil_image.size # Should match window size

                # Coordinates from hit_point are already in window space.
                # Need to clamp and adjust for PIL's coordinate system (Y=0 at top).
                hit_x = int(self.hit_point[0])
                hit_y = int(self.hit_point[1])

                # Clamp coordinates to be within the image bounds
                map_x = max(0, min(img_width - 1, hit_x))
                # Invert Y for PIL coordinate system (0,0 is top-left) and clamp
                map_y = max(0, min(img_height - 1, img_height - 1 - hit_y))

                # Get pixel color from the *resized* image
                rgb = self.resized_color_pil_image.getpixel((map_x, map_y))

                # --- Color Matching Logic ---
                # Use the fuzzy matching function
                selected_game = self._find_closest_game(rgb) # Assuming _find_closest_game exists

                # --- Game Launch Logic ---
                if selected_game:
                    game_name = selected_game.get_name()
                    self.window.game_menu_view_instance = self # Store reference for return
                    score_or_none = selected_game.run(self.window)

                    if score_or_none is None: # Game uses views
                        self.waiting_for_view_score = True
                        self.current_game_instance = selected_game
                        self.state = "in_game"
                        self.result_message = f"Player {self.current_player} playing '{game_name}'..."
                    else: # Game returned score directly
                        self._process_score_and_advance_turn(score_or_none, selected_game)
                        if hasattr(self.window, 'game_menu_view_instance'):
                            delattr(self.window, 'game_menu_view_instance')
                else:
                    # No game found for the color at the hit point, even with fuzzy matching
                    self.result_message = f"Hit color {rgb}, but no game is mapped close enough.\nTry again!\nPress SPACE to continue selecting."
                    self.state = "result_displayed"
                # --- End Game Launch Logic ---

            except Exception as e:
                self.result_message = f"An error occurred during throw: {e}\nPress SPACE to try again."
                print(f"Error details in _perform_throw: {e}") # More detailed logging
                self.state = "result_displayed"
        else:
            # Resized color map image isn't available
            self.result_message = "Error: Resized color map image not available.\nCannot determine location.\nPress SPACE to try again."
            self.state = "result_displayed"

    def _find_closest_game(self, target_rgb: Tuple[int, int, int], tolerance: int = 30) -> IGame | None:
        """Finds the game associated with the color closest to target_rgb within tolerance."""
        min_distance = float('inf')
        closest_game = None

        # Ensure game_color_map is populated
        if not self.game_color_map:
             print("Warning: game_color_map is empty in _find_closest_game.")
             return None

        for game_color, game_instance in self.game_color_map.items():
            # Calculate Manhattan distance (sum of absolute differences)
            # It's generally good enough for distinct colors and faster than Euclidean
            distance = sum(abs(c1 - c2) for c1, c2 in zip(target_rgb, game_color))

            if distance < min_distance:
                min_distance = distance
                closest_game = game_instance

        # Only return the game if it's within the tolerance threshold
        if min_distance <= tolerance:
            # print(f"Debug: Target {target_rgb}, Closest {closest_game.get_color() if closest_game else 'None'}, Dist {min_distance}, Match: {closest_game.get_name() if closest_game else 'None'}")
            return closest_game
        else:
            # print(f"Debug: Target {target_rgb}, Closest {closest_game.get_color() if closest_game else 'None'}, Dist {min_distance} > tolerance {tolerance}. No match.")
            return None

    def _handle_selecting_press(self):
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
        if self.waiting_for_view_score:
            return
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
            if self.state in ["selecting", "displaying_hit", "result_displayed"]:
                self.reset_state()

if __name__ == "__main__":
    class DummyGame(IGame):
        def get_name(self): return "Dummy Blue Game"
        def get_color(self): return (0, 0, 255)
        def run(self, window): return random.choice([0, 5])

    test_width = 1024
    test_height = 768
    window = arcade.Window(test_width, test_height, "Game Menu Test")
    dummy_games = [DummyGame()]
    menu_view = GameMenu(dummy_games, window)
    window.game_menu_view_instance = menu_view
    window.show_view(menu_view)
    arcade.run()
