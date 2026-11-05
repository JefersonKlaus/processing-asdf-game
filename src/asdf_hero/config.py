"""
Game settings: every number that defines the game is here.

Screen positions are in pixels. Speeds are in pixels per frame.
"""

# --- screen -----------------------------------------------------------------
WIDTH = 282
HEIGHT = 800
FPS = 60  # the speed is in pixels per frame, so this also changes the speed

# --- lanes ------------------------------------------------------------------
CHARS = ("A", "S", "D", "F")  # one lane for each char (the game keys)
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
INIT_SPEED = 3.0  # pixels per frame (180 px/s)
MAX_SPEED = 5.0  # pixels per frame (300 px/s)
SPEED_STEP_BY_POINT = 0.02  # max speed at 100 points
INIT_DISTANCE = 150  # free space between two letters
MIN_DISTANCE = 100
DISTANCE_STEP_BY_POINT = 0.5  # min distance at 100 points

# --- gold letter: a surprise challenge ---------------------------------------
# From GOLD_FROM_POINTS, after a random number of normal letters (between
# GOLD_EVERY_MIN_LETTERS and GOLD_EVERY_MAX_LETTERS), a gold letter falls
# GOLD_SPEED_FACTOR times faster than the other letters.
GOLD_FROM_POINTS = 30
GOLD_EVERY_MIN_LETTERS = 5
GOLD_EVERY_MAX_LETTERS = 10
GOLD_SPEED_FACTOR = 2.0

# --- transition to game over (slow motion) -----------------------------------
SLOW_MOTION_STEPS = 13  # game steps shown before the game over page
SLOW_MOTION_STEP_FRAMES = 12  # one step every 12 frames (0.2s at 60 FPS)

# --- start / retry button ---------------------------------------------------
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
