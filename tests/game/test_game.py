import random

import pytest

from asdf_hero import config
from asdf_hero.game import Game, GamePage, Highlight, Letter, LetterStatus

BUTTON_CENTER = (config.WIDTH / 2, config.HEIGHT / 2 - config.BUTTON_HEIGHT / 2)
# frames from the start of the transition until the game over page
GAME_OVER_FRAMES = (config.SLOW_MOTION_STEPS + 1) * config.SLOW_MOTION_STEP_FRAMES


def frames(game, count):
    for _ in range(count):
        game.update()


class TestInit:
    def test_initial_state(self, game):
        assert game.page == GamePage.START
        assert game.points == 0
        assert game.speed == config.INIT_SPEED
        assert game.distance == config.INIT_DISTANCE
        assert game.letters == []
        assert game.transition_to_game_over is False
        assert game.action_bar.highlight == Highlight.NONE

    def test_default_size(self, game):
        assert (game.width, game.height) == (config.WIDTH, config.HEIGHT)

    def test_button_in_the_center(self):
        game = Game(width=400, height=600)

        button = game.button
        assert (button.width, button.height) == (200, 40)
        assert (button.x, button.y) == (100, 260)

    def test_default_random(self):
        assert isinstance(Game().rng, random.Random)

    def test_each_game_has_its_own_state(self):
        first, second = Game(), Game()

        assert first.letters is not second.letters
        assert first.action_bar is not second.action_bar


class TestStartAndRetry:
    def test_click_on_the_button_starts_the_game(self, game):
        game.mouse_pressed(*BUTTON_CENTER)

        assert game.page == GamePage.RUNNING
        assert game.button.clicked is True

    def test_release(self, game):
        game.mouse_pressed(*BUTTON_CENTER)

        game.mouse_released()

        assert game.button.clicked is False

    def test_click_outside_the_button(self, game):
        game.mouse_pressed(0, 0)

        assert game.page == GamePage.START
        assert game.button.clicked is False

    def test_mouse_is_ignored_while_running(self, running_game):
        running_game.points = 5

        running_game.mouse_pressed(*BUTTON_CENTER)

        assert running_game.points == 5
        assert running_game.button.clicked is False

    def test_new_game_is_clean(self, game, place_letter):
        # dirty state from a "previous game"
        game.page = GamePage.GAME_OVER
        place_letter(game, 0, y=300)
        game.points = 80
        game._update_level()
        game.transition_to_game_over = True
        game.slow_motion_steps = 5
        game.action_bar.press(correct=False)

        game.mouse_pressed(*BUTTON_CENTER)

        assert game.page == GamePage.RUNNING
        assert game.letters == []
        assert game.points == 0
        assert game.speed == config.INIT_SPEED  # starts slow again
        assert game.distance == config.INIT_DISTANCE
        assert game.transition_to_game_over is False
        assert game.slow_motion_steps == 0
        assert game.action_bar.highlight == Highlight.NONE


