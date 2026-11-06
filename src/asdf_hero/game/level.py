"""
Game level: the speed of the letters and the distance between them.

First the letters get faster (until MAX_SPEED_FROM_POINTS), then there are
more letters: they get closer until there is always one in the action bar.
"""

from asdf_hero import config


def speed_for(points: int) -> float:
    """From INIT_SPEED (0 points) to MAX_SPEED (MAX_SPEED_FROM_POINTS), evenly."""
    progress = min(max(points, 0), config.MAX_SPEED_FROM_POINTS)
    step = (config.MAX_SPEED - config.INIT_SPEED) / config.MAX_SPEED_FROM_POINTS
    return config.INIT_SPEED + progress * step


def distance_for(points: int) -> float:
    """INIT_DISTANCE until the max speed, then closer until MIN_DISTANCE."""
    more_letters = max(points - config.MAX_SPEED_FROM_POINTS, 0)
    return max(
        config.INIT_DISTANCE - more_letters * config.DISTANCE_STEP_BY_POINT,
        config.MIN_DISTANCE,
    )
