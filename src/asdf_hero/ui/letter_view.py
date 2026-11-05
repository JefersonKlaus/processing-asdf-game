"""Shows a letter: a colored circle, a white circle inside and the char."""

import flet as ft

from asdf_hero.game.letter import Letter
from asdf_hero.game.states import LetterStatus
from asdf_hero.ui import theme

GOLD_GLOW = ft.BoxShadow(
    blur_radius=theme.GLOW_BLUR, spread_radius=2, color=theme.GOLD_GLOW_COLOR
)
SILVER_GLOW = ft.BoxShadow(
    blur_radius=theme.GLOW_BLUR, spread_radius=2, color=theme.SILVER_GLOW_COLOR
)


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
            key="letter-%d" % letter.id,
            width=letter.size,
            height=letter.size,
            shape=ft.BoxShape.CIRCLE,
            alignment=ft.Alignment.CENTER,
            content=ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[self._inner_circle, self._label],
            ),
        )

    def _color_and_glow(self) -> tuple[str, ft.BoxShadow | None]:
        """Gold letter: gold. Swapped letter: silver. Other letters: the lane color."""
        if self.letter.gold:
            return theme.GOLD_COLOR, GOLD_GLOW
        if self.letter.swapped:
            return theme.SILVER_COLOR, SILVER_GLOW
        return theme.LANE_COLORS[self.letter.lane], None

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

        # char (it can change: swap challenge)
        self._label.value = letter.char
        self._label.color = {
            LetterStatus.WAITING: theme.BLACK,
            LetterStatus.NEED_BE_PRESSED: color,
            LetterStatus.WAS_PRESSED: theme.WHITE,
            LetterStatus.FAILED: theme.BLACK,
        }[status]
