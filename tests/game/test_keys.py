"""The keys of the game for each hand, and the names of the keys."""

import pytest

from asdf_hero import config
from asdf_hero.game import is_game_key, normalize_key


@pytest.mark.parametrize("key", ["a", "S", "d", "F"])
def test_left_hand_keys(key):
    assert is_game_key(key, config.LEFT_HAND_KEYS) is True


@pytest.mark.parametrize("key", ["j", "K", "l", "Ç", "ç", ";"])
def test_right_hand_keys(key):
    assert is_game_key(key, config.RIGHT_HAND_KEYS) is True


@pytest.mark.parametrize(
    "key, keys",
    [
        ("g", config.LEFT_HAND_KEYS),
        ("j", config.LEFT_HAND_KEYS),  # key of the other hand
        ("Arrow Up", config.LEFT_HAND_KEYS),
        ("", config.LEFT_HAND_KEYS),
        ("a", config.RIGHT_HAND_KEYS),
        (":", config.RIGHT_HAND_KEYS),
    ],
)
def test_other_keys(key, keys):
    assert is_game_key(key, keys) is False


@pytest.mark.parametrize(
    "key, expected", [("a", "A"), ("F", "F"), ("ç", "Ç"), ("Ç", "Ç"), (";", "Ç")]
)
def test_normalize_key(key, expected):
    assert normalize_key(key) == expected
