"""Hand choice (start and game over pages): left A S D F, right J K L Ç."""

import pytest

from asdf_hero import config
from asdf_hero.game import GamePage, Hand, LetterStatus
from tests.helpers import center


def test_left_hand_by_default(game):
    assert game.hand == Hand.LEFT
    assert game.keys == ("A", "S", "D", "F")


def test_hand_button_below_the_start_button(game):
    start, hand = game.button, game.hand_button

    assert (hand.x, hand.width) == (start.x, start.width)
    assert hand.y == start.y + start.height + config.BUTTON_GAP


@pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
def test_click_changes_the_hand(game, page):
    game.page = page

    game.mouse_pressed(*center(game.hand_button))

    assert game.hand == Hand.RIGHT
    assert game.keys == ("J", "K", "L", "Ç")
    assert game.page == page  # the game does not start

    game.mouse_released()
    game.mouse_pressed(*center(game.hand_button))
    assert game.hand == Hand.LEFT


def test_hand_cannot_change_while_running(running_game):
    running_game.mouse_pressed(*center(running_game.hand_button))

    assert running_game.hand == Hand.LEFT


def test_hand_is_kept_in_a_new_game(game):
    game.toggle_hand()

    game.start_new_game()

    assert game.hand == Hand.RIGHT


def test_right_hand_letters(scripted_rng):
    from asdf_hero.game import Game

    game = Game(rng=scripted_rng([3]))
    game.toggle_hand()
    game.start_new_game()

    game.update()

    assert game.letters[0].char == "Ç"


@pytest.mark.parametrize("key", ["Ç", "ç", ";"])
def test_right_hand_keys_score(game, place_letter, key):
    game.toggle_hand()
    game.start_new_game()
    place_letter(game, 3, y=640, status=LetterStatus.NEED_BE_PRESSED, char="Ç")

    game.key_pressed(key)

    assert game.points == 1


def test_keys_of_the_other_hand_are_ignored(game):
    game.toggle_hand()
    game.start_new_game()

    game.key_pressed("a")

    assert game.transition_to_game_over is False
    assert game.action_bar.presses == 0
