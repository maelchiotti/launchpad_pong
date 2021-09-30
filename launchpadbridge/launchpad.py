import pygame.midi as midi

# Colours
class Color:
    def __init__(self, r, g):
        self.value = 12 + (16 * g) + r 

OFF = Color(0, 0).value
RED = Color(3, 0).value
GREEN = Color(0, 3).value
AMBER = Color(3, 3).value


# Generate lookup table
key_lookup = {}

row_starters = [16 * x  for x in range(8)]

for yValue in range(len(row_starters)):
    for xValue in range(9):
        row_starter = row_starters[yValue]
        current_value = row_starter + xValue
        key_lookup[current_value] = [xValue, yValue]

class CellEvent:
    down = False
    x = 0
    y = 0
    def __init__(self, pressed, cords) -> None:
        self.down = pressed
        self.x = cords[0]
        self.y = cords[1]
    
    @property
    def cords(self):
        return [self.x, self.y]

def decodeMidiEvent(event: list):
    '''Takes midid event list, returns cords of button press'''
    if type(event) != list:
        print("decodeMidiEvent Was not given list. Was given: " + str(event))
        return None
    if not event:
        return None
    
    keyID = event[0][0][1]
    pressed = event[0][0][2]

    pressedBool = pressed == 127
    key = key_lookup[keyID]

    return pressedBool, key

def pollEvent(device) -> CellEvent:
    '''Poll for midi event'''
    event = decodeMidiEvent(device.read(1))
    if event:
        pressed, keyCord = event
        return CellEvent(pressed, keyCord)
    else:
        return None

def setCell(x, y, colour, device: midi.Output):
    '''Set a cell to a colour'''
    for key, value in key_lookup.items():
        if value == [x, y]:
            device.note_on(key, colour)

def setAllCells(colour, device: midi.Output):
    '''Set all cells to a colour'''
    for key in key_lookup:
        device.note_on(key, colour)


def init():
    '''Initialise launchpad.py'''
    inputDevice = None
    outputDevice = None

    midi.init()

    inputDevice = midi.Input(1, 10)

    outputDevice = midi.Output(3)


    setAllCells(OFF, outputDevice)

    return inputDevice, outputDevice
