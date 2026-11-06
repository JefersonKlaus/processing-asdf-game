"""Scoreboard: the best results, names and where they are kept (a store)."""

from datetime import datetime

import pytest

from asdf_hero import config
from asdf_hero.game import MemoryResultStore, Result, Scoreboard
from asdf_hero.game.scoreboard import player_name


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
    result = board.add(33, at(5), "Ana")

    assert (result.points, result.when, result.name) == (33, at(5), "Ana")
    assert board.best[0] is result


def test_best_is_a_copy(board):
    board.add(1, at(1))

    board.best.clear()

    assert points(board) == [1]


# --- best results: who enters ------------------------------------------------


def test_any_result_qualifies_while_there_are_free_places(board):
    for minute in range(4):
        board.add(50, at(minute))

    assert board.qualifies(1) is True


@pytest.mark.parametrize("value", [0, -1])
def test_zero_points_never_qualify(board, value):
    assert board.qualifies(value) is False  # even with free places


def test_zero_point_results_are_not_kept():
    # results saved by old versions (0 points were accepted) are ignored
    store = MemoryResultStore()
    store.save([Result(0, at(1), "Old"), Result(5, at(2), "Ana")])

    board = Scoreboard(store=store)

    assert points(board) == [5]
    assert board.add(0, at(3)) not in board.best


def test_full_board_needs_more_points_than_the_last(board):
    for minute, value in enumerate([90, 80, 70, 60, 50]):
        board.add(value, at(minute))

    assert board.qualifies(51) is True
    assert board.qualifies(50) is False  # same points: the oldest stays
    assert board.qualifies(3) is False


def test_a_qualified_result_enters_the_board(board):
    for minute, value in enumerate([90, 80, 70, 60, 50]):
        board.add(value, at(minute))

    result = board.add(51, at(10))

    assert result in board.best
    assert points(board) == [90, 80, 70, 60, 51]


# --- names --------------------------------------------------------------------


@pytest.mark.parametrize(
    "typed, saved",
    [
        ("Ana", "Ana"),
        ("  Ana   Maria  ", "Ana Maria"),  # extra spaces
        ("Maximiliano Souza", "Maximilian"),  # max length
        ("", ""),  # anonymous (the views show it in the language of the app)
        ("   ", ""),
        ("Joãozinho ", "Joãozinho"),
    ],
)
def test_player_name(typed, saved):
    assert player_name(typed) == saved
    assert len(player_name(typed)) <= config.NAME_MAX_LENGTH


def test_the_name_is_cleaned_when_added(board):
    assert board.add(10, at(1), "  Bia ").name == "Bia"
    assert board.add(10, at(2)).name == ""  # anonymous


# --- store: where the results are kept ----------------------------------------


def test_memory_store_is_the_default(board):
    assert isinstance(board.store, MemoryResultStore)


def test_memory_store_keeps_a_copy():
    store = MemoryResultStore()
    results = [Result(1, at(1))]

    store.save(results)
    results.clear()

    assert store.load() == [Result(1, at(1))]
    store.load().clear()
    assert store.load() == [Result(1, at(1))]


def test_each_change_saves_the_best_results():
    store = MemoryResultStore()
    board = Scoreboard(size=2, store=store)

    for minute, value in enumerate([5, 9, 7]):
        board.add(value, at(minute), f"P{value}")

    assert [(r.points, r.name) for r in store.load()] == [(9, "P9"), (7, "P7")]


def test_the_best_results_are_loaded_from_the_store():
    store = MemoryResultStore()
    store.save([Result(3, at(1)), Result(8, at(2)), Result(5, at(3))])

    board = Scoreboard(size=2, store=store)

    assert points(board) == [8, 5]  # sorted, only the best ``size``
