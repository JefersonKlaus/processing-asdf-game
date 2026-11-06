"""Game level: speed and distance by points."""

import pytest

from asdf_hero import config
from asdf_hero.game.level import distance_for, speed_for

STEP = 1.0 / 51  # speed added by each point (3.0 -> 4.0)


@pytest.mark.parametrize(
    "points, speed, distance",
    [
        (-10, 3.0, 150),  # negative points: initial level
        (0, 3.0, 150),
        # 1. faster letters (the same distance)
        (1, 3.0 + STEP, 150),
        (25, 3.0 + 25 * STEP, 150),
        (50, 3.0 + 50 * STEP, 150),
        (51, 4.0, 150),  # max speed
        # 2. more letters (the same speed): 1 px closer for each point
        (52, 4.0, 149),
        (100, 4.0, 101),
        (121, 4.0, 80),  # max level: always one letter in the action bar
        (500, 4.0, 80),
    ],
)
def test_level_by_points(points, speed, distance):
    assert speed_for(points) == pytest.approx(speed)
    assert distance_for(points) == pytest.approx(distance)


def test_max_speed_at_51_points():
    assert speed_for(50) < config.MAX_SPEED == 4.0
    assert speed_for(51) == config.MAX_SPEED  # exact (no rounding)


def test_more_letters_only_after_the_max_speed():
    assert {distance_for(points) for points in range(52)} == {config.INIT_DISTANCE}
    assert distance_for(52) < config.INIT_DISTANCE


def test_gets_faster_and_closer_with_points():
    points = range(-20, 300)
    speeds = [speed_for(p) for p in points]
    distances = [distance_for(p) for p in points]

    assert speeds == sorted(speeds)
    assert distances == sorted(distances, reverse=True)
