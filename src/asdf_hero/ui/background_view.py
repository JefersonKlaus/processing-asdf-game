"""Shows the lanes (game running) and the banner (start and game over pages)."""

import flet as ft

from asdf_hero import config
from asdf_hero.game.states import GamePage
from asdf_hero.ui import theme
from asdf_hero.ui.texts import PORTUGUESE, Texts


class BackgroundView:
    def __init__(
        self,
        width: float,
        height: float,
        lane_lines: tuple[float, ...] = config.LANE_LINES,
        texts: Texts = PORTUGUESE,
    ) -> None:
        self.texts = texts
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
                for x in lane_lines
            ],
        )
        self.banner_text = ft.Text(
            texts.game_over,
            size=theme.GAME_OVER_FONT_SIZE,
            color=theme.BLACK,
            weight=ft.FontWeight.BOLD,  # "GAME OVER" (and "ASDF HERO")
            no_wrap=True,
        )
        self.game_over_banner = ft.Stack(
            width=width,
            height=height,
            visible=False,
            controls=[
                ft.Container(
                    left=0,
                    top=theme.GAME_OVER_BANNER_TOP,
                    width=width,
                    height=theme.GAME_OVER_BANNER_HEIGHT,
                    bgcolor=theme.BANNER_COLOR,
                ),
                ft.Container(
                    left=0,
                    top=theme.GAME_OVER_TEXT_TOP,
                    width=width,
                    height=65,
                    alignment=ft.Alignment.CENTER,
                    content=self.banner_text,
                ),
            ],
        )

    def render(self, page: GamePage) -> None:
        self.lanes.visible = page == GamePage.RUNNING
        # the same banner: "ASDF HERO" (start page, black) or "GAME OVER" (red)
        self.game_over_banner.visible = page in (GamePage.START, GamePage.GAME_OVER)
        start = page == GamePage.START
        self.banner_text.value = self.texts.home_title if start else self.texts.game_over
        self.banner_text.color = theme.BLACK if start else theme.GAME_OVER_COLOR
