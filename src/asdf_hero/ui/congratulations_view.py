"""The congratulations page: a new best result, the name field, save buttons."""

from collections.abc import Callable

import flet as ft

from asdf_hero import config
from asdf_hero.game.game import Game
from asdf_hero.ui import theme
from asdf_hero.ui.button_view import ButtonView
from asdf_hero.ui.texts import Texts


def _centered_text(
    top: float, width: float, size: int, value: str = "", bold: bool = False
) -> ft.Container:
    return ft.Container(
        left=0,
        top=top,
        width=width,
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.symmetric(horizontal=theme.NAME_FIELD_MARGIN),
        content=ft.Text(
            value,
            size=size,
            color=theme.BLACK,
            weight=ft.FontWeight.BOLD if bold else None,
            text_align=ft.TextAlign.CENTER,
        ),
    )


class CongratulationsView:
    """
    Shows the congratulations page. The name field sends each change to
    ``on_name_change(text)`` and Enter to ``on_name_submit()``; the buttons
    are game buttons (the game handles their clicks).
    """

    def __init__(
        self,
        game: Game,
        texts: Texts,
        on_name_change: Callable[[str], None],
        on_name_submit: Callable[[], None],
    ) -> None:
        width = game.width
        self.texts = texts
        self.on_name_change = on_name_change
        self.on_name_submit = on_name_submit
        self.field: ft.TextField | None = None  # a new one each time

        self.banner = ft.Container(
            left=0,
            top=theme.CONGRATULATIONS_BANNER_TOP,
            width=width,
            height=theme.CONGRATULATIONS_BANNER_HEIGHT,
            bgcolor=theme.BANNER_COLOR,
        )
        self.title = _centered_text(
            theme.CONGRATULATIONS_TITLE_TOP,
            width,
            theme.CONGRATULATIONS_TITLE_FONT_SIZE,
            texts.congratulations_title,
            bold=True,  # like "GAME OVER" and "ASDF HERO"
        )
        self.subtitle = _centered_text(
            theme.CONGRATULATIONS_SUBTITLE_TOP,
            width,
            theme.CONGRATULATIONS_SUBTITLE_FONT_SIZE,
            texts.congratulations_subtitle,
        )
        self.text = _centered_text(
            theme.CONGRATULATIONS_TEXT_TOP, width, theme.CONGRATULATIONS_TEXT_FONT_SIZE
        )
        self.field_box = ft.Container(
            left=theme.NAME_FIELD_MARGIN,
            top=theme.NAME_FIELD_TOP,
            width=width - 2 * theme.NAME_FIELD_MARGIN,
        )
        self.save_button = ButtonView(
            game.save_button, font_size=theme.CONGRATULATIONS_BUTTON_FONT_SIZE
        )
        self.anonymous_button = ButtonView(
            game.anonymous_button,
            font_size=theme.CONGRATULATIONS_BUTTON_FONT_SIZE,
            color=theme.ANONYMOUS_BUTTON_COLOR,  # blue
        )
        self.control = ft.Stack(
            width=width,
            height=game.height,
            visible=False,
            controls=[
                self.banner,
                self.title,
                self.subtitle,
                self.text,
                self.field_box,
                self.save_button.control,
                self.anonymous_button.control,
            ],
        )

    def render(self, visible: bool, points: int) -> None:
        self.control.visible = visible
        if visible and self.field is None:
            # new empty field for each new best result: it gets the focus
            # (the keyboard of the phone opens)
            self.field = self._new_field()
        elif not visible:
            self.field = None
        self.field_box.content = self.field
        self.text.content.value = self.texts.congratulations_text.format(
            points, config.SCOREBOARD_SIZE
        )
        self.save_button.render(visible=visible, text=self.texts.save_button)
        self.anonymous_button.render(visible=visible, text=self.texts.anonymous_button)

    def _new_field(self) -> ft.TextField:
        return ft.TextField(
            label=self.texts.name_label,
            max_length=config.NAME_MAX_LENGTH,
            autofocus=True,
            capitalization=ft.TextCapitalization.WORDS,
            text_size=theme.NAME_FIELD_FONT_SIZE,
            bgcolor=theme.NAME_FIELD_COLOR,
            color=theme.BLACK,
            on_change=self._changed,
            on_submit=self._submitted,
        )

    def _changed(self, e: ft.ControlEvent) -> None:
        self.on_name_change(e.control.value or "")

    def _submitted(self, e: ft.ControlEvent) -> None:
        self.on_name_change(e.control.value or "")  # the last text, then save
        self.on_name_submit()
