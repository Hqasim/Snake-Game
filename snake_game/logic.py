"""Pure, framework-free game rules for Snake.

Nothing in this module touches Tkinter or does any I/O, so it can be
unit-tested directly (see tests/test_logic.py) without a display.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable, Sequence

Position = tuple[int, int]

_OPPOSITES = ({"Up", "Down"}, {"Left", "Right"})
DIRECTIONS = ("Up", "Down", "Left", "Right")


def is_opposite_direction(a: str, b: str) -> bool:
    """True if `a` and `b` are directly opposite (e.g. Up vs Down)."""
    return {a, b} in _OPPOSITES


def next_head_position(head: Position, direction: str, step: int) -> Position:
    """The new head position after moving one step in `direction`."""
    x, y = head
    if direction == "Left":
        return (x - step, y)
    if direction == "Right":
        return (x + step, y)
    if direction == "Up":
        return (x, y - step)
    if direction == "Down":
        return (x, y + step)
    raise ValueError(f"Unknown direction: {direction!r}")


def advance_snake(
    positions: Sequence[Position], direction: str, step: int, grow: bool
) -> list[Position]:
    """Return the snake's new body after moving one step.

    The tail segment is kept when `grow` is True (food was just eaten)
    and dropped otherwise, so the snake gets one segment longer.
    """
    new_head = next_head_position(positions[0], direction, step)
    body = list(positions) if grow else list(positions[:-1])
    return [new_head, *body]


def has_wall_collision(head: Position, wall_x: tuple[int, int], wall_y: tuple[int, int]) -> bool:
    """True if `head` sits exactly on one of the boundary edges."""
    x, y = head
    return x in wall_x or y in wall_y


def has_self_collision(head: Position, body: Iterable[Position]) -> bool:
    """True if `head` overlaps any segment of `body` (the rest of the snake)."""
    return head in set(body)


def random_food_position(
    occupied: Iterable[Position],
    column_range: tuple[int, int],
    row_range: tuple[int, int],
    step: int,
    rng: Callable[[int, int], int] = random.randint,
) -> Position:
    """Pick a random grid cell that isn't currently occupied by the snake."""
    occupied = set(occupied)
    while True:
        position = (rng(*column_range) * step, rng(*row_range) * step)
        if position not in occupied:
            return position


def compute_speed(score: int, base_speed: int, step_every: int) -> int:
    """Moves-per-second for the given score (speeds up every `step_every` points)."""
    return base_speed + score // step_every
