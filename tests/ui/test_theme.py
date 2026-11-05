import pytest

from asdf_hero.game import GamePage, Highlight
from asdf_hero.ui import theme


@pytest.mark.parametrize(
    "args, expected",
    [
        ((0, 0, 0), "#ff000000"),
        ((255, 255, 255), "#ffffffff"),
        ((66, 133, 244), "#ff4285f4"),
        ((255, 255, 255, 200), "#c8ffffff"),
        ((1, 2, 3, 0), "#00010203"),
    ],
)
def test_rgb_returns_flet_argb_color(args, expected):
    assert theme.rgb(*args) == expected


def test_one_color_for_each_lane():
    assert len(theme.LANE_COLORS) == 4
    assert len(set(theme.LANE_COLORS)) == 4


def test_action_bar_colors():
    colors = theme.ACTION_BAR_COLORS
    assert set(colors) == set(Highlight)
    assert colors[Highlight.NONE] == theme.rgb(255, 255, 255, 200)  # white
    assert colors[Highlight.PRESSED] == theme.rgb(255, 249, 196, 220)  # light yellow
    assert colors[Highlight.WRONG] == theme.rgb(255, 205, 210, 220)  # light red


@pytest.mark.parametrize("highlight", [Highlight.PRESSED, Highlight.WRONG])
def test_highlight_colors_are_almost_white(highlight):
    # "#aarrggbb": every channel is light (>= 190 of 255)
    color = theme.ACTION_BAR_COLORS[highlight]
    channels = [int(color[i : i + 2], 16) for i in (3, 5, 7)]
    assert min(channels) >= 190


def test_gold_colors():
    assert theme.GOLD_COLOR not in theme.LANE_COLORS
    assert theme.GOLD_GLOW_BLUR > 0


def test_vibration_is_small_and_short():
    shake = theme.ACTION_BAR_SHAKE
    assert max(abs(offset) for offset in shake) <= 4  # pixels
    assert len(shake) / 60 <= 0.2  # seconds at 60 FPS
    assert shake[-1] == 0  # the bar goes back to its place


def test_button_texts():
    assert theme.BUTTON_TEXTS[GamePage.START] == "Iniciar ASDF Hero"
    assert theme.BUTTON_TEXTS[GamePage.GAME_OVER] == "Falhar novamente"
