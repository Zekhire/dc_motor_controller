# Python Script
# https://www.electronicshub.org/raspberry-pi-l298n-interface-tutorial-control-dc-motor-l298n-raspberry-pi/

import RPi.GPIO as GPIO          
from time import sleep
import time
import atexit
from emergency_script import emergency
import numpy as np

counter = 0
counter_old = 0
ipr = 300

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


in1 = 4
in2 = 3
en = 2
temp1=1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.HIGH)
GPIO.output(in2,GPIO.LOW)

p=GPIO.PWM(en,1000)

p.start(20)


# Set emergency function at script exit
atexit.register(emergency, p, in1, in2)

print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run s-stop f-forward b-backward l-low m-medium h-high e-exit")
print("\n")    

x = "f"

speed = 0
time_start = time.time()


while(1):
    print(counter, speed)
    sleep(0.04)

    time_stop = time.time()
    dt = time_stop-time_start
    speed = (counter*2*np.pi/ipr - counter_old*2*np.pi/ipr)/dt

    counter_old = counter
    time_start = time_stop

    #x=input()
    
    if x=='r':
        print("run")
        if(temp1==1):
            GPIO.output(in1,GPIO.HIGH)
            GPIO.output(in2,GPIO.LOW)
            print("forward")
            x='z'
        else:
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.HIGH)
            print("backward")
            x='z'


    elif x=='s':
        print("stop")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        x='z'

    elif x=='f':
        print("forward")
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        temp1=1
        x='f'

    elif x=='b':
        print("backward")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        temp1=0
        x='z'

    elif x=='l':
        print("low")
        p.ChangeDutyCycle(25)
        x='z'

    elif x=='m':
        print("medium")
        p.ChangeDutyCycle(50)
        x='z'

    elif x=='h':
        print("high")
        p.ChangeDutyCycle(75)
        x='z'
     
    
    elif x=='e':
        p.ChangeDutyCycle(0)		
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        # GPIO.cleanup()
        print("GPIO Clean up")
        break
    
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")
