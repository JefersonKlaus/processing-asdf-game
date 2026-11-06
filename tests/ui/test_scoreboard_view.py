"""ScoreboardView: position, name, date, time and points of the best results."""

from datetime import datetime

import flet as ft
import pytest

from asdf_hero.game import Scoreboard
from asdf_hero.ui import theme
from asdf_hero.ui.scoreboard_view import ScoreboardView
from asdf_hero.ui.texts import ENGLISH


@pytest.fixture
def board():
    return Scoreboard(size=5)


@pytest.fixture
def view(board):
    return ScoreboardView(board, width=282)


def texts(row):
    return [cell.value for cell in row.controls]


def visible_rows(view):
    return [row for row in view.rows if row.visible]


def test_title(view):
    assert view.title.content.value == "Melhores resultados"


def test_one_row_for_each_result(view):
    assert len(view.rows) == 5


@pytest.mark.parametrize("visible", [True, False])
def test_visibility(view, visible):
    view.render(visible=visible)

    assert view.control.visible is visible


def test_empty_scoreboard_shows_no_rows(view):
    view.render(visible=True)

    assert visible_rows(view) == []


def test_position_name_date_time_and_points(view, board):
    board.add(87, datetime(2025, 3, 5, 14, 7), "Ana")
    board.add(120, datetime(2025, 12, 24, 9, 30), "Bruno")

    view.render(visible=True)

    assert [texts(row) for row in visible_rows(view)] == [
        ["1.", "Bruno", "24/12/2025", "09:30", "120"],
        ["2.", "Ana", "05/03/2025", "14:07", "87"],
    ]


def test_last_game_in_bold(view, board):
    board.add(50, datetime(2025, 3, 5, 14, 0))
    last = board.add(20, datetime(2025, 3, 5, 15, 0))

    view.render(visible=True, last_result=last)

    first_row, second_row = visible_rows(view)
    assert {cell.weight for cell in first_row.controls} == {None}
    assert {cell.weight for cell in second_row.controls} == {ft.FontWeight.BOLD}


def test_rows_follow_the_scoreboard(view, board):
    view.render(visible=True)

    board.add(10, datetime(2025, 3, 5, 14, 0))
    view.render(visible=True)

    assert len(visible_rows(view)) == 1


def test_empty_scoreboard_shows_a_message(view, board):
    view.render(visible=True)
    assert view.empty.visible is True
    assert view.empty.value == "Nenhum resultado ainda"

    board.add(10, datetime(2025, 3, 5, 14, 0))
    view.render(visible=True)
    assert view.empty.visible is False


def test_message_below_the_title(view):
    assert view.control.content.controls[:2] == [view.title, view.empty]


def test_anonymous_result(view, board):
    board.add(10, datetime(2025, 3, 5, 14, 0), "")

    view.render(visible=True)

    assert texts(view.rows[0])[1] == "Anônimo"


def test_in_english(board):
    view = ScoreboardView(board, width=282, texts=ENGLISH)
    board.add(120, datetime(2025, 12, 24, 9, 30), "")

    view.render(visible=True)

    assert view.title.content.value == "Best results"
    assert texts(view.rows[0]) == ["1.", "Anonymous", "12/24/2025", "09:30", "120"]


def test_points_are_aligned_to_the_right(view):
    assert view.rows[0].controls[-1].text_align == ft.TextAlign.RIGHT
    assert view.rows[0].controls[0].size == theme.SCOREBOARD_FONT_SIZE


def test_long_names_end_with_ellipsis(view):
    name_cell = view.rows[0].controls[1]

    assert name_cell.overflow == ft.TextOverflow.ELLIPSIS
    assert name_cell.no_wrap is True


def test_the_columns_fit_the_game_width():
    assert sum(theme.SCOREBOARD_COLUMNS) <= 282
