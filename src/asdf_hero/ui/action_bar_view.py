"""
Shows the action bar: after a key press it is highlighted (yellow / red) and
gets a bit bigger for a moment.
"""

import flet as ft

from asdf_hero.game.action_bar import ActionBar
from asdf_hero.ui import theme
from asdf_hero.ui.press_effect import PressEffect


class ActionBarView:
    def __init__(self, action_bar: ActionBar, width: float) -> None:
        self.action_bar = action_bar
        self._width = width
        self.control = ft.Container(
            left=0,
            top=action_bar.top,
            width=width,
            height=action_bar.height,
            bgcolor=theme.ACTION_BAR_COLORS[action_bar.highlight],
            border=ft.Border.all(1, theme.BLACK),
            visible=False,
        )
        self._press_effect = PressEffect(action_bar.presses)

    def render(self, visible: bool) -> None:
        bar, control = self.action_bar, self.control
        control.visible = visible
        control.bgcolor = theme.ACTION_BAR_COLORS[bar.highlight]

        grow = self._press_effect.grow(bar.presses)
        control.left = -grow
        control.top = bar.top - grow
        control.width = self._width + 2 * grow
        control.height = bar.height + 2 * grow
