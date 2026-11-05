"""Game level: speed and distance by points."""

import pytest

from asdf_hero.game.level import distance_for, speed_for


@pytest.mark.parametrize(
    "points, speed, distance",
    [
        (-10, 3.0, 150),  # negative points: initial level
        (0, 3.0, 150),
        (1, 3.02, 149.5),
        (50, 4.0, 125),
        (75, 4.5, 112.5),  # max speed
        (100, 4.5, 100),  # max level
        (500, 4.5, 100),
    ],
)
def test_level_by_points(points, speed, distance):
    assert speed_for(points) == pytest.approx(speed)
    assert distance_for(points) == pytest.approx(distance)


def test_gets_faster_and_closer_with_points():
    points = range(-20, 300)
    speeds = [speed_for(p) for p in points]
    distances = [distance_for(p) for p in points]

    assert speeds == sorted(speeds)
    assert distances == sorted(distances, reverse=True)
