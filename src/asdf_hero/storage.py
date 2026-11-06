"""
The best results in a SQLite database (the ``sqlite3`` module of Python: it
works on the web server and inside the Android / iOS app).
"""

import logging
import os
import sqlite3
import time
from collections.abc import Mapping
from contextlib import closing
from datetime import datetime
from pathlib import Path

from asdf_hero import config
from asdf_hero.game.scoreboard import Result

logger = logging.getLogger(__name__)

# Flet sets this variable in the app (phone / desktop) and in `flet run`: it
# is the data folder of the app, kept when the app is updated
APP_DATA_ENV = "FLET_APP_STORAGE_DATA"
# `python src/main.py` (web server): a folder in the home of the user
DEFAULT_DATA_DIR = Path.home() / ".asdf_hero"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    points INTEGER NOT NULL,
    played_at TEXT NOT NULL
)
"""


def data_dir(environ: Mapping[str, str] = os.environ) -> Path:
    """The data folder of the app (database, logs)."""
    folder = environ.get(APP_DATA_ENV)
    return Path(folder) if folder else DEFAULT_DATA_DIR


def database_path(environ: Mapping[str, str] = os.environ) -> Path:
    """The database file: in the data folder of the app when there is one."""
    return data_dir(environ) / config.DATABASE_FILE


def _log_duration(action: str, started: float, count: int) -> None:
    """Debug log of a database action; a warning when it is slow (phones)."""
    ms = (time.perf_counter() - started) * 1000
    level = logging.WARNING if ms > config.SLOW_STORAGE_MS else logging.DEBUG
    logger.log(level, "%s %d best results in %.1f ms", action, count, ms)


class SqliteResultStore:
    """
    A ResultStore in a SQLite file. The table has only the best results (the
    Scoreboard saves all of them at once). Database errors are logged and do
    not stop the game: the results are kept in memory.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        # one short connection for each operation: simple and thread safe
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.execute(CREATE_TABLE)
        return connection

    def load(self) -> list[Result]:
        started = time.perf_counter()
        try:
            with closing(self._connect()) as connection:
                rows = connection.execute(
                    "SELECT name, points, played_at FROM results"
                ).fetchall()
        except (sqlite3.Error, OSError):
            logger.exception("Could not load the best results from %s", self.path)
            return []
        _log_duration("Loaded", started, len(rows))
        return [
            Result(points, datetime.fromisoformat(played_at), name)
            for name, points, played_at in rows
        ]

    def save(self, results: list[Result]) -> None:
        started = time.perf_counter()
        try:
            with closing(self._connect()) as connection, connection:  # transaction
                connection.execute("DELETE FROM results")
                connection.executemany(
                    "INSERT INTO results (name, points, played_at) VALUES (?, ?, ?)",
                    [(item.name, item.points, item.when.isoformat()) for item in results],
                )
        except (sqlite3.Error, OSError):
            logger.exception("Could not save the best results in %s", self.path)
            return
        _log_duration("Saved", started, len(results))
