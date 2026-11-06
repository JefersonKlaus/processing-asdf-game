"""
Silver letter: a letter is already silver when it is chosen, the next letter
turns silver as soon as it exists, and they swap their chars near the bar.
"""

import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game, LetterStatus
from tests.helpers import play, set_points

SILVER_FROM = config.SILVER_FROM_POINTS
# the swap: the circle is SILVER_SWAP_DISTANCE pixels from the action bar
SWAP_Y = config.ACTION_BAR_TOP - config.SILVER_SWAP_DISTANCE - config.LETTER_SIZE / 2


@pytest.fixture
def game_50(running_game):
    set_points(running_game, SILVER_FROM)
    return running_game


def choose(game_50, place_letter, lane=0, y=0.0, char=None):
    """The challenge chooses this letter: silver right away."""
    letter = place_letter(game_50, lane, y=y, char=char)
    game_50.silver.start(game_50, letter)
    return letter


def add_next(game_50, place_letter, lane=3, y=0.0, char=None):
    """The next normal letter: the partner (or the next try, same char)."""
    letter = place_letter(game_50, lane, y=y, char=char)
    game_50.silver.letter_added(game_50, letter)
    return letter


def test_no_silver_before_50_points():
    game = Game(rng=random.Random(0))
    game.start_new_game()

    for _ in range(60 * 30):
        play(game, 1)
        assert not any(letter.will_swap or letter.silver for letter in game.letters)
        set_points(game, SILVER_FROM - 1)  # stay below 50 points


def test_a_letter_is_chosen_after_some_letters(scripted_rng):
    # rng: lane and char of the first letter, gold count (9), silver count (5)
    game = Game(rng=scripted_rng([0, 0, 9, 5]))
    game.start_new_game()
    set_points(game, SILVER_FROM)

    for _ in range(5):
        game._add_letter_if_needed()
        game.letters[-1].y = 10_000  # no spacing limit: force the next letter

    assert [letter.will_swap for letter in game.letters] == [False] * 4 + [True]


def test_the_chosen_letter_is_already_silver(game_50, place_letter):
    letter = choose(game_50, place_letter)

    assert (letter.silver, letter.will_swap) == (True, True)


def test_the_partner_turns_silver_as_soon_as_it_exists(game_50, place_letter):
    first = choose(game_50, place_letter, char="A")

    second = add_next(game_50, place_letter, char="F")

    assert second.silver is True
    assert (first.char, second.char) == ("A", "F")  # not swapped yet


def test_nothing_happens_before_the_next_letter(game_50, place_letter):
    letter = choose(game_50, place_letter, y=500.0)

    game_50.update()

    assert (letter.silver, letter.will_swap) == (True, True)  # still waiting


def test_they_swap_one_letter_from_the_action_bar(game_50, place_letter):
    first = choose(game_50, place_letter, char="A")
    second = add_next(game_50, place_letter, char="F")

    first.y = SWAP_Y - 1
    game_50.update()  # not near the bar yet
    assert (first.char, second.char) == ("A", "F")

    first.y = SWAP_Y
    game_50.update()
    assert (first.char, second.char) == ("F", "A")
    assert (first.silver, second.silver) == (True, True)  # still silver
    assert first.will_swap is False
    assert (first.lane, second.lane) == (0, 3)  # only the chars change


def test_swap_distance_is_one_letter():
    assert config.SILVER_SWAP_DISTANCE == config.LETTER_SIZE


def test_swaps_only_once(game_50, place_letter):
    first = choose(game_50, place_letter, char="A", y=SWAP_Y)
    second = add_next(game_50, place_letter, char="F")
    game_50.update()

    game_50.update()

    assert (first.char, second.char) == ("F", "A")


def test_the_new_char_must_be_pressed(game_50, place_letter):
    first = choose(game_50, place_letter, char="A", y=SWAP_Y)
    add_next(game_50, place_letter, char="F")
    game_50.update()
    first.y, first.status = 640, LetterStatus.NEED_BE_PRESSED  # in the bar

    game_50.key_pressed("f")

    assert first.status == LetterStatus.WAS_PRESSED
    assert game_50.transition_to_game_over is False


def test_the_old_char_ends_the_game(game_50, place_letter):
    first = choose(game_50, place_letter, char="A", y=SWAP_Y)
    add_next(game_50, place_letter, char="F")
    game_50.update()
    first.y, first.status = 640, LetterStatus.NEED_BE_PRESSED

    game_50.key_pressed("a")

    assert game_50.transition_to_game_over is True


def test_the_gold_letter_is_never_the_partner(game_50, place_letter):
    first = choose(game_50, place_letter, char="A")
    gold = place_letter(game_50, 1, y=0.0, gold=True, char="S")

    assert gold.silver is False  # gold letters do not go through letter_added
    assert first.will_swap is True  # still waiting for a normal letter


def test_same_char_tries_the_next_pair(game_50, place_letter):
    first = choose(game_50, place_letter, char="A")

    second = add_next(game_50, place_letter, char="A")

    assert (first.silver, first.will_swap) == (False, False)  # nothing to swap
    assert (second.silver, second.will_swap) == (True, True)  # it tries next

    third = add_next(game_50, place_letter, char="F")
    assert third.silver is True
    assert (second.char, third.char) == ("A", "F")


@pytest.mark.parametrize("silver_points", [1, 3])
def test_silver_points_from_the_config(monkeypatch, game_50, place_letter, silver_points):
    monkeypatch.setattr(config, "SILVER_POINTS", silver_points)
    letter = place_letter(game_50, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)
    letter.silver = True

    game_50.key_pressed("s")

    assert game_50.points == SILVER_FROM + silver_points


def test_new_game_resets_the_silver_challenge(game_50, place_letter):
    choose(game_50, place_letter)
    game_50.silver.schedule.letters_left = 2

    game_50.start_new_game()

    assert game_50.silver.schedule.letters_left is None
    # a letter chosen before a new game never swaps with one of the new game
    second = add_next(game_50, place_letter, char="F")
    assert second.silver is False
