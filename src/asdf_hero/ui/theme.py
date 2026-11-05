"""Colors, font sizes and texts of the screen."""

from asdf_hero.game.states import GamePage, Highlight


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

# gold letter (surprise challenge): gold color with a glow
GOLD_COLOR = rgb(255, 193, 7)
GOLD_GLOW_COLOR = rgb(255, 215, 0, 180)
GOLD_GLOW_BLUR = 14

# --- action bar: color of each highlight (light colors, almost white) --------
ACTION_BAR_COLORS = {
    Highlight.NONE: rgb(255, 255, 255, 200),
    Highlight.PRESSED: rgb(255, 249, 196, 220),  # light yellow
    Highlight.WRONG: rgb(255, 205, 210, 220),  # light red
}
# small and short vibration on each key press: horizontal offset (pixels) of
# the bar on each frame (9 frames = 0.15s at 60 FPS)
ACTION_BAR_SHAKE = (3, -3, 3, -3, 2, -2, 1, -1, 0)

# --- button -----------------------------------------------------------------
BUTTON_COLOR = rgb(0, 0, 0)
BUTTON_CLICKED_COLOR = rgb(50, 50, 50)
BUTTON_TEXT_COLOR = rgb(255, 255, 255)
BUTTON_FONT_SIZE = 24
BUTTON_TEXTS = {
    GamePage.START: "Iniciar ASDF Hero",
    GamePage.GAME_OVER: "Falhar novamente",
}

# --- points and game over ---------------------------------------------------
POINTS_TEXT = "Pontos: {}"
POINTS_FONT_SIZE = 30
POINTS_BAR_COLOR = rgb(255, 255, 255, 220)
POINTS_BAR_HEIGHT = 35
BANNER_COLOR = rgb(255, 255, 255, 200)
GAME_OVER_TEXT = "GAME OVER"
GAME_OVER_FONT_SIZE = 50
