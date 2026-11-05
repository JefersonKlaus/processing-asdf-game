"""Shows a letter: a colored circle, a white circle inside and the char."""

import flet as ft

from asdf_hero.game.letter import Letter
from asdf_hero.game.states import LetterStatus
from asdf_hero.ui import theme


class LetterView:
    def __init__(self, letter: Letter) -> None:
        self.letter = letter
        self._color = theme.GOLD_COLOR if letter.gold else theme.LANE_COLORS[letter.lane]
        self._stroke = ft.Border.all(1, theme.BLACK)
        self._label = ft.Text(
            letter.char, size=theme.LETTER_FONT_SIZE, color=theme.BLACK, no_wrap=True
        )
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
            shadow=(
                ft.BoxShadow(
                    blur_radius=theme.GOLD_GLOW_BLUR,
                    spread_radius=2,
                    color=theme.GOLD_GLOW_COLOR,
                )
                if letter.gold
                else None
            ),
            content=ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[self._inner_circle, self._label],
            ),
        )

    def render(self) -> None:
        letter, status = self.letter, self.letter.status
        failed = status == LetterStatus.FAILED

        # (x, y) is the center of the circle
        self.control.left = letter.x - letter.size / 2
        self.control.top = letter.y - letter.size / 2

        # big colored circle (white with a black border when failed)
        self.control.bgcolor = theme.WHITE if failed else self._color
        self.control.border = self._stroke if failed else None

        # white circle (colored when pressed)
        pressed = status == LetterStatus.WAS_PRESSED
        self._inner_circle.bgcolor = self._color if pressed else theme.WHITE
        self._inner_circle.border = self._stroke if failed else None

        # char
        self._label.color = {
            LetterStatus.WAITING: theme.BLACK,
            LetterStatus.NEED_BE_PRESSED: self._color,
            LetterStatus.WAS_PRESSED: theme.WHITE,
            LetterStatus.FAILED: theme.BLACK,
        }[status]
