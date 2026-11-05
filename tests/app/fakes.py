"""Fakes for the Flet app tests (a page and a clock)."""

import asyncio
from types import SimpleNamespace
from unittest import mock

REAL_SLEEP = asyncio.sleep


class FakePage:
    """The parts of ft.Page used by the app."""

    def __init__(self, width=None, height=None):
        self.width = width  # size of the browser page (None: unknown)
        self.height = height
        self.controls = []
        self.updates = 0
        self.visible_waits = 0
        self.on_update = None  # called on each update (tests use it to stop)

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        self.updates += 1
        if self.on_update:
            self.on_update()

    async def wait_until_visible(self):
        self.visible_waits += 1


class FakeClock:
    """
    Fake time for the game loop timing tests.

    Real clocks are different on each OS (on Windows the asyncio clock moves
    in steps of ~15.6 ms and timers can run a bit early), so timing tests with
    the real clock are not reliable. This clock only moves when the game loop
    sleeps or when a frame takes time (``frame_cost``).
    """

    def __init__(self, frame_cost=0.0):
        self.now = 0.0
        self.frame_cost = frame_cost
        self.sleeps = []  # delays passed to asyncio.sleep
        self.frame_starts = []  # clock value at the start of each frame

    def time(self):
        return self.now

    def frame(self):
        self.frame_starts.append(self.now)
        self.now += self.frame_cost

    async def sleep(self, delay):
        self.sleeps.append(delay)
        self.now += delay
        await REAL_SLEEP(0)  # still let other tasks run


def tap(x, y):
    return SimpleNamespace(local_position=SimpleNamespace(x=x, y=y))


def stop_after(game_app, frames):
    """Stop the game loop after some page updates (frames)."""

    def on_update():
        if game_app.page.updates >= frames:
            game_app.stop()

    game_app.page.on_update = on_update


def run_with_clock(game_app, clock, frames, frame=None):
    """Run the game loop for some frames with a FakeClock."""
    game_app.frame = frame or clock.frame
    stop_after(game_app, frames)

    async def scenario():
        asyncio.get_running_loop().time = clock.time
        with mock.patch("asdf_hero.app.asyncio.sleep", clock.sleep):
            await game_app.run()

    asyncio.run(scenario())
