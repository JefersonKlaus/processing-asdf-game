"""Colors, font sizes and positions of the screen (the texts: texts.py)."""

from asdf_hero.game.states import Highlight


def rgb(r: int, g: int, b: int, a: int = 255) -> str:
    """Return a Flet color string (``#AARRGGBB``) from 0-255 channels."""
    return f"#{a:02x}{r:02x}{g:02x}{b:02x}"


def with_alpha(color: str, alpha: int) -> str:
    """The same color (``#AARRGGBB``) with another alpha (0-255): glows."""
    return f"#{alpha:02x}{color[3:]}"


def darker(color: str, factor: float = 0.75) -> str:
    """The same color (``#AARRGGBB``), darker: the color of a pressed button."""
    a, r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5, 7))
    return rgb(int(r * factor), int(g * factor), int(b * factor), a)


WHITE = rgb(255, 255, 255)
BLACK = rgb(0, 0, 0)

# --- page -------------------------------------------------------------------
PAGE_TITLE = "ASDF Hero"
PAGE_BGCOLOR = rgb(32, 32, 32)
BACKGROUND_IMAGE = "back.jpg"  # inside src/assets

# --- letters: one color for each lane (A, S, D, F) ---------------------------
# blue, red, purple, green: no yellow / orange, so a normal letter never looks
# like the gold letter
LANE_COLORS = (
    rgb(66, 133, 244),  # blue
    rgb(219, 68, 55),  # red
    rgb(142, 36, 170),  # purple
    rgb(15, 157, 88),  # green
)
LETTER_FONT_SIZE = 45

# every letter has a glow around the circle, in its color. The special
# letters (gold, silver) have a big glow; the normal letters (lane color) a
# small one, so the special letters stand out.
GLOW_BLUR = 14  # special letters
GLOW_SPREAD = 2
LANE_GLOW_BLUR = 6  # normal letters
LANE_GLOW_SPREAD = 0
LANE_GLOW_ALPHA = 110  # more transparent than the special glows
LANE_GLOW_COLORS = tuple(with_alpha(color, LANE_GLOW_ALPHA) for color in LANE_COLORS)
GOLD_COLOR = rgb(255, 193, 7)
GOLD_GLOW_COLOR = rgb(255, 215, 0, 180)
SILVER_COLOR = rgb(158, 158, 158)
SILVER_GLOW_COLOR = rgb(192, 192, 192, 220)

# --- action bar: color of each highlight (light colors, almost white) --------
ACTION_BAR_COLORS = {
    Highlight.NONE: rgb(255, 255, 255, 200),
    Highlight.PRESSED: rgb(255, 249, 196, 220),  # light yellow
    Highlight.WRONG: rgb(255, 205, 210, 220),  # light red
}
# press effect (action bar and touch buttons): on each key press the control
# gets bigger (pixels on each side) for some frames and then gets back to its
# size (8 frames = 0.13s at 60 FPS)
PRESS_EFFECT_GROW = 2
PRESS_EFFECT_FRAMES = 8

# --- touch buttons: the color of the lane, the key of the lane -------------
TOUCH_BUTTON_FONT_SIZE = 30
TOUCH_BUTTON_TEXT_COLOR = rgb(255, 255, 255)
TOUCH_BUTTON_RADIUS = 10
TOUCH_BUTTON_PRESSED_OPACITY = 0.6  # during the press effect

# --- buttons: one color for each action (the colors of the lanes) -----------
# green: start / retry (and save, the same "go on" action)
# purple: change the hand
# blue: save as anonymous
# The same design as the touch buttons (letter buttons): rounded corners and
# bold white text. A pressed button is darker.
START_BUTTON_COLOR = LANE_COLORS[3]  # green
HAND_BUTTON_COLOR = LANE_COLORS[2]  # purple
ANONYMOUS_BUTTON_COLOR = LANE_COLORS[0]  # blue
BUTTON_TEXT_COLOR = TOUCH_BUTTON_TEXT_COLOR  # white
BUTTON_RADIUS = TOUCH_BUTTON_RADIUS
BUTTON_FONT_SIZE = 22  # at least 16: easy to read on a phone
HAND_BUTTON_FONT_SIZE = 18

# --- points and game over ---------------------------------------------------
POINTS_FONT_SIZE = 30
POINTS_BAR_COLOR = rgb(255, 255, 255, 220)
POINTS_BAR_HEIGHT = 35
BANNER_COLOR = rgb(255, 255, 255, 200)
GAME_OVER_FONT_SIZE = 46  # bold "GAME OVER": ~257 px (Roboto), fits in 282
GAME_OVER_COLOR = LANE_COLORS[1]  # red, bold "GAME OVER" ("ASDF HERO" is black)

# start and game over pages (y of each part): banner with "ASDF HERO" (start)
# or "GAME OVER", the points (game over only) and the best results; the
# buttons are at the bottom of the screen
GAME_OVER_BANNER_TOP = 100
GAME_OVER_BANNER_HEIGHT = 252
GAME_OVER_TEXT_TOP = 105
GAME_OVER_POINTS_TOP = 168

# best results (below the points)
SCOREBOARD_TOP = 212
SCOREBOARD_TITLE_HEIGHT = 26
SCOREBOARD_ROW_HEIGHT = 22
SCOREBOARD_FONT_SIZE = 14
# width of each column: position, name, date, time, points (272 of 282 px)
SCOREBOARD_COLUMNS = (24, 86, 78, 44, 40)

# --- congratulations page: a new result in the best results -----------------
# (y of each part; the save / anonymous buttons are at y=350 and y=414,
# config.CONGRATULATIONS_BUTTONS_TOP; everything is in the upper 60% of the
# screen, above the keyboard of the phone)
CONGRATULATIONS_BANNER_TOP = 100
CONGRATULATIONS_BANNER_HEIGHT = 380  # the anonymous button ends at y=466
CONGRATULATIONS_TITLE_TOP = 105
CONGRATULATIONS_TITLE_FONT_SIZE = 40  # bold "NADA MAL!": ~213 px, fits in 242
CONGRATULATIONS_SUBTITLE_TOP = 165
CONGRATULATIONS_SUBTITLE_FONT_SIZE = 26
CONGRATULATIONS_TEXT_TOP = 200
CONGRATULATIONS_TEXT_FONT_SIZE = 16
NAME_FIELD_TOP = 255
NAME_FIELD_MARGIN = 20  # space on the left and on the right of the field
NAME_FIELD_FONT_SIZE = 20
NAME_FIELD_COLOR = rgb(255, 255, 255)
CONGRATULATIONS_BUTTON_FONT_SIZE = 18
