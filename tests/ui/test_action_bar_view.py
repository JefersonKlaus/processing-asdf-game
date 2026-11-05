"""ActionBarView: color of the highlight and the press effect (2px bigger)."""

import flet as ft
import pytest

from asdf_hero.game import ActionBar, Highlight
from asdf_hero.ui import theme
from asdf_hero.ui.action_bar_view import ActionBarView

NORMAL = (0, 600, 282, 80)  # left, top, width, height
BIGGER = (-2, 598, 286, 84)  # 2px bigger on each side


@pytest.fixture
def view():
    return ActionBarView(ActionBar(), width=282)


def geometry(view):
    control = view.control
    return (control.left, control.top, control.width, control.height)


def sizes(view, frames):
    result = []
    for _ in range(frames):
        view.render(visible=True)
        result.append(geometry(view))
    return result


def test_starts_hidden_with_the_normal_color(view):
    assert view.control.visible is False
    assert view.control.bgcolor == theme.ACTION_BAR_COLORS[Highlight.NONE]
    assert view.control.border == ft.Border.all(1, theme.BLACK)


@pytest.mark.parametrize("visible", [True, False])
def test_visibility(view, visible):
    view.render(visible=visible)

    assert view.control.visible is visible


@pytest.mark.parametrize(
    "correct, highlight", [(True, Highlight.PRESSED), (False, Highlight.WRONG)]
)
def test_color_of_the_highlight(view, correct, highlight):
    view.action_bar.press(correct=correct)

    view.render(visible=True)

    assert view.control.bgcolor == theme.ACTION_BAR_COLORS[highlight]


def test_normal_size_without_press(view):
    assert sizes(view, 5) == [NORMAL] * 5


def test_press_makes_the_bar_bigger_for_some_frames(view):
    view.action_bar.press(correct=True)

    frames = theme.ACTION_BAR_PULSE_FRAMES
    assert sizes(view, frames + 2) == [BIGGER] * frames + [NORMAL] * 2


def test_a_new_press_starts_again(view):
    view.action_bar.press(correct=True)
    sizes(view, theme.ACTION_BAR_PULSE_FRAMES - 1)

    view.action_bar.press(correct=False)

    frames = theme.ACTION_BAR_PULSE_FRAMES
    assert sizes(view, frames + 1) == [BIGGER] * frames + [NORMAL]


def test_new_game_does_not_change_the_size(view):
    view.action_bar.press(correct=True)
    sizes(view, theme.ACTION_BAR_PULSE_FRAMES)

    view.action_bar.reset()

    assert sizes(view, 3) == [NORMAL] * 3


def test_press_effect_is_real_time_during_the_slow_motion(running_game):
    view = ActionBarView(running_game.action_bar, width=282)
    running_game.key_pressed("a")  # wrong press: slow motion starts

    result = []
    for _ in range(theme.ACTION_BAR_PULSE_FRAMES + 1):
        running_game.update()  # the game waits (slow motion)...
        view.render(visible=True)  # ...the view still changes on each frame
        result.append(geometry(view))

    assert result == [BIGGER] * theme.ACTION_BAR_PULSE_FRAMES + [NORMAL]
