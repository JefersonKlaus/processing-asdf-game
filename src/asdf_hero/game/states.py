"""States used by the game."""

from enum import Enum


class GamePage(Enum):
    START = 1
    RUNNING = 2
    GAME_OVER = 3


class Hand(Enum):
    """Hand used to play: it chooses the keys of the game."""

    LEFT = "left"  # A S D F
    RIGHT = "right"  # J K L Ç


class LetterStatus(Enum):
    WAITING = 0  # above the action bar
    NEED_BE_PRESSED = 1  # in the action bar, waiting for its key
    WAS_PRESSED = 2  # pressed in the action bar (one point)
    FAILED = 3  # left the action bar without being pressed (game over)


class Highlight(Enum):
    """Feedback of the action bar when a game key is pressed."""

    NONE = 0
    PRESSED = 1  # right press: the letter of the key is in the action bar (yellow)
    WRONG = 2  # wrong moment: no letter of the key in the action bar (red)
