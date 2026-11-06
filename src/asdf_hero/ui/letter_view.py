"""Shows a letter: a colored circle with a glow, a white circle inside, the char."""

import flet as ft

from asdf_hero.game.letter import Letter
from asdf_hero.game.states import LetterStatus
from asdf_hero.ui import theme


def _glow(
    color: str, blur: float = theme.GLOW_BLUR, spread: float = theme.GLOW_SPREAD
) -> ft.BoxShadow:
    return ft.BoxShadow(blur_radius=blur, spread_radius=spread, color=color)


# the same design for every letter, in its color: a big glow for the special
# letters (gold, silver), a small one for the normal letters
LANE_GLOWS = tuple(
    _glow(color, theme.LANE_GLOW_BLUR, theme.LANE_GLOW_SPREAD)
    for color in theme.LANE_GLOW_COLORS
)
GOLD_GLOW = _glow(theme.GOLD_GLOW_COLOR)
SILVER_GLOW = _glow(theme.SILVER_GLOW_COLOR)


class LetterView:
    def __init__(self, letter: Letter) -> None:
        self.letter = letter
        self._stroke = ft.Border.all(1, theme.BLACK)
        self._label = ft.Text(size=theme.LETTER_FONT_SIZE, no_wrap=True)
        self._inner_circle = ft.Container(
            width=letter.size * 0.7,
            height=letter.size * 0.7,
            shape=ft.BoxShape.CIRCLE,
            bgcolor=theme.WHITE,
        )
        # flet controls with the same values are equal (==): the unique key
        # makes sure that two letters are never mixed up
        self.control = ft.Container(
            key=f"letter-{letter.id}",
            width=letter.size,
            height=letter.size,
            shape=ft.BoxShape.CIRCLE,
            alignment=ft.Alignment.CENTER,
            content=ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[self._inner_circle, self._label],
            ),
        )

    def _color_and_glow(self) -> tuple[str, ft.BoxShadow]:
        """Gold letter: gold. Silver letter: silver. Other letters: the lane color."""
        if self.letter.gold:
            return theme.GOLD_COLOR, GOLD_GLOW
        if self.letter.silver:
            return theme.SILVER_COLOR, SILVER_GLOW
        lane = self.letter.lane
        return theme.LANE_COLORS[lane], LANE_GLOWS[lane]

    def render(self) -> None:
        letter, status = self.letter, self.letter.status
        failed = status == LetterStatus.FAILED
        color, glow = self._color_and_glow()

        # (x, y) is the center of the circle
        self.control.left = letter.x - letter.size / 2
        self.control.top = letter.y - letter.size / 2
        self.control.shadow = glow

        # big colored circle (white with a black border when failed)
        self.control.bgcolor = theme.WHITE if failed else color
        self.control.border = self._stroke if failed else None

        # white circle (colored when pressed)
        pressed = status == LetterStatus.WAS_PRESSED
        self._inner_circle.bgcolor = color if pressed else theme.WHITE
        self._inner_circle.border = self._stroke if failed else None

        # char (it can change: silver letter)
        self._label.value = letter.char
        self._label.color = {
            LetterStatus.WAITING: theme.BLACK,
            LetterStatus.NEED_BE_PRESSED: color,
            LetterStatus.WAS_PRESSED: theme.WHITE,
            LetterStatus.FAILED: theme.BLACK,
        }[status]
