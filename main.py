from utils import *


def main():
    global quit

    input, output = init()
    ball = Ball()

    initGame(ball, output)
    showGame(ball, output)

    x = threading.Thread(target=threadInputs, args=(input, output))
    x.start()

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
                x.join()
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
                x.join()
                exit(-1)

        moveBall(ball)
        showGame(ball, output)
        sleep(ball.speed)

    setAllCells(OFF, output)
    exit(1)


if __name__ == "__main__":
    main()
