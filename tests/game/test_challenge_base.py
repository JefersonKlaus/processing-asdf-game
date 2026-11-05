"""
The base of the challenges: the schedule (from some points, a challenge
after 5 to 10 letters) and the hooks called by the game.
"""

import random

import pytest

from asdf_hero.game.challenges import Challenge, ChallengeSchedule
from tests.conftest import ScriptedRandom


def schedule(rng=None):
    return ChallengeSchedule(from_points=40, every_min=5, every_max=10, rng=rng or random.Random(0))


def letters_until_due(sched, points=40, limit=100):
    for count in range(1, limit):
        if sched.count_letter(points):
            return count
    return None


def test_nothing_before_the_points():
    sched = schedule()

    assert letters_until_due(sched, points=39) is None
    assert sched.letters_left is None


@pytest.mark.parametrize("count", [5, 10])
def test_due_after_the_random_number_of_letters(count):
    assert letters_until_due(schedule(ScriptedRandom([count]))) == count


def test_a_new_random_number_after_each_challenge():
    sched = schedule(ScriptedRandom([5, 8]))

    assert letters_until_due(sched) == 5
    assert letters_until_due(sched) == 8


def test_random_number_is_between_5_and_10():
    counts = {letters_until_due(schedule(random.Random(seed))) for seed in range(200)}

    assert counts == set(range(5, 11))


def test_reset():
    sched = schedule(ScriptedRandom([5, 9]))
    sched.count_letter(40)

    sched.reset()

    assert sched.letters_left is None
    assert letters_until_due(sched) == 9  # a new random number


class Recorder(Challenge):
    """A challenge that records when it starts."""

    def __init__(self, sched):
        super().__init__(sched)
        self.started = []

    def start(self, game, letter):
        self.started.append(letter)


def test_challenge_starts_when_due(game):
    challenge = Recorder(schedule(ScriptedRandom([2])))
    game.points = 40

    challenge.letter_added(game, "first")
    challenge.letter_added(game, "second")

    assert challenge.started == ["second"]


def test_challenge_reset_resets_the_schedule(game):
    challenge = Recorder(schedule(ScriptedRandom([5])))
    game.points = 40
    challenge.letter_added(game, "first")

    challenge.update(game)  # nothing by default
    challenge.reset()

    assert challenge.schedule.letters_left is None


def test_a_challenge_must_define_start():
    with pytest.raises(TypeError):
        Challenge(schedule())
