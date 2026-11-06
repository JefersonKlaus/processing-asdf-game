"""setup_logging: the logs of the game on the console and in a file."""

import logging
from logging.handlers import RotatingFileHandler

import pytest

from asdf_hero import config
from asdf_hero.logs import LOG_LEVEL_ENV, setup_logging, stop_logging


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "data" / "asdf_hero.log"


@pytest.fixture(autouse=True)
def no_level_from_the_environment(monkeypatch):
    monkeypatch.delenv(LOG_LEVEL_ENV, raising=False)


def handler_types(logger):
    return sorted(type(handler).__name__ for handler in logger.handlers)


def test_console_and_file(log_file):
    logger = setup_logging(log_file)

    assert logger.name == "asdf_hero"
    assert handler_types(logger) == ["RotatingFileHandler", "StreamHandler"]
    assert logger.propagate is False  # not twice when Flet also logs


def test_the_file_gets_the_logs_of_the_game(log_file):
    setup_logging(log_file)

    logging.getLogger("asdf_hero.app").warning("Slow game: 30 fps")
    stop_logging()  # close the file

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert "INFO asdf_hero: Logs: level INFO, file" in lines[0]
    assert lines[1].endswith("WARNING asdf_hero.app: Slow game: 30 fps")


def test_the_file_does_not_fill_the_phone(log_file):
    logger = setup_logging(log_file)

    [file_handler] = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    assert file_handler.maxBytes == config.LOG_FILE_MAX_BYTES
    assert file_handler.backupCount == 1


@pytest.mark.parametrize(
    "argument, environment, level",
    [
        (None, None, config.LOG_LEVEL),  # config.py
        (None, "debug", "DEBUG"),  # ASDF_HERO_LOG_LEVEL
        ("warning", "debug", "WARNING"),  # the argument wins
    ],
)
def test_level(monkeypatch, log_file, argument, environment, level):
    if environment:
        monkeypatch.setenv(LOG_LEVEL_ENV, environment)

    logger = setup_logging(log_file, level=argument)

    assert logging.getLevelName(logger.level) == level


def test_default_level_is_info():
    assert config.LOG_LEVEL == "INFO"


def test_only_once(log_file, tmp_path):
    setup_logging(log_file)

    logger = setup_logging(tmp_path / "other.log", level="DEBUG")

    assert len(logger.handlers) == 2
    assert logger.level == logging.INFO
    assert not (tmp_path / "other.log").exists()


def test_no_file_when_it_cannot_be_opened(tmp_path, capsys):
    (tmp_path / "data").write_text("a file, not a folder")

    logger = setup_logging(tmp_path / "data" / "asdf_hero.log")

    assert handler_types(logger) == ["StreamHandler"]  # the console still works
    assert "Could not open the log file" in capsys.readouterr().err


def test_stop_logging(log_file):
    setup_logging(log_file)

    stop_logging()

    logger = logging.getLogger("asdf_hero")
    assert logger.handlers == []
    assert (logger.level, logger.propagate) == (logging.NOTSET, True)
