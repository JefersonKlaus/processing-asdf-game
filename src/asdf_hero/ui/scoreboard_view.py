"""Shows the best results (game over page): position, name, date, time, points."""

import flet as ft

from asdf_hero.game.scoreboard import Result, Scoreboard
from asdf_hero.ui import theme
from asdf_hero.ui.texts import PORTUGUESE, Texts

NAME_COLUMN = 1
POINTS_COLUMN = len(theme.SCOREBOARD_COLUMNS) - 1


class ScoreboardView:
    def __init__(
        self, scoreboard: Scoreboard, width: float, texts: Texts = PORTUGUESE
    ) -> None:
        self.scoreboard = scoreboard
        self.texts = texts
        self.title = ft.Container(
            height=theme.SCOREBOARD_TITLE_HEIGHT,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                texts.scoreboard_title,
                size=theme.SCOREBOARD_FONT_SIZE + 2,
                weight=ft.FontWeight.BOLD,
                color=theme.BLACK,
            ),
        )
        # one row for each result (the rows without a result are hidden)
        self.rows = [self._build_row() for _ in range(scoreboard.size)]
        self.empty = ft.Text(
            texts.scoreboard_empty,
            size=theme.SCOREBOARD_FONT_SIZE,
            color=theme.BLACK,
            visible=False,
        )
        self.control = ft.Container(
            left=0,
            top=theme.SCOREBOARD_TOP,
            width=width,
            visible=False,
            content=ft.Column(
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.title, self.empty, *self.rows],
            ),
        )

    @staticmethod
    def _build_row() -> ft.Row:
        cells = [
            ft.Text(
                width=width,
                size=theme.SCOREBOARD_FONT_SIZE,
                color=theme.BLACK,
                text_align=(
                    ft.TextAlign.RIGHT if index == POINTS_COLUMN else ft.TextAlign.LEFT
                ),
                no_wrap=True,
                overflow=ft.TextOverflow.ELLIPSIS if index == NAME_COLUMN else None,
            )
            for index, width in enumerate(theme.SCOREBOARD_COLUMNS)
        ]
        return ft.Row(
            height=theme.SCOREBOARD_ROW_HEIGHT,
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=cells,
            visible=False,
        )

    def render(self, visible: bool, last_result: Result | None = None) -> None:
        self.control.visible = visible
        best = self.scoreboard.best
        self.empty.visible = not best
        for position, row in enumerate(self.rows, start=1):
            result = best[position - 1] if position <= len(best) else None
            row.visible = result is not None
            if result is None:
                continue
            texts = (
                f"{position}.",
                self.texts.name(result.name),
                result.when.strftime(self.texts.date_format),
                result.when.strftime(self.texts.time_format),
                str(result.points),
            )
            # the result of the last game is in bold
            weight = ft.FontWeight.BOLD if result is last_result else None
            for cell, text in zip(row.controls, texts):
                cell.value = text
                cell.weight = weight
