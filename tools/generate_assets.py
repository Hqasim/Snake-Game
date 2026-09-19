"""Procedurally generate the snake/food sprite PNGs used by the game.

Run this to (re)create everything under assets/sprites/. Shapes are drawn
at 4x resolution and downsampled with LANCZOS for anti-aliased edges,
since Pillow's basic drawing primitives are aliased at small sizes.

Usage:
    python tools/generate_assets.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from snake_game.config import CELL_SIZE, SPRITES_DIR  # noqa: E402

SUPERSAMPLE = 4
SIZE = CELL_SIZE * SUPERSAMPLE

BODY_LIGHT = (176, 245, 66, 255)  # #b0f542
BODY_DARK = (79, 138, 32, 255)
HEAD_LIGHT = (198, 255, 110, 255)
HEAD_DARK = (98, 168, 45, 255)
OUTLINE = (46, 79, 20, 255)
EYE_WHITE = (245, 250, 240, 255)
EYE_PUPIL = (20, 22, 18, 255)

APPLE_LIGHT = (255, 99, 90, 255)
APPLE_DARK = (176, 24, 30, 255)
LEAF_COLOR = (98, 168, 45, 255)
STEM_COLOR = (95, 62, 35, 255)
SHINE_COLOR = (255, 255, 255, 160)


def _gradient(size: int, light: tuple, dark: tuple) -> Image.Image:
    """A soft radial gradient from `light` (center) to `dark` (edges)."""
    mask = Image.radial_gradient("L").resize((size, size))
    light_layer = Image.new("RGBA", (size, size), light)
    dark_layer = Image.new("RGBA", (size, size), dark)
    return Image.composite(light_layer, dark_layer, mask)


def _rounded_rect_mask(size: int, inset: float, radius_ratio: float) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    pad = int(size * inset)
    radius = int(size * radius_ratio)
    draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=radius, fill=255)
    return mask


def _circle_mask(size: int, inset: float) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    pad = int(size * inset)
    draw.ellipse([pad, pad, size - pad, size - pad], fill=255)
    return mask


def _finish(image: Image.Image) -> Image.Image:
    return image.resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)


def make_body() -> Image.Image:
    gradient = _gradient(SIZE, BODY_LIGHT, BODY_DARK)
    mask = _rounded_rect_mask(SIZE, inset=0.06, radius_ratio=0.32)
    sprite = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sprite.paste(gradient, (0, 0), mask)

    draw = ImageDraw.Draw(sprite)
    pad = int(SIZE * 0.06)
    radius = int(SIZE * 0.32)
    draw.rounded_rectangle(
        [pad, pad, SIZE - pad, SIZE - pad], radius=radius, outline=OUTLINE, width=max(1, SIZE // 40)
    )
    return _finish(sprite)


def make_tail() -> Image.Image:
    gradient = _gradient(SIZE, BODY_LIGHT, BODY_DARK)
    mask = _rounded_rect_mask(SIZE, inset=0.16, radius_ratio=0.5)
    sprite = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sprite.paste(gradient, (0, 0), mask)
    return _finish(sprite)


def make_head(direction: str) -> Image.Image:
    gradient = _gradient(SIZE, HEAD_LIGHT, HEAD_DARK)
    mask = _rounded_rect_mask(SIZE, inset=0.04, radius_ratio=0.38)
    sprite = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sprite.paste(gradient, (0, 0), mask)

    draw = ImageDraw.Draw(sprite)
    pad = int(SIZE * 0.04)
    radius = int(SIZE * 0.38)
    draw.rounded_rectangle(
        [pad, pad, SIZE - pad, SIZE - pad], radius=radius, outline=OUTLINE, width=max(1, SIZE // 40)
    )

    along, across = 0.22, 0.20
    offsets = {
        "Right": ((along, -across), (along, across)),
        "Left": ((-along, -across), (-along, across)),
        "Up": ((-across, -along), (across, -along)),
        "Down": ((-across, along), (across, along)),
    }[direction]

    eye_r = SIZE * 0.11
    pupil_r = SIZE * 0.05
    for dx, dy in offsets:
        cx, cy = SIZE / 2 + dx * SIZE, SIZE / 2 + dy * SIZE
        draw.ellipse([cx - eye_r, cy - eye_r, cx + eye_r, cy + eye_r], fill=EYE_WHITE)
        draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r], fill=EYE_PUPIL)

    return _finish(sprite)


def make_food() -> Image.Image:
    gradient = _gradient(SIZE, APPLE_LIGHT, APPLE_DARK)
    mask = _circle_mask(SIZE, inset=0.10)
    sprite = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sprite.paste(gradient, (0, 0), mask)

    draw = ImageDraw.Draw(sprite)

    draw.line(
        [(SIZE * 0.5, SIZE * 0.12), (SIZE * 0.56, SIZE * 0.02)],
        fill=STEM_COLOR,
        width=max(1, SIZE // 24),
    )

    draw.polygon(
        [
            (SIZE * 0.56, SIZE * 0.08),
            (SIZE * 0.80, SIZE * 0.00),
            (SIZE * 0.78, SIZE * 0.20),
        ],
        fill=LEAF_COLOR,
    )

    shine = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    shine_draw = ImageDraw.Draw(shine)
    shine_draw.ellipse([SIZE * 0.28, SIZE * 0.26, SIZE * 0.46, SIZE * 0.42], fill=SHINE_COLOR)
    sprite = Image.alpha_composite(sprite, shine)

    return _finish(sprite)


def main() -> None:
    SPRITES_DIR.mkdir(parents=True, exist_ok=True)

    make_body().save(SPRITES_DIR / "body.png")
    make_tail().save(SPRITES_DIR / "tail.png")
    make_food().save(SPRITES_DIR / "food.png")
    for direction in ("Up", "Down", "Left", "Right"):
        make_head(direction).save(SPRITES_DIR / f"head_{direction.lower()}.png")

    print(f"Generated 7 sprites in {SPRITES_DIR}")


if __name__ == "__main__":
    main()
