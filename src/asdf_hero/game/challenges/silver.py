"""
Silver letter: two letters change their chars, with a warning.

1. The chosen letter is already silver when it appears (the warning starts
   right away). As soon as the next letter exists, it turns silver too.
2. When the first letter is one letter from the action bar, the two letters
   swap their chars. Example: A (near the bar) and F (the next one) -> the
   first shows F and the next shows A. The letters stay in their lanes.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from asdf_hero import config
from asdf_hero.game.challenges.base import Challenge, ChallengeSchedule
from asdf_hero.game.letter import Letter

if TYPE_CHECKING:  # pragma: no cover
    from asdf_hero.game.game import Game


class SilverChallenge(Challenge):
    def __init__(self, rng: random.Random) -> None:
        super().__init__(
            ChallengeSchedule(
                config.SILVER_FROM_POINTS,
                config.SILVER_EVERY_MIN_LETTERS,
                config.SILVER_EVERY_MAX_LETTERS,
                rng,
            )
        )
        self._pending: Letter | None = None  # silver, waiting for its partner
        self._partners: dict[int, Letter] = {}  # letter.id -> its partner

    def start(self, game: Game, letter: Letter) -> None:
        letter.silver = True  # already silver: the warning starts now
        letter.will_swap = True
        self._pending = letter

    def letter_added(self, game: Game, letter: Letter) -> None:
        # the next normal letter: the partner of the one waiting for it
        # (checked first: a letter is never its own partner)
        if self._pending is not None:
            self._pair_with(game, letter)
        super().letter_added(game, letter)  # may choose `letter` itself

    def update(self, game: Game) -> None:
        for letter in game.letters:
            if letter.id in self._partners and self._near_the_bar(game, letter):
                partner = self._partners.pop(letter.id)
                letter.will_swap = False
                letter.char, partner.char = partner.char, letter.char

    def reset(self) -> None:
        super().reset()
        self._pending = None
        self._partners = {}

    def _pair_with(self, game: Game, partner: Letter) -> None:
        first = self._pending
        self._pending = None
        if partner.char == first.char:
            first.silver = first.will_swap = False  # nothing to swap
            self.start(game, partner)  # try again with the next pair
        else:
            partner.silver = True  # already silver, before the swap
            self._partners[first.id] = partner

    @staticmethod
    def _near_the_bar(game: Game, letter: Letter) -> bool:
        circle_bottom = letter.y + letter.size / 2
        return circle_bottom >= game.action_bar.top - config.SILVER_SWAP_DISTANCE
