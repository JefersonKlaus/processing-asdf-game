"""Flet app: connects a browser page to a game and runs the game loop."""

import asyncio
import collections
import dataclasses
import functools
import logging
import math
import time

import flet as ft

from asdf_hero import config, storage
from asdf_hero.game.game import Game
from asdf_hero.game.scoreboard import Scoreboard
from asdf_hero.game.states import GamePage
from asdf_hero.performance import FrameTimes, PerformanceMonitor
from asdf_hero.ui import theme
from asdf_hero.ui.game_view import GameView
from asdf_hero.ui.texts import PORTUGUESE, Texts, texts_for

logger = logging.getLogger(__name__)

# seconds to wait for the language of the device (Flet waits forever)
DEVICE_INFO_TIMEOUT = 3.0


@functools.cache
def shared_scoreboard() -> Scoreboard:
    """
    The best results of all the games (all browser tabs), saved in the
    database. Created on the first game (not on import).
    """
    store = storage.SqliteResultStore(storage.database_path())
    return Scoreboard(store=store)


def is_mobile(page: ft.Page) -> bool:
    """A phone / tablet (the app, or the browser of the phone)."""
    return page.platform is not None and page.platform.is_mobile()


def game_width(page_width: float | None, page_height: float | None) -> float:
    """
    On phones the game is as wide as the screen: the same shape as the page,
    so it fills it without black margins (between WIDTH and MAX_WIDTH).
    """
    if not page_width or not page_height:
        return config.WIDTH
    width = config.HEIGHT * page_width / page_height
    return min(max(width, config.WIDTH), config.MAX_WIDTH)


async def device_language(page: ft.Page) -> str | None:
    """
    The main language of the phone (or of the browser): "pt", "en"... None
    when it is not known.
    """
    try:
        info = await asyncio.wait_for(page.get_device_info(), DEVICE_INFO_TIMEOUT)
    except Exception:  # no answer, old client...: the default language
        logger.warning("Could not read the language of the device", exc_info=True)
        return None
    if info is None or not info.locales:
        return None
    return info.locales[0].language_code


async def app_texts(page: ft.Page) -> Texts:
    """The texts in config.LANGUAGE, or else in the language of the device."""
    language = config.LANGUAGE or await device_language(page)
    texts = texts_for(language)
    logger.info("Language: %s (device / config: %s)", texts.language, language)
    return texts


