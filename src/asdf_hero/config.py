"""
Game settings: every number that defines the game is here.

Screen positions are in pixels. Speeds are in pixels per frame.
"""

# --- screen -----------------------------------------------------------------
WIDTH = 282
HEIGHT = 800
# phones: the game gets wider to fill the screen (no black margins on the
# sides); the lanes spread out. Never wider than this (tablets, landscape).
MAX_WIDTH = 600
FPS = 60  # the speed is in pixels per frame, so this also changes the speed

# --- keys: one key for each lane, chosen on the start page -----------------
LEFT_HAND_KEYS = ("A", "S", "D", "F")
RIGHT_HAND_KEYS = ("J", "K", "L", "Ç")  # right hand home row (ABNT2 keyboard)
KEY_ALIASES = {";": "Ç"}  # the key of "Ç" types ";" on US keyboards

# --- lanes ------------------------------------------------------------------
# x for a game WIDTH wide (a wider game multiplies them: see Game.lane_lines)
LANE_CENTERS = (37, 106, 175, 244)  # x of the center of each lane
LANE_LINES = (0, 69, 138, 207, 276)  # x of the lines between the lanes
LANE_LINE_WIDTH = 5

# --- letters ----------------------------------------------------------------
LETTER_SIZE = 62  # diameter of the circle
RANDOM_CHARS_FROM_POINTS = 25  # from here the char does not match the lane

# --- action bar (where the letters must be pressed) --------------------------
ACTION_BAR_TOP = 600
ACTION_BAR_HEIGHT = 80
HIGHLIGHT_FRAMES = 12  # how long the bar is highlighted after a key press

# --- game level: it starts easy and gets harder with the points -------------
# 1. the speed grows a little with each point until MAX_SPEED_FROM_POINTS
# 2. then the speed stays at MAX_SPEED, and the game adds more letters: the
#    distance between them gets smaller until there is always one letter in
#    the action bar (plus the special letters: gold)
INIT_SPEED = 3.0  # pixels per frame (180 px/s)
MAX_SPEED = 4.0  # pixels per frame (240 px/s)
MAX_SPEED_FROM_POINTS = 51
INIT_DISTANCE = 150  # free space between two letters (until MAX_SPEED_FROM_POINTS)
# always one letter in the action bar: the next letter touches the bar when
# the last one leaves it (center to center = bar height + letter size)
MIN_DISTANCE = ACTION_BAR_HEIGHT
DISTANCE_STEP_BY_POINT = 1.0  # from MAX_SPEED_FROM_POINTS: min distance at 121 points

# --- gold letter: a surprise challenge ---------------------------------------
# From GOLD_FROM_POINTS, after a random number of normal letters (between
# GOLD_EVERY_MIN_LETTERS and GOLD_EVERY_MAX_LETTERS), a gold letter falls
# GOLD_SPEED_FACTOR times faster than the other letters.
GOLD_FROM_POINTS = 40
GOLD_EVERY_MIN_LETTERS = 5
GOLD_EVERY_MAX_LETTERS = 10
GOLD_SPEED_FACTOR = 1.5  # faster than the others, but it can be followed
GOLD_POINTS = 1  # points for a gold letter (a normal letter is 1 point)

# --- silver letter: two letters change their chars ---------------------------
# From SILVER_FROM_POINTS, after a random number of normal letters (between
# SILVER_EVERY_MIN_LETTERS and SILVER_EVERY_MAX_LETTERS), a letter is chosen:
# it is already silver when it appears, and the next letter turns silver as
# soon as it exists too. They swap their chars when the first one is
# SILVER_SWAP_DISTANCE pixels from the action bar.
SILVER_FROM_POINTS = 50
SILVER_EVERY_MIN_LETTERS = 5
SILVER_EVERY_MAX_LETTERS = 10
SILVER_SWAP_DISTANCE = LETTER_SIZE  # one letter between the circle and the bar
SILVER_POINTS = 1  # points for a silver letter

# --- transition to game over (slow motion) -----------------------------------
SLOW_MOTION_STEPS = 13  # game steps shown before the game over page
SLOW_MOTION_STEP_FRAMES = 12  # one step every 12 frames (0.2s at 60 FPS)

# --- touch buttons (phone / tablet): one for each lane, below the action bar --
TOUCH_BUTTONS_TOP = 690  # the action bar ends at 680 (682 with the press effect)
TOUCH_BUTTON_HEIGHT = 68  # ends at 758: the points bar starts at 765
TOUCH_BUTTON_MARGIN = 2  # space between the button and the lane lines

# --- best results (start and game over pages) -------------------------------
SCOREBOARD_SIZE = 5
MIN_BEST_RESULT_POINTS = 1  # a game with 0 points never enters the best results
# a result in the best SCOREBOARD_SIZE shows the congratulations page, where
# the player types the name (or saves as anonymous: an empty name, shown as
# "Anônimo" / "Anonymous" in the language of the app)
NAME_MAX_LENGTH = 10
CONGRATULATIONS_BUTTONS_TOP = 350  # save button; the anonymous one is below
# the best results are saved in this SQLite file, in the data folder of the
# app (FLET_APP_STORAGE_DATA on the phone) or in ~/.asdf_hero (web server)
DATABASE_FILE = "asdf_hero.db"

# --- language of the texts (see asdf_hero/ui/texts.py) -----------------------
# None: the language of the phone / browser. "pt" or "en": always this one.
LANGUAGE: str | None = None
# the language of phones / browsers in other languages
DEFAULT_LANGUAGE = "en"

# --- buttons: start / retry and hand (left / right), congratulations ----------
# mobile design: touch targets of at least 48 px (Material 48 dp, Apple 44 pt)
# with space between them, at the bottom of the screen (where the thumb is)
BUTTON_WIDTH = 240
BUTTON_HEIGHT = 52
BUTTON_GAP = 12  # space between two buttons
BUTTONS_BOTTOM_MARGIN = 40  # space below the start button (bottom of the screen)

# --- logs: find out why the game gets slow (see "Logs" in README.md) -------
LOG_LEVEL = "INFO"  # "DEBUG": more details. The env var ASDF_HERO_LOG_LEVEL wins
LOG_FILE = "asdf_hero.log"  # in the data folder, next to the database
LOG_FILE_MAX_BYTES = 1_000_000  # then the file starts again (one old file kept)
PERFORMANCE_REPORT_SECONDS = 10  # one performance line for each 10 s of game
MIN_GOOD_FPS = 54  # a report with fewer frames per second is a warning
FREEZE_MS = 100  # a frame this long is a freeze (the report is a warning)
PAUSE_SECONDS = 1.0  # no frame for this long: the game was paused (hidden tab)
SLOW_STORAGE_MS = 50  # a slower database load / save is a warning
