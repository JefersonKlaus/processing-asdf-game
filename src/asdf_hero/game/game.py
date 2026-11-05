"""The game rules: pages, letters, points, level and game over."""

import random

from asdf_hero import config
from asdf_hero.game import level
from asdf_hero.game.action_bar import ActionBar
from asdf_hero.game.button import Button
from asdf_hero.game.letter import Letter, is_game_key
from asdf_hero.game.states import GamePage, LetterStatus


class Game:
    """
    One game (one player). ``update()`` runs one frame, the input methods are
    called between frames.
    """

    def __init__(
        self,
        width: float = config.WIDTH,
        height: float = config.HEIGHT,
        rng: random.Random | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.rng = rng or random.Random()

        self.page = GamePage.START
        self.points = 0
        self.speed = level.speed_for(0)
        self.distance = level.distance_for(0)
        self.letters: list[Letter] = []
        self.action_bar = ActionBar()
        self.button = Button(
            x=width / 2 - config.BUTTON_WIDTH / 2,
            y=height / 2 - config.BUTTON_HEIGHT,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
        )

        # gold letter: normal letters left before the next gold letter
        self.letters_until_gold: int | None = None
        self.gold_pending = False

        # transition to game over (slow motion)
        self.transition_to_game_over = False
        self.slow_motion_steps = 0
        self._slow_motion_frames = 0

    # --- input ----------------------------------------------------------------

    def key_pressed(self, key: str) -> None:
        """
        Right letter in the action bar: one point. Pressed at the wrong
        moment (the letter is not in the action bar): game over.
        """
        if self.page != GamePage.RUNNING or self.transition_to_game_over:
            return
        if not is_game_key(key):  # other keys are ignored
            return

        # one press hits one letter: the lowest one (the next to leave the bar)
        targets = [letter for letter in self.letters if letter.can_be_pressed(key)]
        hit = max(targets, key=lambda letter: letter.y) if targets else None
        pressed_again = any(letter.already_pressed(key) for letter in self.letters)
        correct = hit is not None or pressed_again

        # yellow: right press / red: wrong moment (game over)
        self.action_bar.press(correct=correct)

        if hit is not None:
            hit.press(key)
            self._add_point()
        elif not correct:
            # wrong moment: no letter with this key in the action bar
            self.transition_to_game_over = True

    def mouse_pressed(self, x: float, y: float) -> None:
        if self.page == GamePage.RUNNING:
            return
        if self.button.contains(x, y):
            self.button.clicked = True
            self.start_new_game()

    def mouse_released(self) -> None:
        self.button.clicked = False

    # --- game -----------------------------------------------------------------

    def start_new_game(self) -> None:
        self.letters = []
        self.points = 0
        self._update_level()
        self.action_bar.reset()
        self.letters_until_gold = None
        self.gold_pending = False
        self.transition_to_game_over = False
        self.slow_motion_steps = 0
        self._slow_motion_frames = 0
        self.page = GamePage.RUNNING

    def update(self) -> None:
        """One frame."""
        if self.page != GamePage.RUNNING:
            return

        if self.transition_to_game_over:
            # slow motion: one game step every SLOW_MOTION_STEP_FRAMES frames
            self._slow_motion_frames += 1
            if self._slow_motion_frames < config.SLOW_MOTION_STEP_FRAMES:
                return
            self._slow_motion_frames = 0
            if self.slow_motion_steps >= config.SLOW_MOTION_STEPS:
                self.page = GamePage.GAME_OVER
                return
            self.slow_motion_steps += 1

        self._step()

    def _step(self) -> None:
        """Move the game forward: new letters, move letters, game over."""
        self.action_bar.update()
        self._add_letter_if_needed()
        self._add_gold_letter_if_needed()

        for letter in self.letters:
            # normal letters use the same speed, so they never overlap;
            # gold letters fall faster (surprise)
            speed = self.speed * config.GOLD_SPEED_FACTOR if letter.gold else self.speed
            letter.move(speed)
            if letter.status == LetterStatus.FAILED:
                self.transition_to_game_over = True

        # remove the letters that left the screen
        self.letters = [
            letter
            for letter in self.letters
            if letter.y <= self.height + letter.size
        ]

    def _last_normal_letter(self) -> Letter | None:
        normal = [letter for letter in self.letters if not letter.gold]
        return normal[-1] if normal else None

    def _add_letter_if_needed(self) -> None:
        last = self._last_normal_letter()
        if last is not None and last.y < self.distance + last.size:
            return
        random_char = self.points >= config.RANDOM_CHARS_FROM_POINTS
        self.letters.append(self._new_letter(random_char))
        self._count_letter_for_gold()

    def _new_letter(self, random_char: bool) -> Letter:
        lane = self.rng.randrange(len(config.LANE_CENTERS))
        if random_char:
            char = config.CHARS[self.rng.randrange(len(config.CHARS))]
        else:
            char = config.CHARS[lane]
        return Letter(lane, char, self.action_bar)

    # --- gold letter (challenge) ------------------------------------------------

    def _count_letter_for_gold(self) -> None:
        """From GOLD_FROM_POINTS, a gold letter comes after 5 to 10 letters."""
        if self.points < config.GOLD_FROM_POINTS:
            return
        if self.letters_until_gold is None:
            self.letters_until_gold = self.rng.randint(
                config.GOLD_EVERY_MIN_LETTERS, config.GOLD_EVERY_MAX_LETTERS
            )
        self.letters_until_gold -= 1
        if self.letters_until_gold == 0:
            self.letters_until_gold = None  # a new random count after this one
            self.gold_pending = True

    def _add_gold_letter_if_needed(self) -> None:
        """The gold letter starts halfway between two normal letters."""
        if not self.gold_pending:
            return
        last = self._last_normal_letter()
        if last is not None and last.y < (self.distance + last.size) / 2:
            return
        self.gold_pending = False
        self.letters.append(self._new_gold_letter())

    def _new_gold_letter(self) -> Letter:
        # avoid the lanes of letters that are still coming: the gold letter
        # passes them, and they must not be on top of each other
        busy = {
            letter.lane
            for letter in self.letters
            if letter.status == LetterStatus.WAITING
        }
        lanes = [lane for lane in range(len(config.LANE_CENTERS)) if lane not in busy]
        lanes = lanes or list(range(len(config.LANE_CENTERS)))
        lane = lanes[self.rng.randrange(len(lanes))]
        char = config.CHARS[self.rng.randrange(len(config.CHARS))]
        return Letter(lane, char, self.action_bar, gold=True)

    # --- level ----------------------------------------------------------------

    def _add_point(self) -> None:
        self.points += 1
        self._update_level()

    def _update_level(self) -> None:
        self.speed = level.speed_for(self.points)
        self.distance = level.distance_for(self.points)
