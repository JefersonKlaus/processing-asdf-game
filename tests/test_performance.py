"""PerformanceMonitor: frame times, reports (logs), garbage collector."""

import gc
import logging

import pytest

from asdf_hero import config
from asdf_hero.performance import FrameTimes, GcWatch, PerformanceMonitor

FRAME = 1 / 64  # exact in binary: 64 frames are exactly 1 s


class Clock:
    """A clock that only moves when the test says so."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def cpu():
    return Clock()


@pytest.fixture
def monitor(clock, cpu):
    return PerformanceMonitor(report_seconds=1.0, clock=clock, cpu_clock=cpu)


def ms(value):
    return value / 1000


def run_frames(monitor, clock, count, times=None, interval=FRAME, letters=3):
    for _ in range(count):
        clock.now += interval
        monitor.frame(times or FrameTimes(update=ms(1), render=ms(2)), letters)


def reports(caplog):
    return [r for r in caplog.records if r.name == "asdf_hero.performance"]


# --- FrameTimes ------------------------------------------------------------------


def test_frame_work_is_the_sum_of_the_parts_without_late():
    times = FrameTimes(input=ms(1), update=ms(2), render=ms(3), send=ms(4), late=ms(50))

    assert times.work == pytest.approx(ms(10))


def test_frame_description():
    times = FrameTimes(input=ms(1), update=ms(2), render=ms(3), send=ms(4), late=ms(5))

    assert times.describe() == (
        "10.0 ms (input 1.0, update 2.0, render 3.0, send 4.0, late 5.0 ms)"
    )


# --- GcWatch -------------------------------------------------------------------


def test_gc_watch_times_the_collections(clock):
    watch = GcWatch(clock)

    for duration in (ms(2), ms(8)):
        watch.callback("start", {})
        clock.now += duration
        watch.callback("stop", {})

    assert watch.collections == 2
    assert watch.total == pytest.approx(ms(10))
    assert watch.longest == pytest.approx(ms(8))

    watch.reset()
    assert (watch.collections, watch.total, watch.longest) == (0, 0, 0)


def test_gc_watch_listens_to_the_real_garbage_collector():
    watch = GcWatch()

    watch.start()
    try:
        gc.collect()
    finally:
        watch.stop()
    watch.stop()  # twice: nothing happens

    assert watch.collections >= 1
    assert watch.callback not in gc.callbacks


# --- reports ---------------------------------------------------------------------


def test_no_report_before_the_time(monitor, clock, caplog):
    with caplog.at_level(logging.DEBUG):
        run_frames(monitor, clock, 33)  # 0.5 s

    assert reports(caplog) == []


def test_report_with_a_good_frame_rate(monitor, clock, caplog):
    with caplog.at_level(logging.DEBUG):
        run_frames(monitor, clock, 65)  # the first frame only starts the time

    [report] = reports(caplog)
    assert report.levelno == logging.INFO
    message = report.getMessage()
    assert message.startswith("Performance: 64.0 fps in 1.0 s")
    assert "frame avg 3.0 ms (input 0.0, update 1.0, render 2.0" in message
    assert "3 letters" in message


def test_low_frame_rate_is_a_warning(monitor, clock, caplog):
    with caplog.at_level(logging.INFO):
        run_frames(monitor, clock, 33, interval=1 / 32)

    [report] = reports(caplog)
    assert report.levelno == logging.WARNING
    assert report.getMessage().startswith("Slow game: 32.0 fps")


def test_a_freeze_is_a_warning_with_the_slowest_frame(monitor, clock, caplog):
    with caplog.at_level(logging.INFO):
        run_frames(monitor, clock, 30)
        # one slow frame: sending the changes to the screen took 150 ms
        run_frames(monitor, clock, 1, FrameTimes(send=ms(150)), interval=0.15)
        run_frames(monitor, clock, 30)

    [report] = reports(caplog)
    assert report.levelno == logging.WARNING
    assert "slowest 150.0 ms (input 0.0, update 0.0, render 0.0, send 150.0" in (
        report.getMessage()
    )


def test_a_late_frame_is_the_slowest(monitor, clock, caplog):
    # the frame itself is fast, but it started 200 ms late (busy event loop)
    with caplog.at_level(logging.INFO):
        run_frames(monitor, clock, 30)
        run_frames(monitor, clock, 1, FrameTimes(update=ms(1), late=ms(200)), interval=0.2)
        run_frames(monitor, clock, 30)

    [report] = reports(caplog)
    assert report.levelno == logging.WARNING
    assert "late 200.0 ms" in report.getMessage()


def test_report_shows_the_cpu_and_the_garbage_collector(monitor, clock, cpu, caplog):
    run_frames(monitor, clock, 10)
    cpu.now += 0.25  # the process used 0.25 s of CPU
    monitor.gc.callback("start", {})
    clock.now += ms(4)
    monitor.gc.callback("stop", {})

    with caplog.at_level(logging.INFO):
        run_frames(monitor, clock, 60)

    message = reports(caplog)[0].getMessage()
    assert "GC 1 collections, 4.0 ms, longest 4.0 ms" in message
    assert "CPU 2" in message  # ~25% of ~1 s


def test_a_new_report_after_each_period(monitor, clock, caplog):
    with caplog.at_level(logging.INFO):
        run_frames(monitor, clock, 65 + 64 + 64)

    assert len(reports(caplog)) == 3


def test_a_pause_is_not_a_slow_frame(monitor, clock, caplog):
    with caplog.at_level(logging.DEBUG):
        run_frames(monitor, clock, 30)
        clock.now += config.PAUSE_SECONDS + 5  # hidden tab / app in the background
        run_frames(monitor, clock, 1)
        run_frames(monitor, clock, 64)

    messages = [r.getMessage() for r in reports(caplog)]
    assert messages[0].startswith("The game was paused for")
    assert messages[1].startswith("Performance: 64.0 fps")  # only after the pause


def test_start_and_stop_the_gc_watch(monitor):
    monitor.start()
    assert monitor.gc.callback in gc.callbacks

    monitor.stop()
    assert monitor.gc.callback not in gc.callbacks
