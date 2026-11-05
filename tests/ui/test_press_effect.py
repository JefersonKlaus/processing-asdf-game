"""PressEffect: bigger for some frames after each press, then normal again."""

from asdf_hero.ui import theme
from asdf_hero.ui.press_effect import PressEffect

GROW, FRAMES = theme.PRESS_EFFECT_GROW, theme.PRESS_EFFECT_FRAMES


def grows(effect, presses, frames):
    return [effect.grow(presses) for _ in range(frames)]


def test_no_effect_without_press():
    assert grows(PressEffect(), 0, 3) == [0, 0, 0]


def test_bigger_for_some_frames_then_normal():
    assert grows(PressEffect(), 1, FRAMES + 2) == [GROW] * FRAMES + [0, 0]


def test_a_new_press_starts_again():
    effect = PressEffect()
    grows(effect, 1, FRAMES - 1)

    assert grows(effect, 2, FRAMES + 1) == [GROW] * FRAMES + [0]


def test_starts_from_the_current_count():
    # a view created after some presses does not show an old press
    assert grows(PressEffect(presses=5), 5, 3) == [0, 0, 0]


def test_effect_is_2px_and_short():
    assert GROW == 2  # pixels on each side
    assert 0 < FRAMES / 60 <= 0.2  # seconds at 60 FPS
