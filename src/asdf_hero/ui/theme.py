"""Colors, font sizes and texts of the screen."""

from asdf_hero.game.states import GamePage, Hand, Highlight


def rgb(r: int, g: int, b: int, a: int = 255) -> str:
    """Return a Flet color string (``#AARRGGBB``) from 0-255 channels."""
    return "#%02x%02x%02x%02x" % (a, r, g, b)


WHITE = rgb(255, 255, 255)
BLACK = rgb(0, 0, 0)

# --- page -------------------------------------------------------------------
PAGE_TITLE = "ASDF Hero"
PAGE_BGCOLOR = rgb(32, 32, 32)
BACKGROUND_IMAGE = "back.jpg"  # inside src/assets

# --- letters: one color for each lane (A, S, D, F) ---------------------------
LANE_COLORS = (
    rgb(66, 133, 244),
    rgb(219, 68, 55),
    rgb(244, 160, 0),
    rgb(15, 157, 88),
)
LETTER_FONT_SIZE = 45

# challenges: gold letter and swapped letters (silver), with a glow
GLOW_BLUR = 14
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

# --- button -----------------------------------------------------------------
BUTTON_COLOR = rgb(0, 0, 0)
BUTTON_CLICKED_COLOR = rgb(50, 50, 50)
BUTTON_TEXT_COLOR = rgb(255, 255, 255)
BUTTON_FONT_SIZE = 24
BUTTON_TEXTS = {
    GamePage.START: "Iniciar ASDF Hero",
    GamePage.GAME_OVER: "Falhar novamente",
}
HAND_BUTTON_FONT_SIZE = 18
HAND_BUTTON_TEXTS = {
    Hand.LEFT: "Mão esquerda: ASDF",
    Hand.RIGHT: "Mão direita: JKLÇ",
}

# --- points and game over ---------------------------------------------------
POINTS_TEXT = "Pontos: {}"
POINTS_FONT_SIZE = 30
POINTS_BAR_COLOR = rgb(255, 255, 255, 220)
POINTS_BAR_HEIGHT = 35
BANNER_COLOR = rgb(255, 255, 255, 200)
GAME_OVER_TEXT = "GAME OVER"
GAME_OVER_FONT_SIZE = 50

# game over page layout (y of each part): banner with "GAME OVER", the points
# and the best results, above the retry button (y=360)
GAME_OVER_BANNER_TOP = 100
GAME_OVER_BANNER_HEIGHT = 252
GAME_OVER_TEXT_TOP = 105
GAME_OVER_POINTS_TOP = 168

# best results (below the points)
SCOREBOARD_TOP = 212
SCOREBOARD_TITLE = "Melhores resultados"
SCOREBOARD_TITLE_HEIGHT = 26
SCOREBOARD_ROW_HEIGHT = 22
SCOREBOARD_FONT_SIZE = 16
SCOREBOARD_DATE_FORMAT = "%d/%m/%Y"
SCOREBOARD_TIME_FORMAT = "%H:%M"
