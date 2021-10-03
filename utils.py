import pygame.midi as midi
from launchpadbridge.launchpad import *
import sys
from threading import Thread
from queue import Queue
from time import time, sleep
from random import randint, uniform
from enum import Enum


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
"""


def getRandomCell(minX, maxX, minY, maxY):
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
"""


def turnOffBall(ball: Ball, out: midi.Output):
    if(ball.lastX != ball.x or ball.lastY != ball.y):
        setCell(ball.lastX, ball.lastY, OFF, out)


"""
Turns on and off all LEDs quickly to produce a flashing effect
@param Color color color to light the LEDs with
@param midi.Output out output device
@param int repeat number of times to flash the LEDs
"""


def flashBoard(color: Color, out: midi.Output, repeat=1):
    for _ in range(repeat):
        setAllCells(color, out)
        sleep(0.5)
        setAllCells(OFF, out)
        sleep(0.5)


"""
Initializes all variables to their default values
"""


def initGame(out: midi.Output):
    global play
    global quit
    global barLeft
    global barRight
    global ball

    barLeft = Bar()
    barRight = Bar()
    ball = Ball()

    ball.x, ball.y = getRandomCell(3, 4, 3, 4)
    ball.lastX = ball.x
    ball.lastY = ball.y
    ball.speed = 0.5
    ball.direction = Direction.E

    barLeft.x = 0
    barLeft.y = getRandomCell(0, 0, 2, 3)[1]

    barRight.x = 7
    barRight.y = getRandomCell(0, 0, 2, 3)[1]

    play = False
    quit = False

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
    turnOffBall(ball, out)
    setCell(ball.x, ball.y, GREEN, out)
    for i in range(barLeft.height):
        setCell(barLeft.x, barLeft.y + i, ORANGE, out)
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
Modifies the coordinates of the ball depending on the player inputs
"""


def moveBar(left: bool, up: bool):
    if(play):
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
    global play
    global quit
    global barLeft
    global barRight
    global ball

    while(not quit):
        event = pollEvent(inp)
        if (event):
            if (event.down):
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
                elif(event.x == 8 and event.y == 3):
                    if(play):
                        break
                        # initGame(ball, out)
                    else:
                        play = True
                elif(event.x == 8 and event.y == 4):
                    quit = True


def threadPrint(output: midi.Output):
    global quit

    while(not quit):
        showGame(output)


def threadGame():
    global play
    global quit
    global barLeft
    global barRight
    global ball

    # Wait for the player to press the play or exit buttons
    while(not play and not quit):
        pass

    while(not quit):
        '''
        Check if the ball is on the edges of the ball grid
        and either changes its direction or ends the game
        '''

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
            # middle of the left bar
            elif(ball.y == barLeft.y + 1):
                ball.direction = Direction.E
            # bottom of the left bar
            elif(ball.y == barLeft.y + 2):
                ball.direction = Direction.SE
            # not touching the left bar
            else:
                print("Orange player looses!")
                quit = True

        # right column of the ball grid
        elif(ball.x == 6):
            # top of the right bar
            if(ball.y == barRight.y):
                ball.direction = Direction.NW
            # middle of the right bar
            elif(ball.y == barRight.y + 1):
                ball.direction = Direction.W
            # bottom of the right bar
            elif(ball.y == barRight.y + 2):
                ball.direction = Direction.SW
            # not touching the right bar
            else:
                print("Red player looses!")
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
        sleep(ball.speed)


'''
Global variables that need to be accessed by both threads
'''
barLeft = None
barRight = None
ball = None
play = None
quit = None