class TestUpdate:
    @pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
    def test_nothing_moves_outside_the_running_page(self, game, page):
        game.page = page

        frames(game, 10)

        assert game.letters == []

    def test_first_frame_adds_a_letter(self, running_game):
        running_game.update()

        [letter] = running_game.letters
        assert isinstance(letter, Letter)
        assert letter.y == config.INIT_SPEED  # already moved once

    def test_letter_lane_and_char_from_rng(self, scripted_rng):
        game = Game(rng=scripted_rng([2]))
        game.start_new_game()

        game.update()

        letter = game.letters[0]
        assert (letter.lane, letter.char) == (2, "D")

    @pytest.mark.parametrize(
        "points, random_char", [(0, False), (24, False), (25, True), (40, True)]
    )
    def test_random_chars_after_25_points(self, scripted_rng, points, random_char):
        game = Game(rng=scripted_rng([0, 3]))  # lane 0 ("A"), char 3 ("F")
        game.start_new_game()
        game.points = points

        game.update()

        assert game.letters[0].char == ("F" if random_char else "A")

    def test_waits_the_distance_before_the_next_letter(self, running_game, place_letter):
        # the next letter comes when last.y >= distance + size (150 + 62)
        place_letter(running_game, 0, y=212 - config.INIT_SPEED - 1)

        running_game.update()

        assert len(running_game.letters) == 1

    def test_adds_a_letter_after_the_distance(self, running_game, place_letter):
        place_letter(running_game, 0, y=212)

        running_game.update()

        assert len(running_game.letters) == 2

    def test_distance_depends_on_the_level(self, running_game, place_letter):
        running_game.distance = 100
        place_letter(running_game, 0, y=162)

        running_game.update()

        assert len(running_game.letters) == 2

    def test_letters_move_with_the_game_speed(self, running_game, place_letter):
        first = place_letter(running_game, 0, y=100)
        second = place_letter(running_game, 1, y=50)
        running_game.speed = 4.5

        running_game.update()

        assert (first.y, second.y) == (104.5, 54.5)

    def test_letters_keep_their_distance_when_the_speed_changes(self, running_game):
        frames(running_game, 100)
        running_game.speed = config.MAX_SPEED
        ys = [letter.y for letter in running_game.letters]
        gaps = [a - b for a, b in zip(ys, ys[1:])]

        running_game.update()

        ys = [letter.y for letter in running_game.letters]
        assert [a - b for a, b in zip(ys, ys[1:])] == pytest.approx(gaps)

    def test_letters_below_the_screen_are_removed(self, running_game, place_letter):
        gone = place_letter(running_game, 0, y=config.HEIGHT + 62, status=LetterStatus.WAS_PRESSED)
        visible = place_letter(running_game, 1, y=500)

        running_game.update()

        assert gone not in running_game.letters
        assert visible in running_game.letters

    def test_every_letter_moves_when_one_is_removed(self, running_game, place_letter):
        # regression: removing a letter during the loop skipped the next one
        place_letter(running_game, 0, y=config.HEIGHT + 62, status=LetterStatus.WAS_PRESSED)
        next_letter = place_letter(running_game, 1, y=500)

        running_game.update()

        assert next_letter.y == 500 + config.INIT_SPEED

    def test_failed_letter_starts_the_transition(self, running_game, place_letter):
        # the circle leaves the bar (center > 711) without being pressed
        place_letter(running_game, 0, y=710, status=LetterStatus.NEED_BE_PRESSED)

        running_game.update()

        assert running_game.transition_to_game_over is True
        assert running_game.page == GamePage.RUNNING


class TestSlowMotion:
    """The transition to game over: the game moves in slow motion."""

    def test_one_step_every_some_frames(self, running_game, place_letter):
        letter = place_letter(running_game, 0, y=100)
        running_game.transition_to_game_over = True

        frames(running_game, config.SLOW_MOTION_STEP_FRAMES - 1)
        assert letter.y == 100  # waiting

        running_game.update()
        assert letter.y == 100 + config.INIT_SPEED  # one step

    def test_game_over_page_after_the_steps(self, running_game):
        running_game.transition_to_game_over = True

        frames(running_game, GAME_OVER_FRAMES - 1)
        assert running_game.page == GamePage.RUNNING
        assert running_game.slow_motion_steps == config.SLOW_MOTION_STEPS

        running_game.update()
        assert running_game.page == GamePage.GAME_OVER

    def test_takes_about_three_seconds(self):
        seconds = GAME_OVER_FRAMES / config.FPS
        assert 2 <= seconds <= 3.5

    def test_keys_are_ignored(self, running_game, place_letter):
        letter = place_letter(running_game, 0, y=640, status=LetterStatus.NEED_BE_PRESSED)
        running_game.transition_to_game_over = True

        running_game.key_pressed("a")

        assert letter.status == LetterStatus.NEED_BE_PRESSED
        assert running_game.points == 0


