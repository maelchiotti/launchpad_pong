import launchpadbridge.launchpad as launchpad
from time import time, sleep
from random import randint, uniform


DEBUG = False


def log(stuff):
    if DEBUG:
        print(f"[LOG] {stuff}")


class Enemy:
    health = 3
    position = None


class Settings:
    enemy_spawn_delay = 5
    diffIncrease = 0.1
    health_dict = {
        3: launchpad.GREEN,
        2: launchpad.ORANGE,
        1: launchpad.RED,
    }


def getRandomCell():
    '''Returns x, y for a random cell in the grid'''
    x = randint(0, 7)
    y = randint(0, 7)
    return x, y


def getEnemyPositions(grid) -> list[list]:
    '''Returns a list of [x, y] lists of positions of enemies'''
    enemies = []

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if isinstance(grid[y][x], Enemy):
                enemies.append([x, y])

    return enemies


def getEnemies(grid) -> list[Enemy]:
    '''Returns a list of enemy objects from the grid'''
    positions = getEnemyPositions(grid)
    enemies = []
    for pos in positions:
        e = grid[pos[1]][pos[0]]
        if e:
            # Give the enemy obj its position
            e.position = pos
            enemies.append(e)
        else:
            log(f"getEnemies was given pos {pos} but there was no enemy there?")

    return enemies


def getSpecificEnemy(grid, cords) -> Enemy:
    '''Returns a specific enemy from cordinaates, if it exists'''
    for enemy in getEnemies(grid):
        if enemy.position == cords:
            return enemy
    return None


def hitEnemy(grid, cords):
    '''Returns True if the cords given hits an enemy'''
    positions = getEnemyPositions(grid)
    if cords in positions:
        return True


def getSpawnDelay(diff):
    maxDelay = 5 * (1 / diff)
    delay = 0.2 + uniform(0, maxDelay)

    return delay


def printInfo(h, s, msgs):
    print("\n" * 15 + msgs + f"\nHealth: {h}\nScore: {s}\n")


def flash_board(colour, out, t=3):
    for _ in range(t):
        launchpad.setAllCells(colour, out)
        sleep(0.2)
        launchpad.setAllCells(launchpad.OFF, out)
        sleep(0.2)


def render_heath_bar(health, device, col=launchpad.ORANGE):
    light_cords = [7, 6, 5, 4, 3]
    # Clear bar
    for l in light_cords:
        launchpad.setCell(8, l, launchpad.OFF, device)

    if health >= 5:
        for l in light_cords:
            launchpad.setCell(8, l, col, device)
        return
    elif health < 1:
        return
    else:
        for i in range(health):
            launchpad.setCell(8, light_cords[i], col, device)
    return


# Generate game grid
grid = [[None for _ in range(8)] for _ in range(8)]


def main():
    # Init launchpad
    InputDevice, OutputDevice = launchpad.init()

    spawnDelay = 0
    lastEnemySpawn = time()
    running = True
    difficulty = 1
    score = 0
    enemyCount = 0
    health = 5

    flash_board(launchpad.GREEN, OutputDevice)
    render_heath_bar(health, OutputDevice)

    while running:

        # Spawn new enemy
        if time() - lastEnemySpawn > spawnDelay:
            log("Time to spawn enemy:")
            x, y = getRandomCell()
            log(f"Got random cell: {x}, {y}")

            if grid[y][x] is None:
                log(f"Cell is clear, spawning")
                enemyCount += 1
                grid[y][x] = Enemy()
                lastEnemySpawn = time()
                spawnDelay = getSpawnDelay(difficulty)
                log(f"Spawn delay: {spawnDelay}")

                if enemyCount > 63:
                    print("\nYOU LOST!\nThere were too many enemies, gg.\n")
                    running = False
                    continue
            else:
                log(f"Cell is not clear. Will try again next round")
                continue

        # Poll for events

        event = launchpad.pollEvent(InputDevice)
        if event:
            if event.down:
                if hitEnemy(grid, event.cords):

                    enemy = grid[event.cords[1]][event.cords[0]]
                    if enemy.health > 1:
                        enemy.health -= 1
                        log(f"Hit enemy")
                    else:
                        log(f"Killed enemy")
                        launchpad.setCell(
                            event.cords[0], event.cords[1], launchpad.OFF, OutputDevice)
                        grid[event.cords[1]][event.cords[0]] = None

                        score += 1
                        difficulty += Settings.diffIncrease
                        enemyCount -= 1
                        printInfo(health, score, "Killed an Enemy!")
                else:
                    health -= 1
                    render_heath_bar(health, OutputDevice)
                    if health > 0:
                        printInfo(health, score,
                                  "Missed! The enemies hit you!")
                    else:
                        print("YOU LOST!\nYou ran out of health, gg.\n")
                        running = False
                        continue

        # Render grid
        for enemyPosition in getEnemyPositions(grid):
            enemy = getSpecificEnemy(grid, enemyPosition)

            # Get colour
            colour = Settings.health_dict[enemy.health]

            x, y = enemy.position

            launchpad.setCell(x, y, colour, OutputDevice)

    flash_board(launchpad.RED, OutputDevice)


if __name__ == "__main__":
    main()
