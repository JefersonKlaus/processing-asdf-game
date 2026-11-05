"""When and where the gold letter appears (from 40 points)."""

import random

from asdf_hero import config
from asdf_hero.game import Game, LetterStatus
from tests.helpers import play, set_points

GOLD_FROM = config.GOLD_FROM_POINTS


def gold_game(rng=None, points=GOLD_FROM):
    game = Game(rng=rng or random.Random(0))
    game.start_new_game()
    set_points(game, points)
    return game


def golds(game):
    return [letter for letter in game.letters if letter.gold]


def test_no_gold_before_40_points():
    game = gold_game(points=GOLD_FROM - 1)

    for _ in range(60 * 30):
        play(game, 1)
        assert not golds(game)
        set_points(game, GOLD_FROM - 1)  # stay below 40 points


def test_gold_after_some_letters(scripted_rng):
    # rng: lane and char of the first letter, then the count for the gold (5)
    game = gold_game(scripted_rng([0, 0, 5]))

    for _ in range(5):
        game._add_letter_if_needed()
        game.letters[-1].y = 10_000  # no spacing limit: force the next letter

    assert game.gold.pending is True


def test_gold_starts_halfway_between_two_letters(place_letter):
    game = gold_game()
    half_spacing = (game.distance + config.LETTER_SIZE) / 2
    last = place_letter(game, 0, y=half_spacing - 1)
    game.gold.pending = True

    game.update()  # the gold is checked before moving: not halfway yet
    assert golds(game) == []
    assert last.y >= half_spacing

    game.update()
    assert len(golds(game)) == 1
    assert game.gold.pending is False


def test_gold_without_normal_letters():
    game = gold_game()
    game.gold.pending = True

    game.gold.update(game)

    assert len(golds(game)) == 1


def test_gold_does_not_change_the_normal_letters_spacing(place_letter):
    game = gold_game()
    place_letter(game, 0, y=100)
    place_letter(game, 1, y=500, gold=True)  # must not count as "the last letter"

    game.update()

    assert len(game.letters) == 2  # no new normal letter yet


def test_gold_lane_and_char_from_rng(scripted_rng):
    game = gold_game(scripted_rng([2, 3]))  # lane 2, char 3 ("F")
    game.gold.pending = True

    game.gold.update(game)

    assert (golds(game)[0].lane, golds(game)[0].char) == (2, "F")


def test_gold_avoids_the_lanes_of_coming_letters(place_letter):
    # the gold letter passes them: they must not be on top of each other
    for seed in range(30):
        game = gold_game(random.Random(seed))
        place_letter(game, 0, y=150)  # waiting: lane 0 busy
        place_letter(game, 2, y=400)  # waiting: lane 2 busy
        place_letter(game, 3, y=640, status=LetterStatus.WAS_PRESSED)  # done
        game.gold.pending = True

        game.gold.update(game)

        assert golds(game)[0].lane in (1, 3)


def test_any_lane_when_all_lanes_are_busy(scripted_rng, place_letter):
    game = gold_game(scripted_rng([3, 0]))
    for lane in range(4):
        place_letter(game, lane, y=200 + lane * 100)  # all waiting, the last at 500
    game.gold.pending = True

    game.gold.update(game)

    assert golds(game)[0].lane == 3
