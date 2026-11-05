"""
Game settings: every number that defines the game is here.

Screen positions are in pixels. Speeds are in pixels per frame.
"""

# --- screen -----------------------------------------------------------------
WIDTH = 282
HEIGHT = 800
FPS = 60  # the speed is in pixels per frame, so this also changes the speed

# --- keys: one key for each lane, chosen on the start page -----------------
LEFT_HAND_KEYS = ("A", "S", "D", "F")
RIGHT_HAND_KEYS = ("J", "K", "L", "Ç")  # right hand home row (ABNT2 keyboard)
KEY_ALIASES = {";": "Ç"}  # the key of "Ç" types ";" on US keyboards

# --- lanes ------------------------------------------------------------------
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
MAX_SPEED = 4.0  # pixels per frame (5=270 px/s)
SPEED_STEP_BY_POINT = 0.02  # max speed at 75 points
INIT_DISTANCE = 150  # free space between two letters
MIN_DISTANCE = 100
DISTANCE_STEP_BY_POINT = 0.5  # min distance at 100 points

# --- gold letter: a surprise challenge ---------------------------------------
# From GOLD_FROM_POINTS, after a random number of normal letters (between
# GOLD_EVERY_MIN_LETTERS and GOLD_EVERY_MAX_LETTERS), a gold letter falls
# GOLD_SPEED_FACTOR times faster than the other letters.
GOLD_FROM_POINTS = 40
GOLD_EVERY_MIN_LETTERS = 5
GOLD_EVERY_MAX_LETTERS = 10
GOLD_SPEED_FACTOR = 2.0
GOLD_POINTS = 1  # points for a gold letter (a normal letter is 1 point)

# --- swap challenge: two letters change their chars --------------------------
# From SWAP_FROM_POINTS, after a random number of normal letters (between
# SWAP_EVERY_MIN_LETTERS and SWAP_EVERY_MAX_LETTERS), a letter swaps its char
# with the next letter when it is SWAP_DISTANCE pixels from the action bar.
# The two letters are highlighted in silver.
SWAP_FROM_POINTS = 50
SWAP_EVERY_MIN_LETTERS = 5
SWAP_EVERY_MAX_LETTERS = 10
SWAP_DISTANCE = 100  # pixels between the letter circle and the action bar
SWAP_POINTS = 1  # points for a silver (swapped) letter

# --- transition to game over (slow motion) -----------------------------------
SLOW_MOTION_STEPS = 13  # game steps shown before the game over page
SLOW_MOTION_STEP_FRAMES = 12  # one step every 12 frames (0.2s at 60 FPS)

# --- buttons: start / retry and hand (left / right) --------------------------
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_GAP = 10  # space between the start button and the hand button
