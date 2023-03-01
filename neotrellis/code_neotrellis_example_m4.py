        # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# not sure why but mu editor/cp keeps doing a reload/soft reboot unless we do this
# so then we have to use Ctrl-D to reload with Mu editor
##import supervisor

##supervisor.disable_autoreload()
##print("autoreload disabled")

import time

from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis

import board
import neopixel

# #### from neoPixel - bottom of M4  pixel
PIXEL_PIN = board.D1  # pin that the NeoPixel is connected to
ORDER = neopixel.RGB  # pixel color channel order
COLOR = (100, 50, 150)  # color to blink
CLEAR = (0, 0, 0)  # clear (or second color)
DELAY = 0.25  # blink rate in seconds

# Create the NeoPixel object
pixel = neopixel.NeoPixel(PIXEL_PIN, 1, pixel_order=ORDER)

def blinkPixel():
    pixel[0] = COLOR
    time.sleep(DELAY)
    pixel[0] = CLEAR
    time.sleep(DELAY)

blinkPixel()

# create the trellis
trellis = NeoTrellis(i2c_bus)

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

# this will be called when button events are received
def blink(event):
    # turn the LED on when a rising edge is detected
    if event.edge == NeoTrellis.EDGE_RISING:
        trellis.pixels[event.number] = CYAN
    # turn the LED off when a falling edge is detected
    elif event.edge == NeoTrellis.EDGE_FALLING:
        trellis.pixels[event.number] = OFF

for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the blink callback
    trellis.callbacks[i] = blink

    # cycle the LEDs on startup
    trellis.pixels[i] = PURPLE
    time.sleep(0.05)

for i in range(16):
    trellis.pixels[i] = OFF
    time.sleep(0.05)

while True:
    # call the sync function call any triggered callbacks
    trellis.sync()
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)
    blinkPixel()
