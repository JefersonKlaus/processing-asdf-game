"""Flet app: connects a browser page to a game and runs the game loop."""

import asyncio
import collections
import logging

import flet as ft

from asdf_hero import config
from asdf_hero.game.game import Game
from asdf_hero.ui import theme
from asdf_hero.ui.game_view import GameView

logger = logging.getLogger(__name__)


class GameApp:
    """One Flet page (browser tab) playing one game."""

    def __init__(self, page: ft.Page, fps: int = config.FPS) -> None:
        self.page = page
        self.fps = fps
        self.game = Game()
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

        page.add(
            ft.GestureDetector(
                content=self.view.control,
                mouse_cursor=ft.MouseCursor.CLICK,
                on_tap_down=self.on_tap_down,
                on_tap_up=self.on_tap_up,
            )
        )
        page.on_keyboard_event = self.on_keyboard
        page.on_connect = self.on_connect
        page.on_disconnect = self.on_disconnect
        page.on_close = self.on_close

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
