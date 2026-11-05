"""Browser tab lifecycle: connect, disconnect (pause) and close (stop)."""

import asyncio
from unittest import mock

from tests.app.fakes import REAL_SLEEP


def test_disconnect_and_connect(game_app):
    game_app.on_disconnect(None)
    assert not game_app.connected.is_set()

    game_app.on_connect(None)
    assert game_app.connected.is_set()


def test_close_stops_the_loop(game_app):
    game_app.running = True
    game_app.on_disconnect(None)

    game_app.on_close(None)

    assert game_app.running is False
    assert game_app.connected.is_set()  # wakes up the loop


def test_paused_while_disconnected(game_app, page):
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
