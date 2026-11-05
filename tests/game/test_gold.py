"""The gold letter: a surprise challenge from 50 points."""

import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game, GamePage, Letter, LetterStatus

GOLD_FROM = config.GOLD_FROM_POINTS


def game_with_points(points, rng=None):
    game = Game(rng=rng or random.Random(0))
    game.start_new_game()
    game.points = points
    game._update_level()
    return game


def normal_letters_spawned(game, count):
    """Run frames until `count` normal letters were added."""
    spawned = 0
    seen = {letter.id for letter in game.letters}
    while spawned < count:
        game.update()
        for letter in game.letters:
            if letter.id not in seen:
                seen.add(letter.id)
                spawned += 0 if letter.gold else 1
        # keep playing (a perfect player), so the game does not end
        for letter in game.letters:
            if letter.status == LetterStatus.NEED_BE_PRESSED:
                game.key_pressed(letter.char)
    return spawned


def golds(game):
    return [letter for letter in game.letters if letter.gold]


class TestSchedule:
    def test_no_gold_before_50_points(self):
        game = game_with_points(GOLD_FROM - 1)

        for _ in range(60 * 30):
            game.update()
            for letter in game.letters:
                assert not letter.gold
                if letter.status == LetterStatus.NEED_BE_PRESSED:
                    game.key_pressed(letter.char)
            game.points = GOLD_FROM - 1  # stay below 50 points

        assert game.letters_until_gold is None

    @pytest.mark.parametrize("count", [5, 7, 10])
    def test_gold_after_a_random_number_of_letters(self, scripted_rng, count):
        # rng: lane and char of the first letter, then the count for the gold
        game = game_with_points(GOLD_FROM, scripted_rng([0, 0, count]))

        game.update()  # first normal letter
        assert game.letters_until_gold == count - 1

        for _ in range(count - 1):
            game.letters[-1].y = 10_000  # force the next normal letter
            game._add_letter_if_needed()
        assert game.gold_pending is True
        assert game.letters_until_gold is None  # a new random count next time

    def test_random_count_is_between_5_and_10(self):
        counts = set()
        for seed in range(200):
            game = game_with_points(GOLD_FROM, random.Random(seed))
            game.update()
            counts.add(game.letters_until_gold + 1)

        assert counts == set(range(5, 11))

    def test_gold_every_5_to_10_letters_in_a_real_game(self):
        game = game_with_points(GOLD_FROM, random.Random(3))
        between, normal_count, seen = [], 0, set()

        for _ in range(60 * 120):
            game.update()
            for letter in game.letters:
                if letter.id not in seen:
                    seen.add(letter.id)
                    if letter.gold:
                        between.append(normal_count)
                        normal_count = 0
                    else:
                        normal_count += 1
            for letter in sorted(game.letters, key=lambda item: -item.y):
                if letter.status == LetterStatus.NEED_BE_PRESSED:
                    game.key_pressed(letter.char)

        assert len(between) >= 5
        assert all(5 <= count <= 10 for count in between)


class TestSpawn:
    def test_gold_starts_halfway_between_two_letters(self, place_letter):
        game = game_with_points(GOLD_FROM)
        half_spacing = (game.distance + config.LETTER_SIZE) / 2
        last = place_letter(game, 0, y=half_spacing - 1)
        game.gold_pending = True

        game.update()  # the gold is checked before moving: not halfway yet
        assert golds(game) == []
        assert last.y >= half_spacing

        game.update()
        [gold] = golds(game)
        assert gold.y == game.speed * config.GOLD_SPEED_FACTOR  # moved once

    def test_gold_without_normal_letters(self):
        game = game_with_points(GOLD_FROM)
        game.gold_pending = True

        game._add_gold_letter_if_needed()

        assert len(golds(game)) == 1
        assert game.gold_pending is False

    def test_gold_does_not_change_the_normal_letters_spacing(self, place_letter):
        game = game_with_points(GOLD_FROM)
        place_letter(game, 0, y=100)
        gold = Letter(1, "S", game.action_bar, gold=True)
        gold.y = 500  # far below: must not count as "the last letter"
        game.letters.append(gold)

        game.update()

        assert len(game.letters) == 2  # no new normal letter yet

    def test_gold_char_is_random(self, scripted_rng):
        # rng: gold lane 2, gold char 3 ("F")
        game = game_with_points(GOLD_FROM, scripted_rng([2, 3]))
        game.gold_pending = True

        game._add_gold_letter_if_needed()

        [gold] = golds(game)
        assert (gold.lane, gold.char) == (2, "F")

    def test_gold_avoids_the_lanes_of_coming_letters(self, place_letter):
        for seed in range(30):
            game = game_with_points(GOLD_FROM, random.Random(seed))
            place_letter(game, 0, y=150)  # waiting: lane 0 busy
            place_letter(game, 2, y=400)  # waiting: lane 2 busy
            place_letter(game, 3, y=640, status=LetterStatus.WAS_PRESSED)  # done
            game.gold_pending = True

            game._add_gold_letter_if_needed()

            assert golds(game)[0].lane in (1, 3)

    def test_any_lane_when_all_lanes_are_busy(self, place_letter, scripted_rng):
        game = game_with_points(GOLD_FROM, scripted_rng([3, 0]))
        for lane in range(4):
            place_letter(game, lane, y=300)
        game.letters[-1].y = 10_000  # no spacing limit for the gold
        game.letters.append(game.letters.pop(0))
        game.gold_pending = True

        game._add_gold_letter_if_needed()

        assert golds(game)[0].lane == 3

    def test_new_game_resets_the_gold(self):
        game = game_with_points(GOLD_FROM)
        game.letters_until_gold = 3
        game.gold_pending = True

        game.start_new_game()

        assert game.letters_until_gold is None
        assert game.gold_pending is False


