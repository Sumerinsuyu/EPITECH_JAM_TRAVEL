
import arcade
from arcade.types import Color, Rect

RUN     = 1
JUMP    = 2
FALL    = 3

FLOOR = 90

def create_rect(x, y, width, height):
    return Rect(x, x + width, y, y + height, width, height, x + (width / 2), y + (height / 2))

class Player:
    def __init__(self, name: str, position: tuple = (0.0, 0.0), size: tuple = (100.0, 100.0)):
        self.name = name
        self.position = position
        self.size = size
        self.state = RUN
        self.color = arcade.color.BLUE
        self.is_dead = False
        self.texture = arcade.load_texture("games/IstanbulCat/assets/player.png")
        self.rect = create_rect(self.position[0], self.position[1], 100, 100)


    def move(self, x: int, y: int):
        self.position = (x, y)
        self.rect = create_rect(self.position[0], self.position[1], 100, 100)
