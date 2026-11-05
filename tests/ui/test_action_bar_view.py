import flet as ft
import pytest

from asdf_hero.game import ActionBar, Highlight
from asdf_hero.ui import theme
from asdf_hero.ui.action_bar_view import ActionBarView

WHITE = theme.rgb(255, 255, 255, 200)
LIGHT_YELLOW = theme.rgb(255, 249, 196, 220)
LIGHT_RED = theme.rgb(255, 205, 210, 220)


@pytest.fixture
def view():
    return ActionBarView(ActionBar(), width=282)


def test_geometry(view):
    control = view.control
    assert (control.left, control.top) == (0, 600)
    assert (control.width, control.height) == (282, 80)
    assert control.border == ft.Border.all(1, theme.BLACK)


def test_starts_hidden_and_white(view):
    assert view.control.visible is False
    assert view.control.bgcolor == WHITE


@pytest.mark.parametrize("visible", [True, False])
def test_visibility(view, visible):
    view.render(visible=visible)

    assert view.control.visible is visible


@pytest.mark.parametrize(
    "correct, color", [(True, LIGHT_YELLOW), (False, LIGHT_RED)], ids=["right", "wrong"]
)
def test_highlight_color(view, correct, color):
    view.action_bar.press(correct=correct)

    view.render(visible=True)

    assert view.control.bgcolor == color


class TestVibration:
    """A small and short vibration of the bar on each key press."""

    def offsets(self, view, frames):
        result = []
        for _ in range(frames):
            view.render(visible=True)
            result.append(view.control.left)
        return result

    def test_no_vibration_without_press(self, view):
        assert self.offsets(view, 5) == [0] * 5

    @pytest.mark.parametrize("correct", [True, False], ids=["right", "wrong"])
    def test_vibration_after_a_press(self, view, correct):
        view.action_bar.press(correct=correct)

        shake = theme.ACTION_BAR_SHAKE
        assert self.offsets(view, len(shake) + 3) == list(shake) + [0, 0, 0]

    def test_only_once_for_each_press(self, view):
        view.action_bar.press(correct=True)
        self.offsets(view, len(theme.ACTION_BAR_SHAKE))

        assert self.offsets(view, 5) == [0] * 5

    def test_a_new_press_starts_again(self, view):
        view.action_bar.press(correct=True)
        self.offsets(view, 3)

        view.action_bar.press(correct=True)

        assert self.offsets(view, 2) == list(theme.ACTION_BAR_SHAKE[:2])

    def test_reset_does_not_shake(self, view):
        view.action_bar.press(correct=True)
        self.offsets(view, len(theme.ACTION_BAR_SHAKE))

        view.action_bar.reset()  # new game

        assert self.offsets(view, 3) == [0] * 3

    def test_vibration_is_real_time_during_the_slow_motion(self, running_game):
        # the view shakes on each frame, even when the game moves slowly
        view = ActionBarView(running_game.action_bar, width=282)
        running_game.key_pressed("a")  # wrong: slow motion starts

        offsets = []
        for _ in range(len(theme.ACTION_BAR_SHAKE)):
            running_game.update()
            view.render(visible=True)
            offsets.append(view.control.left)

        assert offsets == list(theme.ACTION_BAR_SHAKE)


def test_back_to_white_after_the_highlight():
    bar = ActionBar(highlight_frames=1)
    view = ActionBarView(bar, width=282)
    bar.press(correct=True)
    view.render(visible=True)

    bar.update()
    view.render(visible=True)

    assert bar.highlight == Highlight.NONE
    assert view.control.bgcolor == WHITE
