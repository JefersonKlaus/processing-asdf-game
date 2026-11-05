"""Press effect: a control gets bigger for some frames after each press."""

from asdf_hero.ui import theme


class PressEffect:
    """
    Follows a press counter (``ActionBar.presses``, ``Button.presses``): each
    new press starts the effect. It counts real frames (renders), so it also
    works during the slow motion of the game over.
    """

    def __init__(self, presses: int = 0) -> None:
        self._seen_presses = presses
        self._frames_left = 0

    def grow(self, presses: int) -> int:
        """Pixels to grow on each side in this frame (0: normal size)."""
        if presses != self._seen_presses:
            self._seen_presses = presses
            self._frames_left = theme.PRESS_EFFECT_FRAMES
        if self._frames_left > 0:
            self._frames_left -= 1
            return theme.PRESS_EFFECT_GROW
        return 0
