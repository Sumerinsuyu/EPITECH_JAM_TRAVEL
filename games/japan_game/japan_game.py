import arcade
import random
import os
from abc import ABC, abstractmethod
from typing import Tuple

from games.IGame import IGame
from arcade.types import Rect

CUT_ZONE_TOP = 150
CUT_ZONE_BOTTOM = 100
MARGIN = 65

class JapanGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()

        self.title = "Japan - Sushi Rampage"
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")
        self.score = 0
        self.sushi_health = 8
        self.sushi_speed = 600
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        self.game_over_text = "GAME OVER!"
        self.background_texture = arcade.load_texture(
            os.path.join(self.assets_path, "japangamebg.jpg")
        )
        self.background_rect = Rect(0, self.window.width, self.window.height, 0, self.window.width, self.window.height, self.window.width / 2, self.window.height / 2)
        self.sushi_list = arcade.SpriteList()
        self.cut_sprites = arcade.SpriteList()
        self.cut_timers = []
        self.cut_sound = None
        self.life_sprites = arcade.SpriteList()
        self._load_assets()

    def _load_assets(self):
        """Load game assets (background, sounds)"""
        try:
            self.cut_sound = arcade.load_sound(
                os.path.join(self.assets_path, "cut.wav")
            )
        except:
            pass


    def get_name(self) -> str:
        return "Sushi Rampage"

    def get_color(self) -> Tuple[int, int, int]:
        return (255, 0, 254)

    def run(self, window: arcade.Window) -> int:
        """Run the game and return the score"""
        self.setup()
        if not hasattr(window, "game_menu_view_instance"):
            window.game_menu_view_instance = None  # ou mets ton menu ici
        window.show_view(self)

    def setup(self):
        """Initialize game state"""
        self.score = 0
        self.sushi_health = 6
        self.sushi_speed = 600
        self.sushi_list = arcade.SpriteList()
        self.cut_sprites = arcade.SpriteList()
        self.cut_timers = []
        self.window.set_mouse_visible(True)
        self._update_life_sprites()

    def on_draw(self):
        """Render the game"""
        self.clear()
        arcade.draw_texture_rect(self.background_texture, self.background_rect)
        if self.sushi_health <= 0:
            arcade.draw_text(
                self.game_over_text,
                self.window.width / 2,
                self.window.height / 2,
                arcade.color.BLACK, 24,
                anchor_x="center",
                anchor_y="center"
            )
            return
        
        arcade.draw_text(
            "    Press SPACE to slice the sushi!",
            self.window.width * 0.25,
            self.window.height * 0.85,
            arcade.color.BLACK, 46
        )
        
        arcade.draw_text(
            f"Score: {self.score}",
            10,
            self.window.height - 65,
            arcade.color.BLACK, 50
        )
        
        arcade.draw_lrbt_rectangle_outline(
            0, self.window.width,
            100, 150,
            self.rect_color, 2
        )
        
        self.sushi_list.draw()
        self.cut_sprites.draw()
        self.life_sprites.draw()

    def on_update(self, delta_time):
        """Game logic update"""
        self.rect_color = arcade.color.RED 

        if self.sushi_health > 0:
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_interval:
                x = random.randint(50, self.window.width - 50)
                self._spawn_sushi(x, self.window.height)
                self.spawn_timer = 0

            for sushi in self.sushi_list:
                sushi.center_y -= self.sushi_speed * delta_time
                if sushi.center_y < 0:
                    self.sushi_list.remove(sushi)
                    self.sushi_health -= 1
                    self._update_life_sprites()
            
            self._update_cut_pieces(delta_time)
            
            
            if any(CUT_ZONE_BOTTOM - MARGIN < sushi.center_y < CUT_ZONE_TOP + MARGIN for sushi in self.sushi_list):
                self.rect_color = arcade.color.WHITE

    def _update_life_sprites(self):
        """Met à jour les icônes de vies affichées."""
        self.life_sprites = arcade.SpriteList()
        spacing = 10
        icon_path = os.path.join(self.assets_path, "sakurahealth.png")
    
        sample_sprite = arcade.Sprite(icon_path, scale=0.3)
        icon_width = sample_sprite.width
        total_width = self.sushi_health * icon_width + (self.sushi_health - 1) * spacing
        start_x = (self.window.width - total_width) / 2
        y = 40

        for i in range(self.sushi_health):
            x = start_x + i * (icon_width + spacing)
            sprite = arcade.Sprite(icon_path, scale=0.17)
            sprite.center_x = x
            sprite.center_y = y
            self.life_sprites.append(sprite)

    def _spawn_sushi(self, x, y):
        """Create new sushi at position"""
        sushi = arcade.Sprite(
            os.path.join(self.assets_path, "sushi.png"), 
            scale=0.35
        )
        sushi.center_x = x
        sushi.center_y = y
        self.sushi_list.append(sushi)

    def _update_cut_pieces(self, delta_time):
        """Update cut sushi pieces"""
        for sprite in self.cut_sprites:
            sprite.center_x += sprite.change_x * delta_time
            sprite.center_y -= 50 * delta_time

        self.cut_timers = [t - delta_time for t in self.cut_timers]
        while self.cut_timers and self.cut_timers[0] <= 0:
            self.cut_sprites.pop(0)
            self.cut_timers.pop(0)

    def on_key_press(self, key, modifiers):
        """Handle keyboard input"""
        if key == arcade.key.SPACE:
            self._attempt_cut()
        elif key == arcade.key.ESCAPE:
            self._return_to_menu(save_score=False)

    def _return_to_menu(self, save_score: bool = False):
        """Return to the main game menu. Optionally save the score."""
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            print(f"{self.get_name()} finished. Score {'saved' if save_score else 'not saved'}: {self.score}")
            if save_score:
                self.window.last_game_score = self.score
            else:
                 self.window.last_game_score = 0
            self.window.show_view(self.window.game_menu_view_instance)
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close()


    def _attempt_cut(self):
        """Try to cut sushi in the cut zone"""
        for sushi in self.sushi_list:
            if 50 < sushi.center_y < 150:
                self._cut_sushi(sushi)
                break

    def _cut_sushi(self, sushi):
        """Cut a sushi into pieces"""
        self.sushi_list.remove(sushi)
        self.score += 1
        self.sushi_speed += 175

        left = arcade.Sprite(
            os.path.join(self.assets_path, "sushi_half_left.png"),
            scale=0.5
        )
        left.center_x = sushi.center_x
        left.center_y = sushi.center_y
        left.change_x = -150

        right = arcade.Sprite(
            os.path.join(self.assets_path, "sushi_half_right.png"),
            scale=0.5
        )
        right.center_x = sushi.center_x
        right.center_y = sushi.center_y
        right.change_x = 150

        self.cut_sprites.extend([left, right])
        self.cut_timers.extend([0.5, 0.5])

        if self.cut_sound:
            arcade.play_sound(self.cut_sound)
