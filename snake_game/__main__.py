"""Entry point: `python -m snake_game` launches the game window."""

import tkinter as tk

from .ui import Snake


def main() -> None:
    root = tk.Tk()
    root.title("Snake")
    root.resizable(False, False)

    board = Snake()
    board.grid(row=0, column=0)

    root.mainloop()


if __name__ == "__main__":
    main()
