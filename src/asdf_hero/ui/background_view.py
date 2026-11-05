"""Shows the lanes (game running) and the game over banner."""

import flet as ft

from asdf_hero import config
from asdf_hero.game.states import GamePage
from asdf_hero.ui import theme


class BackgroundView:
    def __init__(self, width: float, height: float) -> None:
        self.lanes = ft.Stack(
            width=width,
            height=height,
            visible=False,
            controls=[
                ft.Container(
                    left=x,
                    top=0,
                    width=config.LANE_LINE_WIDTH,
                    height=height,
                    bgcolor=theme.WHITE,
                    border=ft.Border.all(1, theme.BLACK),
                )
                for x in config.LANE_LINES
            ],
        )
        self.game_over_banner = ft.Stack(
            width=width,
            height=height,
            visible=False,
            controls=[
                ft.Container(
                    left=0, top=200, width=width, height=120, bgcolor=theme.BANNER_COLOR
                ),
                ft.Container(
                    left=0,
                    top=205,
                    width=width,
                    height=65,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        theme.GAME_OVER_TEXT,
                        size=theme.GAME_OVER_FONT_SIZE,
                        color=theme.BLACK,
                        no_wrap=True,
                    ),
                ),
            ],
        )

    def render(self, page: GamePage) -> None:
        self.lanes.visible = page == GamePage.RUNNING
        self.game_over_banner.visible = page == GamePage.GAME_OVER
