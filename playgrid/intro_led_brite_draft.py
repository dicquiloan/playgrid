# SPDX-FileCopyrightText: 2022 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import random
import board
from board import SCL, SDA
import digitalio
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

##neotrellis
import qmaze_neotrellis

# Create the I2C object for the NeoTrellis
i2c_bus = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Create the NeoTrellis object
# This is for a 2x2 array of NeoTrellis boards:
trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E), NeoTrellis(i2c_bus, False, addr=0x2F)],
    [NeoTrellis(i2c_bus, False, addr=0x30), NeoTrellis(i2c_bus, False, addr=0x31)],
]

trellis = MultiTrellis(trelli)

DIM_X = 8
DIM_Y = 8

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (127, 127, 127)

# Define the colors of the rainbow
RAINBOW_COLORS = [RED, YELLOW, GREEN, BLUE, PURPLE, WHITE]

# Calculate the number of colors needed for the grid
num_colors = 8 * 8
colors_per_band = len(RAINBOW_COLORS)
num_bands = num_colors // colors_per_band + 1

# Create the rainbow grid
rainbow_grid = []
for i in range(num_bands):
    rainbow_grid += RAINBOW_COLORS

# connect a button to the NeoTrellis board
button_pin = board.D6
button = digitalio.DigitalInOut(button_pin)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


global button_colors

# Initialize color state for each button
button_colors = [[OFF for y in range(DIM_Y)] for x in range(DIM_X)]


# Set the brightness value (0 to 1.0)
trellis.brightness = 0.1

class Host:
    def __init__(self,getColour,setColour):
        self.getColour = getColour
        self.setColour = setColour
        ##self.audio = audio

        ##print("Loading sound files into memory")
        ##self.sounds_dict = {}

        # Load sound files into sounds dictionary
        ##self.sounds_dict['glass_break'] = WaveFile(open("./sounds/GlassBreak.wav", "rb"))
        # Load sound files with text keys to identify them here (just a few CC licensed sound files are included in source as examples)
        # self.sounds_dict['sound_key'] = WaveFile(open("./sounds/soundfile.wav", "rb"))

    def getColour(self):
        return self.getColour

    def setColour(self):
        return self.setColour

    def restoreColour(self,x,y):
        self.setColour(x,y,self.getColour(x,y),False)

leds = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        [0,0,0],[0,0,0],[0,0,0],[0,0,0],
        ]

def setColour(x,y,colour,store=True):
    if 0 <= x <= 7 and 0 <= y <= 7:
        if store:
            leds[y * dimY + x] = colour
        trellis.color(x, y, colour)
        #print(f"At {x},{y}: {colour}")
    else:
        print(f"Request to set colour outside trellis at: {x},{y}")


def getColour(x,y):
    return leds[y * dimY + x]


def gridReset(colour):
    """
    Resets all lights and stored colours to the same colour value
    """
    for y in range(dimY):
        for x in range(dimX):
            setColour( x, y, colour)

# This will be called when button events are received
def blink(xcoord, ycoord, edge):

    # Turn the LED on when a rising edge is detected
    if edge == NeoTrellis.EDGE_RISING:
        current_color = button_colors[xcoord][ycoord]

        if current_color == OFF:
            if ycoord == 0:
                if xcoord == 0:
                    print("It worked!")
                    activeGame = qmaze_neotrellis(host)
            trellis.color(xcoord, ycoord, YELLOW)
            button_colors[xcoord][ycoord] = YELLOW
        elif current_color == YELLOW:
            trellis.color(xcoord, ycoord, RED)
            button_colors[xcoord][ycoord] = RED
        elif current_color == RED:
            trellis.color(xcoord, ycoord, GREEN)
            button_colors[xcoord][ycoord] = GREEN
        elif current_color == GREEN:
            trellis.color(xcoord, ycoord, BLUE)
            button_colors[xcoord][ycoord] = BLUE
        elif current_color == BLUE:
            trellis.color(xcoord, ycoord, PURPLE)
            button_colors[xcoord][ycoord] = PURPLE
        elif current_color == PURPLE:
            trellis.color(xcoord, ycoord, WHITE)
            button_colors[xcoord][ycoord] = WHITE
        else:
            trellis.color(xcoord, ycoord, OFF)
            button_colors[xcoord][ycoord] = OFF

# this will be called when button events are received
def btnHandler(x, y, edge):
    global lastBtnPressed, lastPressTime
    
    #print(f"Button pressed {x},{y}")
    # Check for button pressed and released events, and pass to active game class
    if edge == NeoTrellis.EDGE_RISING:
        # Store position of button for checking for long press events
        lastBtnPressed = [x,y]
        # Call active game class button event handler
        activeGame.btnEvent(x,y,True)
    elif edge == NeoTrellis.EDGE_FALLING:
        # Check for long button press
        if (lastBtnPressed == [x,y]) and ((time.monotonic_ns() - lastPressTime) > longPressInterval):
            # Long press
            setColour(x, y, (0,0,0), False)
            longPress(x, y)

    # Call active game class button event handler
        activeGame.btnEvent(x,y,False)
        # Clear last pressed position on any button release
        lastBtnPressed = [-1,-1]
    
    # Reset last press time on any button event
    lastPressTime = time.monotonic_ns()

for y in range(DIM_Y):
    for x in range(DIM_X):
        # Activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # Activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, btnHandler)
        trellis.color( x, y, (100, 0, 255) )

host = Host(getColour,setColour)

activeGame = qmaze_neotrellis(host)

## rainbow splash screen
def activate():
    for y in range(DIM_Y):
        for x in range(DIM_X):
            # Activate rising edge events on all keys
            trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
            # Activate falling edge events on all keys
            trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
            trellis.set_callback(x, y, blink)
            color_index = x + y * 8
            trellis.color(x, y, rainbow_grid[color_index % num_colors])
    for y in range(DIM_Y):
        for x in range(DIM_X):
            trellis.color(x, y, OFF)
            time.sleep(0.005)

def option(x, y):
    if y == 0:
        if x == 0:
            print("It worked!")

activate()
##splash()

while True:
    # The NeoTrellis can only be read every 17 milliseconds or so
    trellis.sync()
    time.sleep(0.02)
