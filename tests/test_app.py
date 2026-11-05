"""Tests for the Flet app (game loop and input), with a fake Flet page."""

import asyncio
import logging
from types import SimpleNamespace
from unittest import mock

import flet as ft
import pytest

from asdf_hero import app as app_module
from asdf_hero.app import GameApp
from asdf_hero.game import Game, GamePage
from asdf_hero.ui import GameView

REAL_SLEEP = asyncio.sleep


class FakePage:
    """The parts of ft.Page used by the app."""

    def __init__(self):
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


@pytest.fixture(autouse=True)
def auto_update():
    """ft.context only works inside a Flet session: replace it."""
    with mock.patch.object(ft.context, "disable_auto_update") as disable:
        yield disable


@pytest.fixture
def page():
    return FakePage()


@pytest.fixture
def game_app(page):
    return GameApp(page)


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


class TestBuild:
    def test_page_settings(self, game_app, page):
        game_app.build()

        assert page.title == "ASDF Hero"
        assert page.padding == 0
        assert page.horizontal_alignment == ft.CrossAxisAlignment.CENTER
        assert page.vertical_alignment == ft.MainAxisAlignment.CENTER

    def test_game_view_inside_a_gesture_detector(self, game_app, page):
        game_app.build()

        [detector] = page.controls
        assert isinstance(detector, ft.GestureDetector)
        assert detector.content is game_app.view.control

    def test_handlers(self, game_app, page):
        game_app.build()

        detector = page.controls[0]
        assert detector.on_tap_down == game_app.on_tap_down
        assert detector.on_tap_up == game_app.on_tap_up
        assert page.on_keyboard_event == game_app.on_keyboard
        assert page.on_connect == game_app.on_connect
        assert page.on_disconnect == game_app.on_disconnect
        assert page.on_close == game_app.on_close

    def test_each_page_has_its_own_game(self):
        first, second = GameApp(FakePage()), GameApp(FakePage())

        assert isinstance(first.game, Game)
        assert isinstance(first.view, GameView)
        assert first.game is not second.game
        assert first.view.game is first.game


class TestInput:
    """Flet events are only queued; the game loop applies them."""

    def test_keyboard_is_queued(self, game_app, auto_update):
        game_app.on_keyboard(SimpleNamespace(key="A"))

        assert list(game_app.events) == [("key", "A")]
        auto_update.assert_called_once_with()

    def test_tap_down_is_queued(self, game_app, auto_update):
        game_app.on_tap_down(tap(120, 380))

        assert list(game_app.events) == [("press", 120, 380)]
        auto_update.assert_called_once_with()

    def test_tap_up_is_queued(self, game_app, auto_update):
        game_app.on_tap_up(tap(1, 2))

        assert list(game_app.events) == [("release",)]
        auto_update.assert_called_once_with()

    def test_events_do_not_change_the_game(self, game_app):
        game_app.game = mock.Mock(spec=Game)

        game_app.on_keyboard(SimpleNamespace(key="A"))
        game_app.on_tap_down(tap(1, 2))
        game_app.on_tap_up(tap(1, 2))

        assert game_app.game.mock_calls == []


class TestProcessEvents:
    @pytest.fixture
    def game(self, game_app):
        game_app.game = mock.Mock(spec=Game)
        return game_app.game

    def test_events_are_applied_in_order_and_removed(self, game_app, game):
        game_app.events.extend(
            [("key", "A"), ("press", 1, 2), ("release",), ("key", "s")]
        )

        game_app.process_events()

        assert game.mock_calls == [
            mock.call.key_pressed("A"),
            mock.call.mouse_pressed(1, 2),
            mock.call.mouse_released(),
            mock.call.key_pressed("s"),
        ]
        assert not game_app.events

    def test_unknown_event_is_ignored(self, game_app, game):
        game_app.events.append(("scroll",))

        game_app.process_events()

        assert game.mock_calls == []


