
import arcade
from arcade.types import Color

FLOOR   = 90
EDGE    = 800

class Ennemy:
    def __init__(self, name: str, position: tuple = (EDGE, 0.0), size: tuple = (50.0, 50.0)):
        self.name = name
        self.position = position
        self.size = size
        self.color = arcade.color.RED

    def move(self, x: int, y: int):
        self.position = (x, y)
