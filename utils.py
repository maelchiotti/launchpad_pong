import pygame.midi as midi
from launchpadbridge.launchpad import *
import sys
import threading
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
Return a random cell on the grid, among the for ones in the center
Allows to place the ball at the begining of the game
"""


def getRandomCell(minX, maxX, minY, maxY):
    x = randint(minX, maxX)
    y = randint(minY, maxY)
    return x, y


"""
Turns off all the LEDs in the middle of the grid
(not the first and last columns or the buttons)
"""


def cleanMiddle(out: midi.Output):
    for x in range(1, 7):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""
Turns off all the LEDs in the first column of the grid
(effectively turning off the left bar)
"""


def cleanLeftBar(out: midi.Output):
    for x in range(0, 1):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""Turns off all the LEDs in the last column of the grid
(effectively turning off the right bar)"""


def cleanRightBar(out: midi.Output):
    for x in range(7, 8):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""
Turns off all the LEDs in the buttons column of the grid
(effectively turning off all buttons)
"""


def cleanButtons(out: midi.Output):
    for x in range(8, 9):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


"""
Turns off the LED at the last remembered position of the ball
"""


def cleanBall(ball: Ball, out: midi.Output):
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


def initGame(ball: Ball, out: midi.Output):
    ball.x, ball.y = getRandomCell(3, 4, 3, 4)
    ball.lastX = ball.x
    ball.lastY = ball.y
    ball.speed = 0.5
    ball.direction = Direction.E

    barLeft.x = 0
    barLeft.y = getRandomCell(0, 0, 2, 3)[1]

    barRight.x = 7
    barRight.y = getRandomCell(0, 0, 2, 3)[1]

    setCell(8, 0, ORANGE, out)
    setCell(8, 1, ORANGE, out)
    setCell(8, 6, RED, out)
    setCell(8, 7, RED, out)


"""
Lights on LEDs according to the current game state
"""


def showGame(ball: Ball, out: midi.Output):
    cleanBall(ball, out)
    setCell(ball.x, ball.y, GREEN, out)
    for i in range(barLeft.height):
        setCell(barLeft.x, barLeft.y + i, ORANGE, out)
    for i in range(barRight.height):
        setCell(barRight.x, barRight.y + i, RED, out)


"""
Modifies the coordinates of the ball depending on its direction
"""


def moveBall(ball: Ball):
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
    global quit
    global barLeft
    global barRight

    while(1):
        event = pollEvent(inp)
        if (event):
            if (event.down):
                if(event.x == 8 and event.y == 0):
                    if(moveBar(True, True)):
                        cleanLeftBar(out)
                elif(event.x == 8 and event.y == 1):
                    if(moveBar(True, False)):
                        cleanLeftBar(out)
                elif(event.x == 8 and event.y == 6):
                    if(moveBar(False, True)):
                        cleanRightBar(out)
                elif(event.x == 8 and event.y == 7):
                    if(moveBar(False, False)):
                        cleanRightBar(out)
                elif(event.x == 8 and event.y == 4):
                    quit = True
                    sys.exit()


barLeft = Bar()  # Left bar, corresponding to the left and orange player
barRight = Bar()  # Left bar, corresponding to the right and red player
quit = False  # If the game needs to be ended, from a player input or one of them won
