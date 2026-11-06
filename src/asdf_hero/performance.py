"""
Performance logs: find out why the game gets slow.

``PerformanceMonitor.frame()`` receives the time of each part of every frame.
Every PERFORMANCE_REPORT_SECONDS of game it logs one line: frames per second,
the average and the slowest frame (split in its parts), the garbage collector
and the CPU. The line is a WARNING when the game was slow, INFO otherwise.

How to read a slow report (the slowest frame):
- ``update`` / ``render`` big: the game rules / the views are slow;
- ``send`` big: ``page.update()`` (Flet sends the changes to the screen);
- ``late`` big: the frame started late, something else kept Python busy
  (another browser tab, the garbage collector, the phone);
- ``gc`` big: the garbage collector paused the game.
"""

import gc
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, fields

from asdf_hero import config

logger = logging.getLogger(__name__)


@dataclass
class FrameTimes:
    """The time of each part of one frame, in seconds."""

    input: float = 0.0  # queued keys / taps
    update: float = 0.0  # game rules
    render: float = 0.0  # views
    send: float = 0.0  # page.update(): the changes go to the screen
    late: float = 0.0  # the frame started late (the event loop was busy)

    @property
    def work(self) -> float:
        """The time of the frame itself (without ``late``)."""
        return self.input + self.update + self.render + self.send

    def describe(self) -> str:
        parts = ", ".join(
            f"{part.name} {getattr(self, part.name) * 1000:.1f}" for part in fields(self)
        )
        return f"{self.work * 1000:.1f} ms ({parts} ms)"


class GcWatch:
    """Time spent in the garbage collector (it pauses everything)."""

    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        self.clock = clock
        self._started = 0.0
        self.reset()

    def reset(self) -> None:
        self.collections = 0
        self.total = 0.0
        self.longest = 0.0

    def callback(self, phase: str, info: dict) -> None:
        if phase == "start":
            self._started = self.clock()
            return
        duration = self.clock() - self._started
        self.collections += 1
        self.total += duration
        self.longest = max(self.longest, duration)

    def start(self) -> None:
        gc.callbacks.append(self.callback)

    def stop(self) -> None:
        if self.callback in gc.callbacks:
            gc.callbacks.remove(self.callback)


class PerformanceMonitor:
    """Collects the frame times and logs a report every ``report_seconds``."""

    def __init__(
        self,
        report_seconds: float = config.PERFORMANCE_REPORT_SECONDS,
        clock: Callable[[], float] = time.perf_counter,
        cpu_clock: Callable[[], float] = time.process_time,
    ) -> None:
        self.report_seconds = report_seconds
        self.clock = clock
        self.cpu_clock = cpu_clock
        self.gc = GcWatch(clock)
        self._last_frame: float | None = None
        self.letters = 0  # letters on the screen in the last frame
        self._reset()

    def start(self) -> None:
        self.gc.start()

    def stop(self) -> None:
        self.gc.stop()

    def _reset(self) -> None:
        self.frames = 0
        self.seconds = 0.0  # time between the frames of this report
        self.parts = FrameTimes()  # sum of each part
        self.slowest = FrameTimes()
        self._cpu_started = self.cpu_clock()
        self.gc.reset()

    def frame(self, times: FrameTimes, letters: int) -> None:
        """One frame of the game loop (call it at the end of the frame)."""
        now, last = self.clock(), self._last_frame
        self._last_frame = now
        if last is None:  # the first frame: the time starts here
            return
        interval = now - last
        if interval > config.PAUSE_SECONDS:
            # the game was paused (hidden tab, app in the background)
            logger.debug("The game was paused for %.1f s", interval)
            self._reset()
            return

        self.frames += 1
        self.seconds += interval
        for part in fields(FrameTimes):
            name = part.name
            setattr(self.parts, name, getattr(self.parts, name) + getattr(times, name))
        if times.work + times.late > self.slowest.work + self.slowest.late:
            self.slowest = times
        self.letters = letters

        if self.seconds >= self.report_seconds:
            self.report()
            self._reset()

    def report(self) -> None:
        fps = self.frames / self.seconds
        slowest_ms = (self.slowest.work + self.slowest.late) * 1000
        slow = fps < config.MIN_GOOD_FPS or slowest_ms > config.FREEZE_MS
        cpu = (self.cpu_clock() - self._cpu_started) / self.seconds * 100
        average = FrameTimes(
            **{
                part.name: getattr(self.parts, part.name) / self.frames
                for part in fields(FrameTimes)
            }
        )
        logger.log(
            logging.WARNING if slow else logging.INFO,
            "%s: %.1f fps in %.1f s | frame avg %s | slowest %s | "
            "GC %d collections, %.1f ms, longest %.1f ms | CPU %.0f%% | %d letters",
            "Slow game" if slow else "Performance",
            fps,
            self.seconds,
            average.describe(),
            self.slowest.describe(),
            self.gc.collections,
            self.gc.total * 1000,
            self.gc.longest * 1000,
            cpu,
            self.letters,
        )
