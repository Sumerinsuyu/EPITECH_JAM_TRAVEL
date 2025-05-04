import arcade
import random
from games.IGame import IGame
from arcade.types import Color

# Game state
MENU = 0
RUNNING = 1
GAME_OVER = 2

# Directions
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

# Player status
IDLE = 0
KICK = 1
DEAD = 2

# Main Character
ROWS = 4
IDLE_COLS = 19
KICK_COLS = 10

# Capybara
WALK_COLS = 9
WALK_ROWS = 9
CAPYBARA_SIZE = 64
ENEMY_SPEED = 300

class GameOverView(arcade.View):
    def __init__(self, final_score):
        super().__init__()
        self.final_score = int(final_score)

    def on_draw(self):
        self.clear()
        arcade.Text("GAME OVER", self.window.width/2, self.window.height/2 + 50,
                         arcade.color.RED, 40, anchor_x="center").draw()
        arcade.Text(f"Final Score: {self.final_score}", self.window.width/2, self.window.height/2,
                         arcade.color.WHITE, 20, anchor_x="center").draw()
    def on_key_press(self, key, modifiers):
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            print(f"Brazil Game finished (Game Over). Score: {self.final_score}")
            self.window.last_game_score = self.final_score
            menu_view = getattr(self.window, "game_menu_view_instance", None)
            if menu_view:
                self.window.show_view(menu_view)
            else:
                print("Error: game_menu_view_instance not found on window.")
                self.window.close() # Fallback
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close() # Fallback


class VictoryView(arcade.View):
    def __init__(self, final_score):
        super().__init__()
        self.final_score = int(final_score)

    def on_draw(self):
        self.clear()
        arcade.Text("VICTORY!", self.window.width/2, self.window.height/2 + 50,
                         arcade.color.GREEN, 40, anchor_x="center").draw()
        arcade.Text(f"Final Score: {self.final_score}", self.window.width/2, self.window.height/2,
                         arcade.color.WHITE, 20, anchor_x="center").draw()
    def on_key_press(self, key, modifiers):
        if self.window and hasattr(self.window, "game_menu_view_instance"):
            print(f"Brazil Game finished (Victory). Score: {self.final_score}")
            self.window.last_game_score = self.final_score
            menu_view = getattr(self.window, "game_menu_view_instance", None)
            if menu_view:
                self.window.show_view(menu_view)
            else:
                print("Error: game_menu_view_instance not found on window.")
                self.window.close() # Fallback
        else:
            print("Error: Cannot return to menu. Window or menu instance missing.")
            if self.window:
                self.window.close() # Fallback


class Player(arcade.Sprite):
    def __init__(self, texture_list):
        super().__init__(texture_list[0])
        self.status = IDLE
        self.textures = texture_list
        self.direction = RIGHT
        self.cur_texture_index = self.direction * IDLE_COLS
        self.time_elapsed = 0
        self.scale = 5

    def update(self, delta_time=1/60, *args, **kwargs):
        self.time_elapsed += delta_time

        if self.time_elapsed > .1:
            if self.cur_texture_index < len(self.textures):
                self.set_texture(self.cur_texture_index)
                self.cur_texture_index += 1
            self.time_elapsed = 0
            
        if self.status == KICK:
            if self.cur_texture_index == (self.status*ROWS*IDLE_COLS)+(IDLE_COLS*self.direction+KICK_COLS)-1:
                self.status = IDLE
                self.cur_texture_index = IDLE_COLS * self.direction
        elif self.cur_texture_index == (IDLE_COLS * (self.direction+1))-1:
            self.cur_texture_index = IDLE_COLS * self.direction

    def is_at_the_end_of_kick(self):
        return self.status == KICK and self.cur_texture_index % IDLE_COLS > KICK_COLS - 6


class Enemy(arcade.Sprite):
    def __init__(self, texture_list):
        super().__init__(texture_list[0])
        self.scale = 2
        self.textures = texture_list
        self.cur_texture_index = WALK_COLS * (WALK_ROWS-1)
        self.time_elapsed = 0

    def update(self, delta_time=1/60):
        self.center_x += self.change_x * delta_time
        self.time_elapsed += delta_time
        
        if self.time_elapsed > 0.1:
            if self.cur_texture_index < len(self.textures):
                self.set_texture(self.cur_texture_index)
                self.cur_texture_index += 1
            self.time_elapsed = 0

        if self.cur_texture_index == (WALK_COLS * WALK_ROWS) - 1:
            self.cur_texture_index = WALK_COLS * (WALK_ROWS-1)


