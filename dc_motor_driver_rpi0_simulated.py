from multiprocessing import Process, Queue
import time
import socket
import struct
from threading import Thread
import numpy as np
import json

from dc_motor_driver.dc_motor_driver_simulated import dc_motor_driver_simulated
from dc_motor_driver.client import client


if __name__ == "__main__":
    dc_motor_driver_data_path = "./dc_motor_driver/dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))

    debug = False

    q_ss2cli = Queue()
    q_cli2ss = Queue()

    process_simulated_system = Thread(target=dc_motor_driver_simulated, 
                                    args=(q_ss2cli, q_cli2ss, dc_motor_driver_data, False),
                                    kwargs={"show":True, "debug":debug})
    process_client           = Thread(target=client,
                                    args=(q_ss2cli, q_cli2ss, dc_motor_driver_data), 
                                    kwargs={"show":True, "debug":debug})

    process_simulated_system.start()
    process_client.start()

    # process_simulated_system.join()
    # process_client.join()