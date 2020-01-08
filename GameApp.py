"""
This is a snake game application made in Python using Tkinter library.
@author  Hamzah Qasim
@email hqqasim55@gmail.com
@version 2.0
@since   2019-06-08
"""
import tkinter as tk
from PIL import Image, ImageTk  # Allows to load and place assets on canvas
from random import randint

moves_per_second = 15
GAME_SPEED = 1500 // moves_per_second  # More speed is slower snake movement on screen and vice versa
MOVE_STEP = 20


class Snake(tk.Canvas):  # Snake Class inherits from tk.Canvas
    def __init__(self):
        # Game window Dimensions and Color
        super().__init__(width=600, height=620, background="#22241f", highlightthickness=0)
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]  # First tuple head location, rest body
        self.food_position = self.set_new_food_position()  # sets new food position
        self.score = 0
        self.direction = "Right"
        self.game_status = True  # Indicates game status
        self.bind_all("<Key>", self.on_key_press)  # when ever a key is pressed run method in second argument
        self.load_assets()
        self.create_objects()
        self.after(GAME_SPEED, self.perform_actions)  # calls functions after 75 milli Seconds

    def load_assets(self):  # Loads the snake images
        try:
            self.snake_body_image = Image.open("./Assets/SnakeBody.png")
            self.snake_body = ImageTk.PhotoImage(self.snake_body_image)

            self.food_image = Image.open("./Assets/Food.png")
            self.food = ImageTk.PhotoImage(self.food_image)

        except IOError as error:
            print(error)
            root.destroy()

    def create_objects(self):  # Creates different objects on canvas to be displayed on screen
        # Creates the Score text
        self.create_text(
            100, 15, text=f"Score: {self.score}   Speed: {moves_per_second}", tag="score", fill="#fff",
            font=("Times", 16)
        )

        # Creates Snake Body
        for x_position, y_position in self.snake_positions:
            self.create_image(x_position, y_position, image=self.snake_body, tag="snake")

        # Creates Food
        self.create_image(self.food_position[0], self.food_position[1], image=self.food, tag="food")

        # Creates Boundaries
        self.create_rectangle(7, 27, 593, 613, outline="#42f5aa")
        self.create_rectangle(6, 26, 594, 614, outline="#b0f542")

    def move_snake(self):   # Move Snake
        headXPosition, headYPosition = self.snake_positions[0]

        if self.direction == "Left":
            newHeadPosition = (headXPosition - MOVE_STEP, headYPosition)
        elif self.direction == "Right":
            newHeadPosition = (headXPosition + MOVE_STEP, headYPosition)
        elif self.direction == "Down":
            newHeadPosition = (headXPosition, headYPosition + MOVE_STEP)
        elif self.direction == "Up":
            newHeadPosition = (headXPosition, headYPosition - MOVE_STEP)

        # Logic is to move head and chop off one block from the tail
        self.snake_positions = [newHeadPosition] + self.snake_positions[:-1]

        # Moves the snake. Finds the image and its location and changes its coordinates
        for segment, position in zip(self.find_withtag("snake"), self.snake_positions):
            self.coords(segment, position)

    def perform_actions(self):  # Function call on every frame of game instance
        if self.check_collisions():  # Stops the movement of condition is true
            self.end_game()  # Ends the game
            return

        self.check_food_collision()
        self.move_snake()
        self.after(GAME_SPEED, self.perform_actions)  # calls functions after 75 milli Seconds

    def check_collisions(self):  # Checks snake collision with itself or boundaries
        headXPosition, headYPosition = self.snake_positions[0]  # Gets current head position of snake

        return(
            headXPosition in (0, 600)  # Check against boundaries (left and right)
            or headYPosition in (20, 620)  # Check against boundaries (top and bottom)
            or (headXPosition, headYPosition) in self.snake_positions[1:]  # Check against snake body
        )

    def set_new_food_position(self):  # Food needs to appear at random locations where snake is not present
        while True:
            x_position = randint(1, 29) * MOVE_STEP
            y_position = randint(3, 30) * MOVE_STEP
            food_position = (x_position, y_position)

            if food_position not in self.snake_positions:
                return food_position

    def on_key_press(self, e):  # key listener function
        newDirection = e.keysym
        all_directions = ("Up", "Down", "Left", "Right")
        opposites = ({"Up", "Down"}, {"Left", "Right"})
        # Changes snake movement direction
        if (  # Checks if snake does not move back into itself.
            newDirection in all_directions
            and {newDirection, self.direction} not in opposites
        ):
            self.direction = newDirection
        # If at game over screen, restarts game with Space Bar Key
        if e.keysym == "space" and self.game_status is False:
            self.restart_game()

    def check_food_collision(self):  # Collision with the food
        if self.snake_positions[0] == self.food_position:
            self.score += 1  # Incrementing Score
            self.snake_positions.append(self.snake_positions[-1])

            if self.score % 5 == 0:  # increase speed of snake for every +5 score
                global moves_per_second
                moves_per_second += 1

            self.create_image(
                *self.snake_positions[-1], image=self.snake_body, tag="snake"
            )

            self.food_position = self.set_new_food_position()
            self.coords(self.find_withtag("food"), self.food_position)

            # Displaying updated score
            score = self.find_withtag("score")
            self.itemconfigure(score, text=f"Score: {self.score}   Speed: {moves_per_second}", tag="score")

    def restart_game(self):
        self.game_status = True
        self.delete(tk.ALL)
        global moves_per_second
        moves_per_second = 15  # Resets the speed
        newgame = Snake()
        newgame.grid(row=0, column=0)

    def end_game(self):
        self.delete(tk.ALL)  # deletes everything in Canvas
        self.game_status = False
        global moves_per_second
        moves_per_second = 15  # Resets the speed
        self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2,
            text=f"Game Over! You scored {self.score}!",
            fill="#fff",
            font=("Times", 24)
        )
        self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2 + 50,
            text=f"Press Space Bar to restart",
            fill="#fff",
            font=("Times", 20)
        )
        self.create_rectangle(7, 27, 593, 613, outline="#42f5aa")
        self.create_rectangle(6, 26, 594, 614, outline="#b0f542")


# Main Window
root = tk.Tk()
root.title("Snake Game")
root.resizable(False, False)
board = Snake()  # calls the snake class
board.grid(row=0, column=0)  # Places canvas into window

root.mainloop()  # Runs the game loop
