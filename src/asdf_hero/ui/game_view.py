"""The whole screen of a game."""

from collections.abc import Callable

import flet as ft

from asdf_hero import config
from asdf_hero.game.game import Game
from asdf_hero.game.states import GamePage
from asdf_hero.ui import theme
from asdf_hero.ui.action_bar_view import ActionBarView
from asdf_hero.ui.background_view import BackgroundView
from asdf_hero.ui.button_view import ButtonView
from asdf_hero.ui.congratulations_view import CongratulationsView
from asdf_hero.ui.letter_view import LetterView
from asdf_hero.ui.scoreboard_view import ScoreboardView
from asdf_hero.ui.texts import PORTUGUESE, Texts
from asdf_hero.ui.touch_buttons_view import TouchButtonsView


class GameView:
    """
    Shows the state of a Game. ``render()`` is called after each frame; it
    only changes control properties, and Flet sends only the real changes to
    the browser.
    """

    def __init__(
        self,
        game: Game,
        texts: Texts = PORTUGUESE,
        on_name_change: Callable[[str], None] = lambda text: None,
        on_name_submit: Callable[[], None] = lambda: None,
    ) -> None:
        self.game = game
        self.texts = texts
        width, height = game.width, game.height

        self.background = BackgroundView(width, height, game.lane_lines, texts)
        self.action_bar = ActionBarView(game.action_bar, width)
        # the letters hide behind the touch buttons: nothing of the letters is
        # drawn below the top of the buttons
        self.letters = ft.Stack(
            width=width, height=config.TOUCH_BUTTONS_TOP, visible=False
        )
        self._letter_views: dict[int, LetterView] = {}
        self.touch_buttons = TouchButtonsView(game.touch_buttons, width, height)
        self.points_bar = ft.Container(
            left=0,
            top=height - theme.POINTS_BAR_HEIGHT,
            width=width,
            height=theme.POINTS_BAR_HEIGHT,
            bgcolor=theme.POINTS_BAR_COLOR,
            padding=ft.Padding.only(left=10),
            alignment=ft.Alignment.CENTER_LEFT,
            content=ft.Text(size=theme.POINTS_FONT_SIZE, color=theme.BLACK),
            visible=False,
        )
        self.game_over_points = ft.Container(
            left=0,
            top=theme.GAME_OVER_POINTS_TOP,
            width=width,
            height=40,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(size=theme.POINTS_FONT_SIZE, color=theme.BLACK),
            visible=False,
        )
        self.scoreboard = ScoreboardView(game.scoreboard, width, texts)
        self.button = ButtonView(game.button)
        self.hand_button = ButtonView(
            game.hand_button,
            font_size=theme.HAND_BUTTON_FONT_SIZE,
            color=theme.HAND_BUTTON_COLOR,
        )
        self.congratulations = CongratulationsView(
            game, texts, on_name_change, on_name_submit
        )

        self.control = ft.Stack(
            width=width,
            height=height,
            controls=[
                ft.Image(
                    src=theme.BACKGROUND_IMAGE,
                    width=width,
                    height=height,
                    fit=ft.BoxFit.FILL,
                ),
                self.background.lanes,
                self.action_bar.control,
                self.background.game_over_banner,
                self.letters,
                self.touch_buttons.control,  # on top of the letters that passed
                self.points_bar,
                self.game_over_points,
                self.scoreboard.control,
                self.button.control,
                self.hand_button.control,
                self.congratulations.control,
            ],
        )

    def render(self) -> None:
        game = self.game
        running = game.page == GamePage.RUNNING
        points = self.texts.points.format(game.points)

        self.background.render(game.page)
        self.action_bar.render(visible=running)
        self._render_letters(visible=running)
        self.touch_buttons.render(visible=running, keys=game.keys)

        self.points_bar.visible = running
        self.points_bar.content.value = points
        self.game_over_points.visible = game.page == GamePage.GAME_OVER
        self.game_over_points.content.value = points
        # start and game over pages: the best results, and the buttons
        start_page = game.page in (GamePage.START, GamePage.GAME_OVER)
        self.scoreboard.render(visible=start_page, last_result=game.last_result)
        self.congratulations.render(
            visible=game.page == GamePage.CONGRATULATIONS, points=game.points
        )

        self.button.render(visible=start_page, text=self.texts.button(game.page))
        self.hand_button.render(
            visible=start_page, text=self.texts.hand_button(game.hand)
        )

    def _render_letters(self, visible: bool) -> None:
        self.letters.visible = visible

        views = []
        # gold letters are drawn on top of the others
        for letter in sorted(self.game.letters, key=lambda letter: letter.gold):
            view = self._letter_views.get(letter.id) or LetterView(letter)
            view.render()
            views.append(view)
        self._letter_views = {view.letter.id: view for view in views}

        # replace the list only when letters were added / removed
        controls = [view.control for view in views]
        current = self.letters.controls
        if len(controls) != len(current) or any(
            new is not old for new, old in zip(controls, current)
        ):
            self.letters.controls = controls