class GameApp:
    """One Flet page (browser tab) playing one game."""

    running_sessions = 0  # game loops running now (browser tabs on the web server)

    def __init__(
        self,
        page: ft.Page,
        fps: int = config.FPS,
        scoreboard: Scoreboard | None = None,
        texts: Texts = PORTUGUESE,
    ) -> None:
        self.page = page
        self.fps = fps
        self.mobile = is_mobile(page)
        width = game_width(page.width, page.height) if self.mobile else config.WIDTH
        self.game = Game(width=width, scoreboard=scoreboard or shared_scoreboard())
        self.view = GameView(
            self.game,
            texts=texts,
            on_name_change=self.on_name_change,
            on_name_submit=self.on_name_submit,
        )
        # keyboard / mouse events waiting for the game loop
        self.events: collections.deque[tuple] = collections.deque()
        # performance logs: the time of each part of the last frame
        self.monitor = PerformanceMonitor()
        self.scale = 1.0  # set by fit_to_page()
        self.frame_times = FrameTimes()
        self._last_page = self.game.page
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
        Scale the game to fit the page. On a computer the game is only made
        smaller (never bigger than its size); on a phone it also gets bigger,
        to fill the screen. Taps keep the game pixels.
        """
        scale = 1.0
        if page_width and page_height:
            max_scale = math.inf if self.mobile else 1.0
            scale = min(
                max_scale, page_width / self.game.width, page_height / self.game.height
            )
        self.scale = scale
        # the game keeps its size inside, and it is drawn smaller from the top left
        self.detector.scale = ft.Scale(scale, alignment=ft.Alignment.TOP_LEFT)
        self.screen.width = self.game.width * scale
        self.screen.height = self.game.height * scale

    def on_resize(self, e: ft.PageResizeEvent) -> None:
        self.fit_to_page(e.width, e.height)
        logger.debug("Page resized to %sx%s: scale %.2f", e.width, e.height, self.scale)

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

    def on_name_change(self, text: str) -> None:
        ft.context.disable_auto_update()
        self.events.append(("name", text))

    def on_name_submit(self) -> None:
        ft.context.disable_auto_update()
        self.events.append(("save_name",))

    def process_events(self) -> None:
        while self.events:
            event = self.events.popleft()
            if event[0] == "key":
                self.game.key_pressed(event[1])
            elif event[0] == "press":
                self.game.mouse_pressed(event[1], event[2])
            elif event[0] == "release":
                self.game.mouse_released()
            elif event[0] == "name":
                self.game.type_name(event[1])
            elif event[0] == "save_name":
                self.game.save_name()

    # --- lifecycle -------------------------------------------------------------

    def on_connect(self, e: ft.ControlEvent) -> None:
        logger.info("Page connected")
        self.connected.set()

    def on_disconnect(self, e: ft.ControlEvent) -> None:
        logger.info("Page disconnected: the game is paused")
        self.connected.clear()  # pause the game while the tab is closed

    def on_close(self, e: ft.ControlEvent) -> None:
        logger.info("Page closed: the game stops")
        self.stop()

    def stop(self) -> None:
        self.running = False
        self.connected.set()  # wake up the loop so it can finish

    # --- game loop -------------------------------------------------------------

    def frame(self) -> None:
        """One frame of the game loop: input -> update -> render (timed)."""
        clock = time.perf_counter
        started = clock()
        self.process_events()
        after_input = clock()
        self.game.update()
        after_update = clock()
        self.view.render()
        self.frame_times = FrameTimes(
            input=after_input - started,
            update=after_update - after_input,
            render=clock() - after_update,
        )
        self._log_page_change()

    def _log_page_change(self) -> None:
        page = self.game.page
        if page != self._last_page:
            name = page.name if isinstance(page, GamePage) else page
            logger.info("Page: %s (%s points)", name, self.game.points)
            self._last_page = page

    async def run(self) -> None:
        """Game loop: one frame every 1/FPS seconds."""
        loop = asyncio.get_running_loop()
        frame_time = 1.0 / self.fps
        next_frame = loop.time()
        late = 0.0  # how late the frame starts (the sleep took longer)
        self.running = True
        GameApp.running_sessions += 1
        self._log_start()
        self.monitor.start()
        try:
            while self.running:
                await self.connected.wait()
                await self.page.wait_until_visible()  # pause on hidden tabs
                if not self.running:
                    break

                try:
                    self.frame()
                except Exception:
                    logger.exception("Error in the game frame")
                self._send(late)

                next_frame += frame_time
                delay = next_frame - loop.time()
                if delay < 0:  # late (slow frame): do not try to catch up
                    next_frame = loop.time()
                    delay = 0
                before_sleep = loop.time()
                await asyncio.sleep(delay)
                late = max(0.0, loop.time() - before_sleep - delay)
        finally:
            self.monitor.stop()
            GameApp.running_sessions -= 1
            logger.info("Game stopped (%d running)", GameApp.running_sessions)

    def _send(self, late: float) -> None:
        """page.update() (the changes go to the screen), timed for the logs."""
        started = time.perf_counter()
        self.page.update()
        # a new record for each frame (the monitor may keep the old ones)
        self.frame_times = dataclasses.replace(
            self.frame_times, send=time.perf_counter() - started, late=late
        )
        self.monitor.frame(self.frame_times, letters=len(self.game.letters))

    def _log_start(self) -> None:
        page = self.page
        logger.info(
            "Game started (%d running): platform %s, page %sx%s, game %.0fx%.0f, "
            "scale %.2f, %d FPS",
            GameApp.running_sessions,
            page.platform.value if page.platform else "unknown",
            page.width,
            page.height,
            self.game.width,
            self.game.height,
            self.scale,
            self.fps,
        )


async def main(page: ft.Page) -> None:
    app = GameApp(page, texts=await app_texts(page))
    app.build()
    await app.run()
