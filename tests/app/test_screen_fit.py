"""The game is made smaller to fit small pages (phones); taps keep game pixels."""

from types import SimpleNamespace

import flet as ft
import pytest

from asdf_hero.app import GameApp
from asdf_hero.game import Scoreboard
from tests.app.fakes import FakePage


def build(width, height):
    game_app = GameApp(FakePage(width, height), scoreboard=Scoreboard())
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
