from abc import ABC, abstractmethod

class IGame(ABC):
    @abstractmethod
    def run(self, window=None):
        """Run the game and return the score as an integer. Accepts an optional window argument for compatibility."""
        pass

    @abstractmethod
    def get_name(self):
        """Return the name of the game."""
        pass
    @abstractmethod
    def get_color(self):
        """Return the color of the game."""
        pass
