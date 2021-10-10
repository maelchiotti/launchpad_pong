import pygame.midi as midi
from launchpadbridge.launchpad import *
from threading import Thread
from time import sleep
from random import randint
from enum import Enum
import os
import sys


"""
List of all the directions in wich the ball can move
"""


class Direction(Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


"""
Ball the players have to hit
"""


class Ball:
    x = None
    y = None
    lastX = None
    lastY = None
    speed = None
    direction = None


"""
Bars the players have to move to hit the ball
"""


class Bar:
    x = None
    y = None
    height = 3


"""
Return a random cell on the grid
(allows to place the ball at the begining of the game)
@param int minX minimum value for x
@param int minX maximum value for x
@param int minY minimum value for y
@param int minY maximum value for y
"""


def getRandomCell(minX: int, maxX: int, minY: int, maxY: int):
    x = randint(minX, maxX)
    y = randint(minY, maxY)
    return x, y


"""
Turns off all the LEDs in the middle of the grid
(not the first and last columns or the buttons)
"""


def turnOffMiddle(out: midi.Output):
    for x in range(1, 7):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""
Turns off all the LEDs in the first column of the grid
(effectively turning off the left bar)
"""


def turnOffLeftBar(out: midi.Output):
    for x in range(0, 1):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""Turns off all the LEDs in the last column of the grid
(effectively turning off the right bar)"""


def turnOffRightBar(out: midi.Output):
    for x in range(7, 8):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""
Turns off all the LEDs in the buttons column of the grid
(effectively turning off all buttons)
"""


def turnOffButtons(out: midi.Output):
    for x in range(8, 9):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""
Turns off the LED at the last remembered position of the ball
if it has moved since
"""


def turnOffBall(out: midi.Output):
    if(ball.lastX != ball.x or ball.lastY != ball.y):
        setCell(ball.lastX, ball.lastY, OFF, out)


"""
Turns on and off all LEDs quickly to produce a flashing effect
@param Color color color to light the LEDs with
@param int delay delay after wich the LEDs are turned on are off
@param int repeat number of times to flash the LEDs
"""


def flashBoard(out: midi.Output, color: Color, delay: int = 0.5, repeat: int = 1):
    for i in range(repeat):
        setAllCells(color, out)
        sleep(delay)
        setAllCells(OFF, out)
        # avoid calling the sleep() function on the last iteration
        if(i < repeat - 1):
            sleep(delay)


"""
Initializes all variables to their default values
@param int initialSpeed initial speed of the ball
"""


def initGame(out: midi.Output, initialSpeed: int):
    global barLeft
    global barRight
    global ball
    global winner
    global play
    global quit

    barLeft = Bar()
    barRight = Bar()
    ball = Ball()

    ball.x, ball.y = getRandomCell(3, 4, 3, 4)
    ball.lastX = ball.x
    ball.lastY = ball.y
    ball.speed = initialSpeed
    ball.direction = Direction.E

    barLeft.x = 0
    barLeft.y = ball.y - 1  # bars are aligned with the ball

    barRight.x = 7
    barRight.y = ball.y - 1  # bars are aligned with the ball

    play = False
    quit = False
    winner = "NONE"

    # right bar controls
    setCell(8, 6, RED, out)
    setCell(8, 7, RED, out)

    # left bar controls
    setCell(8, 0, ORANGE, out)
    setCell(8, 1, ORANGE, out)

    setCell(8, 3, GREEN, out)  # play button
    setCell(8, 4, RED, out)  # quit button


"""
Lights on LEDs according to the current game state
"""


def showGame(out: midi.Output):
    # ball
    turnOffBall(out)
    setCell(ball.x, ball.y, GREEN, out)
    # left bar
    for i in range(barLeft.height):
        setCell(barLeft.x, barLeft.y + i, ORANGE, out)
    # right bar
    for i in range(barRight.height):
        setCell(barRight.x, barRight.y + i, RED, out)


"""
Modifies the coordinates of the ball depending on its direction
"""


def moveBall():
    if(ball.direction == Direction.N):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.y -= 1
    elif(ball.direction == Direction.NE):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.x += 1
        ball.y -= 1
    elif(ball.direction == Direction.E):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.x += 1
    elif(ball.direction == Direction.SE):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.x += 1
        ball.y += 1
    elif(ball.direction == Direction.S):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.y += 1
    elif(ball.direction == Direction.SW):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.x -= 1
        ball.y += 1
    elif(ball.direction == Direction.W):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.x -= 1
    elif(ball.direction == Direction.NW):
        ball.lastX = ball.x
        ball.lastY = ball.y
        ball.x -= 1
        ball.y -= 1
    else:
        print("[ERROR] Ball has no direction")
        exit(-1)


"""
Modifies the coordinates of the bar depending on the player inputs
@param bool left if the left bar needs to be moved, otherwise it's the right one
@param bool up if the bar needs to be moved upwards, otherwise it's downwards
"""


def moveBar(left: bool, up: bool):
    if(left):
        if(up):
            if(barLeft.y >= 1):
                barLeft.y -= 1
                return True
        else:
            if(barLeft.y <= 4):
                barLeft.y += 1
                return True
    else:
        if(up):
            if(barRight.y >= 1):
                barRight.y -= 1
                return True
        else:
            if(barRight.y <= 4):
                barRight.y += 1
                return True
    return False


"""
Thread that monitors player inputs while the game is running
"""


def threadInputs(inp: midi.Input, out: midi.Output):
    global barLeft
    global barRight
    global ball
    global play
    global quit

    while(not quit):
        event = pollEvent(inp)
        if (event and event.down):
            if(event.x == 8 and event.y == 3):
                if(not play):
                    play = True
            elif(event.x == 8 and event.y == 4):
                quit = True
            elif(play):
                if(event.x == 8 and event.y == 0):
                    if(moveBar(True, True)):
                        turnOffLeftBar(out)
                elif(event.x == 8 and event.y == 1):
                    if(moveBar(True, False)):
                        turnOffLeftBar(out)
                elif(event.x == 8 and event.y == 6):
                    if(moveBar(False, True)):
                        turnOffRightBar(out)
                elif(event.x == 8 and event.y == 7):
                    if(moveBar(False, False)):
                        turnOffRightBar(out)


"""
Thread that prints informations while the game is running
"""


def threadPrint(out: midi.Output):
    global quit

    while(not quit):
        showGame(out)

    if(winner == "RED"):
        flashBoard(out, RED, 2, 1)
    elif(winner == "ORANGE"):
        flashBoard(out, ORANGE, 2, 1)
    elif(winner == "NONE"):
        pass
    else:
        print("[ERROR] Winner has an unknown value: " + winner)
        exit(-1)


"""
Thread that handles the game
"""


def threadGame(out: midi.Output, speedDrop: int, speedMin: int):
    global barLeft
    global barRight
    global ball
    global winner
    global play
    global quit

    # Wait for the player to press the play or exit buttons
    while(not play and not quit):
        pass

    setCell(8, 3, OFF, out)  # play button

    barHitCounter = 0

    while(not quit):
        """
        Check if the ball is on the edges of the ball grid
        and either changes its direction or ends the game
        """

        # top left corner
        if(ball.x == 1 and ball.y == 0 and barLeft.y == 0):
            ball.direction = Direction.SE
        # top right corner
        elif(ball.x == 6 and ball.y == 0 and barRight.y == 0):
            ball.direction = Direction.SW
        # bottom left corner
        elif(ball.x == 1 and ball.y == 7 and barLeft.y == 5):
            ball.direction = Direction.NE
        # bottom right corner
        elif(ball.x == 6 and ball.y == 7 and barRight.y == 5):
            ball.direction = Direction.NW

        # left column of the ball grid
        elif(ball.x == 1):
            # top of the left bar
            if(ball.y == barLeft.y):
                ball.direction = Direction.NE
                barHitCounter += 1
            # middle of the left bar
            elif(ball.y == barLeft.y + 1):
                ball.direction = Direction.E
                barHitCounter += 1
            # bottom of the left bar
            elif(ball.y == barLeft.y + 2):
                ball.direction = Direction.SE
                barHitCounter += 1
            # not touching the left bar
            else:
                winner = "RED"
                quit = True

        # right column of the ball grid
        elif(ball.x == 6):
            # top of the right bar
            if(ball.y == barRight.y):
                ball.direction = Direction.NW
                barHitCounter += 1
            # middle of the right bar
            elif(ball.y == barRight.y + 1):
                ball.direction = Direction.W
                barHitCounter += 1
            # bottom of the right bar
            elif(ball.y == barRight.y + 2):
                ball.direction = Direction.SW
                barHitCounter += 1
            # not touching the right bar
            else:
                winner = "ORANGE"
                quit = True

        # top row of the ball grid
        elif(ball.y == 0):
            # coming from the NW
            if(ball.direction == Direction.NW):
                ball.direction = Direction.SW
            # coming from the NE
            elif(ball.direction == Direction.NE):
                ball.direction = Direction.SE
            else:
                print("[ERROR] Ball in (" + str(ball.x) + " + " + str(ball.y) +
                      ") has an impossible direction : " + str(ball.direction))
                exit(-1)

        # bottom row of the ball grid
        elif(ball.y == 7):
            # coming from the SW
            if(ball.direction == Direction.SW):
                ball.direction = Direction.NW
            # coming from the SE
            elif(ball.direction == Direction.SE):
                ball.direction = Direction.NE
            else:
                print("[ERROR] Ball in (" + str(ball.x) + " + " + str(ball.y) +
                      ") has an impossible direction : " + str(ball.direction))
                exit(-1)

        moveBall()
        finalSpeed = ball.speed - barHitCounter * speedDrop
        if(finalSpeed < speedMin):
            finalSpeed = speedMin
        sleep(finalSpeed)


"""
Global variables that need to be accessed by all threads
"""
barLeft = None
barRight = None
ball = None
winner = None
play = None
quit = None
