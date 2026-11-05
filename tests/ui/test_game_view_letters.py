"""GameView: one LetterView for each letter of the game."""

import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.ui import GameView


@pytest.fixture
def view(running_game):
    return GameView(running_game)


def keys(view):
    return [control.key for control in view.letters.controls]


def test_one_view_for_each_letter(view, running_game, place_letter):
    first = place_letter(running_game, 0, y=100)
    second = place_letter(running_game, 1, y=300)

    view.render()

    assert keys(view) == ["letter-%d" % first.id, "letter-%d" % second.id]


def test_views_are_kept_between_frames(view, running_game):
    running_game.update()
    view.render()
    control = view.letters.controls[0]

    running_game.update()
    view.render()

    assert view.letters.controls[0] is control
    assert control.top == running_game.letters[0].y - 31


def test_removed_letters_leave_the_screen(view, running_game, place_letter):
    gone = place_letter(running_game, 0, y=100)
    kept = place_letter(running_game, 1, y=300)
    view.render()

    running_game.letters.remove(gone)
    view.render()

    assert keys(view) == ["letter-%d" % kept.id]


def test_gold_letters_are_drawn_on_top(view, running_game, place_letter):
    gold = place_letter(running_game, 2, y=200, gold=True)
    normal = place_letter(running_game, 0, y=100)  # added after the gold

    view.render()

    assert keys(view) == ["letter-%d" % normal.id, "letter-%d" % gold.id]


def test_list_is_not_replaced_when_nothing_changes(view, running_game, place_letter):
    # a new list would be sent to the browser again
    place_letter(running_game, 0, y=100)
    view.render()
    controls = view.letters.controls

    view.render()

    assert view.letters.controls is controls


def test_letters_hide_behind_the_touch_buttons(view):
    # the letters layer ends at the top of the buttons: it cuts the letters
    assert view.letters.height == config.TOUCH_BUTTONS_TOP
    assert view.letters.clip_behavior == ft.ClipBehavior.HARD_EDGE


def test_letters_show_the_keys_of_the_hand(running_game):
    running_game.toggle_hand()
    running_game.start_new_game()
    view = GameView(running_game)
    for _ in range(200):
        running_game.update()

    view.render()

    chars = {c.content.controls[1].value for c in view.letters.controls}
    assert chars and chars <= {"J", "K", "L", "Ç"}
