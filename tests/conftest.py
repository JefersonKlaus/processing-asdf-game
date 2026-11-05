"""
Shared fixtures.

The tests mirror the package:
- tests/game: game rules (no Flet)
- tests/ui: Flet views (the controls are plain Python objects, the tests check
  their properties without a browser)
- tests/test_app.py, tests/test_main.py: Flet app and entry point
"""

import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game, Letter, LetterStatus


class ScriptedRandom(random.Random):
    """A Random whose randrange() returns the given values (then 0)."""

    def __init__(self, values=()):
        super().__init__(0)
        self.values = list(values)

    def randrange(self, *args, **kwargs):
        return self.values.pop(0) if self.values else 0


@pytest.fixture
def scripted_rng():
    """Factory: ``scripted_rng([1, 3])`` -> randrange returns 1, then 3."""
    return ScriptedRandom


@pytest.fixture
def game():
    return Game(rng=random.Random(0))


@pytest.fixture
def running_game(game):
    game.start_new_game()
    return game


@pytest.fixture
def place_letter():
    """Factory: put a letter of a lane (0-3: A, S, D, F) in a game."""

    def place(game, lane, y, status=LetterStatus.WAITING, char=None):
        letter = Letter(lane, char or config.CHARS[lane], game.action_bar)
        letter.y = y
        letter.status = status
        game.letters.append(letter)
        return letter

    return place
