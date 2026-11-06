"""The congratulations page in the app: name events, save, the database."""

from types import SimpleNamespace
from unittest import mock

from asdf_hero.app import GameApp, shared_scoreboard
from asdf_hero.game import Game, GamePage
from tests.app.fakes import FakePage, tap
from tests.helpers import GAME_OVER_FRAMES, center


def lose(game_app, points):
    game = game_app.game
    game.start_new_game()
    game.points = points
    game_app.on_keyboard(SimpleNamespace(key="A"))  # wrong moment
    for _ in range(GAME_OVER_FRAMES + 1):
        game_app.frame()


def type_name(game_app, text):
    field = game_app.view.congratulations.field
    field.value = text
    field.on_change(SimpleNamespace(control=field))


def click(game_app, button):
    game_app.on_tap_down(tap(*center(button)))
    game_app.on_tap_up(tap(*center(button)))
    game_app.frame()


def test_name_events_are_only_queued(game_app, auto_update):
    game_app.game = mock.Mock(spec=Game)

    game_app.on_name_change("Ana")
    game_app.on_name_submit()

    assert list(game_app.events) == [("name", "Ana"), ("save_name",)]
    assert game_app.game.mock_calls == []  # the game is not changed here
    assert auto_update.call_count == 2


def test_the_game_loop_applies_the_name_events(game_app):
    game_app.game = mock.Mock(spec=Game)
    game_app.events.extend([("name", "Ana"), ("save_name",)])

    game_app.process_events()

    assert game_app.game.mock_calls == [mock.call.type_name("Ana"), mock.call.save_name()]


def test_a_best_result_shows_the_congratulations_page(game_app):
    lose(game_app, 42)

    assert game_app.game.page == GamePage.CONGRATULATIONS
    assert game_app.view.congratulations.control.visible is True
    assert game_app.view.congratulations.field.value == ""


def test_type_the_name_and_save(game_app):
    lose(game_app, 42)

    type_name(game_app, "Ana")
    click(game_app, game_app.game.save_button)

    game = game_app.game
    assert game.page == GamePage.GAME_OVER
    assert game.last_result.name == "Ana"
    first_row = game_app.view.scoreboard.rows[0]
    assert [cell.value for cell in first_row.controls][1::3] == ["Ana", "42"]


def test_enter_saves(game_app):
    lose(game_app, 42)
    field = game_app.view.congratulations.field
    field.value = "Bia"

    field.on_submit(SimpleNamespace(control=field))
    game_app.frame()

    assert game_app.game.last_result.name == "Bia"


def test_save_as_anonymous(game_app):
    lose(game_app, 42)
    type_name(game_app, "Ana")

    click(game_app, game_app.game.anonymous_button)

    assert game_app.game.last_result.name == ""
    first_row = game_app.view.scoreboard.rows[0]
    assert first_row.controls[1].value == "Anônimo"
    assert game_app.view.congratulations.control.visible is False


def test_the_results_are_kept_when_the_app_opens_again(app_data_dir):
    # the app uses the database of the phone (FLET_APP_STORAGE_DATA)
    game_app = GameApp(FakePage())
    lose(game_app, 42)
    type_name(game_app, "Ana")
    click(game_app, game_app.game.save_button)

    shared_scoreboard.cache_clear()  # the app is closed and opened again
    best = GameApp(FakePage()).game.scoreboard.best

    assert [(r.name, r.points) for r in best] == [("Ana", 42)]
    assert (app_data_dir / "asdf_hero.db").is_file()


def test_the_home_screen_shows_the_saved_best_results(app_data_dir):
    game_app = GameApp(FakePage())
    lose(game_app, 42)
    type_name(game_app, "Ana")
    click(game_app, game_app.game.save_button)

    shared_scoreboard.cache_clear()  # the app is opened again: home screen
    home = GameApp(FakePage())
    home.frame()

    assert home.game.page == GamePage.START
    assert home.view.scoreboard.control.visible is True
    first_row = home.view.scoreboard.rows[0]
    assert [cell.value for cell in first_row.controls][1::3] == ["Ana", "42"]


def test_zero_points_in_the_app_go_to_game_over(game_app):
    lose(game_app, 0)

    assert game_app.game.page == GamePage.GAME_OVER
    assert game_app.view.congratulations.control.visible is False
