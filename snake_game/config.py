"""Static configuration: board geometry, timing, colors, and file paths."""

from pathlib import Path

# --- Paths -------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
DATA_DIR = PROJECT_ROOT / "data"
HIGH_SCORE_FILE = DATA_DIR / "highscore.json"

# --- Board geometry ------------------------------------------------------
BOARD_WIDTH = 600
BOARD_HEIGHT = 620
MOVE_STEP = 20
CELL_SIZE = MOVE_STEP
HUD_HEIGHT = 20  # y-coordinate below which the score/HUD text sits

# Wall collision: a move onto these exact edges ends the game.
WALL_X = (0, BOARD_WIDTH)
WALL_Y = (HUD_HEIGHT, BOARD_HEIGHT)

# Valid range for random food placement, in grid cells (matches the
# playable area inside the boundary rectangle).
FOOD_COLUMN_RANGE = (1, 29)
FOOD_ROW_RANGE = (3, 30)

# --- Timing / difficulty --------------------------------------------------
BASE_MOVES_PER_SECOND = 15
SPEED_STEP_EVERY_N_POINTS = 5

# --- Colors ----------------------------------------------------------------
COLORS = {
    "background": "#1b1d17",
    "grid_a": "#1f2119",
    "grid_b": "#23261d",
    "boundary_outer": "#42f5aa",
    "boundary_inner": "#b0f542",
    "text": "#f5f5f0",
    "accent": "#b0f542",
    "muted": "#8a8d80",
}

FONT_FAMILY = "Segoe UI"
