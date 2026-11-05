"""Touch buttons (phone / tablet): each one works like the key of its lane."""

import pytest

from asdf_hero import config
from asdf_hero.game import GamePage, LetterStatus
from tests.helpers import center

NEED = LetterStatus.NEED_BE_PRESSED


def test_one_button_inside_each_lane(game):
    for lane, button in enumerate(game.touch_buttons):
        left_line, right_line = config.LANE_LINES[lane], config.LANE_LINES[lane + 1]
        assert left_line + config.LANE_LINE_WIDTH <= button.x
        assert button.x + button.width <= right_line
        assert button.y == config.TOUCH_BUTTONS_TOP


@pytest.mark.parametrize("lane, key", [(0, "a"), (1, "s"), (2, "d"), (3, "f")])
def test_touch_presses_the_key_of_the_lane(running_game, place_letter, lane, key):
    letter = place_letter(running_game, lane, y=640, status=NEED)

    running_game.mouse_pressed(*center(running_game.touch_buttons[lane]))

    assert letter.status == LetterStatus.WAS_PRESSED
    assert running_game.points == 1


def test_touch_at_the_wrong_moment_ends_the_game(running_game):
    running_game.mouse_pressed(*center(running_game.touch_buttons[0]))

    assert running_game.transition_to_game_over is True


def test_buttons_follow_the_chars_not_the_letter_lane(running_game, place_letter):
    # after 25 points the char does not match the lane: "F" in lane A
    place_letter(running_game, 0, y=640, status=NEED, char="F")

    running_game.mouse_pressed(*center(running_game.touch_buttons[3]))  # F button

    assert running_game.points == 1


def test_right_hand_buttons(running_game, place_letter):
    running_game.toggle_hand()
    place_letter(running_game, 3, y=640, status=NEED, char="Ç")

    running_game.mouse_pressed(*center(running_game.touch_buttons[3]))

    assert running_game.points == 1


def test_touch_outside_the_buttons_is_ignored(running_game):
    running_game.mouse_pressed(141, 300)  # on the lanes
    running_game.mouse_pressed(70, 720)  # between two buttons

    assert running_game.transition_to_game_over is False
    assert running_game.action_bar.presses == 0


def test_pressed_until_released(running_game):
    button = running_game.touch_buttons[2]

    running_game.mouse_pressed(*center(button))
    assert button.clicked is True

    running_game.mouse_released()
    assert button.clicked is False


@pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
def test_touch_buttons_only_while_running(game, page):
    game.page = page

    game.mouse_pressed(*center(game.touch_buttons[0]))

    assert game.action_bar.presses == 0
    assert game.touch_buttons[0].clicked is False
