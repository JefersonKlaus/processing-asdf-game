"""New letters, spacing, movement and removal of the normal letters."""

import pytest

from asdf_hero import config
from asdf_hero.game import Game, LetterStatus
from tests.helpers import frames

SPACING = config.INIT_DISTANCE + config.LETTER_SIZE  # initial level


def test_first_frame_adds_a_letter(running_game):
    running_game.update()

    [letter] = running_game.letters
    assert letter.y == config.INIT_SPEED  # already moved once


def test_lane_and_char_from_rng(scripted_rng):
    game = Game(rng=scripted_rng([2]))
    game.start_new_game()

    game.update()

    assert (game.letters[0].lane, game.letters[0].char) == (2, "D")


@pytest.mark.parametrize("points, char", [(24, "A"), (25, "F")])
def test_random_chars_from_25_points(scripted_rng, points, char):
    game = Game(rng=scripted_rng([0, 3]))  # lane 0 ("A"), random char 3 ("F")
    game.start_new_game()
    game.points = points

    game.update()

    assert game.letters[0].char == char


@pytest.mark.parametrize("last_y, count", [(SPACING - 1, 1), (SPACING, 2)])
def test_next_letter_after_the_distance(running_game, place_letter, last_y, count):
    place_letter(running_game, 0, y=last_y)

    running_game.update()

    assert len(running_game.letters) == count


def test_distance_depends_on_the_level(running_game, place_letter):
    running_game.distance = 100
    place_letter(running_game, 0, y=100 + config.LETTER_SIZE)

    running_game.update()

    assert len(running_game.letters) == 2


def test_letters_move_with_the_game_speed(running_game, place_letter):
    first = place_letter(running_game, 0, y=100)
    second = place_letter(running_game, 1, y=50)
    running_game.speed = 4.5

    running_game.update()

    assert (first.y, second.y) == (104.5, 54.5)


def test_letters_keep_their_distance_when_the_speed_changes(running_game):
    frames(running_game, 100)
    running_game.speed = config.MAX_SPEED
    ys = [letter.y for letter in running_game.letters]

    running_game.update()

    assert [letter.y - y for letter, y in zip(running_game.letters, ys)] == [
        config.MAX_SPEED
    ] * len(ys)


def test_letters_below_the_screen_are_removed(running_game, place_letter):
    gone = place_letter(running_game, 0, y=config.HEIGHT + 62, status=LetterStatus.WAS_PRESSED)
    next_letter = place_letter(running_game, 1, y=500)

    running_game.update()

    assert gone not in running_game.letters
    # regression: removing a letter during the loop skipped the next one
    assert next_letter.y == 500 + config.INIT_SPEED
