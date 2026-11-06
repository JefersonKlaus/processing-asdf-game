"""SqliteResultStore: the best results in a SQLite file (web server and app)."""

import logging
import sqlite3
from contextlib import closing
from datetime import datetime

import pytest

from asdf_hero import storage
from asdf_hero.game import Result, Scoreboard
from asdf_hero.storage import SqliteResultStore, database_path

RESULTS = [
    Result(90, datetime(2025, 3, 5, 14, 30, 15), "Ana"),
    Result(40, datetime(2025, 12, 24, 9, 5), "Joãozinho"),
]


@pytest.fixture
def store(tmp_path):
    return SqliteResultStore(tmp_path / "data" / "asdf_hero.db")


# --- where is the database ----------------------------------------------------


def test_database_in_the_app_data_folder(tmp_path):
    # Flet sets FLET_APP_STORAGE_DATA in the Android / iOS app
    path = database_path({"FLET_APP_STORAGE_DATA": str(tmp_path)})

    assert path == tmp_path / "asdf_hero.db"


@pytest.mark.parametrize("environ", [{}, {"FLET_APP_STORAGE_DATA": ""}])
def test_database_in_the_home_folder_without_an_app(environ):
    # python src/main.py (web server)
    assert database_path(environ) == storage.DEFAULT_DATA_DIR / "asdf_hero.db"
    assert storage.DEFAULT_DATA_DIR.name == ".asdf_hero"


def test_database_path_reads_the_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("FLET_APP_STORAGE_DATA", str(tmp_path))

    assert database_path() == tmp_path / "asdf_hero.db"


# --- load / save --------------------------------------------------------------


def test_empty_database(store):
    assert store.load() == []


def test_creates_the_folder_and_the_file(store):
    store.load()

    assert store.path.is_file()


def test_saved_results_are_loaded(store):
    store.save(RESULTS)

    assert store.load() == RESULTS  # name, points, date and time (seconds)


def test_save_replaces_the_results(store):
    store.save(RESULTS)

    store.save(RESULTS[1:])

    assert store.load() == RESULTS[1:]


def test_results_are_kept_after_a_restart(store):
    # the app is closed and opened again: a new store on the same file
    Scoreboard(store=store).add(77, datetime(2025, 3, 5, 14, 0), "Bia")

    board = Scoreboard(store=SqliteResultStore(store.path))

    assert [(r.points, r.name) for r in board.best] == [(77, "Bia")]


def test_the_table(store):
    store.save(RESULTS[:1])

    with closing(sqlite3.connect(store.path)) as connection:
        rows = connection.execute("SELECT name, points, played_at FROM results").fetchall()

    assert rows == [("Ana", 90, "2025-03-05T14:30:15")]


# --- errors: logged, the game goes on (results in memory) ---------------------


@pytest.fixture
def broken_store(tmp_path):
    # the database path is a folder: sqlite cannot open it
    path = tmp_path / "asdf_hero.db"
    path.mkdir()
    return SqliteResultStore(path)


def test_load_error_returns_no_results(broken_store, caplog):
    with caplog.at_level(logging.ERROR):
        assert broken_store.load() == []

    assert "Could not load the best results" in caplog.text


def test_save_error_is_logged(broken_store, caplog):
    with caplog.at_level(logging.ERROR):
        broken_store.save(RESULTS)

    assert "Could not save the best results" in caplog.text


def test_scoreboard_works_without_the_database(broken_store):
    board = Scoreboard(store=broken_store)

    result = board.add(10, datetime(2025, 3, 5, 14, 0), "Ana")

    assert board.best == [result]


def test_folder_error_is_logged(tmp_path, caplog):
    # the data folder cannot be created (a file has its name)
    (tmp_path / "data").write_text("not a folder")
    store = SqliteResultStore(tmp_path / "data" / "asdf_hero.db")

    with caplog.at_level(logging.ERROR):
        assert store.load() == []

    assert "Could not load" in caplog.text


# --- logs: how long the database takes (slow phones) ---------------------------


def test_load_and_save_times_are_logged(store, caplog):
    with caplog.at_level(logging.DEBUG, logger="asdf_hero.storage"):
        store.save(RESULTS)
        store.load()

    messages = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
    assert messages[0].startswith("Saved 2 best results in")
    assert messages[1].startswith("Loaded 2 best results in")
    assert messages[1].endswith(" ms")


def test_slow_database_is_a_warning(store, caplog, monkeypatch):
    monkeypatch.setattr(storage.config, "SLOW_STORAGE_MS", -1)  # everything is slow

    with caplog.at_level(logging.DEBUG, logger="asdf_hero.storage"):
        store.save(RESULTS)

    [record] = caplog.records
    assert record.levelno == logging.WARNING
    assert record.getMessage().startswith("Saved 2 best results in")


def test_data_folder(tmp_path):
    assert storage.data_dir({"FLET_APP_STORAGE_DATA": str(tmp_path)}) == tmp_path
    assert storage.data_dir({}) == storage.DEFAULT_DATA_DIR
