"""Congratulations page: a new best result, the name, save / save as anonymous."""

import random
from datetime import datetime

import pytest

from asdf_hero import config
from asdf_hero.game import Game, GamePage, Hand, Scoreboard
from tests.helpers import GAME_OVER_FRAMES, center, fill_scoreboard, frames

GAME_OVER_TIME = datetime(2025, 3, 5, 14, 30)


@pytest.fixture
def board():
    return Scoreboard(size=5)


@pytest.fixture
def new_game(board):
    game = Game(rng=random.Random(0), scoreboard=board, clock=lambda: GAME_OVER_TIME)
    game.start_new_game()
    return game


def lose_with(game, points):
    game.points = points
    game.key_pressed("a")  # wrong moment
    frames(game, GAME_OVER_FRAMES)


def names(board):
    return [result.name for result in board.best]


# --- which page after the game -------------------------------------------------


def test_a_best_result_shows_the_congratulations_page(new_game, board):
    lose_with(new_game, 42)

    assert new_game.page == GamePage.CONGRATULATIONS
    assert new_game.last_result is None
    assert board.best == []  # saved only with the name


def test_a_result_out_of_the_best_goes_to_game_over(new_game, board):
    fill_scoreboard(board, points=50)

    lose_with(new_game, 50)  # same points as the last one: out

    assert new_game.page == GamePage.GAME_OVER
    assert new_game.last_result is None
    assert names(board) == ["Old"] * 5  # nothing changed


def test_zero_points_go_to_game_over(new_game, board):
    # an empty board has free places, but 0 points is not a result
    lose_with(new_game, 0)

    assert new_game.page == GamePage.GAME_OVER
    assert board.best == []


def test_one_point_is_a_best_result(new_game):
    lose_with(new_game, 1)

    assert new_game.page == GamePage.CONGRATULATIONS


def test_the_name_field_starts_empty(new_game):
    new_game.typed_name = "Old text"

    lose_with(new_game, 42)

    assert new_game.typed_name == ""


# --- typing and saving ----------------------------------------------------------


def test_save_with_the_typed_name(new_game, board):
    lose_with(new_game, 42)
    new_game.type_name("An")
    new_game.type_name("Ana")  # each change of the field

    new_game.save_name()

    assert new_game.page == GamePage.GAME_OVER
    assert board.best == [new_game.last_result]  # shown in bold
    result = new_game.last_result
    assert (result.points, result.when, result.name) == (42, GAME_OVER_TIME, "Ana")


def test_save_as_anonymous(new_game):
    lose_with(new_game, 42)
    new_game.type_name("Ana")  # typed, but the player chose anonymous

    new_game.save_anonymous()

    assert new_game.page == GamePage.GAME_OVER
    assert new_game.last_result.name == ""  # anonymous: no name


def test_save_an_empty_name_is_anonymous(new_game):
    lose_with(new_game, 42)
    new_game.type_name("   ")

    new_game.save_name()

    assert new_game.last_result.name == ""  # anonymous


def test_the_result_enters_a_full_board(new_game, board):
    fill_scoreboard(board, points=50)

    lose_with(new_game, 51)
    new_game.type_name("Bia")
    new_game.save_name()

    assert new_game.last_result is board.best[0]
    assert [r.points for r in board.best] == [51, 50, 50, 50, 50]


def test_the_time_is_the_end_of_the_game(board):
    times = iter([GAME_OVER_TIME, datetime(2030, 1, 1)])
    game = Game(rng=random.Random(0), scoreboard=board, clock=lambda: next(times))
    game.start_new_game()
    lose_with(game, 5)

    game.save_name()  # later: the clock is not read again

    assert game.last_result.when == GAME_OVER_TIME


def test_saved_only_once(new_game, board):
    lose_with(new_game, 42)
    new_game.type_name("Ana")

    new_game.save_name()
    new_game.save_name()  # double tap
    new_game.save_anonymous()

    assert names(board) == ["Ana"]


@pytest.mark.parametrize("page", [GamePage.START, GamePage.RUNNING, GamePage.GAME_OVER])
def test_name_only_on_the_congratulations_page(new_game, board, page):
    new_game.page = page

    new_game.type_name("Ana")
    new_game.save_name()
    new_game.save_anonymous()

    assert new_game.typed_name == ""
    assert new_game.page == page
    assert board.best == []


# --- buttons ------------------------------------------------------------------


def test_buttons_centered_in_the_upper_part(new_game):
    # above the keyboard of the phone (it covers about 40% of the screen)
    save, anonymous = new_game.save_button, new_game.anonymous_button

    assert save.x == anonymous.x == new_game.button.x  # centered
    assert save.y == config.CONGRATULATIONS_BUTTONS_TOP
    assert anonymous.y == save.y + config.BUTTON_HEIGHT + config.BUTTON_GAP
    assert anonymous.y + anonymous.height <= new_game.height * 0.6


def test_click_on_save(new_game):
    lose_with(new_game, 42)
    new_game.type_name("Ana")

    new_game.mouse_pressed(*center(new_game.save_button))

    assert new_game.save_button.clicked is True
    assert new_game.last_result.name == "Ana"

    new_game.mouse_released()
    assert new_game.save_button.clicked is False


def test_click_on_save_as_anonymous(new_game):
    lose_with(new_game, 42)

    new_game.mouse_pressed(*center(new_game.anonymous_button))

    assert new_game.anonymous_button.clicked is True
    assert new_game.last_result.name == ""  # anonymous

    new_game.mouse_released()
    assert new_game.anonymous_button.clicked is False


def test_click_outside_the_buttons(new_game):
    lose_with(new_game, 42)

    new_game.mouse_pressed(5, 5)

    assert new_game.page == GamePage.CONGRATULATIONS


@pytest.mark.parametrize("button", ["button", "hand_button"])
def test_the_start_and_hand_buttons_are_not_on_this_page(new_game, board, button):
    lose_with(new_game, 42)

    new_game.mouse_pressed(*center(getattr(new_game, button)))

    assert new_game.page == GamePage.CONGRATULATIONS  # not a new game
    assert new_game.hand == Hand.LEFT
    assert getattr(new_game, button).clicked is False
    assert board.best == []


def test_retry_after_saving(new_game):
    lose_with(new_game, 42)
    new_game.save_anonymous()

    new_game.mouse_pressed(*center(new_game.button))

    assert new_game.page == GamePage.RUNNING
