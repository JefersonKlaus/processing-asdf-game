import pytest

from asdf_hero import config
from asdf_hero.game import ActionBar, Letter, LetterStatus, is_game_key


def make_letter(lane=1, y=0.0, status=LetterStatus.WAITING, char=None):
    letter = Letter(lane, char or config.CHARS[lane], ActionBar())
    letter.y = y
    letter.status = status
    return letter


class TestGameKeys:
    @pytest.mark.parametrize("key", ["a", "A", "s", "S", "d", "D", "f", "F"])
    def test_game_keys(self, key):
        assert is_game_key(key) is True

    @pytest.mark.parametrize("key", ["g", "1", " ", "", "Arrow Up", "Enter", "AS"])
    def test_other_keys(self, key):
        assert is_game_key(key) is False


class TestInit:
    @pytest.mark.parametrize("lane", range(4))
    def test_position_of_the_lane(self, lane):
        letter = Letter(lane, "A", ActionBar())

        assert letter.lane == lane
        assert letter.x == config.LANE_CENTERS[lane]
        assert letter.y == 0
        assert letter.char == "A"

    def test_defaults(self):
        letter = make_letter()

        assert letter.status == LetterStatus.WAITING
        assert letter.size == config.LETTER_SIZE

    def test_unique_ids(self):
        assert make_letter().id != make_letter().id

    def test_not_gold_by_default(self):
        assert make_letter().gold is False

    def test_gold(self):
        assert Letter(0, "A", ActionBar(), gold=True).gold is True


class TestMove:
    @pytest.mark.parametrize("dy", [1, 3.5, 5])
    def test_moves_down(self, dy):
        letter = make_letter(y=100)

        letter.move(dy)

        assert letter.y == pytest.approx(100 + dy)

    def test_stays_waiting_above_the_action_bar(self):
        letter = make_letter(y=560)

        letter.move(5)  # circle bottom at 596: above the bar

        assert letter.status == LetterStatus.WAITING

    @pytest.mark.parametrize("y", [564, 600, 640, 706])
    def test_waiting_becomes_need_be_pressed(self, y):
        # the circle touches the bar: center from 569 to 711
        letter = make_letter(y=y)

        letter.move(5)

        assert letter.status == LetterStatus.NEED_BE_PRESSED

    def test_need_be_pressed_fails_after_the_action_bar(self):
        letter = make_letter(y=710, status=LetterStatus.NEED_BE_PRESSED)

        letter.move(5)  # circle top at 684: left the bar

        assert letter.status == LetterStatus.FAILED

    def test_still_in_the_bar_while_the_circle_touches_it(self):
        letter = make_letter(y=700, status=LetterStatus.NEED_BE_PRESSED)

        letter.move(5)  # center below the bar, circle still touches it

        assert letter.status == LetterStatus.NEED_BE_PRESSED

    @pytest.mark.parametrize(
        "status", [LetterStatus.WAS_PRESSED, LetterStatus.FAILED, LetterStatus.WAITING]
    )
    def test_other_statuses_do_not_change_below_the_bar(self, status):
        letter = make_letter(y=720, status=status)

        letter.move(5)

        assert letter.status == status

    def test_was_pressed_is_final_in_the_bar(self):
        letter = make_letter(y=640, status=LetterStatus.WAS_PRESSED)

        letter.move(5)

        assert letter.status == LetterStatus.WAS_PRESSED

    @pytest.mark.parametrize("speed", [3, 4.2, 5])
    def test_full_fall_without_press_fails(self, speed):
        letter = make_letter()
        seen = set()

        while letter.y < 800:
            letter.move(speed)
            seen.add(letter.status)

        assert seen == {
            LetterStatus.WAITING,
            LetterStatus.NEED_BE_PRESSED,
            LetterStatus.FAILED,
        }


class TestPress:
    @pytest.mark.parametrize("key", ["s", "S"])
    def test_right_key_in_the_bar(self, key):
        letter = make_letter(lane=1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        assert letter.press(key) is True
        assert letter.status == LetterStatus.WAS_PRESSED

    def test_wrong_key(self):
        letter = make_letter(lane=1, y=640, status=LetterStatus.NEED_BE_PRESSED)

        assert letter.press("a") is False
        assert letter.status == LetterStatus.NEED_BE_PRESSED

    @pytest.mark.parametrize(
        "status", [LetterStatus.WAITING, LetterStatus.WAS_PRESSED, LetterStatus.FAILED]
    )
    def test_right_key_outside_the_bar(self, status):
        letter = make_letter(lane=1, status=status)

        assert letter.press("s") is False
        assert letter.status == status

    @pytest.mark.parametrize(
        "status, key, expected",
        [
            (LetterStatus.NEED_BE_PRESSED, "s", True),
            (LetterStatus.NEED_BE_PRESSED, "a", False),
            (LetterStatus.WAITING, "s", False),
            (LetterStatus.WAS_PRESSED, "s", False),
        ],
    )
    def test_can_be_pressed(self, status, key, expected):
        letter = make_letter(lane=1, y=640, status=status)

        assert letter.can_be_pressed(key) is expected
        assert letter.status == status  # only checks

    def test_random_char_uses_the_char_not_the_lane(self):
        letter = make_letter(lane=0, char="F", status=LetterStatus.NEED_BE_PRESSED)

        assert letter.press("a") is False
        assert letter.press("f") is True


class TestActionBarHelpers:
    @pytest.mark.parametrize(
        "y, expected",
        [(568, False), (569, True), (640, True), (711, True), (712, False)],
    )
    def test_in_action_bar_while_the_circle_touches_it(self, y, expected):
        assert make_letter(y=y).in_action_bar() is expected

    @pytest.mark.parametrize("key", ["s", "S"])
    def test_already_pressed(self, key):
        letter = make_letter(lane=1, y=640, status=LetterStatus.WAS_PRESSED)

        assert letter.already_pressed(key) is True

    @pytest.mark.parametrize(
        "status, y, key",
        [
            (LetterStatus.WAS_PRESSED, 720, "s"),  # left the action bar
            (LetterStatus.WAS_PRESSED, 640, "a"),  # other key
            (LetterStatus.NEED_BE_PRESSED, 640, "s"),  # not pressed yet
            (LetterStatus.WAITING, 300, "s"),
        ],
    )
    def test_not_already_pressed(self, status, y, key):
        letter = make_letter(lane=1, y=y, status=status)

        assert letter.already_pressed(key) is False
