import json
import numpy as np
import time
import sys
sys.path.insert(1, './models')
sys.path.insert(1, '../models')
from pi_controller import PI_Controller
from dc_motor_model_bs import DC_Motor

import sys
sys.path.insert(1, './offline_substitution_modules')
sys.path.insert(1, '../offline_substitution_modules')

import platform
if platform.system() != "Windows":
    import RPi.GPIO as GPIO
else:
    from RPi_substitution import GPIO
import atexit

sys.path.insert(1, './dc_motor_driver')
from emergency_script import emergency
import queue

# global variables (ultimately veeeeeeeery veeery ugly :<)
counter_old = 0
counter = 0

# GPIO Ports
in_A = 20  # Encoder input A: input GPIO 23 (active high)
in_B = 21  # Encoder input B: input GPIO 24 (active high)

# Clockwise         +
# Counter clockwise -


def rotation_decode_A(in_A):
    global counter
    Switch_B = GPIO.input(in_B)
    counter += Switch_B
    

def rotation_decode_B(in_B):
    global counter
    Switch_A = GPIO.input(in_A)
    counter -= Switch_A


def dc_motor_driver(q_ss2cli, q_cli2ss, dc_motor_driver_data, rapidly=False, **kwargs):
    global counter
    global counter_old
    # Input desired desired and actual speed to PI controller
    # and set PWM and DC supply to control DC motor
    if "show" in kwargs.keys() and kwargs["show"]:
        print("PI controller: Running")

    # Create PI controller object
    pi_controller_data = dc_motor_driver_data["pi_controller"]
    pi_controller	   = PI_Controller(pi_controller_data)

    # Get "sampling period"
    tachometer_data = dc_motor_driver_data["tachometer"]
    Td = tachometer_data["Td"]

    # Hardware spec
    rpi_dc_motor_controller_data = dc_motor_driver_data["rpi_dc_motor_controller"]
    in1      = rpi_dc_motor_controller_data["in1"]
    in2      = rpi_dc_motor_controller_data["in2"]
    en       = rpi_dc_motor_controller_data["en"]
    pwm_freq = rpi_dc_motor_controller_data["pwm_freq"]
    v        = rpi_dc_motor_controller_data["v"]

    # Prepare GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in1, GPIO.OUT)   # Run forward
    GPIO.setup(in2, GPIO.OUT)   # Run backward
    GPIO.setup(en,  GPIO.OUT)   # PWM pin
    p = GPIO.PWM(en, pwm_freq)
    p.start(0)

    # Encoder
    encoder_data = dc_motor_driver_data["encoder"]
    ipr = encoder_data["ipr"]
    GPIO.setup(in_A, GPIO.IN)
    GPIO.setup(in_B, GPIO.IN)

    # setup an event detection threads for the A and B encoder switches
    GPIO.add_event_detect(in_A, GPIO.RISING, callback=rotation_decode_A)
    GPIO.add_event_detect(in_B, GPIO.RISING, callback=rotation_decode_B)

    # Set emergency function at script exit
    atexit.register(emergency, p, in1, in2)

    # Initial w ref value
    w_ref_sample = 0
    w_actual_sample = 0

    # Get time of script start
    w_actual_sample_time_old = time.time()
    time.sleep(Td)

    if "show" in kwargs.keys() and kwargs["show"]:
        print("PI controller: Main loop start")

    while True:
        # We can change this to get uniform time from one place
        # instead of letting every script have its own clock

        w_actual_sample_time = time.time()
        dt = w_actual_sample_time - w_actual_sample_time_old    # Compute real delta time

        # Get sample of w_ref
        try:
            w_ref_sample_new = q_cli2ss.get(timeout=0)
        except queue.Empty:
            w_ref_sample_new = w_ref_sample

        w_ref_sample = w_ref_sample_new

        # Get sample of w_actual
        theta_m_actual = counter    *2*np.pi/ipr
        theta_m_old    = counter_old*2*np.pi/ipr

        w_actual_sample = (theta_m_actual - theta_m_old)/dt
        counter_old = counter

        # PI controller control
        w_error = w_ref_sample - w_actual_sample                  # Get speed error
        u_dict = {"e": np.array([w_error])}
        y_dict_pi_controller = pi_controller.simulation_euler_anti_windup(dt, 1, u_dict)
        v_s = y_dict_pi_controller["y"][0]  # Control signal 
        #print(v_s)

        # Set DC motor direction
        if v_s >= 0:
            GPIO.output(in1, GPIO.HIGH)     # Run forward
            GPIO.output(in2, GPIO.LOW)
        elif v_s < 0:
            GPIO.output(in1, GPIO.LOW)      # Run backward
            GPIO.output(in2, GPIO.HIGH)
        else:
            GPIO.output(in1, GPIO.LOW)      # Stop
            GPIO.output(in2, GPIO.LOW)

        # Compute duty cycle
        dc = int(abs(v_s)*100/v)

        # Change PWM duty cycle
        p.ChangeDutyCycle(dc)

        # Send simulation data to client
        q_ss2cli.put(w_actual_sample)
        q_ss2cli.put(w_ref_sample)
        q_ss2cli.put(w_actual_sample_time)

        # Update time
        w_actual_sample_time_old = w_actual_sample_time

        # Wait for specified time (veeery ugly :<)
        time.sleep(Td)




if __name__ == "__main__":
    dc_motor_driver_data_path = "dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))
    
    dc_motor_driver(queue.Queue(), queue.Queue(),
                    dc_motor_driver_data, show=True, debug=True)
