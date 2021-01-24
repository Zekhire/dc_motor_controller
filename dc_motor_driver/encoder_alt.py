import RPi.GPIO as GPIO
import time
from time import sleep

counter = 0


def rotation_decode_A(in_A):
    global counter
    Switch_B = GPIO.input(in_B)
    counter += Switch_B
    
    
def rotation_decode_B(in_B):
    global counter
    Switch_A = GPIO.input(in_A)
    counter -= Switch_A


# GPIO Ports
in_A = 20  # Encoder input A: input GPIO 23 (active high)
in_B = 21  # Encoder input B: input GPIO 24 (active high)

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
GPIO.setup(in_A, GPIO.IN)
GPIO.setup(in_B, GPIO.IN)
# setup an event detection thread for the A encoder switch
GPIO.add_event_detect(in_A, GPIO.RISING, callback=rotation_decode_A)
GPIO.add_event_detect(in_B, GPIO.RISING, callback=rotation_decode_B)

def encoder():
    global counter
    interval = 0.01
    time_start = time.time()
    i = 0
    while(True):
        sleep(0.1)
        i+=1
        #print(counter)
        #continue
    
        #time_stop = time.time()

        #dt = time_stop - time_start
        #if dt >= interval:
        print(counter)
            #time_start = time_stop
        continue

        if counter%300 == 0:
            print(counter, ":D")
        continue
        print(counter)
        continue
        if i%1000 == 0:
            i=0
            print(counter)
        i+=1
        continue



if __name__ == "__main__":
    encoder()
