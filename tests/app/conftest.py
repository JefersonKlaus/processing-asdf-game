from unittest import mock

import flet as ft
import pytest

from asdf_hero.app import GameApp
from asdf_hero.game import Scoreboard
from tests.app.fakes import FakePage


@pytest.fixture(autouse=True)
def auto_update():
    """ft.context only works inside a Flet session: replace it."""
    with mock.patch.object(ft.context, "disable_auto_update") as disable:
        yield disable


@pytest.fixture
def page():
    return FakePage()


@pytest.fixture
def game_app(page):
    return GameApp(page, scoreboard=Scoreboard())
