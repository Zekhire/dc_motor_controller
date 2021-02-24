from multiprocessing import Process, Queue
import time
import socket
import struct
from threading import Thread
import numpy as np
import json

from dc_motor_driver.dc_motor_driver_simulated import dc_motor_driver_simulated
from dc_motor_driver.server import server


if __name__ == "__main__":
    dc_motor_driver_data_path = "./dc_motor_driver/dc_motor_driver.json"
    dc_motor_driver_data = json.load(open(dc_motor_driver_data_path))

    debug = False

    q_dc2s = Queue()
    q_s2dc = Queue()
    key    = Queue()

    process_server = Thread(target=server,
                            args=(q_s2dc, q_dc2s, dc_motor_driver_data), 
                            kwargs={"show":True, "debug":debug, "key":key})

    process_server.start()
    key.get()

    process_simulated_system = Thread(target=dc_motor_driver_simulated, 
                                    args=(q_s2dc, q_dc2s, dc_motor_driver_data, False),
                                    kwargs={"show":True, "debug":False})


    process_simulated_system.start()
    # process_server.start()

    # process_simulated_system.join()
    # process_server.join()
