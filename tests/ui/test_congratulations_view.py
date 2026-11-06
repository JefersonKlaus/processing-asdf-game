"""CongratulationsView: a new best result, the name field and the save buttons."""

from types import SimpleNamespace

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import Game
from asdf_hero.ui import theme
from asdf_hero.ui.congratulations_view import CongratulationsView
from asdf_hero.ui.texts import ENGLISH, PORTUGUESE


@pytest.fixture
def events():
    return []


@pytest.fixture
def view(events):
    return CongratulationsView(
        Game(),
        PORTUGUESE,
        on_name_change=lambda text: events.append(("change", text)),
        on_name_submit=lambda: events.append(("submit",)),
    )


def text_of(container):
    return container.content.value


def test_hidden_at_the_start(view):
    view.render(visible=False, points=0)

    assert view.control.visible is False
    assert view.field is None
    assert view.field_box.content is None


def test_texts(view):
    view.render(visible=True, points=42)

    assert view.control.visible is True
    assert text_of(view.title) == "NADA MAL!"
    assert text_of(view.subtitle) == "Novo recorde!"
    assert text_of(view.text) == "Você fez 42 pontos e entrou nos 5 melhores resultados."


def test_title_is_bold_like_game_over(view):
    view.render(visible=True, points=1)

    assert view.title.content.weight == ft.FontWeight.BOLD
    assert view.subtitle.content.weight is None  # only the title


def test_texts_in_english():
    view = CongratulationsView(Game(), ENGLISH, lambda text: None, lambda: None)

    view.render(visible=True, points=42)

    assert text_of(view.title) == "NOT BAD!"
    assert text_of(view.subtitle) == "New record!"
    assert text_of(view.text) == "You scored 42 points and entered the 5 best results."
    assert view.field.label == "Your name"
    assert view.save_button.control.content.value == "Save"
    assert view.anonymous_button.control.content.value == "Save as anonymous"


def test_layers(view):
    assert view.control.controls == [
        view.banner,
        view.title,
        view.subtitle,
        view.text,
        view.field_box,
        view.save_button.control,
        view.anonymous_button.control,
    ]


def test_buttons(view):
    view.render(visible=True, points=1)

    save, anonymous = view.save_button.control, view.anonymous_button.control
    assert (save.visible, anonymous.visible) == (True, True)
    assert save.content.value == "Salvar"
    assert anonymous.content.value == "Salvar como anônimo"
    assert save.top == config.CONGRATULATIONS_BUTTONS_TOP
    assert anonymous.top == save.top + config.BUTTON_HEIGHT + config.BUTTON_GAP
    assert save.content.size == theme.CONGRATULATIONS_BUTTON_FONT_SIZE


def test_buttons_colors(view):
    view.render(visible=True, points=1)

    # green: save (like start), blue: save as anonymous; white text
    assert view.save_button.control.bgcolor == theme.START_BUTTON_COLOR
    assert view.anonymous_button.control.bgcolor == theme.ANONYMOUS_BUTTON_COLOR
    for button in (view.save_button, view.anonymous_button):
        assert button.control.content.color == theme.BUTTON_TEXT_COLOR


def test_buttons_hidden_with_the_page(view):
    view.render(visible=True, points=1)

    view.render(visible=False, points=1)

    assert view.save_button.control.visible is False
    assert view.anonymous_button.control.visible is False


def test_everything_inside_the_banner(view):
    banner_bottom = view.banner.top + view.banner.height

    assert view.banner.top <= view.title.top
    assert view.title.top < view.subtitle.top < view.text.top < view.field_box.top
    assert view.field_box.top < config.CONGRATULATIONS_BUTTONS_TOP
    anonymous_bottom = (
        config.CONGRATULATIONS_BUTTONS_TOP + 2 * config.BUTTON_HEIGHT + config.BUTTON_GAP
    )
    assert anonymous_bottom < banner_bottom


def test_name_field(view):
    view.render(visible=True, points=1)

    field = view.field
    assert isinstance(field, ft.TextField)
    assert view.field_box.content is field
    assert field.value == ""
    assert field.label == "Seu nome"
    assert field.max_length == config.NAME_MAX_LENGTH
    assert field.autofocus is True  # the keyboard of the phone opens
    assert view.field_box.width == 282 - 2 * theme.NAME_FIELD_MARGIN


def test_the_field_is_kept_while_the_page_shows(view):
    view.render(visible=True, points=1)
    field = view.field
    field.value = "An"

    view.render(visible=True, points=1)  # next frames

    assert view.field is field
    assert field.value == "An"  # the typed text is not changed by the view


def test_a_new_empty_field_for_each_new_best_result(view):
    view.render(visible=True, points=1)
    first = view.field
    first.value = "Ana"
    view.render(visible=False, points=1)

    view.render(visible=True, points=2)

    assert view.field is not first
    assert view.field.value == ""


def test_each_change_is_sent(view, events):
    view.render(visible=True, points=1)
    view.field.value = "Ana"

    view.field.on_change(SimpleNamespace(control=view.field))

    assert events == [("change", "Ana")]


def test_enter_sends_the_text_and_saves(view, events):
    view.render(visible=True, points=1)
    view.field.value = "Bia"

    view.field.on_submit(SimpleNamespace(control=view.field))

    assert events == [("change", "Bia"), ("submit",)]


def test_empty_field_sends_an_empty_text(view, events):
    view.render(visible=True, points=1)
    view.field.value = None

    view.field.on_change(SimpleNamespace(control=view.field))

    assert events == [("change", "")]
