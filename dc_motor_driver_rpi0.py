from multiprocessing import Process, Queue
import time
import socket
import struct
from threading import Thread
import numpy as np
import json

from dc_motor_driver.dc_motor_driver import dc_motor_driver
from dc_motor_driver.server import server


if __name__ == "__main__":
    dc_motor_driver_data_path = "./dc_motor_driver/dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))

    debug = False

    q_ss2cli = Queue()
    q_cli2ss = Queue()

    process_simulated_system = Thread(target=dc_motor_driver, 
                                    args=(q_ss2cli, q_cli2ss, dc_motor_driver_data, False),
                                    kwargs={"show":True, "debug":debug})
                                    
    process_server           = Thread(target=server,
                                    args=(q_ss2cli, q_cli2ss, dc_motor_driver_data), 
                                    kwargs={"show":True, "debug":debug})

    process_simulated_system.start()
    process_server.start()

    # process_simulated_system.join()
    # process_server.join()
