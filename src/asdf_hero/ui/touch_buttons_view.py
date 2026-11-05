"""
Shows the touch buttons (phone / tablet): one for each lane. A button shows a
press effect when it is touched or when its key is pressed on the keyboard.
"""

import flet as ft

from asdf_hero.game.button import Button
from asdf_hero.ui import theme
from asdf_hero.ui.press_effect import PressEffect


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
        self._press_effects = [PressEffect(button.presses) for button in buttons]

    def render(self, visible: bool, keys: tuple[str, ...]) -> None:
        self.control.visible = visible
        for button, control, effect, key in zip(
            self.buttons, self.controls, self._press_effects, keys
        ):
            control.content.value = key
            grow = effect.grow(button.presses)
            control.left = button.x - grow
            control.top = button.y - grow
            control.width = button.width + 2 * grow
            control.height = button.height + 2 * grow
            control.opacity = theme.TOUCH_BUTTON_PRESSED_OPACITY if grow else 1.0
