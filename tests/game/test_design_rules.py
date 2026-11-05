"""
The rules agreed for the game design (config.py). If the design changes,
update these tests on purpose.
"""

from asdf_hero import config
from asdf_hero.game.level import distance_for, speed_for

HIT_AREA = config.ACTION_BAR_HEIGHT + config.LETTER_SIZE  # circle touches the bar


def seconds(frames):
    return frames / config.FPS


def test_starts_slow():
    assert speed_for(0) * config.FPS == 180  # pixels per second


def test_max_speed_is_not_too_fast():
    # room for the challenges: max 270 px/s
    assert config.MAX_SPEED * config.FPS == 270


def test_letters_come_faster_at_the_max_level():
    def frames_between_letters(points):
        return (distance_for(points) + config.LETTER_SIZE) / speed_for(points)

    assert frames_between_letters(500) < frames_between_letters(0)


def test_only_one_normal_letter_in_the_action_bar():
    # normal letters are at least MIN_DISTANCE + size apart, so a key press is
    # never ambiguous (only the gold letter can pass them)
    assert config.MIN_DISTANCE + config.LETTER_SIZE > HIT_AREA + config.MAX_SPEED


def test_gold_letter_challenge():
    assert config.GOLD_FROM_POINTS == 40
    assert (config.GOLD_EVERY_MIN_LETTERS, config.GOLD_EVERY_MAX_LETTERS) == (5, 10)
    assert config.GOLD_SPEED_FACTOR > 1
    assert config.GOLD_POINTS >= 1


def test_swap_challenge():
    assert config.SWAP_FROM_POINTS == 50
    assert (config.SWAP_EVERY_MIN_LETTERS, config.SWAP_EVERY_MAX_LETTERS) == (5, 10)
    assert config.SWAP_POINTS >= 1


def test_swap_gives_time_to_react_at_the_max_speed():
    # from the swap until the circle touches the bar
    assert config.SWAP_DISTANCE == 150
    assert seconds(config.SWAP_DISTANCE / config.MAX_SPEED) >= 0.5


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
    assert seconds(HIT_AREA / gold_speed) >= 0.2


def test_game_over_transition_takes_about_three_seconds():
    frames = (config.SLOW_MOTION_STEPS + 1) * config.SLOW_MOTION_STEP_FRAMES
    assert 2 <= seconds(frames) <= 3.5
