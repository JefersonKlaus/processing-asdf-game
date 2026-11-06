"""
Challenges: surprises that start after some points (gold, silver letters).

To add a challenge: create a Challenge subclass with its schedule, and add it
to ``Game.challenges``.
"""

from asdf_hero.game.challenges.base import Challenge, ChallengeSchedule
from asdf_hero.game.challenges.gold import GoldChallenge
from asdf_hero.game.challenges.silver import SilverChallenge

__all__ = ["Challenge", "ChallengeSchedule", "GoldChallenge", "SilverChallenge"]
