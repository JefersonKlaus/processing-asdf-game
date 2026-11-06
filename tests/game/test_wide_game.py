"""A wider game (phones): the lanes, letters and touch buttons spread out."""

import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game
from asdf_hero.game.challenges.gold import GoldChallenge


@pytest.fixture
def wide_game():
    game = Game(width=config.WIDTH * 1.5, rng=random.Random(0))
    game.start_new_game()
    return game


def test_default_width_uses_the_lanes_of_the_config(game):
    assert game.lane_lines == config.LANE_LINES
    assert game.lane_centers == config.LANE_CENTERS


def test_wider_lanes(wide_game):
    assert wide_game.lane_lines == tuple(x * 1.5 for x in config.LANE_LINES)
    # each center is in the middle of the space between two lines
    for center, line, next_line in zip(
        wide_game.lane_centers, wide_game.lane_lines, wide_game.lane_lines[1:]
    ):
        assert center == (line + config.LANE_LINE_WIDTH + next_line) / 2
    assert wide_game.lane_lines[-1] + config.LANE_LINE_WIDTH <= wide_game.width


def test_letters_fall_in_the_middle_of_the_wide_lanes(wide_game):
    wide_game.update()

    [letter] = wide_game.letters
    assert letter.x == wide_game.lane_centers[letter.lane]


def test_gold_letters_too(wide_game):
    letter = GoldChallenge(random.Random(0))._new_gold_letter(wide_game)

    assert letter.gold is True
    assert letter.x == wide_game.lane_centers[letter.lane]


def test_touch_buttons_fill_the_wide_lanes(wide_game):
    for button, line, next_line in zip(
        wide_game.touch_buttons, wide_game.lane_lines, wide_game.lane_lines[1:]
    ):
        assert button.x == line + config.LANE_LINE_WIDTH + config.TOUCH_BUTTON_MARGIN
        assert button.x + button.width == next_line - config.TOUCH_BUTTON_MARGIN


def test_buttons_stay_centered(wide_game):
    for button in (wide_game.button, wide_game.save_button):
        assert button.x + button.width / 2 == wide_game.width / 2
