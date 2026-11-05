"""Shows a button (start / retry, hand)."""

import flet as ft

from asdf_hero.game.button import Button
from asdf_hero.ui import theme


class ButtonView:
    def __init__(self, button: Button, font_size: int = theme.BUTTON_FONT_SIZE) -> None:
        self.button = button
        self._label = ft.Text(
            size=font_size, color=theme.BUTTON_TEXT_COLOR, no_wrap=True
        )
        self.control = ft.Container(
            visible=False, alignment=ft.Alignment.CENTER, content=self._label
        )

    def render(self, visible: bool, text: str = "") -> None:
        button, control = self.button, self.control
        control.visible = visible
        control.left = button.x
        control.top = button.y
        control.width = button.width
        control.height = button.height
        control.bgcolor = (
            theme.BUTTON_CLICKED_COLOR if button.clicked else theme.BUTTON_COLOR
        )
        self._label.value = text
