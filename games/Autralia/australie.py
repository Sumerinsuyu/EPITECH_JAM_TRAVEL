import arcade
from arcade.types import Color
from games.IGame import IGame
import time

WIDTH = 800
HEIGHT = 600
TITLE = "Test Fenêtre Arcade"

class AustralieGame(arcade.View, IGame):
    def __init__(self):
        super().__init__()
        self.counter = 10
        self.punch = 0
        self.punch_timer_playeur = 0
        self.punch_timer_kangaroo = 0
        self.stun_timer_playeur = 0
        self.window = arcade.get_window()
        self.keys = set()
        self.player_hp = 100
        self.kangaroo_hp = 100
        self.game_over = False
        self.game_over_time = 0
        self.final_score = 0

        # Load background sprite
        try:
            self.background_sprite = arcade.Sprite("games/Autralia/assets/sydney.png")
            self.background_sprite.width = self.window.width
            self.background_sprite.height = self.window.height
            self.background_sprite.center_x = self.window.width / 2
            self.background_sprite.center_y = self.window.height / 2
            self.background_list = arcade.SpriteList()
            self.background_list.append(self.background_sprite)
        except FileNotFoundError:
            print("Error: Background file not found.")
            self.background_list = None

        self.kangaroo_wait = arcade.Sprite("games/Autralia/assets/kangaroo_wait.png", 0.5)
        self.kangaroo_wait.center_x = 200
        self.kangaroo_wait.center_y = 300

        self.kangaroo_hit = arcade.Sprite("games/Autralia/assets/kangaroo_hit.png", 0.5)
        self.kangaroo_hit.center_x = 200
        self.kangaroo_hit.center_y = 300

        self.kangaroo_wait_list = arcade.SpriteList()
        self.kangaroo_wait_list.append(self.kangaroo_wait)

        self.kangaroo_hit_list = arcade.SpriteList()
        self.kangaroo_hit_list.append(self.kangaroo_hit)

        # Sprites du joueur (wait/hit)
        self.playeur_wait = arcade.Sprite("games/Autralia/assets/playeur_wait.png", 0.6)
        self.playeur_wait.center_x = self.window.width - 200
        self.playeur_wait.center_y = 240

        self.playeur_hit = arcade.Sprite("games/Autralia/assets/playeur_hit.png", 0.6)
        self.playeur_hit.center_x = self.window.width - 200
        self.playeur_hit.center_y = 240

        self.playeur_wait_list = arcade.SpriteList()
        self.playeur_wait_list.append(self.playeur_wait)

        self.playeur_hit_list = arcade.SpriteList()
        self.playeur_hit_list.append(self.playeur_hit)

    def setup(self):
        """ Reset game state """
        self.player_hp = 100
        self.kangaroo_hp = 100
        self.punch_timer_playeur = 0
        self.punch_timer_kangaroo = 0
        self.stun_timer_playeur = 0
        self.game_over = False
        self.game_over_time = 0
        self.final_score = 0
        # Reset positions
        self.kangaroo_wait.center_x = 200
        self.kangaroo_wait.center_y = 300
        self.kangaroo_hit.center_x = 200
        self.kangaroo_hit.center_y = 300
        self.playeur_wait.center_x = self.window.width - 200
        self.playeur_wait.center_y = 240
        self.playeur_hit.center_x = self.window.width - 200
        self.playeur_hit.center_y = 240
        # Ensure background is sized correctly if window changed
        if self.background_list:
            self.background_sprite.width = self.window.width
            self.background_sprite.height = self.window.height
            self.background_sprite.center_x = self.window.width / 2
            self.background_sprite.center_y = self.window.height / 2

    def display_end_screen(self):
        # Affiche le résultat si un des deux est mort
        if self.player_hp <= 0:
            arcade.draw_text("LOOSE", self.window.width // 2 - 100, self.window.height // 2, arcade.color.RED, 60)
            arcade.draw_text("Press SPACE to return to menu", self.window.width // 2, self.window.height // 2 - 50, arcade.color.WHITE, 20, anchor_x="center")
        elif self.kangaroo_hp <= 0:
            # Calcul des points selon la vie restante du joueur
            hp = self.player_hp
            if 0 <= hp < 10:
                points = 1
            elif 10 <= hp < 20:
                points = 2
            elif 20 <= hp < 40:
                points = 3
            elif 40 <= hp < 70:
                points = 4
            elif 70 <= hp <= 100:
                points = 5
            else:
                points = 0
            self.final_score = points
            arcade.draw_text(f"WIN  {points} point(s)", self.window.width // 2 - 180, self.window.height // 2, arcade.color.GREEN, 60)
            arcade.draw_text("Press SPACE to return to menu", self.window.width // 2, self.window.height // 2 - 50, arcade.color.WHITE, 20, anchor_x="center")

    def on_draw(self):
        self.clear()
        # Draw background first
        if self.background_list:
            self.background_list.draw()
        # Barres de vie en haut, plus basses et plus grosses, avec bordure noire
        hp_bar_width = int(300 * 1.2)
        hp_bar_height = int(40 * 1.2)
        border_thickness = 4
        y_bar = self.window.height - 100
        # Joueur (gauche)
        # Bordure noire
        arcade.draw_lbwh_rectangle_filled(30 - border_thickness, y_bar - border_thickness, hp_bar_width + 2*border_thickness, hp_bar_height + 2*border_thickness, arcade.color.BLACK)
        # Barre verte
        arcade.draw_lbwh_rectangle_filled(30, y_bar, hp_bar_width * (self.player_hp / 100), hp_bar_height, arcade.color.GREEN)
        arcade.draw_text(f"{self.player_hp} HP", 40 + hp_bar_width, y_bar + 10, arcade.color.BLACK, 28)
        # Kangourou (droite)
        # Bordure noire
        arcade.draw_lbwh_rectangle_filled(self.window.width - 30 - hp_bar_width - border_thickness, y_bar - border_thickness, hp_bar_width + 2*border_thickness, hp_bar_height + 2*border_thickness, arcade.color.BLACK)
        # Barre rouge
        arcade.draw_lbwh_rectangle_filled(self.window.width - 30 - hp_bar_width, y_bar, hp_bar_width * (self.kangaroo_hp / 100), hp_bar_height, arcade.color.RED)
        arcade.draw_text(f"{self.kangaroo_hp} HP", self.window.width - 50 - hp_bar_width - 100, y_bar + 10, arcade.color.BLACK, 28)
        # Affiche le sprite du joueur
        if self.punch_timer_playeur > 0:
            self.playeur_hit_list.draw()
        else:
            self.playeur_wait_list.draw()
        # Affiche le sprite du kangourou
        if self.punch_timer_kangaroo > 0:
            self.kangaroo_hit_list.draw()
        else:
            self.kangaroo_wait_list.draw()
        # Affiche le résultat si un des deux est mort
        if self.game_over:
            self.display_end_screen()

    def on_update(self, delta_time):
        # Check if game is already over
        if self.game_over:
            self.game_over_time += delta_time
            return

        # Décrémente le timer du punch joueur
        if self.punch_timer_playeur > 0:
            self.punch_timer_playeur -= delta_time
            if self.punch_timer_playeur < 0:
                self.punch_timer_playeur = 0
        # Décrémente le timer du punch kangourou
        if self.punch_timer_kangaroo > 0:
            self.punch_timer_kangaroo -= delta_time
            if self.punch_timer_kangaroo < 0:
                self.punch_timer_kangaroo = 0
        # Décrémente le timer de stun du joueur
        if self.stun_timer_playeur > 0:
            self.stun_timer_playeur -= delta_time
            if self.stun_timer_playeur < 0:
                self.stun_timer_playeur = 0

        # Arrête le jeu si un des deux est mort (après 5 secondes d'affichage de l'écran de fin)
        if self.player_hp <= 0 or self.kangaroo_hp <= 0:
            self.game_over = True
            self.game_over_time = 0
            self.display_end_screen()
            return

        # Mouvement et attaque aléatoire du kangourou (zone de jeu limitée)
        import random
        # Définir les zones de déplacement
        zone_kangaroo_min = int(self.window.width * 0.0)
        zone_kangaroo_max = int(self.window.width * 0.7)
        zone_player_min = int(self.window.width * 0.3)
        zone_player_max = int(self.window.width * 1.0)
        # Mouvement : 30% avance, 20% recule, 50% rien (bouge moins)
        move = random.random()
        kangaroo_speed = 20
        if move < 0.3:
            # Avance vers le joueur
            if self.kangaroo_wait.center_x + kangaroo_speed < min(self.playeur_wait.center_x - 100, zone_kangaroo_max):
                self.kangaroo_wait.center_x += kangaroo_speed
                self.kangaroo_hit.center_x += kangaroo_speed
        elif move < 0.5:
            # Recule
            if self.kangaroo_wait.center_x - kangaroo_speed > zone_kangaroo_min:
                self.kangaroo_wait.center_x -= kangaroo_speed
                self.kangaroo_hit.center_x -= kangaroo_speed
        # Attaque aléatoire (2% de chance par frame, frappe moins souvent)
        if random.random() < 0.02 and self.punch_timer_kangaroo == 0:
            self.punch_timer_kangaroo = 0.5
            # Si à moins de 300px du joueur, inflige des dégâts
            distance = abs(self.playeur_wait.center_x - self.kangaroo_wait.center_x)
            if distance <= 300:
                self.player_hp -= 10
                self.stun_timer_playeur = 0.2  # Le joueur est stun 0.2s
                # Recul du joueur de 50px vers la droite
                self.playeur_wait.center_x += 50
                self.playeur_hit.center_x += 50

        # Collision : le joueur ne peut pas dépasser le kangourou et vice versa
        if self.playeur_wait.center_x < self.kangaroo_wait.center_x + 100:
            self.playeur_wait.center_x = self.kangaroo_wait.center_x + 100
            self.playeur_hit.center_x = self.kangaroo_wait.center_x + 100
        if self.kangaroo_wait.center_x > self.playeur_wait.center_x - 100:
            self.kangaroo_wait.center_x = self.playeur_wait.center_x - 100
            self.kangaroo_hit.center_x = self.playeur_wait.center_x - 100
        # Le joueur ne peut pas sortir de sa zone (30% à 100%)
        if self.playeur_wait.center_x < zone_player_min:
            self.playeur_wait.center_x = zone_player_min
            self.playeur_hit.center_x = zone_player_min
        if self.playeur_wait.center_x > zone_player_max:
            self.playeur_wait.center_x = zone_player_max
            self.playeur_hit.center_x = zone_player_max
        # Le kangourou ne peut pas sortir de sa zone (0% à 70%)
        if self.kangaroo_wait.center_x < zone_kangaroo_min:
            self.kangaroo_wait.center_x = zone_kangaroo_min
            self.kangaroo_hit.center_x = zone_kangaroo_min
        if self.kangaroo_wait.center_x > zone_kangaroo_max:
            self.kangaroo_wait.center_x = zone_kangaroo_max
            self.kangaroo_hit.center_x = zone_kangaroo_max

    def on_key_press(self, symbol, modifiers):
        if self.game_over:
            if symbol == arcade.key.SPACE and self.game_over_time > 0.5:
                self._return_to_menu(save_score=True)
            elif symbol == arcade.key.ESCAPE:
                self._return_to_menu(save_score=False)
            return

        self.keys.add(symbol)
        # Animation du coup toujours lancée
        if symbol == arcade.key.SPACE and self.punch_timer_playeur == 0 and self.stun_timer_playeur == 0:
            self.punch_timer_playeur = 0.5
            # Les PV ne descendent que si à 300px ou moins
            distance = abs(self.playeur_wait.center_x - self.kangaroo_wait.center_x)
            if distance <= 300:
                self.kangaroo_hp -= 10
                # Recul du kangourou de 50px vers la gauche
                self.kangaroo_wait.center_x -= 50
                self.kangaroo_hit.center_x -= 50
        # Quitter (use ESCAPE now for consistency)
        if symbol == arcade.key.ESCAPE:
            self._return_to_menu(save_score=False)
        # Déplacement joueur gauche
        if symbol == arcade.key.Q and self.punch_timer_playeur == 0:
            self.playeur_wait.center_x -= 100
            self.playeur_hit.center_x -= 100
        # Déplacement joueur droite
        if symbol == arcade.key.D and self.punch_timer_playeur == 0:
            self.playeur_wait.center_x += 100
            self.playeur_hit.center_x += 100

    def _return_to_menu(self, save_score: bool = False):
        """Return to the main game menu. Optionally save the score."""
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            score_to_save = self.final_score if save_score else 0
            print(f"{self.get_name()} finished. Score {'saved' if save_score else 'not saved'}: {score_to_save}")
            self.window.last_game_score = score_to_save
            menu_view = getattr(self.window, "game_menu_view_instance", None)
            if menu_view:
                self.window.show_view(menu_view)
            else:
                print("Error: game_menu_view_instance not found on window.")
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close()

    def get_name(self):
        return "Australie Fight"

    def get_color(self):
        return Color(255, 125, 0)

    def run(self, window=None):
        if window is None:
            window = self.window if hasattr(self, 'window') else arcade.get_window()
        self.window = window
        self.setup()
        window.show_view(self)
