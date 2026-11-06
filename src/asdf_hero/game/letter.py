"""A letter that falls down a lane."""

import itertools

from asdf_hero import config
from asdf_hero.game.action_bar import ActionBar
from asdf_hero.game.states import LetterStatus


def normalize_key(key: str) -> str:
    """Upper case, and the same char for keys with other names (";" -> "Ç")."""
    key = key.upper()
    return config.KEY_ALIASES.get(key, key)


def is_game_key(key: str, keys: tuple[str, ...] = config.LEFT_HAND_KEYS) -> bool:
    """True for the keys of the game (any case)."""
    return normalize_key(key) in keys


class Letter:
    size = config.LETTER_SIZE
    _ids = itertools.count()

    def __init__(
        self,
        lane: int,
        char: str,
        action_bar: ActionBar,
        gold: bool = False,
        x: float | None = None,
    ) -> None:
        self.id = next(Letter._ids)  # unique: two letters are never mixed up
        self.lane = lane
        self.char = char
        self.gold = gold  # surprise letter: falls faster than the others
        self.will_swap = False  # silver letter challenge: it will swap its char
        self.silver = False  # silver letter: it swaps (or swapped) its char
        # center of the circle (the game gives it: wider games, wider lanes)
        self.x = config.LANE_CENTERS[lane] if x is None else x
        self.y = 0.0
        self.status = LetterStatus.WAITING
        self._action_bar = action_bar

    def in_action_bar(self) -> bool:
        """
        True while the circle touches the action bar: the letter can be
        pressed as soon as the player sees it in the bar.
        """
        return self._action_bar.touches(self.y, self.size)

    def matches(self, key: str) -> bool:
        return self.char == normalize_key(key)

    def move(self, dy: float) -> None:
        self.y += dy
        self._update_status()

    def can_be_pressed(self, key: str) -> bool:
        return self.status == LetterStatus.NEED_BE_PRESSED and self.matches(key)

    def press(self, key: str) -> bool:
        """Press a key: True (one point) when it hits this letter."""
        if self.can_be_pressed(key):
            self.status = LetterStatus.WAS_PRESSED
            return True
        return False

    def already_pressed(self, key: str) -> bool:
        """
        True when this letter was pressed with this key and it is still in the
        action bar (the player pressed the same letter again).
        """
        return (
            self.status == LetterStatus.WAS_PRESSED
            and self.in_action_bar()
            and self.matches(key)
        )

    def _update_status(self) -> None:
        if self.in_action_bar():
            if self.status == LetterStatus.WAITING:
                self.status = LetterStatus.NEED_BE_PRESSED
        elif self.status == LetterStatus.NEED_BE_PRESSED:
            self.status = LetterStatus.FAILED
