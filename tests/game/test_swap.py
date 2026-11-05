"""Swap challenge: near the action bar, a letter swaps its char with the next one."""

import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game, LetterStatus
from tests.helpers import play, set_points

SWAP_FROM = config.SWAP_FROM_POINTS
# the swap happens when the circle is SWAP_DISTANCE pixels from the action bar
SWAP_Y = config.ACTION_BAR_TOP - config.SWAP_DISTANCE - config.LETTER_SIZE / 2


@pytest.fixture
def game_50(running_game):
    set_points(running_game, SWAP_FROM)
    return running_game


def test_no_swap_before_50_points():
    game = Game(rng=random.Random(0))
    game.start_new_game()

    for _ in range(60 * 30):
        play(game, 1)
        assert not any(letter.will_swap or letter.swapped for letter in game.letters)
        set_points(game, SWAP_FROM - 1)  # stay below 50 points


def test_a_letter_is_chosen_after_some_letters(scripted_rng):
    # rng: lane and char of the first letter, gold count (9), swap count (5)
    game = Game(rng=scripted_rng([0, 0, 9, 5]))
    game.start_new_game()
    set_points(game, SWAP_FROM)

    for _ in range(5):
        game._add_letter_if_needed()
        game.letters[-1].y = 10_000  # no spacing limit: force the next letter

    assert [letter.will_swap for letter in game.letters] == [False] * 4 + [True]


def test_chosen_letter_looks_normal_until_the_swap(game_50, place_letter):
    letter = place_letter(game_50, 0, y=100)
    letter.will_swap = True

    game_50.update()

    assert letter.char == "A"
    assert letter.swapped is False


def test_swap_near_the_action_bar(game_50, place_letter):
    first = place_letter(game_50, 0, y=SWAP_Y - 1)  # "A"
    second = place_letter(game_50, 3, y=SWAP_Y - 200)  # "F"
    first.will_swap = True

    game_50.update()  # checked before moving: not near the bar yet
    assert (first.char, second.char) == ("A", "F")

    game_50.update()
    assert (first.char, second.char) == ("F", "A")
    assert first.swapped is second.swapped is True
    assert first.will_swap is False
    assert (first.lane, second.lane) == (0, 3)  # only the chars change


def test_the_new_char_must_be_pressed(game_50, place_letter):
    first = place_letter(game_50, 0, y=SWAP_Y)
    place_letter(game_50, 3, y=SWAP_Y - 200)
    first.will_swap = True
    game_50.update()
    first.y, first.status = 640, LetterStatus.NEED_BE_PRESSED  # in the bar

    game_50.key_pressed("f")

    assert first.status == LetterStatus.WAS_PRESSED
    assert game_50.transition_to_game_over is False


def test_the_old_char_ends_the_game(game_50, place_letter):
    first = place_letter(game_50, 0, y=SWAP_Y)
    place_letter(game_50, 3, y=SWAP_Y - 200)
    first.will_swap = True
    game_50.update()
    first.y, first.status = 640, LetterStatus.NEED_BE_PRESSED

    game_50.key_pressed("a")

    assert game_50.transition_to_game_over is True


def test_swap_with_the_next_normal_letter_not_the_gold(game_50, place_letter):
    first = place_letter(game_50, 0, y=SWAP_Y)
    gold = place_letter(game_50, 1, y=300, gold=True)
    second = place_letter(game_50, 3, y=SWAP_Y - 200)
    first.will_swap = True

    game_50.update()

    assert (first.char, gold.char, second.char) == ("F", "S", "A")
    assert gold.swapped is False


def test_same_char_swaps_with_the_next_pair(game_50, place_letter):
    first = place_letter(game_50, 0, y=SWAP_Y)  # "A"
    second = place_letter(game_50, 1, y=SWAP_Y - 200, char="A")
    first.will_swap = True

    game_50.update()

    assert first.swapped is False  # nothing to swap
    assert second.will_swap is True  # it swaps with the next letter


def test_no_next_letter(game_50, place_letter):
    first = place_letter(game_50, 0, y=SWAP_Y)
    first.will_swap = True

    game_50.swap.update(game_50)

    assert (first.char, first.swapped, first.will_swap) == ("A", False, False)


@pytest.mark.parametrize("swap_points", [1, 3])
def test_swap_points_from_the_config(monkeypatch, game_50, place_letter, swap_points):
    monkeypatch.setattr(config, "SWAP_POINTS", swap_points)
    letter = place_letter(game_50, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)
    letter.swapped = True

    game_50.key_pressed("s")

    assert game_50.points == SWAP_FROM + swap_points


def test_new_game_resets_the_swap(game_50):
    game_50.swap.schedule.letters_left = 2

    game_50.start_new_game()

    assert game_50.swap.schedule.letters_left is None
