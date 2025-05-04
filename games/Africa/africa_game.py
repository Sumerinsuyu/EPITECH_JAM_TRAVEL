import arcade
import os
import random
from games.IGame import IGame
from PIL import Image
from arcade import Rect

# Game constants
MAX_FRUIT = 10
GAME_DURATION = 30.0 # seconds
MAX_SCORE = 5

class AfricaGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()
        self.title = "Africa Fruit Catcher"
        self.window = arcade.get_window() # Get window early for dimensions
        if not self.window:
             # Fallback dimensions if window doesn't exist yet (e.g., during testing)
             print("Warning: Window not found during AfricaGame init. Using default dimensions.")
             self._window_width = 800
             self._window_height = 600
        else:
             self._window_width = self.window.width
             self._window_height = self.window.height

        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self._load_assets()
        self._setup_sprites()
        self._setup_text()
        # Game state variables will be initialized in setup()

    def _load_assets(self):
        """Load textures and sounds."""
        # Load and resize background
        try:
            bg_path = os.path.join(self.assets_dir, "savanaBG.png")
            pil_bg = Image.open(bg_path).convert("RGBA").resize((self._window_width, self._window_height))
            self.bg_texture = arcade.Texture.create_empty("bg_resized", (self._window_width, self._window_height))
            self.bg_texture.image = pil_bg
        except FileNotFoundError:
            print(f"Error: Background file not found at {bg_path}")
            self.bg_texture = None
        except Exception as e:
            print(f"Error loading/resizing background: {e}")
            self.bg_texture = None

        # Load fruit spritesheet info (3 rows x 3 cols)
        try:
            fruit_path = os.path.join(self.assets_dir, "fruit.png")
            self.fruit_image, self.fruit_w, self.fruit_h, self.fruit_rows, self.fruit_cols = self.load_fruit_info(fruit_path)
        except FileNotFoundError:
             print(f"Error: Fruit spritesheet not found at {fruit_path}")
             self.fruit_image = None # Handle missing spritesheet
        except Exception as e:
             print(f"Error loading fruit info: {e}")
             self.fruit_image = None

    def _setup_sprites(self):
        """Create sprite lists and player sprite."""
        # Load zebra
        try:
            self.zebra_sprite = arcade.Sprite(os.path.join(self.assets_dir, "zebraS.png"), scale=0.3)
        except FileNotFoundError:
             print("Error: Zebra sprite not found. Using placeholder.")
             self.zebra_sprite = arcade.SpriteCircle(30, arcade.color.GRAY) # Placeholder

        self.zebra_sprite.center_x = self._window_width // 2
        self.zebra_sprite.center_y = 60
        self.zebra_speed = 8
        self.zebra_list = arcade.SpriteList()
        self.zebra_list.append(self.zebra_sprite)

        self.fruit_list = arcade.SpriteList()

    def _setup_text(self):
        """Initialize text objects."""
        self.fruit_count_text = arcade.Text(
            "Fruit: 0",
            20, self._window_height - 40, arcade.color.BLACK, 28
        )
        self.timer_text = arcade.Text(
            f"Time: {GAME_DURATION:.1f}",
             self._window_width // 2, self._window_height - 40, arcade.color.BLACK, 28, anchor_x="center"
        )
        self.game_over_display_text = arcade.Text(
            "", self._window_width // 2, self._window_height // 2, arcade.color.RED, 48,
            anchor_x="center", anchor_y="center", multiline=True, width=self._window_width * 0.8
        )

    def setup(self):
        """Reset game state for a new round."""
        self.fruit_count = 0
        self.game_over = False
        self.game_timer = GAME_DURATION
        self.final_score = 0 # Score calculated at the end
        self.fruit_spawn_timer = 0
        self.fruit_spawn_interval = 0.8
        self.held_keys = set()

        # Clear sprite lists
        self.fruit_list.clear()

        # Reset zebra position
        self.zebra_sprite.center_x = self._window_width // 2
        self.zebra_sprite.center_y = 60

        # Update text displays
        self.fruit_count_text.text = f"Fruit: {self.fruit_count}"
        self.timer_text.text = f"Time: {self.game_timer:.1f}"
        self.game_over_display_text.text = ""


    def get_name(self):
        return self.title

    def run(self, window):
        """Called by the menu to start the game."""
        self.window = window # Ensure window reference is updated
        # Update dimensions if they changed since init
        self._window_width = self.window.width
        self._window_height = self.window.height
        # Re-setup positions based on potentially new window size
        self._setup_sprites()
        self._setup_text()
        self.setup() # Initialize/reset game state
        window.show_view(self)
        # Score is no longer returned here, it's set via _return_to_menu

    def on_draw(self):
        self.clear()
        # Draw background
        if self.bg_texture:
            rect = Rect(
                0, self._window_width, 0, self._window_height,
                self._window_width, self._window_height,
                self._window_width // 2, self._window_height // 2
            )
            arcade.draw_texture_rect(self.bg_texture, rect)
        else:
             arcade.set_background_color(arcade.color.DARK_GREEN) # Fallback background

        # Draw game elements
        self.zebra_list.draw()
        self.fruit_list.draw()

        # Draw UI text
        self.fruit_count_text.draw()
        self.timer_text.draw()

        # Draw game over message if applicable
        if self.game_over:
            self.game_over_display_text.draw()

    def on_update(self, delta_time):
        if self.game_over:
            return

        # Update timer
        self.game_timer -= delta_time
        if self.game_timer <= 0:
            self.game_timer = 0
            self.end_game() # Timer ran out

        # Update UI text
        self.timer_text.text = f"Time: {self.game_timer:.1f}"
        self.fruit_count_text.text = f"Fruit: {self.fruit_count}"

        # Game logic
        self.handle_input()
        self.spawn_fruit(delta_time)
        self.fruit_list.update()
        self.check_catch()
        self.remove_missed_fruit()

    def handle_input(self):
        """Move the zebra based on held keys."""
        if arcade.key.LEFT in self.held_keys:
            self.zebra_sprite.center_x -= self.zebra_speed
            self.zebra_sprite.scale_x = 0.3 # Face left
            if self.zebra_sprite.left < 0:
                self.zebra_sprite.left = 0
        if arcade.key.RIGHT in self.held_keys:
            self.zebra_sprite.center_x += self.zebra_speed
            self.zebra_sprite.scale_x = -0.3 # Face right (flipped sprite)
            if self.zebra_sprite.right > self._window_width:
                self.zebra_sprite.right = self._window_width

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.held_keys.add(key)
        elif key == arcade.key.ESCAPE:
             # Return to menu without saving score
             self._return_to_menu(save_score=False)
        elif self.game_over and key == arcade.key.SPACE:
             # Return to menu with final score
             self._return_to_menu(save_score=True)

    def on_key_release(self, key, modifiers):
        if key in self.held_keys:
            self.held_keys.remove(key)

    def spawn_fruit(self, delta_time):
        """Spawn a random fruit if the timer allows."""
        if not self.fruit_image: return # Don't spawn if spritesheet failed to load

        self.fruit_spawn_timer += delta_time
        if self.fruit_spawn_timer >= self.fruit_spawn_interval:
            self.fruit_spawn_timer = 0
            row = random.randint(0, self.fruit_rows - 1)
            col = random.randint(0, self.fruit_cols - 1)
            left = col * self.fruit_w
            upper = row * self.fruit_h
            right = left + self.fruit_w
            lower = upper + self.fruit_h

            try:
                frame_img = self.fruit_image.crop((left, upper, right, lower))
                texture = arcade.Texture.create_empty(f"fruit_{row}_{col}", (self.fruit_w, self.fruit_h))
                texture.image = frame_img

                fruit = arcade.Sprite()
                fruit.texture = texture
                fruit.center_x = random.randint(40, self._window_width - 40)
                fruit.center_y = self._window_height + 30
                fruit.change_y = -random.uniform(4, 7) # Speed
                fruit.scale = 0.6
                self.fruit_list.append(fruit)
            except Exception as e:
                 print(f"Error creating fruit sprite from image: {e}")


    def check_catch(self):
        """Check if the zebra caught any fruit."""
        caught = arcade.check_for_collision_with_list(self.zebra_sprite, self.fruit_list)
        for fruit in caught:
            self.fruit_count += 1
            fruit.remove_from_sprite_lists()

        # Check for win condition
        if self.fruit_count >= MAX_FRUIT:
            self.end_game() # Reached max fruit

    def remove_missed_fruit(self):
        """Remove fruit that falls off the bottom."""
        for fruit in self.fruit_list:
            if fruit.top < 0: # Use top for removal check
                fruit.remove_from_sprite_lists()

    def end_game(self):
        """Set game over state and calculate final score."""
        if self.game_over: return # Prevent multiple calls

        self.game_over = True
        self.final_score = self._calculate_final_score()

        if self.fruit_count >= MAX_FRUIT:
            message = f"You caught {MAX_FRUIT} fruits!\nScore: {self.final_score}/{MAX_SCORE}"
        else: # Timer ran out
            message = f"Time's up!\nYou caught {self.fruit_count} fruits.\nScore: {self.final_score}/{MAX_SCORE}"
        message += "\nPress SPACE to return to menu."
        self.game_over_display_text.text = message


    def _calculate_final_score(self) -> int:
        """Calculate score based on fruit count."""
        if self.fruit_count >= MAX_FRUIT:
            return MAX_SCORE
        else:
            # Score proportional to fruits caught out of the max possible
            score = (self.fruit_count / MAX_FRUIT) * MAX_SCORE
            return round(score) # Round to nearest integer

    def _return_to_menu(self, save_score: bool = False):
        """Return to the main game menu, optionally saving the score."""
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            score_to_save = self._calculate_final_score() if save_score else 0
            print(f"{self.get_name()} finished. Score {'saved' if save_score else 'not saved'}: {score_to_save}")
            self.window.last_game_score = score_to_save
            self.window.show_view(self.window.game_menu_view_instance)
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close() # Fallback

    def load_fruit_info(self, path):
        """Load PIL image and calculate frame dimensions."""
        pil_image = Image.open(path).convert("RGBA")
        width, height = pil_image.size
        rows, cols = 3, 3
        frame_width = width // cols
        frame_height = height // rows
        return pil_image, frame_width, frame_height, rows, cols

    def get_color(self):
        return (255, 255, 0) # Gold/yellow for Africa
