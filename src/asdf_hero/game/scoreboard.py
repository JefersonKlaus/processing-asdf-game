"""The best results (in memory: they are kept while the server runs)."""

from dataclasses import dataclass
from datetime import datetime

from asdf_hero import config


@dataclass(frozen=True)
class Result:
    points: int
    when: datetime


class Scoreboard:
    def __init__(self, size: int = config.SCOREBOARD_SIZE) -> None:
        self.size = size
        self._results: list[Result] = []

    def add(self, points: int, when: datetime) -> Result:
        """Add the result of a game (only the best ``size`` results are kept)."""
        result = Result(points, when)
        self._results.append(result)
        # more points first; same points: the oldest first
        self._results.sort(key=lambda item: (-item.points, item.when))
        del self._results[self.size :]
        return result

    @property
    def best(self) -> list[Result]:
        return list(self._results)
