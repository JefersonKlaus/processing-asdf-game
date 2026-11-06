"""BackgroundView: lanes (running) and the game over banner."""

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


def test_lanes_of_a_wider_game():
    view = BackgroundView(400, 800, lane_lines=(0, 100, 200, 300, 395))

    assert [line.left for line in view.lanes.controls] == [0, 100, 200, 300, 395]


@pytest.mark.parametrize(
    "page, visible, text",
    [
        (GamePage.GAME_OVER, True, "GAME OVER"),
        (GamePage.START, True, "ASDF HERO"),  # home screen: the best results
        (GamePage.RUNNING, False, "GAME OVER"),
    ],
)
def test_banner_text_of_each_page(view, page, visible, text):
    view.render(page)

    assert view.game_over_banner.visible is visible
    assert view.banner_text.value == text


@pytest.mark.parametrize(
    "page, color",
    [(GamePage.GAME_OVER, theme.GAME_OVER_COLOR), (GamePage.START, theme.BLACK)],
)
def test_banner_text_color(view, page, color):
    view.render(page)

    assert view.banner_text.color == color


@pytest.mark.parametrize("page", [GamePage.GAME_OVER, GamePage.START])
def test_banner_text_is_bold(view, page):
    view.render(page)

    assert view.banner_text.weight == ft.FontWeight.BOLD


def test_game_over_is_red_again_after_the_start_page(view):
    view.render(GamePage.START)
    view.render(GamePage.GAME_OVER)

    assert view.banner_text.color == theme.GAME_OVER_COLOR


def test_game_over_banner():
    view = BackgroundView(400, 800)
    bar, text = view.game_over_banner.controls

    assert (bar.left, bar.top, bar.width) == (0, theme.GAME_OVER_BANNER_TOP, 400)
    assert bar.height == theme.GAME_OVER_BANNER_HEIGHT
    assert text.content.value == "GAME OVER"
    assert text.content.size == theme.GAME_OVER_FONT_SIZE


def test_starts_hidden(view):
    assert (view.lanes.visible, view.game_over_banner.visible) == (False, False)


@pytest.mark.parametrize(
    "page, expected",
    [
        (GamePage.START, (False, True)),  # the banner with the best results
        (GamePage.RUNNING, (True, False)),
        (GamePage.GAME_OVER, (False, True)),
    ],
)
def test_render(view, page, expected):
    view.render(page)

    assert (view.lanes.visible, view.game_over_banner.visible) == expected
