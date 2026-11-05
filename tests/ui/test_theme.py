"""Theme: color helper and the rules of the colors and texts."""

import pytest

from asdf_hero.game import Hand, Highlight
from asdf_hero.ui import theme


@pytest.mark.parametrize(
    "args, expected",
    [
        ((0, 0, 0), "#ff000000"),
        ((66, 133, 244), "#ff4285f4"),
        ((255, 255, 255, 200), "#c8ffffff"),
    ],
)
def test_rgb_returns_flet_argb_color(args, expected):
    assert theme.rgb(*args) == expected


def test_lane_gold_and_silver_colors_are_different():
    colors = list(theme.LANE_COLORS) + [theme.GOLD_COLOR, theme.SILVER_COLOR]
    assert len(set(colors)) == 6


@pytest.mark.parametrize("highlight", [Highlight.PRESSED, Highlight.WRONG])
def test_highlight_colors_are_almost_white(highlight):
    color = theme.ACTION_BAR_COLORS[highlight]  # "#aarrggbb"
    assert min(int(color[i : i + 2], 16) for i in (3, 5, 7)) >= 190


def test_one_action_bar_color_for_each_highlight():
    assert set(theme.ACTION_BAR_COLORS) == set(Highlight)


def test_press_effect_is_2px_and_short():
    assert theme.ACTION_BAR_PULSE == 2  # pixels on each side
    assert 0 < theme.ACTION_BAR_PULSE_FRAMES / 60 <= 0.2  # seconds


def test_hand_button_texts_show_the_keys():
    assert "ASDF" in theme.HAND_BUTTON_TEXTS[Hand.LEFT]
    assert "JKLÇ" in theme.HAND_BUTTON_TEXTS[Hand.RIGHT]
