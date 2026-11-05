"""GameView: the layers of the screen and what each page shows."""

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import GamePage
from asdf_hero.ui import GameView, theme


@pytest.fixture
def view(game):
    return GameView(game)


def shown(view):
    """lanes, action bar, letters, points bar, game over points, button, hand button"""
    return (
        view.background.lanes.visible,
        view.action_bar.control.visible,
        view.letters.visible,
        view.points_bar.visible,
        view.game_over_points.visible,
        view.button.control.visible,
        view.hand_button.control.visible,
    )


def test_layers_in_order(view):
    image, *layers = view.control.controls

    assert isinstance(image, ft.Image)
    assert image.src == theme.BACKGROUND_IMAGE
    assert layers == [
        view.background.lanes,
        view.action_bar.control,
        view.background.game_over_banner,
        view.letters,
        view.points_bar,
        view.game_over_points,
        view.button.control,
        view.hand_button.control,
    ]


@pytest.mark.parametrize(
    "page, expected",
    [
        (GamePage.START, (False, False, False, False, False, True, True)),
        (GamePage.RUNNING, (True, True, True, True, False, False, False)),
        (GamePage.GAME_OVER, (False, False, False, False, True, True, True)),
    ],
)
def test_what_each_page_shows(view, page, expected):
    view.game.page = page

    view.render()

    assert shown(view) == expected


@pytest.mark.parametrize(
    "page, text",
    [(GamePage.START, "Iniciar ASDF Hero"), (GamePage.GAME_OVER, "Falhar novamente")],
)
def test_button_text(view, page, text):
    view.game.page = page

    view.render()

    assert view.button.control.content.value == text


@pytest.mark.parametrize(
    "page, label", [(GamePage.RUNNING, "points_bar"), (GamePage.GAME_OVER, "game_over_points")]
)
def test_points(view, page, label):
    view.game.page = page
    view.game.points = 12

    view.render()

    assert getattr(view, label).content.value == "Pontos: 12"


def test_hand_button_below_the_start_button(view):
    view.render()

    start, hand = view.button.control, view.hand_button.control
    assert hand.left == start.left
    assert hand.top == start.top + start.height + config.BUTTON_GAP
    assert hand.content.size == theme.HAND_BUTTON_FONT_SIZE


def test_hand_button_text_follows_the_hand(view, game):
    view.render()
    assert view.hand_button.control.content.value == "Mão esquerda: ASDF"

    game.toggle_hand()
    view.render()
    assert view.hand_button.control.content.value == "Mão direita: JKLÇ"
