"""
Swap: near the action bar, a letter swaps its char with the next letter.
Example: A (near the bar) and F (the next one) -> the first shows F and the
next shows A. Both letters are highlighted in silver.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from asdf_hero import config
from asdf_hero.game.challenges.base import Challenge, ChallengeSchedule
from asdf_hero.game.letter import Letter

if TYPE_CHECKING:  # pragma: no cover
    from asdf_hero.game.game import Game


class SwapChallenge(Challenge):
    def __init__(self, rng: random.Random) -> None:
        super().__init__(
            ChallengeSchedule(
                config.SWAP_FROM_POINTS,
                config.SWAP_EVERY_MIN_LETTERS,
                config.SWAP_EVERY_MAX_LETTERS,
                rng,
            )
        )

    def start(self, game: Game, letter: Letter) -> None:
        letter.will_swap = True  # a surprise: it looks normal until the swap

    def update(self, game: Game) -> None:
        normal = [letter for letter in game.letters if not letter.gold]
        for index, letter in enumerate(normal):
            if not letter.will_swap or not self._near_the_bar(game, letter):
                continue
            letter.will_swap = False
            partner = normal[index + 1] if index + 1 < len(normal) else None
            if partner is None:
                continue
            if partner.char == letter.char:
                partner.will_swap = True  # nothing to swap: try the next pair
                continue
            letter.char, partner.char = partner.char, letter.char
            letter.swapped = partner.swapped = True

    @staticmethod
    def _near_the_bar(game: Game, letter: Letter) -> bool:
        circle_bottom = letter.y + letter.size / 2
        return circle_bottom >= game.action_bar.top - config.SWAP_DISTANCE
