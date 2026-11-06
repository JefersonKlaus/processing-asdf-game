"""The language of the app: the language of the phone / browser."""

import asyncio
from unittest import mock

import pytest

from asdf_hero import app as app_module
from asdf_hero.app import GameApp, app_texts, device_language
from asdf_hero.ui.texts import ENGLISH, PORTUGUESE
from tests.app.fakes import FakePage


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.mark.parametrize(
    "languages, language",
    [
        (["pt"], "pt"),
        (["en", "pt"], "en"),  # the first one is the main language
        ([], None),
    ],
)
def test_device_language(languages, language):
    assert run(device_language(FakePage(languages=languages))) == language


def test_unknown_device_info():
    page = FakePage()
    page.get_device_info = mock.AsyncMock(return_value=None)

    assert run(device_language(page)) is None


def test_device_info_error_uses_the_default(caplog):
    page = FakePage()
    page.get_device_info = mock.AsyncMock(side_effect=TimeoutError)

    assert run(device_language(page)) is None
    assert run(app_texts(page)) is ENGLISH
    assert "Could not read the language" in caplog.text


def test_no_answer_from_the_device(monkeypatch):
    monkeypatch.setattr(app_module, "DEVICE_INFO_TIMEOUT", 0.01)
    page = FakePage()

    async def never_answers():
        await asyncio.Event().wait()

    page.get_device_info = never_answers

    assert run(device_language(page)) is None  # the game still starts


def test_device_info_timeout_is_short():
    assert 0 < app_module.DEVICE_INFO_TIMEOUT <= 5


@pytest.mark.parametrize(
    "languages, texts",
    [
        (["pt"], PORTUGUESE),  # phone in Portuguese
        (["en"], ENGLISH),  # phone in English
        (["es"], ENGLISH),  # other languages: config.DEFAULT_LANGUAGE
        ([], ENGLISH),
    ],
)
def test_app_texts(languages, texts):
    assert run(app_texts(FakePage(languages=languages))) is texts


def test_config_language_wins(monkeypatch):
    monkeypatch.setattr(app_module.config, "LANGUAGE", "pt")
    page = FakePage(languages=["en"])
    page.get_device_info = mock.AsyncMock()

    assert run(app_texts(page)) is PORTUGUESE
    page.get_device_info.assert_not_called()  # the device is not asked


@pytest.mark.parametrize(
    "languages, button",
    [(["pt"], "Iniciar ASDF Hero"), (["en"], "Start ASDF Hero")],
)
def test_main_uses_the_language_of_the_device(languages, button):
    page = FakePage(languages=languages)

    with mock.patch.object(GameApp, "run", autospec=True) as run_app:
        run(app_module.main(page))

    game_app = run_app.call_args.args[0]
    game_app.frame()
    assert game_app.view.button.control.content.value == button


def test_portuguese_by_default(game_app):
    # GameApp without texts (tests, old callers): the original language
    game_app.frame()

    assert game_app.view.texts is PORTUGUESE
