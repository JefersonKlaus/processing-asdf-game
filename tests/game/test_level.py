import pytest

from asdf_hero import config
from asdf_hero.game.level import distance_for, speed_for


@pytest.mark.parametrize(
    "points, speed, distance",
    [
        (-10, 3.0, 150),  # negative points: initial level
        (0, 3.0, 150),
        (1, 3.02, 149.5),
        (10, 3.2, 145),
        (50, 4.0, 125),
        (99, 4.98, 100.5),
        (100, 5.0, 100),  # max level
        (101, 5.0, 100),
        (500, 5.0, 100),
    ],
)
def test_level_by_points(points, speed, distance):
    assert speed_for(points) == pytest.approx(speed)
    assert distance_for(points) == pytest.approx(distance)


class TestLevelDesign:
    """The rules agreed for the game level. Update them if the design changes."""

    def test_starts_slow(self):
        assert speed_for(0) < config.MAX_SPEED
        assert speed_for(0) * config.FPS == 180  # pixels per second

    def test_max_speed_is_not_too_fast(self):
        # room for new challenges later: max 300 px/s
        assert config.MAX_SPEED * config.FPS <= 300

    def test_gets_faster_and_closer_with_points(self):
        points = range(-20, 300)
        speeds = [speed_for(p) for p in points]
        distances = [distance_for(p) for p in points]

        assert speeds == sorted(speeds)
        assert distances == sorted(distances, reverse=True)
        assert (min(speeds), max(speeds)) == (config.INIT_SPEED, config.MAX_SPEED)
        assert (max(distances), min(distances)) == (
            config.INIT_DISTANCE,
            config.MIN_DISTANCE,
        )

    def test_more_letters_come_faster_at_the_max_level(self):
        # frames between two letters = (distance + size) / speed
        def frames_between_letters(points):
            return (distance_for(points) + config.LETTER_SIZE) / speed_for(points)

        assert frames_between_letters(500) < frames_between_letters(0) / 2

    def test_gold_letter_is_a_challenge_from_50_points(self):
        assert config.GOLD_FROM_POINTS == 50
        assert (config.GOLD_EVERY_MIN_LETTERS, config.GOLD_EVERY_MAX_LETTERS) == (5, 10)
        assert config.GOLD_SPEED_FACTOR > 1  # faster than the other letters

    def test_gold_letter_can_still_be_pressed_at_the_max_speed(self):
        # time (seconds) the gold circle touches the action bar at max speed
        hit_area = config.ACTION_BAR_HEIGHT + config.LETTER_SIZE
        gold_speed = config.MAX_SPEED * config.GOLD_SPEED_FACTOR
        assert hit_area / gold_speed / config.FPS >= 0.2

    def test_only_one_letter_in_the_action_bar(self):
        # normal letters (the gold letter is the exception: it passes them).
        # A letter is in the action bar while its circle touches it, so the
        # hit area is the bar + one letter size. Letters are at least
        # MIN_DISTANCE + size apart: never two normal letters in the action
        # bar at the same time
        hit_area = config.ACTION_BAR_HEIGHT + config.LETTER_SIZE
        assert config.MIN_DISTANCE + config.LETTER_SIZE > hit_area + config.MAX_SPEED
