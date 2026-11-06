"""The gold letter: faster fall, points and game over."""

import pytest

from asdf_hero import config
from asdf_hero.game import LetterStatus
from tests.helpers import set_points

NEED = LetterStatus.NEED_BE_PRESSED


@pytest.fixture
def game_50(running_game):
    set_points(running_game, config.GOLD_FROM_POINTS)
    return running_game


def test_gold_falls_faster(game_50, place_letter):
    normal = place_letter(game_50, 0, y=300)
    gold = place_letter(game_50, 1, y=100, gold=True)

    game_50.update()

    assert normal.y == 300 + game_50.speed
    assert gold.y == 100 + game_50.speed * config.GOLD_SPEED_FACTOR


@pytest.mark.parametrize("gold_points", [1, 3])
def test_gold_points_from_the_config(monkeypatch, game_50, place_letter, gold_points):
    monkeypatch.setattr(config, "GOLD_POINTS", gold_points)
    place_letter(game_50, 1, y=640, status=NEED, gold=True)

    game_50.key_pressed("s")

    assert game_50.points == config.GOLD_FROM_POINTS + gold_points


def test_normal_letter_is_always_one_point(monkeypatch, game_50, place_letter):
    monkeypatch.setattr(config, "GOLD_POINTS", 5)
    place_letter(game_50, 1, y=640, status=NEED)

    game_50.key_pressed("s")

    assert game_50.points == config.GOLD_FROM_POINTS + 1


def test_missed_gold_ends_the_game(game_50, place_letter):
    # half a move before the circle leaves the bar (bar bottom + radius)
    gold_speed = game_50.speed * config.GOLD_SPEED_FACTOR
    last_y = game_50.action_bar.bottom + config.LETTER_SIZE / 2
    gold = place_letter(game_50, 1, y=last_y - gold_speed / 2, status=NEED, gold=True)

    game_50.update()  # the circle left the bar

    assert gold.status == LetterStatus.FAILED
    assert game_50.transition_to_game_over is True


@pytest.mark.parametrize("gold_points", [1, 3])
def test_gold_and_normal_letter_with_the_same_char(
    monkeypatch, game_50, place_letter, gold_points
):
    # the gold letter reached the normal letter in the bar: one press, both
    monkeypatch.setattr(config, "GOLD_POINTS", gold_points)
    normal = place_letter(game_50, 0, y=620, status=NEED)  # "A"
    gold = place_letter(game_50, 2, y=650, status=NEED, gold=True, char="A")

    game_50.key_pressed("a")

    assert (normal.status, gold.status) == (LetterStatus.WAS_PRESSED,) * 2
    assert game_50.points == config.GOLD_FROM_POINTS + 1 + gold_points
    assert game_50.transition_to_game_over is False


def test_gold_and_normal_letter_in_the_bar(game_50, place_letter):
    normal = place_letter(game_50, 0, y=620, status=NEED)
    gold = place_letter(game_50, 1, y=650, status=NEED, gold=True)

    game_50.key_pressed("s")
    game_50.key_pressed("a")

    assert (normal.status, gold.status) == (LetterStatus.WAS_PRESSED,) * 2
    assert game_50.transition_to_game_over is False
