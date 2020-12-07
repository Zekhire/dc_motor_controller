from multiprocessing import Process, Queue
import time
import socket
import struct
from threading import Thread
import numpy as np
import json

from monitor.server import server
from monitor.visualization import controll_visualization


if __name__ == "__main__":
    q_s2cm = Queue()
    monitor_data_path = ".\\monitor\\monitor.json"
    monitor_data = json.load(open(monitor_data_path))

    process_server       = Thread(target=server,        
                                    args=(q_s2cm, monitor_data, ), 
                                    kwargs={"show":True, "debug":False})

    process_visualization = Thread(target=controll_visualization,  
                                    args=(q_s2cm, monitor_data, ), 
                                    kwargs={"show":True, "debug":True})

    process_server.start()
    process_visualization.start()

    # process_server.join()
    # process_visualization.join()