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

# Initialize color state for each button
button_colors = [[OFF for y in range(8)] for x in range(8)]

# Set the brightness value (0 to 1.0)
trellis.brightness = 0.1

# This will be called when button events are received
def blink(xcoord, ycoord, edge):
    global button_colors

    # Turn the LED on when a rising edge is detected
    if edge == NeoTrellis.EDGE_RISING:
        current_color = button_colors[xcoord][ycoord]

        if current_color == OFF:
            trellis.color(xcoord, ycoord, RED)
            button_colors[xcoord][ycoord] = RED
        elif current_color == RED:
            trellis.color(xcoord, ycoord, YELLOW)
            button_colors[xcoord][ycoord] = YELLOW
        elif current_color == YELLOW:
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

for y in range(8):
    for x in range(8):
        # Activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # Activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, blink)
        color_index = x + y * 8
        trellis.color(x, y, rainbow_grid[color_index % num_colors])
for y in range(8):
    for x in range(8):
        trellis.color(x, y, OFF)
        time.sleep(0.005)

while True:
    # The NeoTrellis can only be read every 17 milliseconds or so
    trellis.sync()
    time.sleep(0.02)
