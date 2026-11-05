"""Game pages: start, running, game over and retry."""

import pytest

from asdf_hero import config
from asdf_hero.game import Game, GamePage, Highlight
from tests.helpers import center, frames, set_points


def test_initial_state(game):
    assert game.page == GamePage.START
    assert (game.points, game.letters) == (0, [])
    assert (game.speed, game.distance) == (config.INIT_SPEED, config.INIT_DISTANCE)
    assert game.transition_to_game_over is False


def test_button_in_the_center_of_the_screen():
    game = Game(width=400, height=600)

    button = game.button
    assert (button.x, button.y) == (100, 260)
    assert (button.width, button.height) == (config.BUTTON_WIDTH, config.BUTTON_HEIGHT)


def test_each_game_has_its_own_state():
    # one game for each browser tab
    first, second = Game(), Game()

    assert first.letters is not second.letters
    assert first.action_bar is not second.action_bar


@pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
def test_click_on_the_button_starts_a_game(game, page):
    game.page = page

    game.mouse_pressed(*center(game.button))

    assert game.page == GamePage.RUNNING
    assert game.button.clicked is True

    game.mouse_released()
    assert game.button.clicked is False


def test_click_outside_the_button(game):
    game.mouse_pressed(0, 0)

    assert game.page == GamePage.START


def test_mouse_is_ignored_while_running(running_game):
    running_game.points = 5

    running_game.mouse_pressed(*center(running_game.button))

    assert running_game.points == 5


@pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
def test_nothing_moves_outside_the_running_page(game, page):
    game.page = page

    frames(game, 10)

    assert game.letters == []


def test_new_game_is_clean(game, place_letter):
    # state of a "previous game"
    game.page = GamePage.GAME_OVER
    place_letter(game, 0, y=300)
    set_points(game, 80)
    game.transition_to_game_over = True
    game.slow_motion_steps = 5
    game.gold.schedule.letters_left, game.gold.pending = 3, True
    game.swap.schedule.letters_left = 4
    game.action_bar.press(correct=False)

    game.mouse_pressed(*center(game.button))

    assert game.page == GamePage.RUNNING
    assert (game.points, game.letters) == (0, [])
    assert (game.speed, game.distance) == (config.INIT_SPEED, config.INIT_DISTANCE)
    assert (game.transition_to_game_over, game.slow_motion_steps) == (False, 0)
    assert (game.gold.schedule.letters_left, game.gold.pending) == (None, False)
    assert game.swap.schedule.letters_left is None
    assert game.action_bar.highlight == Highlight.NONE
