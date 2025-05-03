
IDLE    = 0
RUN     = 1
JUMP    = 2

import arcade
from arcade.types import Color

class Player:
    def __init__(self, name: str, position: tuple = (0.0, 0.0), size: tuple = (50.0, 50.0)):
        self.name = name
        self.position = position
        self.size = size
        self.state = IDLE
        self.color = arcade.color.BLUE

    def move(self, x: int, y: int):
        self.position = (x, y)
