"""The game fits the page: smaller on small pages, fills the phone screen."""

from types import SimpleNamespace

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.app import GameApp, game_width
from asdf_hero.game import Scoreboard
from tests.app.fakes import FakePage

ANDROID = ft.PagePlatform.ANDROID


def build(width, height, platform=None):
    game_app = GameApp(FakePage(width, height, platform), scoreboard=Scoreboard())
    game_app.build()
    return game_app


@pytest.mark.parametrize(
    "page_size, scale",
    [
        ((1280, 900), 1.0),  # desktop: the game keeps its size
        ((None, None), 1.0),  # unknown page size
        ((390, 700), 700 / 800),  # phone: the height limits
        ((200, 800), 200 / 282),  # narrow page: the width limits
    ],
)
def test_scale(page_size, scale):
    game_app = build(*page_size)

    assert game_app.scale == pytest.approx(scale)
    assert game_app.detector.scale.scale == pytest.approx(scale)
    assert game_app.screen.width == pytest.approx(282 * scale)
    assert game_app.screen.height == pytest.approx(800 * scale)


def test_scaled_from_the_top_left():
    game_app = build(390, 600)

    assert game_app.detector.scale.alignment == ft.Alignment.TOP_LEFT
    assert (game_app.detector.left, game_app.detector.top) == (0, 0)


def test_resize_the_page():
    game_app = build(1280, 900)

    game_app.on_resize(SimpleNamespace(width=390, height=400))

    assert game_app.scale == pytest.approx(0.5)
    assert game_app.screen.height == pytest.approx(400)


# --- phones: the game fills the screen (no black margins) ----------------------


@pytest.mark.parametrize(
    "page_size",
    [(390, 844), (412, 915), (360, 640), (1080 / 3, 2400 / 3)],
)
@pytest.mark.parametrize("platform", [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS])
def test_phone_screen_is_filled(page_size, platform):
    page_width, page_height = page_size

    game_app = build(page_width, page_height, platform)

    assert game_app.screen.width == pytest.approx(page_width)  # no side margins
    assert game_app.screen.height == pytest.approx(page_height)
    assert game_app.game.height == config.HEIGHT  # the rules keep the height


def test_phone_game_is_wider_and_bigger():
    game_app = build(390, 844, ANDROID)

    assert game_app.game.width == pytest.approx(800 * 390 / 844)  # ~370 instead of 282
    assert game_app.scale == pytest.approx(844 / 800)  # bigger than its size
    assert game_app.view.control.width == game_app.game.width


def test_computer_keeps_the_game_size():
    game_app = build(1280, 900, ft.PagePlatform.WINDOWS)

    assert game_app.game.width == config.WIDTH
    assert game_app.scale == 1.0  # never bigger on a computer


def test_phone_with_an_unknown_page_size():
    game_app = build(None, None, ANDROID)

    assert game_app.game.width == config.WIDTH
    assert game_app.scale == 1.0


def test_resize_on_a_phone_keeps_the_game_width():
    # the keyboard of the phone opens: the page is shorter
    game_app = build(390, 844, ANDROID)
    width = game_app.game.width

    game_app.on_resize(SimpleNamespace(width=390, height=500))

    assert game_app.game.width == width
    assert game_app.scale == pytest.approx(500 / 800)  # all the game is visible
    assert game_app.screen.height == pytest.approx(500)


@pytest.mark.parametrize(
    "page_size, width",
    [
        ((None, None), config.WIDTH),  # unknown
        ((390, 844), 800 * 390 / 844),  # phone: same shape as the screen
        ((200, 800), config.WIDTH),  # narrower than the game: never narrower
        ((768, 1024), config.MAX_WIDTH),  # tablet: max width
        ((844, 390), config.MAX_WIDTH),  # landscape: max width
    ],
)
def test_game_width(page_size, width):
    assert game_width(*page_size) == pytest.approx(width)
