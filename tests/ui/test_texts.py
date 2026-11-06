"""Texts: Portuguese and English, chosen by the language of the device."""

import dataclasses
import string
from datetime import datetime

import pytest

from asdf_hero import config
from asdf_hero.game import GamePage, Hand
from asdf_hero.ui.texts import ENGLISH, LANGUAGES, PORTUGUESE, Texts, texts_for

ALL = [PORTUGUESE, ENGLISH]


@pytest.mark.parametrize(
    "code, texts",
    [
        ("pt", PORTUGUESE),
        ("pt-BR", PORTUGUESE),
        ("pt_PT", PORTUGUESE),
        ("PT", PORTUGUESE),
        ("en", ENGLISH),
        ("en-US", ENGLISH),
        ("en_GB", ENGLISH),
    ],
)
def test_language_of_the_device(code, texts):
    assert texts_for(code) is texts


@pytest.mark.parametrize("code", ["es", "fr-FR", "und", "", None])
def test_other_languages_use_the_default(code):
    assert texts_for(code) is LANGUAGES[config.DEFAULT_LANGUAGE] is ENGLISH


def test_languages():
    assert LANGUAGES == {"pt": PORTUGUESE, "en": ENGLISH}
    assert config.LANGUAGE is None  # the language of the device


@pytest.mark.parametrize("texts", ALL)
def test_every_text_is_filled(texts):
    for field in dataclasses.fields(Texts):
        assert getattr(texts, field.name), field.name


def placeholders(text):
    return [name for _, name, _, _ in string.Formatter().parse(text) if name is not None]


@pytest.mark.parametrize("field", [f.name for f in dataclasses.fields(Texts)])
def test_same_placeholders_in_each_language(field):
    assert placeholders(getattr(PORTUGUESE, field)) == placeholders(getattr(ENGLISH, field))


@pytest.mark.parametrize("texts", ALL)
def test_date_and_time_formats_work(texts):
    when = datetime(2025, 12, 24, 9, 30)

    assert "2025" in when.strftime(texts.date_format)
    assert when.strftime(texts.time_format) == "09:30"


@pytest.mark.parametrize(
    "texts, page, text",
    [
        (PORTUGUESE, GamePage.START, "Iniciar ASDF Hero"),
        (PORTUGUESE, GamePage.GAME_OVER, "Falhar novamente"),
        (ENGLISH, GamePage.START, "Start ASDF Hero"),
        (ENGLISH, GamePage.GAME_OVER, "Fail again"),
    ],
)
def test_main_button(texts, page, text):
    assert texts.button(page) == text


@pytest.mark.parametrize("texts", ALL)
def test_hand_buttons_show_the_keys(texts):
    assert "ASDF" in texts.hand_button(Hand.LEFT)
    assert "JKLÇ" in texts.hand_button(Hand.RIGHT)


@pytest.mark.parametrize("texts, anonymous", [(PORTUGUESE, "Anônimo"), (ENGLISH, "Anonymous")])
def test_names(texts, anonymous):
    assert texts.name("Ana") == "Ana"
    assert texts.name("") == anonymous
    assert len(anonymous) <= config.NAME_MAX_LENGTH
