
import arcade
from arcade.types import Color, Rect

FLOOR   = 90
EDGE    = 800

def create_rect(x, y, width, height):
    return Rect(x, x + width, y, y + height, width, height, x + (width / 2), y + (height / 2))

class Ennemy:
    def __init__(self, name: str, position: tuple = (EDGE, 0.0), size: tuple = (100.0, 100.0)):
        self.name = name
        self.position = position
        self.size = size
        self.color = arcade.color.RED
        self.texture = arcade.load_texture("games/IstanbulCat/assets/ennemy.png")
        self.rect = create_rect(self.position[0], self.position[1], 100, 100)

    def move(self, x: int, y: int):
        self.position = (x, y)
        self.rect = create_rect(self.position[0], self.position[1], 100, 100)
