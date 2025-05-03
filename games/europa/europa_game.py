import arcade
from games.IGame import IGame
import random # Import random module
import os # Import os module

from arcade.types import Color

class EuropaGame(IGame, arcade.View):
    def __init__(self):
        super().__init__(window=None) # Pass window=None initially
        self.score = 0
        # Create a SpriteList for the background
        self.background_list = arcade.SpriteList()
        # Load background image
        background_path = os.path.join(os.path.dirname(__file__), "assets", "bar.jpg")
        try:
            self.background_sprite = arcade.Sprite(background_path)
            # Add the sprite to the list
            self.background_list.append(self.background_sprite)
            # We will set position and size in on_show_view or when window is available
        except FileNotFoundError:
            print(f"Error: Background image not found at {background_path}")
            self.background_sprite = None # Keep track if loading failed
        # Remove the running_text or update its position if needed
        # self.running_text = arcade.Text("Europa Game Running", 100, 300, arcade.color.WHITE, 24)

    def on_show_view(self):
        """ Called when switching to this view"""
        arcade.set_background_color(arcade.color.BLACK) # Or another appropriate color
        # Check if the sprite exists before trying to position/scale it
        if self.background_sprite and self.window:
            self.background_sprite.center_x = self.window.width / 2
            self.background_sprite.center_y = self.window.height / 2
            # Optional: Scale background to fit window
            scale_x = self.window.width / self.background_sprite.width
            scale_y = self.window.height / self.background_sprite.height
            # Use scale attribute directly on the sprite
            self.background_sprite.scale = min(scale_x, scale_y) # Maintain aspect ratio

    def on_draw(self):
        self.clear()
        # Draw the SpriteList containing the background
        self.background_list.draw()
        # Draw other game elements here if needed
        # self.running_text.draw() # Example: draw text if you keep it

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Calculate score before returning
            score = random.randint(5, 10) # Calculate score here
            print(f"{self.get_name()} finished, returning score: {score}")
            # Store score on the window object for the menu to retrieve
            self.window.last_game_score = score

            # Access the stored menu view instance to return
            if hasattr(self.window, 'game_menu_view_instance'):
                self.window.show_view(self.window.game_menu_view_instance)
            else:
                print("Error: Could not find game_menu_view_instance on window to return.")

    def run(self, window):
        """ Launch the game view instead of returning a score directly """
        self.window = window # Store the window reference
        # Ensure the sprite list is updated if window size changed before showing
        self.on_show_view() # Call on_show_view to set position/scale correctly
        window.show_view(self)
        # Return None to indicate the game is launched as a view
        # The score will be handled when returning via ESCAPE key press
        return None

    def get_name(self):
        return "Europa Game"

    def get_color(self):
        # Using Blue for Europa, ensure this color is unique on the map
        return Color(0, 0, 255)
