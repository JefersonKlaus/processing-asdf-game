"""ButtonView: a button of the start / game over pages."""

import pytest

from asdf_hero.game import Button
from asdf_hero.ui import theme
from asdf_hero.ui.button_view import ButtonView


@pytest.fixture
def view():
    return ButtonView(Button(x=10, y=20, width=200, height=40))


def test_starts_hidden(view):
    assert view.control.visible is False


def test_render(view):
    view.render(visible=True, text="Play")

    control = view.control
    assert control.visible is True
    assert (control.left, control.top, control.width, control.height) == (10, 20, 200, 40)
    assert control.bgcolor == theme.BUTTON_COLOR
    assert (control.content.value, control.content.size) == ("Play", theme.BUTTON_FONT_SIZE)


def test_clicked_color(view):
    view.button.clicked = True

    view.render(visible=True)

    assert view.control.bgcolor == theme.BUTTON_CLICKED_COLOR


def test_custom_font_size():
    view = ButtonView(Button(0, 0, 10, 10), font_size=18)

    view.render(visible=True)

    assert view.control.content.size == 18
