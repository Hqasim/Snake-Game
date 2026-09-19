"""Tkinter rendering layer: wires snake_game.logic + persistence to the screen."""

from __future__ import annotations

import tkinter as tk

from PIL import Image, ImageTk

from . import config, persistence
from .logic import (
    DIRECTIONS,
    advance_snake,
    compute_speed,
    has_self_collision,
    has_wall_collision,
    is_opposite_direction,
    next_head_position,
    random_food_position,
)


class Snake(tk.Canvas):
    """The game board: a Tkinter canvas that owns the render + input loop."""

    def __init__(self):
        super().__init__(
            width=config.BOARD_WIDTH,
            height=config.BOARD_HEIGHT,
            background=config.COLORS["background"],
            highlightthickness=0,
        )
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.moves_per_second = config.BASE_MOVES_PER_SECOND
        self.score = 0
        self.high_score = persistence.load_high_score(config.HIGH_SCORE_FILE)
        self.game_status = "menu"  # "menu" | "playing" | "paused" | "over"

        self.bind_all("<KeyPress>", self.on_key_press)
        self.load_assets()
        self.draw_grid_background()
        self.show_start_menu()

    # --- Setup ------------------------------------------------------------

    def load_assets(self):
        try:
            self.sprites = {
                "food": self._load_sprite("food.png"),
                "body": self._load_sprite("body.png"),
                "tail": self._load_sprite("tail.png"),
                "head_up": self._load_sprite("head_up.png"),
                "head_down": self._load_sprite("head_down.png"),
                "head_left": self._load_sprite("head_left.png"),
                "head_right": self._load_sprite("head_right.png"),
            }
        except OSError as error:
            print(error)
            self.winfo_toplevel().destroy()

    def _load_sprite(self, filename: str) -> ImageTk.PhotoImage:
        image = Image.open(config.SPRITES_DIR / filename)
        return ImageTk.PhotoImage(image)

    def draw_grid_background(self):
        step = config.MOVE_STEP
        for row, y in enumerate(range(config.HUD_HEIGHT, config.BOARD_HEIGHT, step)):
            for col, x in enumerate(range(0, config.BOARD_WIDTH, step)):
                shade = config.COLORS["grid_a"] if (row + col) % 2 == 0 else config.COLORS["grid_b"]
                self.create_rectangle(x, y, x + step, y + step, fill=shade, outline="", tag="grid")
        self.draw_boundary()

    def draw_boundary(self):
        self.create_rectangle(
            7, 27, config.BOARD_WIDTH - 7, config.BOARD_HEIGHT - 7,
            outline=config.COLORS["boundary_outer"], tag="boundary",
        )
        self.create_rectangle(
            6, 26, config.BOARD_WIDTH - 6, config.BOARD_HEIGHT - 6,
            outline=config.COLORS["boundary_inner"], tag="boundary",
        )

    # --- Screens ------------------------------------------------------------

    def show_start_menu(self):
        self.game_status = "menu"
        self.delete("overlay")
        cx, cy = config.BOARD_WIDTH / 2, config.BOARD_HEIGHT / 2
        self.create_text(
            cx, cy - 60, text="SNAKE", fill=config.COLORS["accent"],
            font=(config.FONT_FAMILY, 42, "bold"), tag="overlay",
        )
        self.create_text(
            cx, cy, text="Press Space to Start", fill=config.COLORS["text"],
            font=(config.FONT_FAMILY, 18), tag="overlay",
        )
        self.create_text(
            cx, cy + 40,
            text="Arrow keys to move   •   P to pause   •   Space to restart after Game Over",
            fill=config.COLORS["muted"], font=(config.FONT_FAMILY, 11), tag="overlay",
        )
        if self.high_score:
            self.create_text(
                cx, cy + 80, text=f"High Score: {self.high_score}",
                fill=config.COLORS["muted"], font=(config.FONT_FAMILY, 11), tag="overlay",
            )

    def start_game(self):
        self.delete("overlay")
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.moves_per_second = config.BASE_MOVES_PER_SECOND
        self.score = 0
        self.game_status = "playing"
        self.food_position = random_food_position(
            self.snake_positions, config.FOOD_COLUMN_RANGE, config.FOOD_ROW_RANGE, config.MOVE_STEP
        )
        self.create_objects()
        self.schedule_next_frame()

    def create_objects(self):
        self.create_text(
            config.BOARD_WIDTH / 2, 13, text=self._hud_text(), tag="score",
            fill=config.COLORS["text"], font=(config.FONT_FAMILY, 13),
        )
        for index, position in enumerate(self.snake_positions):
            self.create_image(*position, image=self._sprite_for_segment(index), tag="snake")
        self.create_image(*self.food_position, image=self.sprites["food"], tag="food")

    def _hud_text(self) -> str:
        return (
            f"Score: {self.score}   "
            f"High Score: {self.high_score}   "
            f"Speed: {self.moves_per_second}"
        )

    def _sprite_for_segment(self, index: int):
        if index == 0:
            return self.sprites[f"head_{self.direction.lower()}"]
        if index == len(self.snake_positions) - 1:
            return self.sprites["tail"]
        return self.sprites["body"]

    # --- Input ------------------------------------------------------------

    def on_key_press(self, event):
        key = event.keysym

        if self.game_status == "menu" and key == "space":
            self.start_game()
            return
        if self.game_status == "over" and key == "space":
            self.start_game()
            return
        if self.game_status in ("playing", "paused") and key in ("p", "P"):
            self.toggle_pause()
            return
        if self.game_status != "playing":
            return

        if key in DIRECTIONS and not is_opposite_direction(key, self.direction):
            self.direction = key

    def toggle_pause(self):
        if self.game_status == "playing":
            self.game_status = "paused"
            cx, cy = config.BOARD_WIDTH / 2, config.BOARD_HEIGHT / 2
            self.create_text(
                cx, cy, text="Paused", fill=config.COLORS["text"],
                font=(config.FONT_FAMILY, 28, "bold"), tag="overlay",
            )
        elif self.game_status == "paused":
            self.game_status = "playing"
            self.delete("overlay")
            self.schedule_next_frame()

    # --- Game loop ------------------------------------------------------------

    def schedule_next_frame(self):
        delay_ms = 1500 // self.moves_per_second
        self.after(delay_ms, self.tick)

    def tick(self):
        if self.game_status != "playing":
            return

        # Look ahead before drawing anything: if the next step would hit a
        # wall or the snake's own body, end the game now so the head never
        # visibly overshoots the boundary before the collision is caught.
        next_head = next_head_position(self.snake_positions[0], self.direction, config.MOVE_STEP)
        will_grow = next_head == self.food_position
        body_after_move = self.snake_positions if will_grow else self.snake_positions[:-1]

        if has_wall_collision(
            next_head, config.WALL_X, config.WALL_Y
        ) or has_self_collision(next_head, body_after_move):
            self.end_game()
            return

        if will_grow:
            self.grow_snake()
        self.move_snake()
        self.schedule_next_frame()

    def move_snake(self):
        # Always drop the tail and prepend a new head; growth is handled
        # separately in grow_snake by pre-extending the list (and its
        # matching canvas item) before this runs, so the two counts never
        # drift apart.
        self.snake_positions = advance_snake(
            self.snake_positions, self.direction, config.MOVE_STEP, grow=False
        )
        segment_ids = self.find_withtag("snake")
        for segment_id, position in zip(segment_ids, self.snake_positions):
            self.coords(segment_id, *position)
        self.itemconfigure(segment_ids[0], image=self._sprite_for_segment(0))
        self.itemconfigure(segment_ids[-1], image=self._sprite_for_segment(len(segment_ids) - 1))

    def grow_snake(self):
        self.score += 1
        self.moves_per_second = compute_speed(
            self.score, config.BASE_MOVES_PER_SECOND, config.SPEED_STEP_EVERY_N_POINTS
        )

        self.snake_positions.append(self.snake_positions[-1])
        self.create_image(*self.snake_positions[-1], image=self.sprites["tail"], tag="snake")

        self.food_position = random_food_position(
            self.snake_positions, config.FOOD_COLUMN_RANGE, config.FOOD_ROW_RANGE, config.MOVE_STEP
        )
        self.coords(self.find_withtag("food"), *self.food_position)

        self.itemconfigure(self.find_withtag("score"), text=self._hud_text())

    def end_game(self):
        self.game_status = "over"
        is_new_high_score = self.score > self.high_score
        if is_new_high_score:
            self.high_score = self.score
            persistence.save_high_score(config.HIGH_SCORE_FILE, self.high_score)

        self.delete("snake", "food", "score")
        cx, cy = config.BOARD_WIDTH / 2, config.BOARD_HEIGHT / 2
        self.create_text(
            cx, cy - 20, text=f"Game Over! You scored {self.score}", fill=config.COLORS["text"],
            font=(config.FONT_FAMILY, 22, "bold"), tag="overlay",
        )
        if is_new_high_score:
            self.create_text(
                cx, cy + 15, text="New High Score!", fill=config.COLORS["accent"],
                font=(config.FONT_FAMILY, 14, "bold"), tag="overlay",
            )
        self.create_text(
            cx, cy + 50, text="Press Space Bar to play again", fill=config.COLORS["muted"],
            font=(config.FONT_FAMILY, 13), tag="overlay",
        )
