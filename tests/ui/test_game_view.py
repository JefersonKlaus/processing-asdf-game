"""GameView: the layers of the screen and what each page shows."""

from datetime import datetime
from types import SimpleNamespace

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import Game, GamePage
from asdf_hero.ui import GameView, theme
from asdf_hero.ui.texts import ENGLISH


@pytest.fixture
def view(game):
    return GameView(game)


SHOWN = (
    "lanes",
    "action bar",
    "letters",
    "touch buttons",
    "points bar",
    "banner",
    "game over points",
    "best results",
    "button",
    "hand button",
    "congratulations",
)


def shown(view):
    """The names (SHOWN) of the visible parts."""
    visible = (
        view.background.lanes.visible,
        view.action_bar.control.visible,
        view.letters.visible,
        view.touch_buttons.control.visible,
        view.points_bar.visible,
        view.background.game_over_banner.visible,
        view.game_over_points.visible,
        view.scoreboard.control.visible,
        view.button.control.visible,
        view.hand_button.control.visible,
        view.congratulations.control.visible,
    )
    return {name for name, is_visible in zip(SHOWN, visible) if is_visible}


def test_layers_in_order(view):
    image, *layers = view.control.controls

    assert isinstance(image, ft.Image)
    assert image.src == theme.BACKGROUND_IMAGE
    assert layers == [
        view.background.lanes,
        view.action_bar.control,
        view.background.game_over_banner,
        view.letters,
        view.touch_buttons.control,
        view.points_bar,
        view.game_over_points,
        view.scoreboard.control,
        view.button.control,
        view.hand_button.control,
        view.congratulations.control,  # on top of everything
    ]


@pytest.mark.parametrize(
    "page, expected",
    [
        # the home screen keeps the best results
        (GamePage.START, {"banner", "best results", "button", "hand button"}),
        (
            GamePage.RUNNING,
            {"lanes", "action bar", "letters", "touch buttons", "points bar"},
        ),
        (
            GamePage.GAME_OVER,
            {"banner", "game over points", "best results", "button", "hand button"},
        ),
        (GamePage.CONGRATULATIONS, {"congratulations"}),
    ],
)
def test_what_each_page_shows(view, page, expected):
    view.game.page = page

    view.render()

    assert shown(view) == expected


@pytest.mark.parametrize(
    "page, text",
    [
        (GamePage.START, "Iniciar ASDF Hero"),
        (GamePage.GAME_OVER, "Falhar novamente"),
    ],
)
def test_button_text(view, page, text):
    view.game.page = page

    view.render()

    assert view.button.control.content.value == text


@pytest.mark.parametrize(
    "page, title", [(GamePage.START, "ASDF HERO"), (GamePage.GAME_OVER, "GAME OVER")]
)
def test_banner_title(view, page, title):
    view.game.page = page

    view.render()

    assert view.background.banner_text.value == title


def test_home_screen_shows_the_best_results(view, game):
    last = game.scoreboard.add(42, datetime(2025, 3, 5, 14, 0), "Ana")

    view.render()

    first_row = view.scoreboard.rows[0]
    assert [cell.value for cell in first_row.controls][1::3] == ["Ana", "42"]
    assert game.last_result is not last  # nothing in bold on the home screen
    assert {cell.weight for cell in first_row.controls} == {None}


def test_buttons_are_colored_with_the_lane_colors(view):
    view.render()

    assert view.button.control.bgcolor == theme.START_BUTTON_COLOR == theme.LANE_COLORS[3]
    assert view.hand_button.control.bgcolor == theme.HAND_BUTTON_COLOR
    assert theme.HAND_BUTTON_COLOR == theme.LANE_COLORS[2]  # purple


@pytest.mark.parametrize(
    "page, texts",
    [
        (GamePage.START, ["Start ASDF Hero", "Left hand: ASDF"]),
        (GamePage.GAME_OVER, ["Fail again", "Left hand: ASDF"]),
    ],
)
def test_buttons_in_english(game, page, texts):
    view = GameView(game, texts=ENGLISH)
    game.page = page

    view.render()

    buttons = (view.button, view.hand_button)
    assert [button.control.content.value for button in buttons] == texts


def test_points_in_english(game):
    view = GameView(game, texts=ENGLISH)
    game.page = GamePage.GAME_OVER
    game.points = 7

    view.render()

    assert view.game_over_points.content.value == "Points: 7"
    assert view.scoreboard.title.content.value == "Best results"
    assert view.background.banner_text.value == "GAME OVER"


@pytest.mark.parametrize(
    "page, label", [(GamePage.RUNNING, "points_bar"), (GamePage.GAME_OVER, "game_over_points")]
)
def test_points(view, page, label):
    view.game.page = page
    view.game.points = 12

    view.render()

    assert getattr(view, label).content.value == "Pontos: 12"


def test_best_results_below_the_points_and_above_the_buttons(view):
    points = view.game_over_points
    best = view.scoreboard.control
    best_height = theme.SCOREBOARD_TITLE_HEIGHT + 5 * theme.SCOREBOARD_ROW_HEIGHT
    banner_bottom = theme.GAME_OVER_BANNER_TOP + theme.GAME_OVER_BANNER_HEIGHT

    assert best.top >= points.top + points.height  # below "Pontos: "
    assert best.top + best_height <= banner_bottom  # inside the white banner
    assert banner_bottom <= view.game.hand_button.y  # above the buttons


def test_keyboard_key_shows_the_press_effect_on_its_button(view, running_game):
    view.render()

    running_game.key_pressed("d")
    view.render()

    pressed = view.touch_buttons.controls[2]
    assert pressed.width == running_game.touch_buttons[2].width + 2 * theme.PRESS_EFFECT_GROW


def test_hand_button_above_the_start_button(view):
    view.render()

    start, hand = view.button.control, view.hand_button.control
    assert hand.left == start.left
    assert start.top == hand.top + hand.height + config.BUTTON_GAP
    assert hand.content.size == theme.HAND_BUTTON_FONT_SIZE


def test_congratulations_shows_the_points(view):
    view.game.page = GamePage.CONGRATULATIONS
    view.game.points = 42

    view.render()

    assert "42 pontos" in view.congratulations.text.content.value


def test_name_field_events_go_to_the_callbacks(game):
    changes, submits = [], []
    view = GameView(game, on_name_change=changes.append, on_name_submit=lambda: submits.append(1))
    game.page = GamePage.CONGRATULATIONS
    view.render()

    field = view.congratulations.field
    field.value = "Ana"
    field.on_submit(SimpleNamespace(control=field))

    assert (changes, submits) == (["Ana"], [1])


def test_name_field_callbacks_are_optional(view):
    view.game.page = GamePage.CONGRATULATIONS
    view.render()
    field = view.congratulations.field

    field.on_change(SimpleNamespace(control=field))
    field.on_submit(SimpleNamespace(control=field))  # nothing happens


def test_wide_game_draws_the_wide_lanes():
    game = Game(width=400)
    view = GameView(game)

    assert [line.left for line in view.background.lanes.controls] == list(game.lane_lines)
    assert view.control.width == 400


def test_hand_button_text_follows_the_hand(view, game):
    view.render()
    assert view.hand_button.control.content.value == "Mão esquerda: ASDF"

    game.toggle_hand()
    view.render()
    assert view.hand_button.control.content.value == "Mão direita: JKLÇ"
