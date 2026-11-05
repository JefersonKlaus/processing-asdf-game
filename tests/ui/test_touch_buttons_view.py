"""TouchButtonsView: the color of the lane and the key of the lane."""

import pytest

from asdf_hero.game import Game
from asdf_hero.ui import theme
from asdf_hero.ui.touch_buttons_view import TouchButtonsView


@pytest.fixture
def game():
    return Game()


@pytest.fixture
def view(game):
    return TouchButtonsView(game.touch_buttons, game.width, game.height)


def test_one_button_for_each_lane_with_its_color(view, game):
    for button, control, color in zip(game.touch_buttons, view.controls, theme.LANE_COLORS):
        assert (control.left, control.top) == (button.x, button.y)
        assert (control.width, control.height) == (button.width, button.height)
        assert control.bgcolor == color


def test_starts_hidden(view):
    assert view.control.visible is False


@pytest.mark.parametrize(
    "keys", [("A", "S", "D", "F"), ("J", "K", "L", "Ç")], ids=["left hand", "right hand"]
)
def test_shows_the_keys(view, keys):
    view.render(visible=True, keys=keys)

    assert view.control.visible is True
    assert tuple(control.content.value for control in view.controls) == keys


def test_pressed_button_is_lighter(view, game):
    game.touch_buttons[1].clicked = True

    view.render(visible=True, keys=("A", "S", "D", "F"))

    assert [control.opacity for control in view.controls] == [
        1.0,
        theme.TOUCH_BUTTON_PRESSED_OPACITY,
        1.0,
        1.0,
    ]
