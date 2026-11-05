"""LetterView: the circles and the char of a letter."""

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import ActionBar, Letter, LetterStatus
from asdf_hero.ui import theme
from asdf_hero.ui.letter_view import LetterView

BORDER = ft.Border.all(1, theme.BLACK)
LANE = theme.LANE_COLORS[0]
GOLD = theme.GOLD_COLOR
WHITE, BLACK = theme.WHITE, theme.BLACK


def render(lane=0, y=300, status=LetterStatus.WAITING, gold=False):
    letter = Letter(lane, config.LEFT_HAND_KEYS[lane], ActionBar(), gold=gold)
    letter.y = y
    letter.status = status
    view = LetterView(letter)
    view.render()
    inner, label = view.control.content.controls
    return view, view.control, inner, label


def test_circle_with_the_char():
    _, outer, inner, label = render(lane=2)

    assert outer.shape == inner.shape == ft.BoxShape.CIRCLE
    assert (outer.width, outer.height) == (62, 62)
    assert inner.width == pytest.approx(62 * 0.7)
    assert label.value == "D"


def test_unique_key():
    # flet controls with the same values are ==, the key avoids it
    first, second = render()[1], render()[1]

    assert first.key != second.key
    assert first != second


def test_position_follows_the_letter():
    view, outer, _, _ = render(lane=3, y=300)
    assert (outer.left, outer.top) == (config.LANE_CENTERS[3] - 31, 300 - 31)

    view.letter.move(4.5)
    view.render()
    assert outer.top == pytest.approx(304.5 - 31)


# colors: (outer, outer border, inner, inner border, char)
@pytest.mark.parametrize(
    "status, gold, colors",
    [
        (LetterStatus.WAITING, False, (LANE, None, WHITE, None, BLACK)),
        (LetterStatus.NEED_BE_PRESSED, False, (LANE, None, WHITE, None, LANE)),
        (LetterStatus.WAS_PRESSED, False, (LANE, None, LANE, None, WHITE)),
        (LetterStatus.FAILED, False, (WHITE, BORDER, WHITE, BORDER, BLACK)),
        (LetterStatus.NEED_BE_PRESSED, True, (GOLD, None, WHITE, None, GOLD)),
        (LetterStatus.WAS_PRESSED, True, (GOLD, None, GOLD, None, WHITE)),
        (LetterStatus.FAILED, True, (WHITE, BORDER, WHITE, BORDER, BLACK)),
    ],
    ids=["waiting", "need", "pressed", "failed", "gold need", "gold pressed", "gold failed"],
)
def test_colors(status, gold, colors):
    _, outer, inner, label = render(status=status, gold=gold)

    assert (outer.bgcolor, outer.border, inner.bgcolor, inner.border, label.color) == colors


def test_colors_follow_the_status():
    view, outer, _, _ = render(status=LetterStatus.FAILED)

    view.letter.status = LetterStatus.WAITING
    view.render()

    assert (outer.bgcolor, outer.border) == (LANE, None)


@pytest.mark.parametrize(
    "gold, swapped, glow",
    [(False, False, None), (True, False, theme.GOLD_GLOW_COLOR), (False, True, theme.SILVER_GLOW_COLOR)],
    ids=["normal", "gold", "silver"],
)
def test_glow_of_the_challenges(gold, swapped, glow):
    view, outer, _, _ = render(gold=gold)
    view.letter.swapped = swapped
    view.render()

    assert (outer.shadow.color if outer.shadow else None) == glow


def test_swapped_letter_is_silver_with_the_new_char():
    view, outer, _, label = render(lane=0)  # "A"

    view.letter.char, view.letter.swapped = "F", True
    view.render()

    assert (outer.bgcolor, label.value) == (theme.SILVER_COLOR, "F")