class BrazilGame(IGame, arcade.View):
    def __init__(self):
        super().__init__()
        self.hp = 5
        self.win_w = 0
        self.win_h = 0
        self.score = 0
        self.sprite_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        self.background = arcade.Sprite('games/brazil/assets/background/background.png')
        self.background.center_x = self.window.width / 2
        self.background.center_y = self.window.height / 2
        self.background.width = self.window.width
        self.background.height = self.window.height
        self.background_list.append(self.background)

        player_idle_sheet = arcade.load_spritesheet('games/brazil/assets/fighter/idle.png')
        idle_list = player_idle_sheet.get_texture_grid(size=(100, 100), columns=IDLE_COLS, count=IDLE_COLS*ROWS)
        player_kick_sheet = arcade.load_spritesheet('games/brazil/assets/fighter/front_kick.png')
        kick_list = player_kick_sheet.get_texture_grid(size=(100, 100), columns=IDLE_COLS, count=IDLE_COLS*ROWS)

        self.player = Player(idle_list + kick_list)
        self.player.position = 500, 400

        capybara_sheet = arcade.load_spritesheet('games/brazil/assets/capybara/capybara.png')
        self.capybara_list = capybara_sheet.get_texture_grid(size=(64, 64), columns=WALK_COLS, count=WALK_COLS*WALK_ROWS)

        self.sprite_list.append(self.background)
        self.sprite_list.append(self.player)

    def spawn_enemy(self):
        from_left = random.choice([True, False])
        enemy = Enemy(self.capybara_list)

        if from_left:
            enemy.center_x = -CAPYBARA_SIZE
            enemy.change_x = ENEMY_SPEED
        else:
            enemy.center_x = self.window.width + CAPYBARA_SIZE
            enemy.change_x = -ENEMY_SPEED
            enemy.scale_x = -2

        enemy.center_y = self.window.height // 4
        self.enemy_list.append(enemy)

    def on_update(self, delta_time):
        if random.randrange(10000) % 127 == 0:
            self.spawn_enemy()
        self.sprite_list.update()
        self.enemy_list.update()

        hit_list = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for hit in hit_list:
            hit.remove_from_sprite_lists()
            if self.player.is_at_the_end_of_kick():
                self.score += 1 # Increased score increment from 0.5 to 1
                if self.score >= 5: # Check if score reached or exceeded 5
                    self.score = 5 # Cap score at 5
                    self.window.show_view(VictoryView(self.score))
            else:
                self.hp -= 1
                if self.hp == 0:
                    self.window.show_view(GameOverView(self.score))

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()
        self.enemy_list.draw()

        hp_text = f"HP: {self.hp}"
        arcade.Text(
            hp_text,
            x=10,
            y=self.win_h - 30,
            color=arcade.color.RED,
            font_size=20,
            bold=True
        ).draw()
        score_text = f"Score: {self.score}"
        arcade.Text(
            score_text,
            x=10,
            y=self.win_h - 60,
            color=arcade.color.WHITE,
            font_size=20,
            bold=True
        ).draw()

    def on_key_press(self, key, _):
        if key == arcade.key.RIGHT:
            self.player.direction = RIGHT
            self.player.cur_texture_index = self.player.status*IDLE_COLS*ROWS + self.player.direction * IDLE_COLS
        elif key == arcade.key.LEFT:
            self.player.direction = LEFT
            self.player.cur_texture_index = self.player.status*IDLE_COLS*ROWS + self.player.direction * IDLE_COLS
        elif key == arcade.key.SPACE:
            self.player.status = KICK
            self.player.cur_texture_index = self.player.status*IDLE_COLS*ROWS + self.player.direction * IDLE_COLS

    def run(self, window):
        self.win_w = window.width
        self.win_h = window.height
        self.player.position = (self.win_w / 2, self.win_h / 4)
        window.show_view(self)

    def get_name(self):
        return 'Tha Brazil Game Thing'

    def get_color(self):
        return Color(0, 255, 0)
