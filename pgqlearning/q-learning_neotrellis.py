"""
modified q-leanring_sensehat.py
removed all unnecessary libraries
removed graphics displayed on screen
"""

##import numpy as np
from ulab import numpy as np

#from PIL import Image
#import cv2
#import matplotlib.pyplot as plt
##import pickle
import ujson as json
##from matplotlib import style
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

##red = (255, 0, 0)
##green = (0, 128, 0)
##blue = (0, 0, 255)
##clear = (0, 0, 0)

style.use("ggplot")

SIZE = 8

##HM_EPISODES = 25000
HM_EPISODES = 3000
MOVE_PENALTY = 1
ENEMY_PENALTY = 300
FOOD_REWARD = 25
##epsilon = 0.9
epsilon = 0
EPS_DECAY = 0.9998  # Every episode will be epsilon*EPS_DECAY
##SHOW_EVERY = 3000  # how often to play through env visually.
SHOW_EVERY = 300  # how often to play through env visually.

start_q_table = None # None or Filename

LEARNING_RATE = 0.1
DISCOUNT = 0.95

PLAYER_N = 1  # player key in dict
FOOD_N = 2  # food key in dict
ENEMY_N = 3  # enemy key in dict

# the dict!
d = {1: (255, 175, 0),
     2: (0, 255, 0),
     3: (0, 0, 255)}


class Blob:
    def __init__(self):
        self.x = np.random.randint(0, SIZE)
        self.y = np.random.randint(0, SIZE)

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __sub__(self, other):
        return (self.x-other.x, self.y-other.y)

    def action(self, choice):
        '''
        Gives us 4 total movement options. (0,1,2,3)
        '''
        if choice == 0:
            self.move(x=1, y=1)
        elif choice == 1:
            self.move(x=-1, y=-1)
        elif choice == 2:
            self.move(x=-1, y=1)
        elif choice == 3:
            self.move(x=1, y=-1)

    def move(self, x=False, y=False):

        # If no value for x, move randomly
        if not x:
            self.x += np.random.randint(-1, 2)
        else:
            self.x += x

        # If no value for y, move randomly
        if not y:
            self.y += np.random.randint(-1, 2)
        else:
            self.y += y


        # If we are out of bounds, fix!
        if self.x < 0:
            self.x = 0
        elif self.x > SIZE-1:
            self.x = SIZE-1
        if self.y < 0:
            self.y = 0
        elif self.y > SIZE-1:
            self.y = SIZE-1

if start_q_table is None:
    # initialize the q-table#
    q_table = {}
    for i in range(-SIZE+1, SIZE):
        for ii in range(-SIZE+1, SIZE):
            for iii in range(-SIZE+1, SIZE):
                    for iiii in range(-SIZE+1, SIZE):
                        q_table[((i, ii), (iii, iiii))] = [np.random.uniform(-5, 0) for i in range(4)]

else:
    with open(start_q_table, "rb") as f:
        q_table = ujson.load(f)

# can look up from Q-table with: print(q_table[((-9, -2), (3, 9))]) for example

episode_rewards = []

for episode in range(HM_EPISODES):
    player = Blob()
    food = Blob()
    enemy = Blob()
    if episode % SHOW_EVERY == 0:
        print(f"on #{episode}, epsilon is {epsilon}")
        print(f"{SHOW_EVERY} ep mean: {np.mean(episode_rewards[-SHOW_EVERY:])}")
        show = True
    else:
        show = False

    episode_reward = 0
    for i in range(200):
        obs = (player-food, player-enemy)
        #print(obs)
        if np.random.random() > epsilon:
            # GET THE ACTION
            action = np.argmax(q_table[obs])
        else:
            action = np.random.randint(0, 4)
        # Take the action!
        player.action(action)

        #### MAYBE ###
        enemy.move()
        food.move()
        ##############

        if player.x == enemy.x and player.y == enemy.y:
            reward = -ENEMY_PENALTY
        elif player.x == food.x and player.y == food.y:
            reward = FOOD_REWARD
        else:
            reward = -MOVE_PENALTY
        ## NOW WE KNOW THE REWARD, LET'S CALC YO
        # first we need to obs immediately after the move.
        new_obs = (player-food, player-enemy)
        max_future_q = np.max(q_table[new_obs])
        current_q = q_table[obs][action]

        if reward == FOOD_REWARD:
            new_q = FOOD_REWARD
        else:
            new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
        q_table[obs][action] = new_q

        if show:
            ##env = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)  # starts an rbg of our size
            ##sensehat: clear
            ##pixels = [clear] * 64
            button_colors = [[OFF for y in range(8)] for x in range(8)] 
            trellis.brightness = 0.1

            ##env[food.x][food.y] = d[FOOD_N]  # sets the food location tile to green color
            ##sensehat: food is green
            foodPos = [food.y, food.x]
            ##pixels[foodPos[1] * 8 + foodPos[0]] = green
            ##trellis.color[food.y, food.x, GREEN]
            button_colors[food.x][food.y] = GREEN 


            ##env[player.x][player.y] = d[PLAYER_N]  # sets the player tile to blue
            ##sensehat: player is blue
            playerPos = [player.y, player.x]
            ##pixels[playerPos[1] * 8 + playerPos[0]] = blue
            button_color[food.x][food.y] = BLUE

            ##env[enemy.x][enemy.y] = d[ENEMY_N]  # sets the enemy location to red
            ##sensehat: player is red
            enemyPos = [enemy.y, enemy.x]
            pixels[enemyPos[1] * 8 + enemyPos[0]] = red
            button_color[food.x][food.y] = RED

            ##sense.set_pixels(pixels)

            trellis.sync()
            time.sleep(0.02)

            ##img = Image.fromarray(env, 'RGB')  # reading to rgb. Apparently. Even tho color definitions are bgr. ???

            ##img = img.resize((300, 300), resample=Image.BOX)  # resizing so we can see our agent in all its glory.
            ##cv2.imshow("image", np.array(img))  # show it!

            ##if reward == FOOD_REWARD or reward == -ENEMY_PENALTY:  # crummy code to hang at the end if we reach abrupt end for good reasons or not.
            ##    if cv2.waitKey(500) & 0xFF == ord('q'):
            ##        break
            ##else:
            ##    if cv2.waitKey(1) & 0xFF == ord('q'):
            ##        break

        episode_reward += reward
        if reward == FOOD_REWARD or reward == -ENEMY_PENALTY:
            break

    #print(episode_reward)
    episode_rewards.append(episode_reward)
    epsilon *= EPS_DECAY

moving_avg = np.convolve(episode_rewards, np.ones((SHOW_EVERY,))/SHOW_EVERY, mode='valid')

plt.plot([i for i in range(len(moving_avg))], moving_avg)
plt.ylabel(f"Reward {SHOW_EVERY}ma")
plt.xlabel("episode #")
plt.show()


with open(f"qtable-{int(time.time())}.json", "wb") as f:
    ujson.dump(q_table, f)


sense.clear(0, 0, 0)
