"""The best results. Where they are kept is chosen by the app (a ResultStore)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from asdf_hero import config


@dataclass(frozen=True)
class Result:
    points: int
    when: datetime
    name: str = ""  # empty: anonymous


class ResultStore(Protocol):
    """Keeps the best results between runs (see asdf_hero.storage)."""

    def load(self) -> list[Result]: ...

    def save(self, results: list[Result]) -> None: ...


class MemoryResultStore:
    """Keeps the results only in memory (lost when the app stops)."""

    def __init__(self) -> None:
        self._results: list[Result] = []

    def load(self) -> list[Result]:
        return list(self._results)

    def save(self, results: list[Result]) -> None:
        self._results = list(results)


def player_name(text: str) -> str:
    """The name as it is saved: no extra spaces, max length (empty: anonymous)."""
    return " ".join(text.split())[: config.NAME_MAX_LENGTH].strip()


class Scoreboard:
    def __init__(
        self, size: int = config.SCOREBOARD_SIZE, store: ResultStore | None = None
    ) -> None:
        self.size = size
        self.store = store or MemoryResultStore()
        self._results = self._best_of(self.store.load())

    def _best_of(self, results: list[Result]) -> list[Result]:
        # only results with points; more points first; same points: the oldest
        valid = [item for item in results if item.points >= config.MIN_BEST_RESULT_POINTS]
        return sorted(valid, key=lambda item: (-item.points, item.when))[: self.size]

    def qualifies(self, points: int) -> bool:
        """True when a new result with these points enters the best results."""
        if points < config.MIN_BEST_RESULT_POINTS:  # 0 points: never
            return False
        # same points as the last one: the new result is newer, so it is out
        return len(self._results) < self.size or points > self._results[-1].points

    def add(self, points: int, when: datetime, name: str = "") -> Result:
        """Add the result of a game (only the best ``size`` results are kept)."""
        result = Result(points, when, player_name(name))
        self._results = self._best_of([*self._results, result])
        self.store.save(self._results)
        return result

    @property
    def best(self) -> list[Result]:
        return list(self._results)
