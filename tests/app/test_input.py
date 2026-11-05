"""Input: Flet events are queued, the game loop applies them."""

from types import SimpleNamespace
from unittest import mock

import pytest

from asdf_hero.game import Game, GamePage
from tests.app.fakes import tap
from tests.helpers import center


@pytest.mark.parametrize(
    "handler, event, queued",
    [
        ("on_keyboard", SimpleNamespace(key="A"), ("key", "A")),
        ("on_tap_down", tap(120, 380), ("press", 120, 380)),
        ("on_tap_up", tap(1, 2), ("release",)),
    ],
)
def test_events_are_only_queued(game_app, auto_update, handler, event, queued):
    game_app.game = mock.Mock(spec=Game)

    getattr(game_app, handler)(event)

    assert list(game_app.events) == [queued]
    assert game_app.game.mock_calls == []  # the game is not changed here
    auto_update.assert_called_once_with()  # the game loop updates the page


def test_events_are_applied_in_order(game_app):
    game_app.game = mock.Mock(spec=Game)
    game_app.events.extend([("key", "A"), ("press", 1, 2), ("release",), ("scroll",)])

    game_app.process_events()

    assert game_app.game.mock_calls == [
        mock.call.key_pressed("A"),
        mock.call.mouse_pressed(1, 2),
        mock.call.mouse_released(),
    ]  # unknown events are ignored
    assert not game_app.events


def test_click_on_the_start_button_starts_the_game(game_app):
    game_app.frame()
    game_app.on_tap_down(tap(*center(game_app.game.button)))
    game_app.on_tap_up(tap(*center(game_app.game.button)))

    game_app.frame()

    assert game_app.game.page == GamePage.RUNNING
    assert len(game_app.game.letters) == 1