class TestFrame:
    def test_input_update_render(self, game_app):
        calls = mock.Mock()
        game_app.game = calls.game
        game_app.view = calls.view
        game_app.events.append(("key", "A"))

        game_app.frame()

        assert calls.mock_calls == [
            mock.call.game.key_pressed("A"),
            mock.call.game.update(),
            mock.call.view.render(),
        ]

    def test_click_on_the_start_button_starts_the_game(self, game_app):
        game_app.frame()
        button = game_app.game.button
        game_app.on_tap_down(tap(button.x + 10, button.y + 10))
        game_app.on_tap_up(tap(button.x + 10, button.y + 10))

        game_app.frame()

        assert game_app.game.page == GamePage.RUNNING
        assert game_app.view.letters.visible is True
        assert len(game_app.game.letters) == 1


class TestLifecycle:
    def test_disconnect_and_connect(self, game_app):
        game_app.on_disconnect(None)
        assert not game_app.connected.is_set()

        game_app.on_connect(None)
        assert game_app.connected.is_set()

    def test_close_stops_the_loop(self, game_app):
        game_app.running = True
        game_app.on_disconnect(None)

        game_app.on_close(None)

        assert game_app.running is False
        assert game_app.connected.is_set()  # wakes up the loop


class TestRun:
    def test_runs_frames_and_updates_the_page(self, game_app, page):
        game_app.frame = mock.Mock()
        stop_after(game_app, 3)

        asyncio.run(game_app.run())

        assert game_app.frame.call_count == 3
        assert page.updates == 3
        assert page.visible_waits == 3
        assert game_app.running is False

    def test_runs_at_the_frame_rate(self, page):
        game_app = GameApp(page, fps=20)  # 0.05s per frame
        clock = FakeClock(frame_cost=0.01)

        run_with_clock(game_app, clock, frames=4)

        assert clock.frame_starts == pytest.approx([0, 0.05, 0.10, 0.15])
        assert clock.sleeps == pytest.approx([0.04, 0.04, 0.04, 0.04])

    def test_fast_frames_keep_the_frame_rate(self, page):
        game_app = GameApp(page, fps=60)
        clock = FakeClock()

        run_with_clock(game_app, clock, frames=60)

        assert clock.now == pytest.approx(1.0)  # 60 frames in 1 second

    def test_late_frames_do_not_try_to_catch_up(self, page):
        game_app = GameApp(page, fps=20)
        clock = FakeClock(frame_cost=0.2)

        run_with_clock(game_app, clock, frames=3)

        assert clock.sleeps == [0, 0, 0]
        assert clock.frame_starts == pytest.approx([0, 0.2, 0.4])

    def test_after_a_slow_frame_the_frame_rate_is_back(self, page):
        game_app = GameApp(page, fps=20)
        clock = FakeClock()
        durations = iter([0.3, 0.01, 0.01, 0.01])  # first frame is slow

        def frame():
            clock.frame()
            clock.now += next(durations)

        run_with_clock(game_app, clock, frames=4, frame=frame)

        assert clock.frame_starts == pytest.approx([0, 0.3, 0.35, 0.40])

    def test_an_error_in_a_frame_is_logged_and_the_game_goes_on(
        self, game_app, page, caplog
    ):
        game_app.frame = mock.Mock(side_effect=[ValueError("boom"), None, None])
        stop_after(game_app, 3)

        with caplog.at_level(logging.ERROR, logger="asdf_hero.app"):
            asyncio.run(game_app.run())

        assert game_app.frame.call_count == 3
        assert "Error in the game frame" in caplog.text
        assert "boom" in caplog.text

    def test_paused_while_disconnected(self, game_app, page):
        game_app.frame = mock.Mock()

        async def scenario():
            game_app.on_disconnect(None)
            loop_task = asyncio.ensure_future(game_app.run())
            await REAL_SLEEP(0.05)
            frames_while_disconnected = game_app.frame.call_count
            game_app.on_close(None)
            await loop_task
            return frames_while_disconnected

        assert asyncio.run(scenario()) == 0
        assert page.updates == 0

    def test_real_game_frames(self, game_app):
        game_app.build()
        stop_after(game_app, 2)

        asyncio.run(game_app.run())

        assert game_app.view.button.control.visible is True


def test_main_builds_and_runs_the_app(page):
    with mock.patch.object(GameApp, "run", new=mock.AsyncMock()) as run:
        asyncio.run(app_module.main(page))

    run.assert_awaited_once()
    assert isinstance(page.controls[0], ft.GestureDetector)
