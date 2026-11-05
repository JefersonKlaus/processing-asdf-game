import pytest

from asdf_hero import config
from asdf_hero.game import ActionBar, Highlight


@pytest.fixture
def bar():
    return ActionBar()


def test_defaults(bar):
    assert (bar.top, bar.height) == (config.ACTION_BAR_TOP, config.ACTION_BAR_HEIGHT)
    assert bar.bottom == config.ACTION_BAR_TOP + config.ACTION_BAR_HEIGHT
    assert bar.highlight == Highlight.NONE


@pytest.mark.parametrize(
    "y, expected", [(599, False), (600, True), (640, True), (680, True), (681, False)]
)
def test_contains(bar, y, expected):
    assert bar.contains(y) is expected


@pytest.mark.parametrize(
    "y, expected",
    [
        (568, False),  # circle bottom at 599: above the bar
        (569, True),  # circle bottom at 600: touches the top of the bar
        (640, True),
        (711, True),  # circle top at 680: touches the bottom of the bar
        (712, False),  # circle top at 681: below the bar
    ],
)
def test_touches(bar, y, expected):
    assert bar.touches(y, size=62) is expected


def test_custom_position():
    bar = ActionBar(top=100, height=10)

    assert bar.contains(105) is True
    assert bar.contains(111) is False


@pytest.mark.parametrize(
    "correct, highlight", [(True, Highlight.PRESSED), (False, Highlight.WRONG)]
)
def test_press_highlights(bar, correct, highlight):
    bar.press(correct=correct)

    assert bar.highlight == highlight


def test_highlight_lasts_some_frames():
    bar = ActionBar(highlight_frames=3)
    bar.press(correct=True)

    bar.update()
    bar.update()
    assert bar.highlight == Highlight.PRESSED

    bar.update()
    assert bar.highlight == Highlight.NONE


def test_new_press_restarts_the_highlight():
    bar = ActionBar(highlight_frames=2)
    bar.press(correct=True)
    bar.update()

    bar.press(correct=False)
    bar.update()

    assert bar.highlight == Highlight.WRONG


def test_update_without_highlight(bar):
    bar.update()

    assert bar.highlight == Highlight.NONE


def test_presses_are_counted(bar):
    bar.press(correct=True)
    bar.press(correct=False)

    assert bar.presses == 2


def test_reset_keeps_the_presses_count(bar):
    # the view compares the count to start a vibration: it never goes back
    bar.press(correct=True)

    bar.reset()

    assert bar.presses == 1


def test_reset(bar):
    bar.press(correct=False)

    bar.reset()
    bar.update()

    assert bar.highlight == Highlight.NONE
