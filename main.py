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
    exit(1)


if __name__ == "__main__":
    main()
