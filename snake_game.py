# Testing the snake game
import turtle
import time
import random

delay = 0.1 # In Seconds

# Score
score = 0
high_score = 0

# Screen Setup
wn = turtle.Screen()
wn.title("Snake Game by Hamzah Qasim")
wn.bgcolor("#f8e597")
wn.setup(width = 600, height = 600)
wn.tracer(0) # turns off the screen update

# Snake Head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("#006622")
head.penup()
head.goto(0,0)
head.direction = "stop"

# Snake Food
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("#db494a")
food.penup()
food.goto(random.randint(-290, 290),random.randint(-290, 290))

segments = [] # Initializing Snake Body

# Pen (Score Boad)
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("black")
pen.penup()
pen.hideturtle()
pen.goto(0,265)
pen.write("Score: 0 High Score: 0", align="center", font=("Courier", 24, "normal"))

# Functions
def go_up():
    if head.direction != "down":
        head.direction = "up"
def go_down():
    if head.direction != "up":
        head.direction = "down"
def go_left():
    if head.direction != "right":
        head.direction = "left"
def go_right():
    if head.direction != "left":
        head.direction = "right"
def move():
    if head.direction == "up": 
        head.sety(head.ycor() + 20)
    if head.direction == "down":
        head.sety(head.ycor() - 20)
    if head.direction == "right":
        head.setx(head.xcor() + 20)
    if head.direction == "left":
        head.setx(head.xcor() - 20)
def game_reset():
    time.sleep(1)
    head.goto(0,0)
    head.direction = "stop"
    score = 0
    delay = 0.1 # Reset the delay
    pen.clear()
    pen.write("Score: {} High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))
    for segment in segments:
        segment.goto(1000,1000)
    segments.clear()
    food.goto(random.randint(-290, 290),random.randint(-290, 290))

# Keyboard Bidings
wn.listen()
wn.onkeypress(go_up,"Up")
wn.onkeypress(go_down,"Down")
wn.onkeypress(go_left,"Left")
wn.onkeypress(go_right,"Right")

# Main Loop
while True:
    wn.update()

    # Check for collision with the border
    if head.xcor()>290 or head.xcor()<-290 or head.ycor()>290 or head.ycor()<-290:
        game_reset()

    #Check for collision with food
    if head.distance(food) < 20:
        # Move the food to a random spot
        x = random.randint(-290, 290)
        y = random.randint(-290, 290)
        food.goto(x, y)
        #Add a segment
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#00b300")
        new_segment.penup()
        segments.append(new_segment)

        delay -= 0.001 # Shorten the delay

        # Increase the Score
        score += 10
        if score > high_score:
            high_score = score
        pen.clear()
        pen.write("Score: {} High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))
    
    # Move the end segments first in reverse order
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x,y)
    
    # Move Segment 0 to where the head is
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x,y)

    move() 

    #Check for head collision with the body segments
    for segment in segments:
        if segment.distance(head) < 20:
            game_reset()

    time.sleep(delay)
wn.mainloop()