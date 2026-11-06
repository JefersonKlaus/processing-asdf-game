"""
The rules agreed for the game design (config.py). If the design changes,
update these tests on purpose.
"""

import random

from asdf_hero import config
from asdf_hero.game import Game
from asdf_hero.game.level import distance_for, speed_for
from tests.helpers import play, set_points

HIT_AREA = config.ACTION_BAR_HEIGHT + config.LETTER_SIZE  # circle touches the bar


def seconds(frames):
    return frames / config.FPS


def test_starts_slow():
    assert speed_for(0) * config.FPS == 180  # pixels per second


def test_max_speed_is_not_too_fast():
    # more letters instead of more speed: max 240 px/s, at 51 points
    assert config.MAX_SPEED * config.FPS == 240
    assert config.MAX_SPEED_FROM_POINTS == 51


def test_letters_come_faster_at_the_max_level():
    def frames_between_letters(points):
        return (distance_for(points) + config.LETTER_SIZE) / speed_for(points)

    assert frames_between_letters(500) < frames_between_letters(0)


def test_max_level_has_always_one_letter_in_the_action_bar():
    # center to center = the hit area: the next letter touches the bar when
    # the last one leaves it
    assert config.MIN_DISTANCE + config.LETTER_SIZE == HIT_AREA


def normal_letters_in_the_bar(game):
    return [
        letter for letter in game.letters if not letter.gold and letter.in_action_bar()
    ]


def test_a_perfect_game_at_the_max_level():
    # always one normal letter in the action bar (two only for one frame, when
    # one leaves and the next arrives, both on the edges of the hit area)
    game = Game(rng=random.Random(1))
    game.start_new_game()
    set_points(game, 200)
    play(game, 400)  # the bar is full of letters

    counts = []
    for _ in range(600):
        play(game, 1)
        counts.append(len(normal_letters_in_the_bar(game)))

    assert min(counts) == 1
    assert max(counts) <= 2
    assert counts.count(2) <= len(counts) // 30  # at most 1 frame in 35


def test_before_the_max_level_there_are_moments_without_letters():
    game = Game(rng=random.Random(1))
    game.start_new_game()
    play(game, 400)

    counts = []
    for _ in range(300):
        play(game, 1)
        counts.append(len(normal_letters_in_the_bar(game)))

    assert min(counts) == 0 and max(counts) == 1


def test_gold_letter_challenge():
    assert config.GOLD_FROM_POINTS == 40
    assert (config.GOLD_EVERY_MIN_LETTERS, config.GOLD_EVERY_MAX_LETTERS) == (5, 10)
    assert config.GOLD_SPEED_FACTOR > 1
    assert config.GOLD_POINTS >= 1


def test_silver_letter_challenge():
    assert config.SILVER_FROM_POINTS == 50
    assert (config.SILVER_EVERY_MIN_LETTERS, config.SILVER_EVERY_MAX_LETTERS) == (5, 10)
    assert config.SILVER_POINTS >= 1


# y of the center of the circle: the swap, and leaving the action bar
SWAP_Y = config.ACTION_BAR_TOP - config.SILVER_SWAP_DISTANCE - config.LETTER_SIZE / 2
LEAVES_THE_BAR_Y = config.ACTION_BAR_TOP + config.ACTION_BAR_HEIGHT + config.LETTER_SIZE / 2


def test_silver_warns_from_the_top_of_the_screen():
    # the letter is already silver when it appears (y=0): almost all its fall
    assert seconds(SWAP_Y / config.MAX_SPEED) >= 1.0


def test_silver_gives_time_to_react_at_the_max_speed():
    # from the swap until the letter leaves the bar (it can be pressed until then)
    assert seconds((LEAVES_THE_BAR_Y - SWAP_Y) / config.MAX_SPEED) >= 0.8
    # the swap happens before the letter touches the bar
    assert SWAP_Y + config.LETTER_SIZE / 2 < config.ACTION_BAR_TOP


def test_touch_buttons_are_big_enough_for_a_phone():
    # the common minimum for a touch target is 48 x 48 pixels, also when the
    # game is made smaller to fit a phone (a page of 360 x 700)
    lane_width = config.LANE_LINES[1] - config.LANE_LINES[0]
    width = lane_width - config.LANE_LINE_WIDTH - 2 * config.TOUCH_BUTTON_MARGIN
    scale = min(360 / config.WIDTH, 700 / config.HEIGHT)
    assert width * scale >= 48
    assert config.TOUCH_BUTTON_HEIGHT * scale >= 48


def test_touch_buttons_between_the_action_bar_and_the_points_bar():
    bar_bottom = config.ACTION_BAR_TOP + config.ACTION_BAR_HEIGHT + 2  # press effect
    points_bar_top = config.HEIGHT - 35
    assert bar_bottom <= config.TOUCH_BUTTONS_TOP
    assert config.TOUCH_BUTTONS_TOP + config.TOUCH_BUTTON_HEIGHT <= points_bar_top


def test_gold_letter_can_be_pressed_at_the_max_speed():
    gold_speed = config.MAX_SPEED * config.GOLD_SPEED_FACTOR
    assert seconds(HIT_AREA / gold_speed) >= 0.3  # was 0.26 s (too fast)


def test_gold_letter_is_faster_but_not_too_fast():
    assert 1 < config.GOLD_SPEED_FACTOR <= 1.5
    assert config.MAX_SPEED * config.GOLD_SPEED_FACTOR * config.FPS <= 405  # px/s


def test_game_over_transition_takes_about_three_seconds():
    frames = (config.SLOW_MOTION_STEPS + 1) * config.SLOW_MOTION_STEP_FRAMES
    assert 2 <= seconds(frames) <= 3.5
