"""
The result of a key press: points, game over and the highlight of the bar
(yellow: right press / red: wrong moment, game over).
"""

import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game, GamePage, Highlight, LetterStatus
from tests.helpers import frames, set_points

WAITING = LetterStatus.WAITING
NEED = LetterStatus.NEED_BE_PRESSED
PRESSED = LetterStatus.WAS_PRESSED


# letters: (lane, y, status, char); A is lane 0, S is lane 1
@pytest.mark.parametrize(
    "letters, key, points, game_over, highlight",
    [
        pytest.param([(1, 640, NEED, None)], "s", 1, False, Highlight.PRESSED, id="hit"),
        pytest.param([(1, 640, PRESSED, None)], "s", 0, False, Highlight.PRESSED, id="same letter again"),
        pytest.param([(0, 300, WAITING, None)], "a", 0, True, Highlight.WRONG, id="too early"),
        pytest.param([], "a", 0, True, Highlight.WRONG, id="no letters"),
        pytest.param([(1, 720, PRESSED, None)], "s", 0, True, Highlight.WRONG, id="too late"),
        pytest.param([(1, 640, NEED, None)], "a", 0, True, Highlight.WRONG, id="other letter in the bar"),
        pytest.param([(0, 640, NEED, "F")], "a", 0, True, Highlight.WRONG, id="wrong char in the lane"),
        pytest.param(
            [(1, 675, PRESSED, None), (0, 513, WAITING, None)], "a", 0, True, Highlight.WRONG,
            id="next letter too early",
        ),
        pytest.param([(1, 640, NEED, None)], "g", 0, False, Highlight.NONE, id="not a game key"),
    ],
)
def test_key_press(running_game, place_letter, letters, key, points, game_over, highlight):
    for lane, y, status, char in letters:
        place_letter(running_game, lane, y=y, status=status, char=char)

    running_game.key_pressed(key)

    assert running_game.points == points
    assert running_game.transition_to_game_over is game_over
    assert running_game.action_bar.highlight == highlight


def test_letter_half_inside_the_bar_can_be_pressed(running_game, place_letter):
    # regression: the circle was in the bar but its center was not
    letter = place_letter(running_game, 0, y=590 - config.INIT_SPEED)
    running_game.update()

    running_game.key_pressed("a")

    assert letter.status == PRESSED
    assert running_game.transition_to_game_over is False


def test_point_levels_up(running_game, place_letter):
    place_letter(running_game, 1, y=640, status=NEED)

    running_game.key_pressed("s")

    assert running_game.speed > config.INIT_SPEED
    assert running_game.distance < config.INIT_DISTANCE


def test_one_press_hits_only_the_lowest_letter(running_game, place_letter):
    # two letters with the same char in the bar (the gold letter can pass)
    upper = place_letter(running_game, 0, y=600, status=NEED)
    lower = place_letter(running_game, 1, y=690, status=NEED, char="A")

    running_game.key_pressed("a")
    assert (lower.status, upper.status) == (PRESSED, NEED)

    running_game.key_pressed("a")
    assert upper.status == PRESSED
    assert running_game.points == 2


@pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
def test_keys_are_ignored_when_not_playing(game, page):
    game.page = page

    game.key_pressed("a")

    assert game.transition_to_game_over is False
    assert game.action_bar.highlight == Highlight.NONE


def test_keys_are_ignored_during_the_slow_motion(running_game, place_letter):
    letter = place_letter(running_game, 0, y=640, status=NEED)
    running_game.transition_to_game_over = True

    running_game.key_pressed("a")

    assert letter.status == NEED


def test_yellow_goes_away_after_some_frames(running_game, place_letter):
    place_letter(running_game, 1, y=640, status=NEED)
    running_game.key_pressed("s")

    frames(running_game, config.HIGHLIGHT_FRAMES - 1)
    assert running_game.action_bar.highlight == Highlight.PRESSED

    running_game.update()
    assert running_game.action_bar.highlight == Highlight.NONE


def test_red_stays_during_the_slow_motion(running_game):
    running_game.key_pressed("a")  # the red bar shows why the game ended

    frames(running_game, config.HIGHLIGHT_FRAMES * 5)

    assert running_game.action_bar.highlight == Highlight.WRONG


@pytest.mark.parametrize("points", [0, 30, 100])
def test_yellow_is_never_followed_by_game_over(points, place_letter):
    # regression: every letter position x every key
    for y in range(0, 800, 3):
        for key in "asdfg":
            game = Game(rng=random.Random(0))
            game.start_new_game()
            set_points(game, points)
            place_letter(game, 0, y=y)
            game.update()

            game.key_pressed(key)

            if game.action_bar.highlight == Highlight.PRESSED:
                assert game.transition_to_game_over is False, (y, key)
            if game.transition_to_game_over:
                assert game.action_bar.highlight == Highlight.WRONG, (y, key)
