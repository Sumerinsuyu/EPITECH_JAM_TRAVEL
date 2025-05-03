import arcade
from games.IGame import IGame
import random
import os

from arcade.types import Color

class EuropaGame(IGame, arcade.View):
    def __init__(self):
        super().__init__(window=None)
        self.score = 0 # Score for the current attempt (0 or 1)
        self.round_score = 0 # Total score for the 5 beers
        self.current_beer_index = 0 # Index of the current beer (0-4)
        self.total_beers = 5 # Total number of beers to fill
        self.game_state = "IDLE" # States: IDLE, FILLING, STOPPED, BETWEEN_BEERS, ROUND_OVER, DONE

        # Sprites
        self.background_list = arcade.SpriteList() # New list for background
        self.glass_list = arcade.SpriteList()      # New list for glass
        self.glass_sprite = None
        self.background_sprite = None

        # Load background image
        background_path = os.path.join(os.path.dirname(__file__), "assets", "bar.jpg")
        try:
            self.background_sprite = arcade.Sprite(background_path)
            self.background_list.append(self.background_sprite)
        except FileNotFoundError:
            print(f"Error: Background image not found at {background_path}")

        # Load empty glass image
        glass_path = os.path.join(os.path.dirname(__file__), "assets", "emptyglass.png")
        try:
            # Adjust scale if needed, make sure it's appropriate for the game
            self.glass_sprite = arcade.Sprite(glass_path, scale=1.0)
            self.glass_list.append(self.glass_sprite)
        except FileNotFoundError:
            print(f"Error: Glass image not found at {glass_path}")

        # Beer properties
        self.beer_level = 0 # Current height of the beer, starts at 0
        self.beer_max_level = 0 # Calculated based on glass size in on_show_view
        self.beer_fill_rate = 0 # Initial fill rate, randomized on start
        self.beer_color = arcade.color.YELLOW
        self.beer_width_ratio = 0.35# How wide the beer rect is compared to glass (Reduced from 0.8)
        # Add missing margin ratio initializations
        self.beer_fillable_bottom_margin_ratio = 0.1 # Ratio of glass height for bottom margin
        self.beer_fillable_top_margin_ratio = 0.1 # Ratio of glass height for top margin

        # Target line properties
        self.target_line_y = 0 # Calculated in on_show_view
        self.target_line_height_ratio = 0.6 # Initial value, will be randomized
        self.target_line_color = arcade.color.RED
        self.target_line_thickness = 8 # Increased thickness (from 4)
        self.target_line_tolerance = 15 # Increased tolerance slightly due to thicker line

        # Result message
        self.result_text = arcade.Text("", 0, 0, arcade.color.WHITE, 24, anchor_x="center")


    def setup_positions(self):
        """Sets up sprite positions and calculates dynamic properties."""
        if not self.window or not self.glass_sprite:
            return

        # Background
        if self.background_sprite:
            self.background_sprite.center_x = self.window.width / 2
            self.background_sprite.center_y = self.window.height / 2
            self.background_sprite.width = self.window.width
            self.background_sprite.height = self.window.height

        # Glass - Position it appropriately (e.g., lower center)
        self.glass_sprite.center_x = self.window.width / 2
        self.glass_sprite.bottom = self.window.height / 5 # Adjust as needed

        # Calculate beer max level based on glass sprite's height (adjust if glass base exists)
        # Assuming the fillable area starts slightly above the bottom and ends slightly below the top
        fillable_area_ratio = 0.7
        self.beer_max_level = self.glass_sprite.height * (fillable_area_ratio * 0.7)

        # Randomize target line position
        # Y position is relative to the bottom of the fillable area
        self.target_line_height_ratio = random.uniform(0.3, 0.9) # Randomize between 30% and 80% height
        fillable_bottom_y = (self.glass_sprite.bottom + (self.glass_sprite.height * (1 - fillable_area_ratio) / 2))
        self.target_line_y = fillable_bottom_y + (self.beer_max_level * self.target_line_height_ratio)

        # Reset game state variables
        self.beer_level = 0
        self.score = 0
        self.round_score = 0
        self.current_beer_index = 0
        self.game_state = "IDLE"
        self.result_text.text = f"Beer {self.current_beer_index + 1}/{self.total_beers}: Hold SPACE to fill"
        self.result_text.x = self.window.width / 2
        self.result_text.y = self.glass_sprite.top + 30


    def on_show_view(self):
        """ Called when switching to this view"""
        arcade.set_background_color(arcade.color.BLACK)
        self.setup_positions()


    def on_draw(self):
        self.clear()
        # Draw background separately behind beer
        self.background_list.draw()

        if not self.glass_sprite:
            return

        # Calculate beer rectangle properties
        beer_rect_width = self.glass_sprite.width * self.beer_width_ratio
        beer_rect_x = self.glass_sprite.center_x - beer_rect_width / 2
        # Assuming fillable area starts slightly above the bottom
        fillable_bottom_y = self.glass_sprite.bottom + (self.glass_sprite.height * (1 - 0.9) / 2) # Matches calculation in setup

        # Draw beer level
        if self.beer_level > 0:
            arcade.draw_lrbt_rectangle_filled( # Corrected function name
                left=beer_rect_x,
                right=beer_rect_x + beer_rect_width,
                top=fillable_bottom_y + self.beer_level,
                bottom=fillable_bottom_y * 0.95,
                color=self.beer_color
            )

        self.glass_list.draw()


        # Draw target line
        line_start_x = self.glass_sprite.center_x - beer_rect_width / 2
        line_end_x = self.glass_sprite.center_x + beer_rect_width / 2
        arcade.draw_line(
            start_x=line_start_x, start_y=self.target_line_y,
            end_x=line_end_x, end_y=self.target_line_y,
            color=self.target_line_color,
            line_width=self.target_line_thickness
        )
        # Draw glass over beer so beer appears behind glass

        # Draw result/instruction text
        self.result_text.draw()


    def on_update(self, delta_time):
        if self.game_state == "FILLING":
            self.beer_level += self.beer_fill_rate * delta_time
            if self.beer_level >= self.beer_max_level:
                self.beer_level = self.beer_max_level
                self.stop_filling() # Auto-stop if overflow


    def setup_next_beer(self):
        """Resets the state for the next beer attempt."""
        self.beer_level = 0
        self.score = 0 # Reset score for the new attempt

        # Randomize target line position for the new beer
        self.target_line_height_ratio = random.uniform(0.3, 0.9)
        fillable_bottom_y = self.glass_sprite.bottom + (self.glass_sprite.height * self.beer_fillable_bottom_margin_ratio)
        self.target_line_y = fillable_bottom_y + (self.beer_max_level * self.target_line_height_ratio)

        self.game_state = "IDLE"
        self.result_text.text = f"Beer {self.current_beer_index + 1}/{self.total_beers}: Hold SPACE to fill"
        # Ensure text position is updated if needed (might not be necessary if static)
        self.result_text.x = self.window.width / 2
        self.result_text.y = self.glass_sprite.top + 30

    def start_filling(self):
        if self.game_state == "IDLE":
            self.beer_level = 0 # Reset just in case
            self.game_state = "FILLING"
            # Set a random fill rate each time filling starts
            self.beer_fill_rate = random.uniform(150, 300) # Faster range (e.g., 150-300 pixels/sec)
            self.result_text.text = f"Beer {self.current_beer_index + 1}/{self.total_beers}: Release SPACE to stop"

    def stop_filling(self):
        if self.game_state == "FILLING":
            # Calculate score for the current beer
            fillable_bottom_y = self.glass_sprite.bottom + (self.glass_sprite.height * self.beer_fillable_bottom_margin_ratio)
            final_beer_top_y = fillable_bottom_y + self.beer_level
            line_bottom = self.target_line_y - self.target_line_thickness / 2 - self.target_line_tolerance
            line_top = self.target_line_y + self.target_line_thickness / 2 + self.target_line_tolerance

            if line_bottom <= final_beer_top_y <= line_top:
                self.score = 1 # Score for this attempt
                attempt_result_text = "Perfect! +1 point."
            else:
                self.score = 0 # Score for this attempt
                attempt_result_text = "Missed! +0 points."

            self.round_score += self.score # Add attempt score to round score
            self.current_beer_index += 1 # Move to the next beer index

            if self.current_beer_index < self.total_beers:
                # More beers to fill
                self.game_state = "BETWEEN_BEERS"
                self.result_text.text = f"{attempt_result_text} Press SPACE for Beer {self.current_beer_index + 1}/{self.total_beers}."
            else:
                # All beers filled
                self.game_state = "ROUND_OVER"
                self.result_text.text = f"Round Over! Final Score: {self.round_score}/{self.total_beers}. Press SPACE to exit."


    def return_to_menu(self, final_score):
        """Handles returning the score and switching view back to menu."""
        print(f"{self.get_name()} finished, returning score: {final_score}")
        self.window.last_game_score = final_score
        if hasattr(self.window, 'game_menu_view_instance'):
            self.window.show_view(self.window.game_menu_view_instance)
        else:
            print("Error: Could not find game_menu_view_instance on window to return.")
        self.game_state = "DONE" # Prevent further input


    def on_key_press(self, key, modifiers):
        if self.game_state == "DONE": return # Ignore input if game already finished

        if key == arcade.key.SPACE:
            if self.game_state == "IDLE":
                self.start_filling()
            elif self.game_state == "BETWEEN_BEERS":
                self.setup_next_beer() # Prepare and start the next beer
            elif self.game_state == "ROUND_OVER":
                # User pressed SPACE after the round finished, return to menu with final round score
                self.return_to_menu(self.round_score)

        elif key == arcade.key.ESCAPE:
            # Allow escaping anytime, return current round score
            self.return_to_menu(self.round_score)


    def on_key_release(self, key, modifiers):
        if self.game_state == "DONE": return

        if key == arcade.key.SPACE:
            if self.game_state == "FILLING":
                self.stop_filling()


    def run(self, window):
        """ Launch the game view instead of returning a score directly """
        self.window = window
        self.setup_positions() # Ensure positions are set before showing
        window.show_view(self)
        return None # Score is returned via return_to_menu

    def get_name(self):
        return "Europa Bar Challenge"

    def get_color(self):
        return Color(0, 0, 255)
