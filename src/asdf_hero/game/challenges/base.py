"""The base of the challenges and their schedule."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from asdf_hero.game.game import Game
    from asdf_hero.game.letter import Letter


class ChallengeSchedule:
    """
    From ``from_points``, a challenge is due after a random number of normal
    letters (between ``every_min`` and ``every_max``). Then a new random
    number is chosen.
    """

    def __init__(
        self, from_points: int, every_min: int, every_max: int, rng: random.Random
    ) -> None:
        self.from_points = from_points
        self.every_min = every_min
        self.every_max = every_max
        self.rng = rng
        self.letters_left: int | None = None

    def count_letter(self, points: int) -> bool:
        """A normal letter was added: True when the challenge is due."""
        if points < self.from_points:
            return False
        if self.letters_left is None:
            self.letters_left = self.rng.randint(self.every_min, self.every_max)
        self.letters_left -= 1
        if self.letters_left == 0:
            self.letters_left = None  # a new random number next time
            return True
        return False

    def reset(self) -> None:
        self.letters_left = None


class Challenge(ABC):
    """A challenge. The game calls the hooks ``letter_added`` and ``update``."""

    def __init__(self, schedule: ChallengeSchedule) -> None:
        self.schedule = schedule

    def letter_added(self, game: Game, letter: Letter) -> None:
        """A normal letter was added to the game."""
        if self.schedule.count_letter(game.points):
            self.start(game, letter)

    @abstractmethod
    def start(self, game: Game, letter: Letter) -> None:
        """The challenge is due (``letter`` is the normal letter just added)."""

    def update(self, game: Game) -> None:
        """One game step, before the letters move."""

    def reset(self) -> None:
        """New game."""
        self.schedule.reset()
