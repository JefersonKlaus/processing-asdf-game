"""
Game level: the speed of the letters and the distance between them.

More points = faster letters and closer to each other, between the initial
level (0 points or less) and the max level.
"""

from asdf_hero import config


def speed_for(points: int) -> float:
    points = max(points, 0)
    return min(
        config.INIT_SPEED + points * config.SPEED_STEP_BY_POINT, config.MAX_SPEED
    )


def distance_for(points: int) -> float:
    points = max(points, 0)
    return max(
        config.INIT_DISTANCE - points * config.DISTANCE_STEP_BY_POINT,
        config.MIN_DISTANCE,
    )
