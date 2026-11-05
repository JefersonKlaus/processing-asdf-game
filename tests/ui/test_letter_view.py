import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import ActionBar, Letter, LetterStatus
from asdf_hero.ui import theme
from asdf_hero.ui.letter_view import LetterView

BORDER = ft.Border.all(1, theme.BLACK)


def make_view(lane=0, y=300, status=LetterStatus.WAITING, char=None, gold=False):
    letter = Letter(lane, char or config.CHARS[lane], ActionBar(), gold=gold)
    letter.y = y
    letter.status = status
    view = LetterView(letter)
    view.render()
    outer = view.control
    inner, label = outer.content.controls
    return view, outer, inner, label


class TestControl:
    def test_is_a_circle_with_the_letter_size(self):
        _, outer, _, _ = make_view()

        assert outer.shape == ft.BoxShape.CIRCLE
        assert (outer.width, outer.height) == (62, 62)

    def test_inner_circle_and_char(self):
        _, _, inner, label = make_view(lane=2)

        assert inner.shape == ft.BoxShape.CIRCLE
        assert inner.width == pytest.approx(62 * 0.7)
        assert label.value == "D"
        assert label.size == theme.LETTER_FONT_SIZE

    def test_random_char_is_shown(self):
        _, _, _, label = make_view(lane=0, char="F")

        assert label.value == "F"

    def test_unique_key(self):
        # flet controls with the same values are ==, the key avoids it
        first, second = make_view()[1], make_view()[1]

        assert first.key != second.key
        assert first != second


class TestGold:
    def test_normal_letter_has_no_glow(self):
        _, outer, _, _ = make_view()

        assert outer.shadow is None

    def test_gold_color_and_glow(self):
        _, outer, _, _ = make_view(lane=2, gold=True)

        assert outer.bgcolor == theme.GOLD_COLOR
        assert outer.shadow == ft.BoxShadow(
            blur_radius=theme.GOLD_GLOW_BLUR, spread_radius=2, color=theme.GOLD_GLOW_COLOR
        )

    def test_gold_need_be_pressed(self):
        _, _, _, label = make_view(gold=True, status=LetterStatus.NEED_BE_PRESSED)

        assert label.color == theme.GOLD_COLOR

    def test_gold_was_pressed(self):
        _, outer, inner, label = make_view(gold=True, status=LetterStatus.WAS_PRESSED)

        assert (outer.bgcolor, inner.bgcolor, label.color) == (
            theme.GOLD_COLOR,
            theme.GOLD_COLOR,
            theme.WHITE,
        )

    def test_gold_failed(self):
        _, outer, _, _ = make_view(gold=True, status=LetterStatus.FAILED)

        assert (outer.bgcolor, outer.border) == (theme.WHITE, BORDER)


class TestRender:
    COLOR = theme.LANE_COLORS[0]

    def test_position_is_the_center_of_the_circle(self):
        _, outer, _, _ = make_view(lane=3, y=300)

        assert outer.left == config.LANE_CENTERS[3] - 31
        assert outer.top == 300 - 31

    def test_follows_the_letter(self):
        view, outer, _, _ = make_view(y=100)

        view.letter.move(4.5)
        view.render()

        assert outer.top == pytest.approx(104.5 - 31)

    def test_waiting(self):
        _, outer, inner, label = make_view(status=LetterStatus.WAITING)

        assert (outer.bgcolor, outer.border) == (self.COLOR, None)
        assert (inner.bgcolor, inner.border) == (theme.WHITE, None)
        assert label.color == theme.BLACK

    def test_need_be_pressed(self):
        _, outer, inner, label = make_view(status=LetterStatus.NEED_BE_PRESSED)

        assert (outer.bgcolor, outer.border) == (self.COLOR, None)
        assert (inner.bgcolor, inner.border) == (theme.WHITE, None)
        assert label.color == self.COLOR

    def test_was_pressed(self):
        _, outer, inner, label = make_view(status=LetterStatus.WAS_PRESSED)

        assert (outer.bgcolor, outer.border) == (self.COLOR, None)
        assert (inner.bgcolor, inner.border) == (self.COLOR, None)
        assert label.color == theme.WHITE

    def test_failed(self):
        _, outer, inner, label = make_view(status=LetterStatus.FAILED)

        assert (outer.bgcolor, outer.border) == (theme.WHITE, BORDER)
        assert (inner.bgcolor, inner.border) == (theme.WHITE, BORDER)
        assert label.color == theme.BLACK

    def test_status_change(self):
        view, outer, _, _ = make_view(status=LetterStatus.FAILED)

        view.letter.status = LetterStatus.WAITING
        view.render()

        assert (outer.bgcolor, outer.border) == (self.COLOR, None)
