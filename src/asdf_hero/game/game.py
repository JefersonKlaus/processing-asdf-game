"""The game rules: pages, letters, points, level and game over."""

import random
from collections.abc import Callable
from datetime import datetime

from asdf_hero import config
from asdf_hero.game import level
from asdf_hero.game.action_bar import ActionBar
from asdf_hero.game.button import Button
from asdf_hero.game.challenges import Challenge, GoldChallenge, SilverChallenge
from asdf_hero.game.letter import Letter, is_game_key, normalize_key
from asdf_hero.game.scoreboard import Result, Scoreboard
from asdf_hero.game.states import GamePage, Hand, LetterStatus

HAND_KEYS = {Hand.LEFT: config.LEFT_HAND_KEYS, Hand.RIGHT: config.RIGHT_HAND_KEYS}


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
        scoreboard: Scoreboard | None = None,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        # best results: the app shares one scoreboard between all the games
        self.scoreboard = scoreboard or Scoreboard()
        self.clock = clock
        self.last_result: Result | None = None  # result of the last game
        # congratulations page: the name typed so far, the end of the game
        self.typed_name = ""
        self._finished_at: datetime | None = None

        # lanes: a wider game (phones) has wider lanes
        self.lane_lines = tuple(x * width / config.WIDTH for x in config.LANE_LINES)
        self.lane_centers = tuple(
            (line + config.LANE_LINE_WIDTH + next_line) / 2
            for line, next_line in zip(self.lane_lines, self.lane_lines[1:])
        )

        self.page = GamePage.START
        self.hand = Hand.LEFT
        self.points = 0
        self.speed = level.speed_for(0)
        self.distance = level.distance_for(0)
        self.letters: list[Letter] = []
        self.action_bar = ActionBar()
        # start and game over pages, at the bottom of the screen: the start /
        # retry button (main action, the lowest) and, above it, the hand
        # button (left: ASDF / right: JKLÇ)
        self.button = Button(
            x=width / 2 - config.BUTTON_WIDTH / 2,
            y=height - config.BUTTONS_BOTTOM_MARGIN - config.BUTTON_HEIGHT,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
        )
        self.hand_button = Button(
            x=self.button.x,
            y=self.button.y - config.BUTTON_GAP - config.BUTTON_HEIGHT,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
        )
        # congratulations page: save the typed name / save as anonymous
        self.save_button = Button(
            x=self.button.x,
            y=config.CONGRATULATIONS_BUTTONS_TOP,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
        )
        self.anonymous_button = Button(
            x=self.button.x,
            y=self.save_button.y + config.BUTTON_HEIGHT + config.BUTTON_GAP,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
        )
        # running page: one touch button for each lane (each one is a key)
        self.touch_buttons = [
            Button(
                x=line + config.LANE_LINE_WIDTH + config.TOUCH_BUTTON_MARGIN,
                y=config.TOUCH_BUTTONS_TOP,
                width=next_line - line - config.LANE_LINE_WIDTH - 2 * config.TOUCH_BUTTON_MARGIN,
                height=config.TOUCH_BUTTON_HEIGHT,
            )
            for line, next_line in zip(self.lane_lines, self.lane_lines[1:])
        ]

        # challenges: surprises after some points
        self.gold = GoldChallenge(self.rng)
        self.silver = SilverChallenge(self.rng)
        self.challenges: list[Challenge] = [self.gold, self.silver]

        # transition to game over (slow motion)
        self.transition_to_game_over = False
        self.slow_motion_steps = 0
        self._slow_motion_frames = 0

    @property
    def keys(self) -> tuple[str, ...]:
        """The keys of the game (one for each lane) for the chosen hand."""
        return HAND_KEYS[self.hand]

    # --- input ----------------------------------------------------------------

    def key_pressed(self, key: str) -> None:
        """
        Right letter in the action bar: its points. One press hits all the
        letters of the key in the action bar (a gold letter and a normal letter
        with the same char: both, and the points of both). Pressed at the wrong
        moment (no letter of the key in the action bar): game over.
        """
        if self.page != GamePage.RUNNING or self.transition_to_game_over:
            return
        if not is_game_key(key, self.keys):  # other keys are ignored
            return

        # the touch button of the key looks pressed (keyboard or touch)
        self.touch_buttons[self.keys.index(normalize_key(key))].press()

        # one press hits all the letters of the key in the action bar
        hits = [letter for letter in self.letters if letter.can_be_pressed(key)]
        pressed_again = any(letter.already_pressed(key) for letter in self.letters)
        correct = bool(hits) or pressed_again

        # yellow: right press / red: wrong moment (game over)
        self.action_bar.press(correct=correct)

        if hits:
            for letter in hits:
                letter.press(key)
            self._add_points(sum(self._points_for(letter) for letter in hits))
        elif not correct:
            # wrong moment: no letter with this key in the action bar
            self.transition_to_game_over = True

    def mouse_pressed(self, x: float, y: float) -> None:
        """A click or a touch (x, y in game pixels)."""
        if self.page == GamePage.RUNNING:
            self._touch(x, y)
        elif self.page == GamePage.CONGRATULATIONS:
            self._congratulations_click(x, y)
        else:
            self._start_page_click(x, y)

    def _start_page_click(self, x: float, y: float) -> None:
        """Start and game over pages: start / retry and hand buttons."""
        if self.button.contains(x, y):
            self.button.clicked = True
            self.start_new_game()
        elif self.hand_button.contains(x, y):
            self.hand_button.clicked = True
            self.toggle_hand()

    def _congratulations_click(self, x: float, y: float) -> None:
        if self.save_button.contains(x, y):
            self.save_button.clicked = True
            self.save_name()
        elif self.anonymous_button.contains(x, y):
            self.anonymous_button.clicked = True
            self.save_anonymous()

    def mouse_released(self) -> None:
        for button in (
            self.button,
            self.hand_button,
            self.save_button,
            self.anonymous_button,
        ):
            button.clicked = False

    def _touch(self, x: float, y: float) -> None:
        """A touch button works like the key of its lane."""
        for key, button in zip(self.keys, self.touch_buttons):
            if button.contains(x, y):
                self.key_pressed(key)
                return

    def toggle_hand(self) -> None:
        self.hand = Hand.RIGHT if self.hand == Hand.LEFT else Hand.LEFT

    # --- congratulations page: the name of a new best result --------------------

    def type_name(self, text: str) -> None:
        """The text of the name field (each change)."""
        if self.page == GamePage.CONGRATULATIONS:
            self.typed_name = text

    def save_name(self) -> None:
        """Save the result with the typed name ("Salvar" button or Enter)."""
        self._save_result(self.typed_name)

    def save_anonymous(self) -> None:
        self._save_result("")  # no name: the views show "anonymous"

    def _save_result(self, name: str) -> None:
        if self.page != GamePage.CONGRATULATIONS:  # saved only once
            return
        self.last_result = self.scoreboard.add(self.points, self._finished_at, name)
        self.page = GamePage.GAME_OVER

    # --- game -----------------------------------------------------------------

    def start_new_game(self) -> None:
        self.letters = []
        self.points = 0
        self._update_level()
        self.action_bar.reset()
        for challenge in self.challenges:
            challenge.reset()
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
                self._game_over()
                return
            self.slow_motion_steps += 1

        self._step()

    def _game_over(self) -> None:
        """
        A result that enters the best results shows the congratulations page
        (the player saves it with a name); the others go to the game over
        page and are not kept.
        """
        self.last_result = None
        self._finished_at = self.clock()
        if self.scoreboard.qualifies(self.points):
            self.typed_name = ""
            self.page = GamePage.CONGRATULATIONS
        else:
            self.page = GamePage.GAME_OVER

    def _step(self) -> None:
        """Move the game forward: new letters, move letters, game over."""
        self.action_bar.update()
        self._add_letter_if_needed()
        for challenge in self.challenges:
            challenge.update(self)

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

    def last_normal_letter(self) -> Letter | None:
        normal = [letter for letter in self.letters if not letter.gold]
        return normal[-1] if normal else None

    def _add_letter_if_needed(self) -> None:
        last = self.last_normal_letter()
        if last is not None and last.y < self.distance + last.size:
            return
        random_char = self.points >= config.RANDOM_CHARS_FROM_POINTS
        letter = self._new_letter(random_char)
        if last is not None:
            # exactly ``distance`` after the last letter (not one frame later),
            # but always at the top of the screen (at most one move down)
            letter.y = min(last.y - (self.distance + last.size), self.speed)
        self.letters.append(letter)
        for challenge in self.challenges:
            challenge.letter_added(self, letter)

    def _new_letter(self, random_char: bool) -> Letter:
        lane = self.rng.randrange(len(self.lane_centers))
        if random_char:
            char = self.keys[self.rng.randrange(len(self.keys))]
        else:
            char = self.keys[lane]
        return Letter(lane, char, self.action_bar, x=self.lane_centers[lane])

    # --- points and level -------------------------------------------------------

    @staticmethod
    def _points_for(letter: Letter) -> int:
        if letter.gold:
            return config.GOLD_POINTS
        if letter.silver:
            return config.SILVER_POINTS
        return 1

    def _add_points(self, points: int) -> None:
        self.points += points
        self._update_level()

    def _update_level(self) -> None:
        self.speed = level.speed_for(self.points)
        self.distance = level.distance_for(self.points)
