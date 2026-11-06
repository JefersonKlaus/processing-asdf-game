"""Theme: color helper and the rules of the colors (the texts: test_texts.py)."""

import pytest

from asdf_hero.game import Highlight
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



def test_darker():
    assert theme.darker(theme.rgb(100, 200, 40)) == theme.rgb(75, 150, 30)
    assert theme.darker(theme.rgb(100, 100, 100, 128), 0.5) == theme.rgb(50, 50, 50, 128)


def test_color_standard():
    # the colors of the lanes: blue, red, purple, green
    blue, red, purple, green = theme.LANE_COLORS

    assert theme.START_BUTTON_COLOR == green
    assert theme.HAND_BUTTON_COLOR == purple
    assert theme.ANONYMOUS_BUTTON_COLOR == blue
    assert theme.GAME_OVER_COLOR == red


def channels(color):
    return [int(color[i : i + 2], 16) for i in (3, 5, 7)]


def distance(first, second):
    return sum((a - b) ** 2 for a, b in zip(channels(first), channels(second))) ** 0.5


@pytest.mark.parametrize("lane_color", theme.LANE_COLORS)
def test_no_lane_looks_like_the_gold_letter(lane_color):
    # the old yellow lane (244, 160, 0) was only 35 away from the gold color
    assert distance(lane_color, theme.GOLD_COLOR) > 120


def test_lane_colors_are_different():
    colors = theme.LANE_COLORS
    assert min(distance(a, b) for a in colors for b in colors if a != b) > 100


def test_with_alpha():
    assert theme.with_alpha(theme.rgb(66, 133, 244), 180) == theme.rgb(66, 133, 244, 180)


def test_one_glow_color_for_each_lane():
    assert len(theme.LANE_GLOW_COLORS) == len(theme.LANE_COLORS)
    for glow, color in zip(theme.LANE_GLOW_COLORS, theme.LANE_COLORS):
        assert glow[3:] == color[3:]  # same color
        assert glow[1:3] == f"{theme.LANE_GLOW_ALPHA:02x}"  # transparent


def test_normal_glow_is_smaller_than_the_special_glow():
    assert theme.LANE_GLOW_BLUR < theme.GLOW_BLUR
    assert theme.LANE_GLOW_SPREAD < theme.GLOW_SPREAD
    gold_alpha = int(theme.GOLD_GLOW_COLOR[1:3], 16)
    assert theme.LANE_GLOW_ALPHA < gold_alpha
