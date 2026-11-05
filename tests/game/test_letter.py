"""Letter: fall, status and key press."""

import pytest

from asdf_hero import config
from asdf_hero.game import ActionBar, Letter, LetterStatus

WAITING = LetterStatus.WAITING
NEED = LetterStatus.NEED_BE_PRESSED
PRESSED = LetterStatus.WAS_PRESSED
FAILED = LetterStatus.FAILED


def make_letter(lane=1, y=0.0, status=WAITING, char=None):
    letter = Letter(lane, char or config.LEFT_HAND_KEYS[lane], ActionBar())
    letter.y = y
    letter.status = status
    return letter


@pytest.mark.parametrize("lane", [0, 3])
def test_starts_at_the_top_of_its_lane(lane):
    letter = make_letter(lane=lane)

    assert (letter.x, letter.y) == (config.LANE_CENTERS[lane], 0)
    assert letter.status == WAITING
    assert letter.gold is False


def test_unique_ids():
    assert make_letter().id != make_letter().id


def test_move():
    letter = make_letter(y=100)

    letter.move(3.5)

    assert letter.y == 103.5


@pytest.mark.parametrize(
    "y, status, expected",
    [
        (560, WAITING, WAITING),  # circle above the bar
        (564, WAITING, NEED),  # circle touches the bar
        (700, NEED, NEED),  # center below the bar, circle still touches it
        (710, NEED, FAILED),  # circle left the bar without a press
        (640, PRESSED, PRESSED),
        (720, PRESSED, PRESSED),
        (720, FAILED, FAILED),
    ],
)
def test_status_after_a_move(y, status, expected):
    letter = make_letter(y=y, status=status)

    letter.move(5)

    assert letter.status == expected


@pytest.mark.parametrize("speed", [3, 10])  # slowest normal, fastest gold
def test_every_speed_gives_time_to_press(speed):
    letter = make_letter()
    seen = set()

    while letter.y < 800:
        letter.move(speed)
        seen.add(letter.status)

    assert seen == {WAITING, NEED, FAILED}


@pytest.mark.parametrize(
    "status, key, expected",
    [(NEED, "s", True), (NEED, "S", True), (NEED, "a", False), (WAITING, "s", False), (PRESSED, "s", False)],
)
def test_press(status, key, expected):
    letter = make_letter(lane=1, y=640, status=status)

    assert letter.press(key) is expected
    assert letter.status == (PRESSED if expected else status)


def test_press_uses_the_char_not_the_lane():
    letter = make_letter(lane=0, y=640, status=NEED, char="F")

    assert letter.press("a") is False
    assert letter.press("f") is True


def test_press_with_another_name_of_the_key():
    letter = make_letter(lane=3, y=640, status=NEED, char="Ç")

    assert letter.press(";") is True


@pytest.mark.parametrize(
    "status, y, key, expected",
    [
        (PRESSED, 640, "s", True),  # pressed and still in the bar
        (PRESSED, 720, "s", False),  # left the bar
        (PRESSED, 640, "a", False),  # other key
        (NEED, 640, "s", False),  # not pressed yet
    ],
)
def test_already_pressed(status, y, key, expected):
    assert make_letter(lane=1, y=y, status=status).already_pressed(key) is expected
