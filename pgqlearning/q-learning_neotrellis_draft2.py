import time
import board
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis
from digitalio import DigitalInOut, Direction, Pull

from btn_demo import BtnDemo
from rain_demo import RainDemo
from TrellisBattleships import Battleships

import digitalio
from board import SCL, SDA

##bootBtn = DigitalInOut(microcontroller.pin.GPIO23)
##bootBtn.direction = Direction.INPUT

# Create the I2C object for the NeoTrellis
i2c_bus = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Create the NeoTrellis object
# This is for a 2x2 array of NeoTrellis boards:
trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E), NeoTrellis(i2c_bus, False, addr=0x2F)],
    [NeoTrellis(i2c_bus, False, addr=0x30), NeoTrellis(i2c_bus, False, addr=0x31)],
]

dimY = 8
dimX = 8

trellis = MultiTrellis(trelli)

#neotrellis some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 100, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (127, 127, 127)

# connect a button to the NeoTrellis board
button_pin = board.D6
button = digitalio.DigitalInOut(button_pin)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

global button_colors

# Initialize color state for each button
#button_colors = [[OFF for y in range(8)] for x in range(8)]

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

# Track long single button presses to use to over-ride game classes
lastBtnPressed = [-1,-1]
lastPressTime = 0
longPressInterval = 1000000000

# Track time since last hardware sync, so we give at a least 17ms pause between sync requests
lastSyncTime = 0

# Set the brightness value (0 to 1.0)
trellis.brightness = 0.1


leds = [[255,255,255],[0,0,0],[0,0,0],[0,0,0],
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
            setColour( x, y, colour )


def longPress(x,y):
    global activeGame
    
    print(f"Button long press at {x},{y} (was colour: {getColour(x,y)})")
    if y == 0:
        if x == 6:
            trellis.brightness = 0.1
        elif x == 7:
            trellis.brightness = 0.2
        elif x == 8:
            trellis.brightness = 0.4
        elif x == 9:
            trellis.brightness = 0.6
        elif x == 10:
            trellis.brightness = 0.8
        elif x == 11:
            trellis.brightness = 1.0
        else:
            # Pass unhandled long press events to active game
            activeGame.longPressEvent(x,y)
    elif y == 11:
        if x == 0:
            gridReset((50,0,50))
            activeGame = BtnDemo(host)
        elif x == 1:
            # gridReset((10,10,10))
            activeGame = Battleships(host)
        elif x == 11:
            gridReset((0,0,0))
            activeGame = RainDemo(host)
        else:
            # Pass unhandled long press events to active game
            activeGame.longPressEvent(x,y)
    else:
        # Pass unhandled long press events to active game
        activeGame.longPressEvent(x,y)

    # Restore button colour
    host.restoreColour(x,y)


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
        
        
for y in range(dimY):
    for x in range(dimX):
        # Activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # Activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, btnHandler)
        trellis.color( x, y, (100, 0, 255) )

host = Host(getColour,setColour)

activeGame = Battleships(host)

"""
trellis.color(0, 0, WHITE)
trellis.color(1, 1, WHITE)
trellis.color(2, 2, WHITE)
trellis.color(3, 3, WHITE)
trellis.color(4, 4, WHITE)
trellis.color(5, 5, WHITE)
trellis.color(6, 6, WHITE)
trellis.color(7, 7, WHITE)


trellis.color(0, 0, OFF)
trellis.color(1, 1, OFF)
trellis.color(2, 2, OFF)
trellis.color(3, 3, OFF)
trellis.color(4, 4, OFF)
trellis.color(5, 5, OFF)
trellis.color(6, 6, OFF)
trellis.color(7, 7, OFF)
"""

while True:
    timenow = time.monotonic_ns()
    if timenow - lastSyncTime > 18000:
        lastSyncTime = timenow
        # The NeoTrellis can only be read every 17 milliseconds or so
        trellis.sync()
        activeGame.animate()

        if (lastBtnPressed[0] >= 0) and ((time.monotonic_ns() - lastPressTime) > longPressInterval):
            #Long press will be activated when key is lifted, so indicate with colour change
            longPressColour = RED
            #Use a different colour to the one this button is currently showing
            colourNow = getColour(lastBtnPressed[0], lastBtnPressed[1])
            if colourNow == RED:
                longPressColour = ORANGE
            #print(f"Long press activated for position {lastBtnPressed[0]},{lastBtnPressed[1]}")
            setColour(lastBtnPressed[0], lastBtnPressed[1], longPressColour, False )

        ##if bootBtn.value == False:
            ##print("Boot button pressed.")
        
    time.sleep(0.002)
