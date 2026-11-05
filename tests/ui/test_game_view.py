import flet as ft
import pytest

from asdf_hero import config
from asdf_hero.game import GamePage, Highlight, Letter, LetterStatus
from asdf_hero.ui import GameView, theme

BUTTON_CENTER = (config.WIDTH / 2, config.HEIGHT / 2 - config.BUTTON_HEIGHT / 2)


@pytest.fixture
def view(game):
    return GameView(game)


def shown(view):
    """What is on the screen: lanes, action bar, letters, points, game over, button."""
    return (
        view.background.lanes.visible,
        view.action_bar.control.visible,
        view.letters.visible,
        view.points_bar.visible,
        view.game_over_points.visible,
        view.button.control.visible,
    )


class TestControl:
    def test_layers_in_order(self, view):
        controls = view.control.controls

        assert isinstance(controls[0], ft.Image)
        assert controls[0].src == theme.BACKGROUND_IMAGE
        assert controls[1:] == [
            view.background.lanes,
            view.action_bar.control,
            view.background.game_over_banner,
            view.letters,
            view.points_bar,
            view.game_over_points,
            view.button.control,
        ]

    def test_size(self, view):
        assert (view.control.width, view.control.height) == (config.WIDTH, config.HEIGHT)


class TestPages:
    @pytest.mark.parametrize(
        "page, expected",
        [
            (GamePage.START, (False, False, False, False, False, True)),
            (GamePage.RUNNING, (True, True, True, True, False, False)),
            (GamePage.GAME_OVER, (False, False, False, False, True, True)),
        ],
    )
    def test_what_each_page_shows(self, view, page, expected):
        view.game.page = page

        view.render()

        assert shown(view) == expected

    @pytest.mark.parametrize(
        "page, text",
        [(GamePage.START, "Iniciar ASDF Hero"), (GamePage.GAME_OVER, "Falhar novamente")],
    )
    def test_button_text(self, view, page, text):
        view.game.page = page

        view.render()

        assert view.button.control.content.value == text

    def test_points_while_running(self, view, running_game):
        running_game.points = 7

        view.render()

        assert view.points_bar.content.value == "Pontos: 7"

    def test_points_on_game_over(self, view, game):
        game.page = GamePage.GAME_OVER
        game.points = 12

        view.render()

        assert view.game_over_points.content.value == "Pontos: 12"


class TestLetters:
    def test_one_view_for_each_letter(self, view, running_game, place_letter):
        first = place_letter(running_game, 0, y=100)
        second = place_letter(running_game, 1, y=300)

        view.render()

        assert [c.key for c in view.letters.controls] == [
            "letter-%d" % first.id,
            "letter-%d" % second.id,
        ]

    def test_letter_views_are_kept_between_frames(self, view, running_game):
        running_game.update()
        view.render()
        control = view.letters.controls[0]

        running_game.update()
        view.render()

        assert view.letters.controls[0] is control
        assert control.top == running_game.letters[0].y - 31

    def test_removed_letters_leave_the_screen(self, view, running_game, place_letter):
        gone = place_letter(running_game, 0, y=100)
        place_letter(running_game, 1, y=300)
        view.render()

        running_game.letters.remove(gone)
        view.render()

        assert len(view.letters.controls) == 1
        assert gone.id not in view._letter_views

    def test_gold_letters_are_drawn_on_top(self, view, running_game, place_letter):
        gold = Letter(2, "D", running_game.action_bar, gold=True)
        running_game.letters.append(gold)
        normal = place_letter(running_game, 0, y=100)  # added after the gold

        view.render()

        keys = [c.key for c in view.letters.controls]
        assert keys == ["letter-%d" % normal.id, "letter-%d" % gold.id]

    def test_action_bar_shakes_after_a_key(self, view, running_game):
        view.render()
        running_game.key_pressed("a")

        view.render()

        assert view.action_bar.control.left == theme.ACTION_BAR_SHAKE[0]

    def test_list_is_not_replaced_when_nothing_changes(self, view, running_game, place_letter):
        place_letter(running_game, 0, y=100)
        view.render()
        controls = view.letters.controls

        view.render()

        assert view.letters.controls is controls


class TestActionBarHighlight:
    def test_yellow_after_a_hit(self, view, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        running_game.key_pressed("s")
        view.render()

        assert view.action_bar.control.bgcolor == theme.ACTION_BAR_COLORS[Highlight.PRESSED]

    def test_red_when_wrong(self, view, running_game):
        running_game.key_pressed("a")  # no letter in the bar
        view.render()

        assert view.action_bar.control.bgcolor == theme.ACTION_BAR_COLORS[Highlight.WRONG]

    def test_white_again_after_the_highlight(self, view, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)
        running_game.key_pressed("s")

        for _ in range(config.HIGHLIGHT_FRAMES):
            running_game.update()
        view.render()

        assert view.action_bar.control.bgcolor == theme.ACTION_BAR_COLORS[Highlight.NONE]


def test_full_flow(view, game):
    view.render()
    game.mouse_pressed(*BUTTON_CENTER)
    game.update()
    view.render()

    assert shown(view) == (True, True, True, True, False, False)
    assert len(view.letters.controls) == 1
