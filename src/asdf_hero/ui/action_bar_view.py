"""
Shows the action bar: highlighted (yellow / red) and with a small vibration
after a key press.
"""

import flet as ft

from asdf_hero.game.action_bar import ActionBar
from asdf_hero.ui import theme


class ActionBarView:
    def __init__(self, action_bar: ActionBar, width: float) -> None:
        self.action_bar = action_bar
        self.control = ft.Container(
            left=0,
            top=action_bar.top,
            width=width,
            height=action_bar.height,
            bgcolor=theme.ACTION_BAR_COLORS[action_bar.highlight],
            border=ft.Border.all(1, theme.BLACK),
            visible=False,
        )
        self._seen_presses = action_bar.presses
        self._shake_frame = len(theme.ACTION_BAR_SHAKE)  # not shaking

    def render(self, visible: bool) -> None:
        self.control.visible = visible
        self.control.bgcolor = theme.ACTION_BAR_COLORS[self.action_bar.highlight]

        # a new press starts the vibration (one offset on each frame)
        if self.action_bar.presses != self._seen_presses:
            self._seen_presses = self.action_bar.presses
            self._shake_frame = 0
        offset = 0
        if self._shake_frame < len(theme.ACTION_BAR_SHAKE):
            offset = theme.ACTION_BAR_SHAKE[self._shake_frame]
            self._shake_frame += 1
        self.control.left = offset
