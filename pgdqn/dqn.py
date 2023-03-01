from keras.model import Sequential
from keras.model import Dense, Dropout, Conv2d, MaxPooling2D, Activation, Flatten
from keras.callbacks import TensorBoard

class DQNAgent:
    def create_model(self):
        model = Sequential()
