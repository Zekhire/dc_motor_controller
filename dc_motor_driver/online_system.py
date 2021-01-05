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


in_A = 23
in_B = 24
counter = 0


def encoder_A():
    switch_B = GPIO.input(in_B)
    counter += switch_B


def encoder_B():
    switch_A = GPIO.input(in_A)
    counter -= switch_A


def get_w_ref_sample(reference_signal, Ts_signal, t_max, time_start, time_stop):
    timespan = time_stop - time_start
    timespan_norm = timespan%t_max
    index = int(timespan_norm/Ts_signal)
    w_ref_sample = reference_signal[index]
    return w_ref_sample


def simulated_system(q_ss2cli, q_cli2ss, dc_motor_driver_data, rapidly=False, **kwargs):
    # Input desired desired and actual speed to PI controller
    # and set PWM and DC supply to control DC motor
    if "show" in kwargs.keys() and kwargs["show"]:
        print("PI controller: Running")

    # Create PI controller object
    pi_controller_data = dc_motor_driver_data["pi_controller"]
    pi_controller	   = PI_Controller(pi_controller_data)

    # Create DC motor model
    dc_motor_data = dc_motor_driver_data["dc_motor_simulation"]
    dc_motor	  = DC_Motor(dc_motor_data)
    dc_motor_dt   = dc_motor_data["dt"]
    
    # Get "sampling period"
    ad_converter_data = dc_motor_driver_data["ad_converter"]
    Ts = ad_converter_data["Ts"]

    # Initial w ref value
    w_ref_sample = 0

    # Get time of script start
    time_pi_controller_start = time.time()
    w_actual_sample_time_old = time_pi_controller_start


    # in_A = 23  					# Encoder input A: input GPIO 23 (active high)
    # in_B = 24  					# Encoder input B: input GPIO 24 (active high)
    GPIO.setup(in_A, GPIO.IN)
    GPIO.setup(in_B, GPIO.IN)
    GPIO.add_event_detect(in_A, GPIO.RISING, callback=encoder_A, bouncetime=2) # bouncetime in mSec
    GPIO.add_event_detect(in_B, GPIO.RISING, callback=encoder_B, bouncetime=2) # bouncetime in mSec

    if "show" in kwargs.keys() and kwargs["show"]:
        print("PI controller: Main loop start")

    w_actual_sample = 0
    sended = 1

    while True:
        # We can change this to get uniform time from one place
        # instead of letting every script have its own clock

        if rapidly:                                                 # When user want to get reasonable data ASAP
            dt = Ts                                                 # Set dt as ideal sampling period
            w_actual_sample_time = w_actual_sample_time_old + dt    # Update time by ideal dt
        else:
            w_actual_sample_time = time.time()
            dt = w_actual_sample_time - w_actual_sample_time_old    # Compute real delta time

        if dt < Ts and rapidly == False:                    # disable this if user want to get reasonable data ASAP
            continue

        # Get sample of w_ref


        try:
            w_ref_sample_new = q_cli2ss.get(timeout=0)
        except queue.Empty:
            w_ref_sample_new = w_ref_sample

        w_ref_sample = w_ref_sample_new

        # PI controller control
        w_error = w_ref_sample - w_actual_sample                  # Get speed error
        u_dict = {"e": np.array([w_error])}
        y_dict_pi_controller = pi_controller.simulation_euler_anti_windup(dt, 1, u_dict)
        v_s = y_dict_pi_controller["y"][0]  # Control signal 
        
        if "debug" in kwargs.keys() and kwargs["debug"]:
            print("PI controller: w_ref", w_ref_sample, "w_act", w_actual_sample, "w_error", w_error)

        # Compute simulation data
        #if dt <= dc_motor_dt:
        #    iterations = 1
        #    dc_motor_dt_actual = dt
        #else:
            # simulated motor need small value of dt, so when dt is bigger than required
            # then there is need to perform several small steps of simulation instead of
            # one big 
        #    iterations = round(dt/dc_motor_dt)
        #    dc_motor_dt_actual = dc_motor_dt
        
        # Create input vectors
        #u_dict = {"v_s": v_s*np.ones(iterations), 
        #          "T_l": 0*np.ones(iterations)}

        # Perform simulation
        # y_dict_dc_motor = dc_motor.simulation_euler(dc_motor_dt_actual, iterations, u_dict)
        # w_m = y_dict_dc_motor["w_m"][-1]

        if v_s > 0:
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
        q_ss2cli.put(w_m)
        q_ss2cli.put(w_ref_sample)
        q_ss2cli.put(w_actual_sample_time)

        if "debug" in kwargs.keys() and kwargs["debug"]:
            print("PI controller: Sended to Tachometer", sended)
            sended += 1

        # Update time
        w_actual_sample = w_m
        w_actual_sample_time_old = w_actual_sample_time


if __name__ == "__main__":
    dc_motor_driver_data_path = ".\dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))
    
    simulated_system(queue_substitution.Queue(),
                     dc_motor_driver_data, show=True, debug=True)
