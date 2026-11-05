"""ActionBar: the hit area and the highlight after a key press."""

import pytest

from asdf_hero.game import ActionBar, Highlight


@pytest.fixture
def bar():
    return ActionBar()  # top 600, height 80


@pytest.mark.parametrize(
    "y, expected",
    [
        (568, False),  # circle bottom at 599: above the bar
        (569, True),  # circle bottom at 600: touches the top
        (640, True),
        (711, True),  # circle top at 680: touches the bottom
        (712, False),  # circle top at 681: below the bar
    ],
)
def test_a_circle_touches_the_bar(bar, y, expected):
    assert bar.touches(y, size=62) is expected


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


def test_reset_removes_the_highlight(bar):
    bar.press(correct=False)

    bar.reset()

    assert bar.highlight == Highlight.NONE


def test_presses_are_counted_and_never_reset(bar):
    # the view compares the count to start the press effect
    bar.press(correct=True)
    bar.press(correct=False)
    bar.reset()

    assert bar.presses == 2
