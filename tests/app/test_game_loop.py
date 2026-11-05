"""The game loop: frame order, frame rate, slow frames and errors."""

import asyncio
import logging
from unittest import mock

import pytest

from asdf_hero.app import GameApp
from tests.app.fakes import FakeClock, run_with_clock, stop_after


def test_frame_is_input_update_render(game_app):
    calls = mock.Mock()
    game_app.game, game_app.view = calls.game, calls.view
    game_app.events.append(("key", "A"))

    game_app.frame()

    assert calls.mock_calls == [
        mock.call.game.key_pressed("A"),
        mock.call.game.update(),
        mock.call.view.render(),
    ]


def test_each_frame_updates_the_page(game_app, page):
    game_app.frame = mock.Mock()
    stop_after(game_app, 3)

    asyncio.run(game_app.run())

    assert game_app.frame.call_count == page.updates == page.visible_waits == 3
    assert game_app.running is False


def test_frame_rate(page):
    game_app = GameApp(page, fps=20)  # 0.05s per frame
    clock = FakeClock(frame_cost=0.01)

    run_with_clock(game_app, clock, frames=4)

    assert clock.frame_starts == pytest.approx([0, 0.05, 0.10, 0.15])
    assert clock.sleeps == pytest.approx([0.04] * 4)  # the rest of each frame


def test_late_frames_do_not_try_to_catch_up(page):
    game_app = GameApp(page, fps=20)
    clock = FakeClock(frame_cost=0.2)

    run_with_clock(game_app, clock, frames=3)

    assert clock.sleeps == [0, 0, 0]
    assert clock.frame_starts == pytest.approx([0, 0.2, 0.4])


def test_normal_frame_rate_after_a_slow_frame(page):
    game_app = GameApp(page, fps=20)
    clock = FakeClock()
    durations = iter([0.3, 0.01, 0.01, 0.01])  # first frame is slow

    def frame():
        clock.frame()
        clock.now += next(durations)

    run_with_clock(game_app, clock, frames=4, frame=frame)

    assert clock.frame_starts == pytest.approx([0, 0.3, 0.35, 0.40])


def test_an_error_in_a_frame_is_logged_and_the_game_goes_on(game_app, caplog):
    game_app.frame = mock.Mock(side_effect=[ValueError("boom"), None, None])
    stop_after(game_app, 3)

    with caplog.at_level(logging.ERROR, logger="asdf_hero.app"):
        asyncio.run(game_app.run())

    assert game_app.frame.call_count == 3
    assert "Error in the game frame" in caplog.text
