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

    debug = True

    q_dc2s = Queue()
    q_s2dc = Queue()
    key    = Queue()

    process_server = Thread(target=server,
                            args=(q_s2dc, q_dc2s, dc_motor_driver_data), 
                            kwargs={"show":True, "debug":debug, "key":key})

    key.get()

    process_simulated_system = Thread(target=dc_motor_driver, 
                                    args=(q_s2dc, q_dc2s, dc_motor_driver_data, False),
                                    kwargs={"show":True, "debug":debug})


    process_simulated_system.start()
    process_server.start()

    # process_simulated_system.join()
    # process_server.join()
