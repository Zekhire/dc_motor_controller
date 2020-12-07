import json
import numpy as np
import time
import sys

from pi_controller import PI_Controller
from dc_motor_model_bs import DC_Motor
from reference_signal import Speed_Reference_Signal

import platform
if platform.system() != "Windows":
    import RPi.GPIO as GPIO
else:
    from RPi_substitution import GPIO
import atexit

sys.path.insert(1, './dc_motor_driver')
from emergency_script import emergency


def get_w_ref_sample(reference_signal, Ts_signal, t_max, time_start, time_stop):
    timespan = time_stop - time_start
    timespan_norm = timespan%t_max
    index = int(timespan_norm/Ts_signal)
    w_ref_sample = reference_signal[index]
    return w_ref_sample


def pi_controller(q_ta2pi, q_pi2ta, dc_motor_driver_data, **kwargs):
    # Input desired desired and actual speed to PI controller
    # and set PWM and DC supply to control DC motor
    if "show" in kwargs.keys() and kwargs["show"]:
        print("PI controller: Running")

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

    # Start PWM with 0% duty cycle
    p.start(0)

    # Prepare reference signal
    ref_signal = Speed_Reference_Signal()
    simulation_data = ref_signal.get_simulation_data()
    w_ref     = simulation_data["w_ref"]
    t_max     = simulation_data["t_max"]
    Ts_signal = simulation_data["dt"]

    # Create PI controller object
    pi_controller_data = dc_motor_driver_data["pi_controller"]
    pi_controller	   = PI_Controller(pi_controller_data)

    # Check if real DC motor is used
    simulation	  = dc_motor_driver_data["simulation"]
    dc_motor_data = dc_motor_driver_data["dc_motor_simulation"]
    dc_motor	  = DC_Motor(dc_motor_data)
    dc_motor_dt   = dc_motor_data["dt"]

    # Set emergency function at script exit
    atexit.register(emergency, p, in1, in2)

    # Get time of script start
    time_pi_controller_start = time.time()
    w_actual_sample_time_old = time_pi_controller_start

    # Send "enable" signal to tachometer in order to ensure that
    # time that will be received be PI controller will be later
    # than that that was measured line above
    q_pi2ta.put(1)

    if "show" in kwargs.keys() and kwargs["show"]:
        print("PI controller: Main loop start")

    received = 1
    sended = 1

    while True:
        # We can change this to get uniform time from one place
        # instead of letting every script have its own clock
        w_actual_sample      = q_ta2pi.get()       # Get actual DC motor speed
        w_actual_sample_time = q_ta2pi.get()       # Get time of sample measurement
        # w_actual_sample_time = time.time()

        if "debug" in kwargs.keys() and kwargs["debug"]:
            print("PI controller: Received", received, w_actual_sample, w_actual_sample_time)
            received += 1

        # Get sample of w_ref
        w_ref_sample = get_w_ref_sample(w_ref, Ts_signal, t_max, time_pi_controller_start, w_actual_sample_time)
        # print("w_ref_sample", w_ref_sample)

        # PI controller control
        dt = w_actual_sample_time - w_actual_sample_time_old      # Compute real delta time
        # dt = 0.01
        w_error = w_ref_sample - w_actual_sample                  # Get speed error
        u_dict = {"e": np.array([w_error])}
        y_dict_pi_controller = pi_controller.simulation_euler_anti_windup(dt, 1, u_dict)
        v_s = y_dict_pi_controller["y"][0]  # Control signal 
        
        if "debug" in kwargs.keys() and kwargs["debug"]:
            print("PI controller: w_ref", w_ref_sample, "w_act", w_actual_sample, "w_error", w_error)
        # print("PI controller dt", dt)

        # Check if there is real DC motor or simulation
        # and stimulate DC motor with new DC supply
        if simulation is False:
            # Change DC supply polarization
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
        else:
            # Perform simulation
            if dt <= dc_motor_dt:
                iterations = 1
                dc_motor_dt_actual = dt
            else:
                iterations = round(dt/dc_motor_dt)
                dc_motor_dt_actual = dc_motor_dt
            
            u_dict = {"v_s": v_s*np.ones(iterations), 
                      "T_l": 0*np.ones(iterations)}

            y_dict_dc_motor = dc_motor.simulation_euler(dc_motor_dt_actual, iterations, u_dict)
            w_m = y_dict_dc_motor["w_m"][-1]
            # print("iterations:", iterations, w_m, dc_motor_dt_actual, v_s, w_error)
            # print("w_ref_sample:", w_ref_sample)
            q_pi2ta.put(w_m)
            if "debug" in kwargs.keys() and kwargs["debug"]:
                print("PI controller: Sended to Tachometer", sended)
                sended += 1
        # Update time
        w_actual_sample_time_old = w_actual_sample_time


if __name__ == "__main__":
    dc_motor_driver_data_path = ".\dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))
    
    pi_controller(queue_substitution.Queue(), 
                    queue_substitution.Queue(), 
                    dc_motor_driver_data, show=True, debug=True)
