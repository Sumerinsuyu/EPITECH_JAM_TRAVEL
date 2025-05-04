import arcade
from games.IGame import IGame
import os
import PIL.Image
import random

class AntarticaGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()
        self.title = "Antarctica Adventure"
        self.info_text = arcade.Text("Welcome to Antarctica Adventure!", 200, 550, arcade.color.WHITE, 24)
        self.init_movement()
        self.init_frames()
        self.init_sprite()
        self.init_fish()
        self.timer = 20.0  # 20 seconds timer
        self.fish_count = 0
        self.score = 0
        self.timer_text = arcade.Text(f"Time: {int(self.timer)}", 0, 0, arcade.color.WHITE, 24, anchor_x="right")
        self.fish_text = arcade.Text(f"Fish: {self.fish_count}", 10, 0, arcade.color.WHITE, 24, anchor_x="left")
        self.score_text = arcade.Text(f"Score: {self.score}", 0, 0, arcade.color.WHITE, 24, anchor_x="center")
        self.game_over = False

    def init_movement(self):
        self.window = arcade.get_window()
        if self.window:
            self.player_x = self.window.width // 2
            self.player_y = self.window.height // 2
        self.is_moving = False
        self.turning = False
        self.turn_direction = None
        self.held_keys = set()
        self.facing_right = False
        self.current_animation = 'idle'

    def init_frames(self):
        sprites_dir = os.path.join(os.path.dirname(__file__), "Spritesheets")
        self.idle_frames = self.load_frames(os.path.join(sprites_dir, "Idle.png"), scale=2.5)
        self.walk_frames = self.load_frames(os.path.join(sprites_dir, "Walk.png"), scale=2.5)
        self.turn_frames = self.load_frames(os.path.join(sprites_dir, "Turn.png"), scale=2.5)
        self.spin_frames = self.load_frames(os.path.join(sprites_dir, "Spin Attack.png"), scale=2.5)
        self.roll_frames = self.load_frames(os.path.join(sprites_dir, "Roll.png"), scale=2.5)
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.1
        self.last_frames = self.idle_frames

    def init_sprite(self):
        # Initialize penguin sprites for snake-like following, each with its own animation state
        self.penguin_sprites = []
        head_sprite = self.create_penguin_sprite(self.player_x, self.player_y)
        self.penguin_sprites.append(head_sprite)
        self.player_sprite = head_sprite  # Keep for compatibility
        self.player_list = arcade.SpriteList()
        self.player_list.append(head_sprite['sprite'])
        # Store previous positions for snake movement
        self.penguin_positions = [(self.player_x, self.player_y)]

    def create_penguin_sprite(self, x, y):
        # Each penguin is a dict with its own animation state
        sprite = arcade.Sprite()
        sprite.texture = self.idle_frames[0]
        sprite.center_x = x
        sprite.center_y = y
        return {
            'sprite': sprite,
            'current_frame': 0,
            'frame_timer': 0,
            'current_animation': 'idle',
            'facing_right': False,
            'last_frames': self.idle_frames
        }

    def init_fish(self):
        self.fish_list = arcade.SpriteList()
        self.spawn_fish()

    def spawn_fish(self):
        window = self.window or arcade.get_window()
        if not window:
            return
        fish_texture = arcade.load_texture(os.path.join(os.path.dirname(__file__), "Spritesheets", "fish.png"))
        fish_sprite = arcade.Sprite()
        fish_sprite.texture = fish_texture
        # Scale down the fish (e.g., 0.1x original size)
        fish_sprite.width = int(fish_texture.width * 0.1)
        fish_sprite.height = int(fish_texture.height * 0.1)
        # Spawn within borders (avoid black bars)
        border = 40
        x = random.randint(border, window.width - border)
        y = random.randint(border, window.height - border)
        fish_sprite.center_x = x
        fish_sprite.center_y = y
        self.fish_list.append(fish_sprite)

    # --- Return to Menu ---
    def _return_to_menu(self, save_score: bool = False):
        """Return to the main game menu. Optionally save the score."""
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            print(f"{self.get_name()} finished. Score {'saved' if save_score else 'not saved'}: {self.score}")
            if save_score:
                # Use the calculated score based on fish count
                self.window.last_game_score = self.score
            else:
                 # Score is 0 if ESC is pressed or not saving
                 self.window.last_game_score = 0
            # Ensure the menu view instance exists before showing it
            menu_view = getattr(self.window, "game_menu_view_instance", None)
            if menu_view:
                self.window.show_view(menu_view)
            else:
                print("Error: game_menu_view_instance not found on window.")
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close() # Fallback: close window if menu is broken

    # --- Public API ---
    def get_name(self):
        return self.title

    def run(self, window):
        # Store window reference and setup initial state relative to window size
        self.window = window
        self.init_movement() # Re-initialize movement based on actual window size
        self.init_sprite() # Re-initialize sprite positions
        self.timer_text.position = (self.window.width - 10, self.window.height - 30)
        self.fish_text.position = (10, self.window.height - 30)
        self.score_text.position = (self.window.width // 2, self.window.height - 30)
        # Reset game state before showing
        self.timer = 20.0
        self.fish_count = 0
        self.score = 0
        self.game_over = False
        self.penguin_sprites = [] # Clear previous penguins
        self.player_list = arcade.SpriteList() # Clear previous list
        self.fish_list = arcade.SpriteList() # Clear previous fish
        self.init_sprite() # Recreate head sprite
        self.init_fish() # Spawn initial fish
        # Show the view
        window.show_view(self)
        # Do not return score here for View-based games

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.SKY_BLUE)
        # Draw black borders
        border_thickness = 40
        # Top
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=self.window.width,
            top=self.window.height,
            bottom=self.window.height - border_thickness,
            color=arcade.color.BLACK,
        )
        # Bottom
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=self.window.width,
            top=border_thickness,
            bottom=0,
            color=arcade.color.BLACK,
        )
        # Left
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=border_thickness,
            top=self.window.height,
            bottom=0,
            color=arcade.color.BLACK,
        )
        # Right
        arcade.draw_lrbt_rectangle_filled(
            left=self.window.width - border_thickness,
            right=self.window.width,
            top=self.window.height,
            bottom=0,
            color=arcade.color.BLACK,
        )

        self.fish_list.draw()
        self.player_list.draw()  # Draw all penguins at once, in order
        # Draw timer in the top right corner (move up)
        self.timer_text.text = f"Time: {int(self.timer)}"
        self.timer_text.position = (self.window.width - 10, self.window.height - 30)  # moved up
        self.timer_text.draw()
        # Draw fish count in the top left corner (move up)
        self.fish_text.text = f"Fish: {self.fish_count}"
        self.fish_text.position = (10, self.window.height - 30)  # moved up
        self.fish_text.draw()
        # Draw score at the top center
        self.score_text.text = f"Score: {self.score} / 5"
        self.score_text.position = (self.window.width // 2, self.window.height - 30)
        self.score_text.draw()
        # Draw controls info at the bottom center
        controls_text = arcade.Text(
            "Space: Spin Attack    Right Shift: Roll",
            self.window.width // 2,
            50,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )
        controls_text.draw()
        if self.fish_count >= 15:
            win_text = arcade.Text(
                "You Win!",
                self.window.width // 2,
                self.window.height // 2,
                arcade.color.GREEN,
                48,
                anchor_x="center"
            )
            win_text.draw()
        elif self.game_over:
            game_over_text = arcade.Text(
                "Game Over",
                self.window.width // 2,
                self.window.height // 2,
                arcade.color.RED,
                48,
                anchor_x="center"
            )
            game_over_text.draw()
            # Add message to return to menu
            return_text = arcade.Text(
                "Press SPACE to return to menu",
                self.window.width // 2,
                self.window.height // 2 - 50, # Below game over/win text
                arcade.color.WHITE,
                20,
                anchor_x="center"
            )
            return_text.draw()


    def on_key_press(self, key, modifiers):
        self.handle_key_press(key)

    def on_key_release(self, key, modifiers):
        self.handle_key_release(key)

    def on_update(self, delta_time):
        if self.game_over or self.fish_count >= 15:
            return
        self.timer -= delta_time
        if self.timer <= 0:
            self.timer = 0
            self.game_over = True
            return
        self.handle_movement()
        self.update_animation(delta_time)
        self.sync_sprite_position()
        self.update_penguin_followers()
        self.update_penguin_animations(delta_time)
        # Fish collection logic during Spin Attack
        if self.current_animation == 'spin':
            hit_list = arcade.check_for_collision_with_list(self.player_sprite['sprite'], self.fish_list)
            if hit_list:
                self.fish_count += len(hit_list)
                for fish in hit_list:
                    self.reposition_fish(fish)
                    self.add_penguin_follower()
        # Update score
        new_score = min(self.fish_count // 3, 5)
        if new_score != self.score:
            self.score = new_score
        if self.fish_count >= 15:
            self.game_over = True
            # Don't return here, let on_draw show the win message and wait for SPACE

    def reposition_fish(self, fish_sprite):
        window = self.window or arcade.get_window()
        if not window:
            return
        border = 40
        x = random.randint(border, window.width - border)
        y = random.randint(border, window.height - border)
        fish_sprite.center_x = x
        fish_sprite.center_y = y

    def get_color(self):
        return (0, 255, 255)

    # --- Input Handling ---
    def handle_key_press(self, key):
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            self.held_keys.add(key)
        if key == arcade.key.SPACE and not self.game_over and self.current_animation not in ('spin', 'roll'):
            self.current_animation = 'spin'
            self.current_frame = 0
            self.frame_timer = 0
        if key == arcade.key.RSHIFT and not self.game_over and self.current_animation not in ('spin', 'roll'):
            self.current_animation = 'roll'
            self.current_frame = 0
            self.frame_timer = 0
        if key == arcade.key.ESCAPE:
            # Return to menu without saving score
            self._return_to_menu(save_score=False)
        if self.game_over and key == arcade.key.SPACE:
             # Return to menu with final score
            self._return_to_menu(save_score=True)


    def handle_key_release(self, key):
        if key in self.held_keys:
            self.held_keys.remove(key)
        if key in (arcade.key.LSHIFT, arcade.key.RSHIFT) and self.current_animation == 'roll':
            self.current_animation = 'idle'

    # --- Movement Logic ---
    def handle_movement(self):
        prev_facing_right = self.facing_right
        self._update_position()
        self._update_direction(prev_facing_right)
        # Only update animation state if not in a special animation
        if self.current_animation not in ('spin', 'roll', 'turn'):
            self._update_animation_state()

    def _update_position(self):
        base_speed = 5
        move_speed = base_speed
        if self.current_animation == 'roll':
            move_speed = int(base_speed * 2.5)
        moving = False
        window = self.window or arcade.get_window()
        sprite_half_width = self.player_sprite['sprite'].texture.width // 2
        sprite_half_height = self.player_sprite['sprite'].texture.height // 2

        # Move and clamp Y
        if arcade.key.UP in self.held_keys:
            new_y = self.player_y + move_speed
            max_y = window.height - sprite_half_height
            if new_y <= max_y:
                self.player_y = new_y
                moving = True
            else:
                self.player_y = max_y
        if arcade.key.DOWN in self.held_keys:
            new_y = self.player_y - move_speed
            min_y = sprite_half_height - 40
            if new_y >= min_y:
                self.player_y = new_y
                moving = True
            else:
                self.player_y = min_y

        # Move and clamp X
        if arcade.key.LEFT in self.held_keys:
            new_x = self.player_x - move_speed
            min_x = sprite_half_width
            if new_x >= min_x:
                self.player_x = new_x
                moving = True
            else:
                self.player_x = min_x
            self.facing_right = False
        if arcade.key.RIGHT in self.held_keys:
            new_x = self.player_x + move_speed
            max_x = window.width - sprite_half_width
            if new_x <= max_x:
                self.player_x = new_x
                moving = True
            else:
                self.player_x = max_x
            self.facing_right = True

        self.is_moving = moving

    def _update_direction(self, prev_facing_right):
        if prev_facing_right != self.facing_right:
            self.turning = True
            self.current_frame = 0
            self.frame_timer = 0
            self.turn_direction = self.facing_right
            self.current_animation = 'turn'

    def _update_animation_state(self):
        # Only update to walk/idle if not in a special animation
        if self.current_animation in ('spin', 'roll', 'turn'):
            return
        if self.is_moving:
            self.current_animation = 'walk'
        else:
            self.current_animation = 'idle'

    # --- Animation Logic ---
    def play_animation(self, frames, delta_time, loop=True, on_end=None, scale_x=None):
        if self.last_frames is not frames:
            self.current_frame = 0
            self.last_frames = frames
        self.frame_timer += delta_time
        if self.frame_timer >= self.frame_duration:
            self.current_frame += 1
            self.frame_timer = 0
        if self.current_frame >= len(frames):
            if loop:
                self.current_frame = 0
            else:
                if on_end:
                    on_end()
                return
        self.player_sprite['sprite'].texture = frames[self.current_frame]
        self.player_sprite['sprite'].scale_y = 1
        if scale_x is not None:
            self.player_sprite['sprite'].scale_x = scale_x

    def update_turn_animation(self, delta_time):
        def end_turn():
            self.turning = False
            self.current_frame = 0
            if self.is_moving:
                self.current_animation = 'walk'
            else:
                self.current_animation = 'idle'
        scale_x = -1 if self.turn_direction else 1
        self.play_animation(self.turn_frames, delta_time, loop=False, on_end=end_turn, scale_x=scale_x)

    def update_animation(self, delta_time):
        # Only update the head's animation state, not the texture
        if self.current_animation == 'spin':
            def end_spin():
                self.current_animation = 'idle'
            # Advance frame for spin, but don't set texture here
            self.player_sprite['frame_timer'] += delta_time * 2
            if self.player_sprite['frame_timer'] >= self.frame_duration:
                self.player_sprite['current_frame'] += 1
                self.player_sprite['frame_timer'] = 0
            if self.player_sprite['current_frame'] >= len(self.spin_frames):
                end_spin()
                self.player_sprite['current_frame'] = 0
        elif self.current_animation == 'roll':
            def end_roll():
                self.current_animation = 'idle'
            self.player_sprite['frame_timer'] += delta_time
            if self.player_sprite['frame_timer'] >= self.frame_duration:
                self.player_sprite['current_frame'] += 1
                self.player_sprite['frame_timer'] = 0
            if self.player_sprite['current_frame'] >= len(self.roll_frames):
                end_roll()
                self.player_sprite['current_frame'] = 0
        elif self.turning or getattr(self, 'current_animation', None) == 'turn':
            self.update_turn_animation(delta_time)
        elif getattr(self, 'current_animation', None) == 'walk':
            self.player_sprite['frame_timer'] += delta_time
            if self.player_sprite['frame_timer'] >= self.frame_duration:
                self.player_sprite['current_frame'] = (self.player_sprite['current_frame'] + 1) % len(self.walk_frames)
                self.player_sprite['frame_timer'] = 0
        elif getattr(self, 'current_animation', None) == 'idle':
            self.player_sprite['frame_timer'] += delta_time
            if self.player_sprite['frame_timer'] >= self.frame_duration:
                self.player_sprite['current_frame'] = (self.player_sprite['current_frame'] + 1) % len(self.idle_frames)
                self.player_sprite['frame_timer'] = 0
        else:
            self.current_animation = 'idle'
            self.player_sprite['frame_timer'] += delta_time
            if self.player_sprite['frame_timer'] >= self.frame_duration:
                self.player_sprite['current_frame'] = (self.player_sprite['current_frame'] + 1) % len(self.idle_frames)
                self.player_sprite['frame_timer'] = 0

    def update_penguin_animations(self, delta_time):
        # Head copies the main animation state, followers always walk or idle
        for i, penguin in enumerate(self.penguin_sprites):
            if i == 0:
                # Head: use the main animation state (including spin/roll)
                anim = self.current_animation
                facing = self.facing_right
            else:
                # Followers: walk if moving, else idle, and face the same as head
                anim = 'walk' if self.is_moving else 'idle'
                facing = self.facing_right
            self.animate_penguin(penguin, anim, facing, delta_time)

    def animate_penguin(self, penguin, anim, facing_right, delta_time):
        # Choose frames for all animation types
        if anim == 'walk':
            frames = self.walk_frames
        elif anim == 'idle':
            frames = self.idle_frames
        elif anim == 'spin':
            frames = self.spin_frames
        elif anim == 'roll':
            frames = self.roll_frames
        else:
            frames = self.idle_frames
        # Animation logic
        if penguin['last_frames'] is not frames:
            penguin['current_frame'] = 0
            penguin['last_frames'] = frames
        penguin['frame_timer'] += delta_time
        # Make spin animation faster
        frame_duration = self.frame_duration
        if anim == 'spin':
            frame_duration /= 2
        if penguin['frame_timer'] >= frame_duration:
            penguin['current_frame'] = (penguin['current_frame'] + 1) % len(frames)
            penguin['frame_timer'] = 0
        penguin['sprite'].texture = frames[penguin['current_frame']]
        penguin['sprite'].scale_y = 1
        penguin['sprite'].scale_x = -1 if facing_right else 1

    # --- Sprite Position Sync ---
    def sync_sprite_position(self):
        # Sync head position
        self.player_sprite['sprite'].center_x = self.player_x
        self.player_sprite['sprite'].center_y = self.player_y

    def update_penguin_followers(self):
        # Always append the head's position, even if not moving
        head_pos = (self.player_sprite['sprite'].center_x, self.player_sprite['sprite'].center_y)
        self.penguin_positions.insert(0, head_pos)
        min_distance = 10  # Adjust for more/less separation
        # Each follower follows the one in front of it, using a delay
        for i in range(1, len(self.penguin_sprites)):
            pos_index = i * min_distance
            if pos_index < len(self.penguin_positions):
                self.penguin_sprites[i]['sprite'].center_x, self.penguin_sprites[i]['sprite'].center_y = self.penguin_positions[pos_index]
        # Limit the positions history to the number of penguins and min_distance
        max_history = len(self.penguin_sprites) * min_distance
        if len(self.penguin_positions) > max_history:
            self.penguin_positions = self.penguin_positions[:max_history]

    def add_penguin_follower(self):
        # Add a new penguin at the last segment's position, with its own animation state
        if self.penguin_sprites:
            last_sprite = self.penguin_sprites[-1]['sprite']
            new_penguin = self.create_penguin_sprite(last_sprite.center_x, last_sprite.center_y)
            self.penguin_sprites.append(new_penguin)
            self.player_list.append(new_penguin['sprite'])
            if self.penguin_positions:
                self.penguin_positions.append((last_sprite.center_x, last_sprite.center_y))

    # --- Frame Loading Helper ---
    def load_frames(self, path, scale=1.0):
        pil_image = PIL.Image.open(path).convert("RGBA")
        width, height = pil_image.size
        frame_count = width // height
        frame_width = width // frame_count
        frames = []
        for i in range(frame_count):
            box = (i * frame_width, 0, (i + 1) * frame_width, height)
            frame_img = pil_image.crop(box)
            if scale != 1.0:
                new_size = (int(frame_img.width * scale), int(frame_img.height * scale))
                frame_img = frame_img.resize(new_size, PIL.Image.Resampling.LANCZOS)
            texture = arcade.Texture.create_empty(f"{os.path.basename(path)}_frame_{i}", frame_img.size)
            texture.image = frame_img
            frames.append(texture)
        return frames