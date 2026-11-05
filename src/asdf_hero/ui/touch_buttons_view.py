"""Shows the touch buttons (phone / tablet): one for each lane."""

import flet as ft

from asdf_hero.game.button import Button
from asdf_hero.ui import theme


class TouchButtonsView:
    def __init__(self, buttons: list[Button], width: float, height: float) -> None:
        self.buttons = buttons
        self.controls = [
            ft.Container(
                left=button.x,
                top=button.y,
                width=button.width,
                height=button.height,
                bgcolor=color,
                border_radius=theme.TOUCH_BUTTON_RADIUS,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    size=theme.TOUCH_BUTTON_FONT_SIZE,
                    color=theme.TOUCH_BUTTON_TEXT_COLOR,
                    weight=ft.FontWeight.BOLD,
                ),
            )
            for button, color in zip(buttons, theme.LANE_COLORS)
        ]
        self.control = ft.Stack(
            width=width, height=height, controls=self.controls, visible=False
        )

    def render(self, visible: bool, keys: tuple[str, ...]) -> None:
        self.control.visible = visible
        for button, control, key in zip(self.buttons, self.controls, keys):
            control.content.value = key
            control.opacity = theme.TOUCH_BUTTON_PRESSED_OPACITY if button.clicked else 1.0
