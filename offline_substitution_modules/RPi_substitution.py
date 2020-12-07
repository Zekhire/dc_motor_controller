import numpy as np


class Pwm:
    def __init__(self):
        pass

    def start(self, a):
        pass

    def ChangeDutyCycle(self, a):
        pass


class Gpio:
    def __init__(self):
        self.BCM = 0
        self.IN = 1
        self.OUT = 0
        self.LOW = 0
        self.HIGH = 1

    def setmode(self, a):
        pass

    def setup(self, a, b):
        pass

    def PWM(self, a, b):
        return Pwm()

    def output(self, a, b):
        pass

    def input(self, a):
        return np.random.randint(2)


GPIO = Gpio()