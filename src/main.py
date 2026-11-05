"""
ASDF Hero - entry point.

Run it in the browser with:

    python src/main.py        (or: flet run --web src/main.py)
"""

import os

import flet as ft

from asdf_hero.app import main

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir=ASSETS_DIR,
        host=os.getenv("FLET_SERVER_IP"),
        port=int(os.getenv("FLET_SERVER_PORT", "8550")),
    )
