"""
Shows a button: the design of the touch buttons (rounded corners, bold white
text) in the color of its action (darker when pressed).
"""

import flet as ft

from asdf_hero.game.button import Button
from asdf_hero.ui import theme


class ButtonView:
    def __init__(
        self,
        button: Button,
        font_size: int = theme.BUTTON_FONT_SIZE,
        color: str = theme.START_BUTTON_COLOR,
    ) -> None:
        self.button = button
        self.color = color
        self._label = ft.Text(
            size=font_size,
            color=theme.BUTTON_TEXT_COLOR,
            weight=ft.FontWeight.BOLD,
            no_wrap=True,
        )
        self.control = ft.Container(
            visible=False,
            alignment=ft.Alignment.CENTER,
            border_radius=theme.BUTTON_RADIUS,
            content=self._label,
        )

    def render(self, visible: bool, text: str = "") -> None:
        button, control = self.button, self.control
        control.visible = visible
        control.left = button.x
        control.top = button.y
        control.width = button.width
        control.height = button.height
        control.bgcolor = theme.darker(self.color) if button.clicked else self.color
        self._label.value = text
