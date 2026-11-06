"""
ASDF Hero - entry point.

Run it in the browser with:

    python src/main.py        (or: flet run --web src/main.py)
"""

import os

import flet as ft

from asdf_hero import config, storage
from asdf_hero.app import main
from asdf_hero.logs import setup_logging

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

if __name__ == "__main__":
    # logs: console and a file in the data folder (see "Logs" in README.md)
    setup_logging(storage.data_dir() / config.LOG_FILE)
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir=ASSETS_DIR,
        host=os.getenv("FLET_SERVER_IP"),
        port=int(os.getenv("FLET_SERVER_PORT", "8550")),
    )