class TestFall:
    def test_gold_falls_faster(self, place_letter):
        game = game_with_points(GOLD_FROM)
        normal = place_letter(game, 0, y=300)
        gold = Letter(1, "S", game.action_bar, gold=True)
        gold.y = 100
        game.letters.append(gold)

        game.update()

        assert normal.y == 300 + game.speed
        assert gold.y == 100 + game.speed * config.GOLD_SPEED_FACTOR

    def test_gold_pressed_in_the_bar_scores(self):
        game = game_with_points(GOLD_FROM)
        gold = Letter(1, "S", game.action_bar, gold=True)
        gold.y = 640
        gold.status = LetterStatus.NEED_BE_PRESSED
        game.letters.append(gold)

        game.key_pressed("s")

        assert gold.status == LetterStatus.WAS_PRESSED
        assert game.points == GOLD_FROM + 1

    def test_missed_gold_ends_the_game(self):
        game = game_with_points(GOLD_FROM)
        gold = Letter(1, "S", game.action_bar, gold=True)
        gold.y = 705
        gold.status = LetterStatus.NEED_BE_PRESSED
        game.letters.append(gold)

        game.update()  # moves 8px (y=713): the circle left the bar

        assert gold.status == LetterStatus.FAILED
        assert game.transition_to_game_over is True


class TestTwoLettersInTheBar:
    """The gold letter can pass a normal letter: two letters in the bar."""

    def test_each_key_hits_its_letter(self, place_letter):
        game = game_with_points(GOLD_FROM)
        normal = place_letter(game, 0, y=620, status=LetterStatus.NEED_BE_PRESSED)
        gold = Letter(1, "S", game.action_bar, gold=True)
        gold.y, gold.status = 650, LetterStatus.NEED_BE_PRESSED
        game.letters.append(gold)

        game.key_pressed("s")
        game.key_pressed("a")

        assert (normal.status, gold.status) == (LetterStatus.WAS_PRESSED,) * 2
        assert game.points == GOLD_FROM + 2
        assert game.transition_to_game_over is False

    def test_same_char_one_press_hits_the_lowest_letter(self, place_letter):
        game = game_with_points(GOLD_FROM)
        upper = place_letter(game, 0, y=600, status=LetterStatus.NEED_BE_PRESSED)
        lower = place_letter(game, 1, y=690, status=LetterStatus.NEED_BE_PRESSED, char="A")

        game.key_pressed("a")

        assert lower.status == LetterStatus.WAS_PRESSED
        assert upper.status == LetterStatus.NEED_BE_PRESSED
        assert game.points == GOLD_FROM + 1

        game.key_pressed("a")
        assert upper.status == LetterStatus.WAS_PRESSED
        assert game.points == GOLD_FROM + 2


def test_perfect_player_with_gold_letters():
    game = game_with_points(GOLD_FROM, random.Random(5))
    gold_seen = set()

    for _ in range(60 * 120):
        game.update()
        gold_seen.update(letter.id for letter in golds(game))
        for letter in sorted(game.letters, key=lambda item: -item.y):
            if letter.status == LetterStatus.NEED_BE_PRESSED:
                game.key_pressed(letter.char)
        assert game.page == GamePage.RUNNING

    assert len(gold_seen) >= 5
