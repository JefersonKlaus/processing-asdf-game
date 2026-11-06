"""
Logs of the game: on the console (terminal, ``flet debug``) and in a file in
the data folder of the app (next to the database), so the logs of a phone
can be read later.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from asdf_hero import config

LOG_LEVEL_ENV = "ASDF_HERO_LOG_LEVEL"
FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(log_file: Path, level: str | None = None) -> logging.Logger:
    """
    Send the logs of the game (the ``asdf_hero`` loggers) to the console and
    to ``log_file``. Level: ``level``, else ASDF_HERO_LOG_LEVEL, else
    config.LOG_LEVEL. Calling it again changes nothing (one set of handlers).
    """
    logger = logging.getLogger("asdf_hero")
    if logger.handlers:
        return logger
    logger.setLevel((level or os.getenv(LOG_LEVEL_ENV) or config.LOG_LEVEL).upper())
    logger.propagate = False  # not twice when Flet also configures logging

    formatter = logging.Formatter(FORMAT)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.LOG_FILE_MAX_BYTES,
            backupCount=1,  # one old file: the logs never fill the phone
            encoding="utf-8",
        )
    except OSError:
        logger.exception("Could not open the log file %s", log_file)
    else:
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    logger.info("Logs: level %s, file %s", logging.getLevelName(logger.level), log_file)
    return logger


def stop_logging() -> None:
    """Undo ``setup_logging`` (tests; the app logs until it stops)."""
    logger = logging.getLogger("asdf_hero")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.NOTSET)
    logger.propagate = True
