"""Helpers used by the tests."""

from datetime import datetime

from asdf_hero import config
from asdf_hero.game import GamePage, LetterStatus

# frames from the start of the transition until the game over page
GAME_OVER_FRAMES = (config.SLOW_MOTION_STEPS + 1) * config.SLOW_MOTION_STEP_FRAMES


def frames(game, count):
    for _ in range(count):
        game.update()


def center(button):
    return (button.x + button.width / 2, button.y + button.height / 2)


def fill_scoreboard(board, points=1000):
    """Full best results: a new game does not enter them (no congratulations)."""
    for minute in range(board.size):
        board.add(points, datetime(2025, 1, 1, 10, minute), "Old")


def set_points(game, points):
    """Set the points and update the game level."""
    game.points = points
    game._update_level()


def play(game, frame_count, press=True):
    """A perfect player: presses each letter as soon as it can (lowest first)."""
    for _ in range(frame_count):
        game.update()
        if game.page != GamePage.RUNNING:
            return
        if press:
            for letter in sorted(game.letters, key=lambda item: -item.y):
                if letter.status == LetterStatus.NEED_BE_PRESSED:
                    game.key_pressed(letter.char)
