"""Gold letter: a surprise letter that falls faster than the others."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from asdf_hero import config
from asdf_hero.game.challenges.base import Challenge, ChallengeSchedule
from asdf_hero.game.letter import Letter
from asdf_hero.game.states import LetterStatus

if TYPE_CHECKING:  # pragma: no cover
    from asdf_hero.game.game import Game


class GoldChallenge(Challenge):
    def __init__(self, rng: random.Random) -> None:
        super().__init__(
            ChallengeSchedule(
                config.GOLD_FROM_POINTS,
                config.GOLD_EVERY_MIN_LETTERS,
                config.GOLD_EVERY_MAX_LETTERS,
                rng,
            )
        )
        self.rng = rng
        self.pending = False

    def start(self, game: Game, letter: Letter) -> None:
        self.pending = True

    def update(self, game: Game) -> None:
        """The gold letter starts halfway between two normal letters."""
        if not self.pending:
            return
        last = game.last_normal_letter()
        if last is not None and last.y < (game.distance + last.size) / 2:
            return
        self.pending = False
        game.letters.append(self._new_gold_letter(game))

    def reset(self) -> None:
        super().reset()
        self.pending = False

    def _new_gold_letter(self, game: Game) -> Letter:
        # avoid the lanes of letters that are still coming: the gold letter
        # passes them, and they must not be on top of each other
        busy = {
            letter.lane
            for letter in game.letters
            if letter.status == LetterStatus.WAITING
        }
        lanes = [lane for lane in range(len(config.LANE_CENTERS)) if lane not in busy]
        lanes = lanes or list(range(len(config.LANE_CENTERS)))
        lane = lanes[self.rng.randrange(len(lanes))]
        char = game.keys[self.rng.randrange(len(game.keys))]
        return Letter(lane, char, game.action_bar, gold=True)
