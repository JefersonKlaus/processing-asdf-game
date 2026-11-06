"""GameApp.build() and main(): the Flet page of a game."""

import asyncio
from unittest import mock

import flet as ft

from asdf_hero import app as app_module
from asdf_hero.app import GameApp
from asdf_hero.game import Game
from asdf_hero.storage import SqliteResultStore
from tests.app.fakes import FakePage


def test_page_settings(game_app, page):
    game_app.build()

    assert page.title == "ASDF Hero"
    assert page.padding == 0
    assert page.horizontal_alignment == ft.CrossAxisAlignment.CENTER


def test_game_view_inside_a_gesture_detector(game_app, page):
    game_app.build()

    [screen] = page.controls
    [detector] = screen.controls
    assert isinstance(detector, ft.GestureDetector)
    assert detector.content is game_app.view.control
    assert detector.on_tap_down == game_app.on_tap_down
    assert detector.on_tap_up == game_app.on_tap_up


def test_page_events(game_app, page):
    game_app.build()

    assert page.on_keyboard_event == game_app.on_keyboard
    assert page.on_resize == game_app.on_resize
    assert page.on_connect == game_app.on_connect
    assert page.on_disconnect == game_app.on_disconnect
    assert page.on_close == game_app.on_close


def test_each_page_has_its_own_game():
    first, second = GameApp(FakePage()), GameApp(FakePage())

    assert isinstance(first.game, Game)
    assert first.game is not second.game
    assert first.view.game is first.game


def test_all_pages_share_the_best_results():
    first, second = GameApp(FakePage()), GameApp(FakePage())

    assert first.game.scoreboard is second.game.scoreboard
    assert first.game.scoreboard is app_module.shared_scoreboard()


def test_the_best_results_are_saved_in_the_app_database(app_data_dir):
    store = GameApp(FakePage()).game.scoreboard.store

    assert isinstance(store, SqliteResultStore)
    assert store.path == app_data_dir / "asdf_hero.db"


def test_main_builds_and_runs_the_app(page):
    with mock.patch.object(GameApp, "run", new=mock.AsyncMock()) as run:
        asyncio.run(app_module.main(page))

    run.assert_awaited_once()
    assert isinstance(page.controls[0].controls[0], ft.GestureDetector)
