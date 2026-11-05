"""Shared fixtures (the helpers without pytest are in tests/helpers.py)."""

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

    def place(game, lane, y, status=LetterStatus.WAITING, char=None, gold=False):
        char = char or config.LEFT_HAND_KEYS[lane]
        letter = Letter(lane, char, game.action_bar, gold=gold)
        letter.y = y
        letter.status = status
        game.letters.append(letter)
        return letter

    return place