class TestKeyPressed:
    def test_right_letter_in_the_action_bar_scores(self, running_game, place_letter):
        letter = place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        running_game.key_pressed("s")

        assert running_game.points == 1
        assert letter.status == LetterStatus.WAS_PRESSED
        assert running_game.transition_to_game_over is False

    def test_point_levels_up(self, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        running_game.key_pressed("S")

        assert running_game.speed > config.INIT_SPEED
        assert running_game.distance < config.INIT_DISTANCE


class TestWrongMoment:
    """Pressing a letter when it is not in the action bar ends the game."""

    def test_letter_above_the_action_bar(self, running_game, place_letter):
        place_letter(running_game, 0, y=300)

        running_game.key_pressed("a")

        assert running_game.transition_to_game_over is True
        assert running_game.points == 0

    def test_without_letters(self, running_game):
        running_game.key_pressed("a")

        assert running_game.transition_to_game_over is True

    def test_other_letter_in_the_action_bar(self, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        running_game.key_pressed("a")

        assert running_game.transition_to_game_over is True

    def test_letter_already_left_the_action_bar(self, running_game, place_letter):
        place_letter(running_game, 1, y=720, status=LetterStatus.WAS_PRESSED)

        running_game.key_pressed("s")

        assert running_game.transition_to_game_over is True

    def test_points_are_kept(self, running_game):
        running_game.points = 7

        running_game.key_pressed("d")
        frames(running_game, GAME_OVER_FRAMES)

        assert running_game.page == GamePage.GAME_OVER
        assert running_game.points == 7

    def test_same_letter_again_in_the_action_bar_is_ignored(
        self, running_game, place_letter
    ):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)
        running_game.key_pressed("s")

        running_game.key_pressed("s")

        assert running_game.transition_to_game_over is False
        assert running_game.points == 1

    @pytest.mark.parametrize("key", ["g", "1", " ", "Arrow Up", "Enter", "Escape"])
    def test_other_keys_are_ignored(self, running_game, key):
        running_game.key_pressed(key)

        assert running_game.transition_to_game_over is False

    @pytest.mark.parametrize("page", [GamePage.START, GamePage.GAME_OVER])
    def test_keys_are_ignored_when_not_playing(self, game, page):
        game.page = page

        game.key_pressed("a")

        assert game.transition_to_game_over is False


class TestHitArea:
    """A letter can be pressed while its circle touches the action bar."""

    @pytest.mark.parametrize("y", [569, 590, 640, 700, 711])
    def test_circle_touching_the_bar_can_be_pressed(self, running_game, place_letter, y):
        letter = place_letter(running_game, 0, y=y - config.INIT_SPEED)
        running_game.update()  # moves to y and updates the status

        running_game.key_pressed("a")

        assert letter.status == LetterStatus.WAS_PRESSED
        assert running_game.points == 1
        assert running_game.transition_to_game_over is False

    def test_circle_above_the_bar_is_too_early(self, running_game, place_letter):
        place_letter(running_game, 0, y=560)  # circle bottom at 591
        running_game.update()

        running_game.key_pressed("a")

        assert running_game.transition_to_game_over is True


class TestActionBarHighlight:
    """
    The bar shows the result of the press: light yellow when it is right,
    light red when it is wrong (no letter of the key in the bar: game over).
    """

    def test_yellow_when_a_letter_is_hit(self, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        running_game.key_pressed("s")

        assert running_game.action_bar.highlight == Highlight.PRESSED

    def test_red_when_the_action_bar_is_empty(self, running_game, place_letter):
        place_letter(running_game, 0, y=300)  # not in the action bar yet

        running_game.key_pressed("a")

        assert running_game.action_bar.highlight == Highlight.WRONG

    def test_red_without_letters(self, running_game):
        running_game.key_pressed("f")

        assert running_game.action_bar.highlight == Highlight.WRONG

    def test_red_with_another_letter_in_the_action_bar(self, running_game, place_letter):
        # bug: this was yellow and then game over
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        running_game.key_pressed("a")

        assert running_game.action_bar.highlight == Highlight.WRONG
        assert running_game.transition_to_game_over is True

    def test_red_when_the_next_letter_is_pressed_too_early(
        self, running_game, place_letter
    ):
        # bug: the hit letter still in the bar made the bar yellow, but the
        # key of the next letter (far above the bar) ends the game
        place_letter(running_game, 1, y=675, status=LetterStatus.WAS_PRESSED)
        place_letter(running_game, 0, y=513)

        running_game.key_pressed("a")

        assert running_game.action_bar.highlight == Highlight.WRONG
        assert running_game.transition_to_game_over is True

    def test_red_with_the_wrong_char(self, running_game, place_letter):
        # after 25 points the char does not match the lane: "F" in lane "A"
        place_letter(running_game, 0, y=640, status=LetterStatus.NEED_BE_PRESSED, char="F")

        running_game.key_pressed("a")

        assert running_game.action_bar.highlight == Highlight.WRONG

    def test_yellow_on_a_double_press(self, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.WAS_PRESSED)

        running_game.key_pressed("s")

        assert running_game.action_bar.highlight == Highlight.PRESSED
        assert running_game.transition_to_game_over is False

    def test_no_highlight_for_other_keys(self, running_game):
        running_game.key_pressed("g")

        assert running_game.action_bar.highlight == Highlight.NONE

    def test_no_highlight_when_not_playing(self, game):
        game.key_pressed("a")

        assert game.action_bar.highlight == Highlight.NONE

    def test_yellow_goes_away_after_some_frames(self, running_game, place_letter):
        place_letter(running_game, 1, y=640, status=LetterStatus.NEED_BE_PRESSED)
        running_game.key_pressed("s")

        frames(running_game, config.HIGHLIGHT_FRAMES - 1)
        assert running_game.action_bar.highlight == Highlight.PRESSED

        running_game.update()
        assert running_game.action_bar.highlight == Highlight.NONE

    def test_red_stays_during_the_slow_motion(self, running_game):
        # the red bar shows why the game ended
        running_game.key_pressed("a")

        frames(running_game, config.HIGHLIGHT_FRAMES * 5)

        assert running_game.action_bar.highlight == Highlight.WRONG

    @pytest.mark.parametrize("points", [0, 30, 100])
    def test_yellow_is_never_followed_by_game_over(self, points, place_letter):
        # every letter position x every key: a yellow press never ends the game
        for y in range(0, 800, 3):
            for key in "asdfg":
                game = Game(rng=random.Random(0))
                game.start_new_game()
                game.points = points
                game._update_level()
                place_letter(game, 0, y=y)
                game.update()

                game.key_pressed(key)

                if game.action_bar.highlight == Highlight.PRESSED:
                    assert game.transition_to_game_over is False, (y, key)
                if game.transition_to_game_over:
                    assert game.action_bar.highlight == Highlight.WRONG, (y, key)


class TestFullGame:
    """End to end flow with real letters."""

    def play(self, game, frame_count, press=True):
        for _ in range(frame_count):
            game.update()
            if game.page != GamePage.RUNNING:
                return
            for letter in list(game.letters):
                if press and letter.status == LetterStatus.NEED_BE_PRESSED:
                    game.key_pressed(letter.char)

    def test_play_level_up_and_lose(self, game):
        game.mouse_pressed(*BUTTON_CENTER)
        game.mouse_released()

        # a perfect player for 1 minute: the game gets faster
        self.play(game, 60 * 60)
        assert game.page == GamePage.RUNNING
        assert game.points > 25
        assert game.speed > config.INIT_SPEED
        assert len(game.letters) >= 3  # more than one letter at the same time

        # stop playing: a letter fails -> game over
        self.play(game, 60 * 30, press=False)
        assert game.page == GamePage.GAME_OVER

        # retry: slow again
        game.mouse_pressed(*BUTTON_CENTER)
        assert game.page == GamePage.RUNNING
        assert (game.points, game.letters) == (0, [])
        assert game.speed == config.INIT_SPEED

    def test_wrong_press_ends_the_game(self, game):
        game.mouse_pressed(*BUTTON_CENTER)
        self.play(game, 60 * 10)
        points = game.points
        assert points > 0 and game.page == GamePage.RUNNING

        # the newest letter is at the top of the screen: wrong moment
        game.key_pressed(game.letters[-1].char)
        self.play(game, GAME_OVER_FRAMES, press=False)

        assert game.page == GamePage.GAME_OVER
        assert game.points == points
