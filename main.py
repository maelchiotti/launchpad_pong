from utils import *


def main():
    input, output = init()

    setAllCells(OFF, output)

    initialSpeed = 0.5
    speedDrop = 0.02
    speedMin = 0.1
    initGame(output, initialSpeed)

    game = Thread(target=threadGame, args=(output, speedDrop, speedMin))
    inputs = Thread(target=threadInputs, args=(input, output))
    print = Thread(target=threadPrint, args=(output, ))

    inputs.start()
    game.start()
    print.start()

    inputs.join()
    game.join()
    print.join()

    setAllCells(OFF, output)
    setCell(8, 3, GREEN, output)  # play button
    setCell(8, 4, RED, output)  # quit button

    # Waits for the player to quit or relaunch the game
    exit = False
    while(not exit):
        event = pollEvent(input)
        if (event and event.down):
            if(event.x == 8 and event.y == 3):
                # relaunches the program entirely
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif(event.x == 8 and event.y == 4):
                exit = True

    setAllCells(OFF, output)
    exit(1)


if __name__ == "__main__":
    main()
