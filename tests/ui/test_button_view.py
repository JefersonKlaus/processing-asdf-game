"""ButtonView: a colored button (start / hand / congratulations)."""

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import Button
from asdf_hero.ui import theme
from asdf_hero.ui.button_view import ButtonView


@pytest.fixture
def view():
    return ButtonView(Button(x=10, y=20, width=240, height=52))


def test_starts_hidden(view):
    assert view.control.visible is False


def test_render(view):
    view.render(visible=True, text="Play")

    control = view.control
    assert control.visible is True
    assert (control.left, control.top, control.width, control.height) == (10, 20, 240, 52)
    assert control.bgcolor == theme.START_BUTTON_COLOR  # green by default
    assert (control.content.value, control.content.size) == ("Play", theme.BUTTON_FONT_SIZE)


def test_the_design_of_the_touch_buttons(view):
    # the same rounded corners and bold white text as the letter buttons
    label = view.control.content

    assert label.color == theme.BUTTON_TEXT_COLOR == theme.TOUCH_BUTTON_TEXT_COLOR
    assert label.weight == ft.FontWeight.BOLD
    assert view.control.border_radius == theme.BUTTON_RADIUS == theme.TOUCH_BUTTON_RADIUS
    assert theme.BUTTON_RADIUS < config.BUTTON_HEIGHT / 4  # not round (pill)


def test_custom_color():
    view = ButtonView(Button(0, 0, 10, 10), color=theme.HAND_BUTTON_COLOR)

    view.render(visible=True)

    assert view.control.bgcolor == theme.HAND_BUTTON_COLOR


def test_pressed_button_is_darker(view):
    view.button.clicked = True

    view.render(visible=True)

    assert view.control.bgcolor == theme.darker(theme.START_BUTTON_COLOR)


def test_custom_font_size():
    view = ButtonView(Button(0, 0, 10, 10), font_size=18)

    view.render(visible=True)

    assert view.control.content.size == 18
