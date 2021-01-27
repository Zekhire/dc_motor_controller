import json

import sys
sys.path.insert(1, './offline_substitution_modules')
sys.path.insert(1, '../offline_substitution_modules')

import platform
if platform.system() != "Windows":
    import RPi.GPIO as GPIO
else:
    from RPi_substitution import GPIO


def emergency(p, in1, in2):
    p.ChangeDutyCycle(0)		
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    print("DC motor is disabled")


if __name__ == "__main__":
    # Load hardware specs
    dc_motor_driver_data_path = "dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))

    # Unpack hardware specs
    rpi_dc_motor_controller_data = dc_motor_driver_data["rpi_dc_motor_controller"]
    in1      = rpi_dc_motor_controller_data["in1"]
    in2      = rpi_dc_motor_controller_data["in2"]
    en       = rpi_dc_motor_controller_data["en"]
    pwm_freq = rpi_dc_motor_controller_data["pwm_freq"]

    # Prepare GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in1, GPIO.OUT)           # Run forward
    GPIO.setup(in2, GPIO.OUT)           # Run backward
    GPIO.setup(en,  GPIO.OUT)           # PWM pin
    p = GPIO.PWM(en, pwm_freq)
    p.start(0)

    # Disable DC motor!
    emergency(p, in1, in2)
