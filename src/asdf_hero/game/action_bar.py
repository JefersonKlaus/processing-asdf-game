"""The action bar: the area where the letters must be pressed."""

from asdf_hero import config
from asdf_hero.game.states import Highlight


class ActionBar:
    def __init__(
        self,
        top: float = config.ACTION_BAR_TOP,
        height: float = config.ACTION_BAR_HEIGHT,
        highlight_frames: int = config.HIGHLIGHT_FRAMES,
    ) -> None:
        self.top = top
        self.height = height
        self.highlight = Highlight.NONE
        self.presses = 0  # number of presses (the view shakes the bar on each one)
        self._highlight_frames = highlight_frames
        self._frames_left = 0

    @property
    def bottom(self) -> float:
        return self.top + self.height

    def contains(self, y: float) -> bool:
        return self.top <= y <= self.bottom

    def touches(self, y: float, size: float) -> bool:
        """True when a circle of this size, centered at y, touches the bar."""
        radius = size / 2
        return self.top - radius <= y <= self.bottom + radius

    def press(self, correct: bool) -> None:
        """A game key was pressed: highlight the bar for some frames."""
        self.highlight = Highlight.PRESSED if correct else Highlight.WRONG
        self._frames_left = self._highlight_frames
        self.presses += 1

    def update(self) -> None:
        """One game step: the highlight ends after its frames."""
        if self._frames_left > 0:
            self._frames_left -= 1
            if self._frames_left == 0:
                self.highlight = Highlight.NONE

    def reset(self) -> None:
        self.highlight = Highlight.NONE
        self._frames_left = 0
