"""The logs of the app: frame times, game loop, sessions, pages, language."""

import asyncio
import gc
import logging
from types import SimpleNamespace
from unittest import mock

import pytest

from asdf_hero import app as app_module
from asdf_hero.app import GameApp, app_texts
from asdf_hero.performance import FrameTimes
from tests.app.fakes import FakeClock, FakePage, run_with_clock, tap
from tests.helpers import center


def app_messages(caplog, level=logging.INFO):
    return [
        r.getMessage()
        for r in caplog.records
        if r.name == "asdf_hero.app" and r.levelno >= level
    ]


# --- frame times -------------------------------------------------------------


def test_each_part_of_the_frame_is_timed(game_app):
    # perf_counter: start 0, after the input 1, after the update 3, after render 6
    with mock.patch("asdf_hero.app.time.perf_counter", side_effect=[0.0, 1.0, 3.0, 6.0]):
        game_app.frame()

    times = game_app.frame_times
    assert (times.input, times.update, times.render) == (1.0, 2.0, 3.0)


def test_the_send_and_the_monitor(game_app):
    game_app.monitor = mock.Mock()
    game_app.frame_times = FrameTimes(update=0.001)

    with mock.patch("asdf_hero.app.time.perf_counter", side_effect=[10.0, 10.5]):
        game_app._send(late=0.2)

    times = game_app.frame_times
    assert (times.send, times.late) == (0.5, 0.2)
    game_app.monitor.frame.assert_called_once_with(times, letters=0)


class LateClock(FakeClock):
    """The event loop is busy: every sleep takes 50 ms more."""

    async def sleep(self, delay):
        await super().sleep(delay)
        self.now += 0.05


def test_late_frames_are_measured(page):
    game_app = GameApp(page, fps=20)
    game_app.monitor = mock.Mock()

    run_with_clock(game_app, LateClock(), frames=3)

    lates = [call.args[0].late for call in game_app.monitor.frame.call_args_list]
    assert lates == pytest.approx([0, 0.05, 0.05])


def test_the_game_loop_watches_the_garbage_collector(game_app):
    gc_callbacks = []

    def frame():
        gc_callbacks.append(list(gc.callbacks))

    run_with_clock(game_app, FakeClock(), frames=1, frame=frame)

    assert game_app.monitor.gc.callback in gc_callbacks[0]  # while running
    assert game_app.monitor.gc.callback not in gc.callbacks  # removed at the end


# --- game loop / sessions -----------------------------------------------------


def test_start_and_stop_are_logged(game_app, caplog):
    with caplog.at_level(logging.INFO):
        run_with_clock(game_app, FakeClock(), frames=1)

    started, stopped = app_messages(caplog)
    assert started.startswith("Game started (1 running): platform unknown, page NonexNone")
    assert "game 282x800, scale 1.00, 60 FPS" in started
    assert stopped == "Game stopped (0 running)"
    assert GameApp.running_sessions == 0


def test_platform_and_page_size_in_the_start_log(caplog):
    import flet as ft

    game_app = GameApp(FakePage(390, 844, ft.PagePlatform.ANDROID))
    game_app.build()

    with caplog.at_level(logging.INFO):
        run_with_clock(game_app, FakeClock(), frames=1)

    assert "platform android, page 390x844, game 370x800, scale 1.05" in (
        app_messages(caplog)[0]
    )


def test_two_sessions(caplog):
    first, second = GameApp(FakePage()), GameApp(FakePage())
    first.frame = second.frame = mock.Mock()

    async def scenario():
        tasks = [asyncio.create_task(app.run()) for app in (first, second)]
        await asyncio.sleep(0.05)
        first.stop()
        second.stop()
        await asyncio.gather(*tasks)

    with caplog.at_level(logging.INFO):
        asyncio.run(scenario())

    messages = app_messages(caplog)
    assert messages[1].startswith("Game started (2 running)")
    assert messages[-1] == "Game stopped (0 running)"


@pytest.mark.parametrize(
    "handler, message",
    [
        ("on_connect", "Page connected"),
        ("on_disconnect", "Page disconnected: the game is paused"),
        ("on_close", "Page closed: the game stops"),
    ],
)
def test_lifecycle_is_logged(game_app, caplog, handler, message):
    with caplog.at_level(logging.INFO):
        getattr(game_app, handler)(None)

    assert app_messages(caplog) == [message]


def test_resize_is_logged_in_debug(game_app, caplog):
    game_app.build()

    with caplog.at_level(logging.DEBUG):
        game_app.on_resize(SimpleNamespace(width=390, height=400))

    assert app_messages(caplog, logging.DEBUG) == ["Page resized to 390x400: scale 0.50"]


# --- pages and language --------------------------------------------------------


def test_page_changes_are_logged(game_app, caplog):
    game_app.frame()

    with caplog.at_level(logging.INFO):
        game_app.on_tap_down(tap(*center(game_app.game.button)))
        game_app.frame()
        game_app.frame()  # the same page: no new log

    assert app_messages(caplog) == ["Page: RUNNING (0 points)"]


def test_the_language_is_logged(caplog):
    with caplog.at_level(logging.INFO):
        asyncio.run(app_texts(FakePage(languages=["pt"])))

    assert app_messages(caplog) == ["Language: pt (device / config: pt)"]


def test_the_monitor_reports_with_the_default_period(game_app):
    assert game_app.monitor.report_seconds == app_module.config.PERFORMANCE_REPORT_SECONDS
