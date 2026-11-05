"""Scoreboard: the best results (in memory)."""

from datetime import datetime

import pytest

from asdf_hero.game import Scoreboard


def at(minute):
    return datetime(2025, 3, 5, 14, minute)


@pytest.fixture
def board():
    return Scoreboard(size=5)


def points(board):
    return [result.points for result in board.best]


def test_empty(board):
    assert board.best == []


def test_best_first(board):
    for value, minute in [(12, 1), (40, 2), (7, 3)]:
        board.add(value, at(minute))

    assert points(board) == [40, 12, 7]


def test_only_the_best_five(board):
    for minute, value in enumerate([12, 40, 7, 95, 3, 60]):
        board.add(value, at(minute))

    assert points(board) == [95, 60, 40, 12, 7]


def test_same_points_the_oldest_first(board):
    board.add(40, at(30))
    board.add(40, at(10))

    assert [result.when for result in board.best] == [at(10), at(30)]


def test_add_returns_the_result(board):
    result = board.add(33, at(5))

    assert (result.points, result.when) == (33, at(5))
    assert board.best[0] is result


def test_best_is_a_copy(board):
    board.add(1, at(1))

    board.best.clear()

    assert points(board) == [1]
