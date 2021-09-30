from pygame.midi import Input, Output
from launchpadbridge.launchpad import *
from time import time, sleep
from random import randint, uniform
import threading


DEBUG = False


def log(stuff):
    if DEBUG:
        print(f"[LOG] {stuff}")


class Ball:
    x = None
    y = None
    lastX = None
    lastY = None


class Bar:
    x = None
    y = None
    height = None


def getRandomCell(minX, maxX, minY, maxY):
    '''Returns x, y for a random cell in the grid'''
    x = randint(minX, maxX)
    y = randint(minY, maxY)
    return x, y


def cleanMiddle(out: Output):
    for x in range(1, 7):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


def cleanLeftBar(out: Output):
    for x in range(0, 1):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


def cleanRightBar(out: Output):
    for x in range(7, 8):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


def cleanButtons(out: Output):
    for x in range(8, 9):
        for y in range(0, 8):
            setCell(x, y, OFF, out)


def cleanBall(ball: Ball, out: Output):
    setCell(ball.lastX, ball.lastY, OFF, out)


def flashBoard(colour: Color, out: Output, repeat=1):
    for _ in range(repeat):
        setAllCells(colour, out)
        sleep(0.5)
        setAllCells(OFF, out)
        sleep(0.5)


def initGame(ball: Ball, barLeft: Bar, barRight: Bar):
    ball.x, ball.y = getRandomCell(3, 4, 3, 4)
    barLeft.x = 0
    barLeft.y = getRandomCell(0, 0, 2, 3)[1]
    barLeft.height = 3
    barRight.x = 7
    barRight.y = getRandomCell(0, 0, 2, 3)[1]
    barRight.height = 3


def showGame(ball: Ball, barLeft: Bar, barRight: Bar, out: Output):
    cleanBall(ball, out)
    setCell(ball.x, ball.y, GREEN, out)
    for i in range(barLeft.height):
        setCell(barLeft.x, barLeft.y + i, RED, out)
    for i in range(barRight.height):
        setCell(barRight.x, barRight.y + i, RED, out)


def thread(inp: Input, out: Output):
    print("oui")
    while(1):
        event = pollEvent(inp)
        if (event):
            if (event.down):
                if(event.x == 8 and event.y == 0):
                    setCell(event.x, event.y, AMBER, out)
                    barLeft.y -= 1
                    cleanLeftBar(out)
                if(event.x == 8 and event.y == 1):
                    setCell(event.x, event.y, AMBER, out)
                    barLeft.y += 1
                    cleanLeftBar(out)
                if(event.x == 8 and event.y == 6):
                    setCell(event.x, event.y, AMBER, out)
                    barRight.y -= 1
                    cleanRightBar(out)
                if(event.x == 8 and event.y == 7):
                    setCell(event.x, event.y, AMBER, out)
                    barRight.y += 1
                    cleanRightBar(out)
                cleanButtons(out)


barLeft = Bar()
barRight = Bar()


def main():
    input, output = init()

    ball = Ball()

    initGame(ball, barLeft, barRight)

    showGame(ball, barLeft, barRight, output)

    x = threading.Thread(target=thread, args=(input, output))
    x.start()

    while(1):
        while(ball.x != 6):
            ball.lastX = ball.x
            ball.lastY = ball.y
            ball.x += 1
            showGame(ball, barLeft, barRight, output)
            sleep(0.1)
        while(ball.x != 1):
            ball.lastX = ball.x
            ball.lastY = ball.y
            ball.x -= 1
            showGame(ball, barLeft, barRight, output)
            sleep(0.1)

    setAllCells(OFF, output)


if __name__ == "__main__":
    main()
