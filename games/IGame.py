from abc import ABC, abstractmethod

class IGame(ABC):
    @abstractmethod
    def run(self):
        """Run the game and return the score as an integer."""
        pass

    @abstractmethod
    def get_name(self):
        """Return the name of the game."""
        pass