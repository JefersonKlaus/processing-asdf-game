"""Flet app: connects a browser page to a game and runs the game loop."""

import asyncio
import collections
import logging

import flet as ft

from asdf_hero import config
from asdf_hero.game.game import Game
from asdf_hero.game.scoreboard import Scoreboard
from asdf_hero.ui import theme
from asdf_hero.ui.game_view import GameView

logger = logging.getLogger(__name__)

# best results of all the games (all browser tabs), in memory while the
# server runs
SCOREBOARD = Scoreboard()


class GameApp:
    """One Flet page (browser tab) playing one game."""

    def __init__(
        self, page: ft.Page, fps: int = config.FPS, scoreboard: Scoreboard = SCOREBOARD
    ) -> None:
        self.page = page
        self.fps = fps
        self.game = Game(scoreboard=scoreboard)
        self.view = GameView(self.game)
        # keyboard / mouse events waiting for the game loop
        self.events: collections.deque[tuple] = collections.deque()
        self.running = False
        self.connected = asyncio.Event()
        self.connected.set()

    def build(self) -> None:
        page = self.page
        page.title = theme.PAGE_TITLE
        page.padding = 0
        page.bgcolor = theme.PAGE_BGCOLOR
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.detector = ft.GestureDetector(
            left=0,
            top=0,
            content=self.view.control,
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap_down=self.on_tap_down,
            on_tap_up=self.on_tap_up,
        )
        # the screen: the game scaled to fit the page (phones)
        self.screen = ft.Stack(
            clip_behavior=ft.ClipBehavior.NONE, controls=[self.detector]
        )
        self.fit_to_page(page.width, page.height)
        page.add(self.screen)

        page.on_resize = self.on_resize
        page.on_keyboard_event = self.on_keyboard
        page.on_connect = self.on_connect
        page.on_disconnect = self.on_disconnect
        page.on_close = self.on_close

    # --- screen size -------------------------------------------------------------

    def fit_to_page(self, page_width: float | None, page_height: float | None) -> None:
        """
        Make the game smaller when the page is smaller than the game (phones).
        The game is never bigger than its size. Taps keep the game pixels.
        """
        scale = 1.0
        if page_width and page_height:
            scale = min(1.0, page_width / self.game.width, page_height / self.game.height)
        self.scale = scale
        # the game keeps its size inside, and it is drawn smaller from the top left
        self.detector.scale = ft.Scale(scale, alignment=ft.Alignment.TOP_LEFT)
        self.screen.width = self.game.width * scale
        self.screen.height = self.game.height * scale

    def on_resize(self, e: ft.PageResizeEvent) -> None:
        self.fit_to_page(e.width, e.height)

    # --- input: only queued here, applied by the game loop ----------------------

    def on_keyboard(self, e: ft.KeyboardEvent) -> None:
        ft.context.disable_auto_update()  # the game loop updates the page
        self.events.append(("key", e.key))

    def on_tap_down(self, e: ft.TapEvent) -> None:
        ft.context.disable_auto_update()
        self.events.append(("press", e.local_position.x, e.local_position.y))

    def on_tap_up(self, e: ft.TapEvent) -> None:
        ft.context.disable_auto_update()
        self.events.append(("release",))

    def process_events(self) -> None:
        while self.events:
            event = self.events.popleft()
            if event[0] == "key":
                self.game.key_pressed(event[1])
            elif event[0] == "press":
                self.game.mouse_pressed(event[1], event[2])
            elif event[0] == "release":
                self.game.mouse_released()

    # --- lifecycle -------------------------------------------------------------

    def on_connect(self, e: ft.ControlEvent) -> None:
        self.connected.set()

    def on_disconnect(self, e: ft.ControlEvent) -> None:
        self.connected.clear()  # pause the game while the tab is closed

    def on_close(self, e: ft.ControlEvent) -> None:
        self.stop()

    def stop(self) -> None:
        self.running = False
        self.connected.set()  # wake up the loop so it can finish

    # --- game loop -------------------------------------------------------------

    def frame(self) -> None:
        """One frame of the game loop: input -> update -> render."""
        self.process_events()
        self.game.update()
        self.view.render()

    async def run(self) -> None:
        """Game loop: one frame every 1/FPS seconds."""
        loop = asyncio.get_running_loop()
        frame_time = 1.0 / self.fps
        next_frame = loop.time()
        self.running = True

        while self.running:
            await self.connected.wait()
            await self.page.wait_until_visible()  # pause on hidden tabs
            if not self.running:
                break

            try:
                self.frame()
            except Exception:
                logger.exception("Error in the game frame")
            self.page.update()

            next_frame += frame_time
            delay = next_frame - loop.time()
            if delay < 0:  # late (slow frame): do not try to catch up
                next_frame = loop.time()
                delay = 0
            await asyncio.sleep(delay)


async def main(page: ft.Page) -> None:
    app = GameApp(page)
    app.build()
    await app.run()
