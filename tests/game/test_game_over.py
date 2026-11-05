"""Game over: a missed letter or a wrong press, then the slow motion."""

from asdf_hero import config
from asdf_hero.game import GamePage, LetterStatus
from tests.helpers import GAME_OVER_FRAMES, frames


def test_missed_letter_starts_the_transition(running_game, place_letter):
    # the circle leaves the bar without being pressed
    place_letter(running_game, 0, y=710, status=LetterStatus.NEED_BE_PRESSED)

    running_game.update()

    assert running_game.transition_to_game_over is True
    assert running_game.page == GamePage.RUNNING


def test_slow_motion_moves_one_step_every_some_frames(running_game, place_letter):
    letter = place_letter(running_game, 0, y=100)
    running_game.transition_to_game_over = True

    frames(running_game, config.SLOW_MOTION_STEP_FRAMES - 1)
    assert letter.y == 100

    running_game.update()
    assert letter.y == 100 + config.INIT_SPEED


def test_game_over_page_after_the_slow_motion(running_game):
    running_game.transition_to_game_over = True

    frames(running_game, GAME_OVER_FRAMES - 1)
    assert running_game.page == GamePage.RUNNING

    running_game.update()
    assert running_game.page == GamePage.GAME_OVER


def test_points_are_kept(running_game):
    running_game.points = 7

    running_game.key_pressed("d")  # wrong moment
    frames(running_game, GAME_OVER_FRAMES)

    assert running_game.page == GamePage.GAME_OVER
    assert running_game.points == 7
