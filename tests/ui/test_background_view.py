import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import GamePage
from asdf_hero.ui import theme
from asdf_hero.ui.background_view import BackgroundView


@pytest.fixture
def view():
    return BackgroundView(282, 800)


def test_lanes(view):
    lines = view.lanes.controls

    assert [line.left for line in lines] == list(config.LANE_LINES)
    for line in lines:
        assert (line.top, line.width, line.height) == (0, 5, 800)
        assert line.bgcolor == theme.WHITE
        assert line.border == ft.Border.all(1, theme.BLACK)


def test_game_over_banner():
    view = BackgroundView(400, 800)
    bar, text = view.game_over_banner.controls

    assert (bar.left, bar.top, bar.width, bar.height) == (0, 200, 400, 120)
    assert text.content.value == "GAME OVER"
    assert text.content.size == theme.GAME_OVER_FONT_SIZE


def test_starts_hidden(view):
    assert (view.lanes.visible, view.game_over_banner.visible) == (False, False)


@pytest.mark.parametrize(
    "page, expected",
    [
        (GamePage.START, (False, False)),
        (GamePage.RUNNING, (True, False)),
        (GamePage.GAME_OVER, (False, True)),
    ],
)
def test_render(view, page, expected):
    view.render(page)

    assert (view.lanes.visible, view.game_over_banner.visible) == expected
