from multiprocessing import Process, Queue
import time
import socket
import struct
from threading import Thread
import numpy as np
import json

from monitor.client import client
from monitor.visualization import controll_visualization


if __name__ == "__main__":
    monitor_data_path = ".\\monitor\\monitor.json"
    monitor_data = json.load(open(monitor_data_path))

    q_s2cm = Queue()

    process_client       = Thread(target=client,        
                                    args=(q_s2cm, monitor_data, ), 
                                    kwargs={"show":True, "debug":True})

    process_visualization = Thread(target=controll_visualization,  
                                    args=(q_s2cm, monitor_data, ), 
                                    kwargs={"show":True, "debug":True})

    process_client.start()
    process_visualization.start()

    # process_client.join()
    # process_visualization.join()

