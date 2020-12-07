import socket
import threading
import struct
import json

import sys
sys.path.insert(1, './offline_substitution_modules')


def server(q_s2cm, monitor_data, **kwargs):
    if "show" in kwargs.keys() and kwargs["show"]:
        print("Server: Running")

    # Get connection data
    server_data = monitor_data["server"]
    server_ip   = server_data["server_ip"]
    server_port = server_data["server_port"]

    # Initial connection data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (server_ip, server_port)                       # IP and port of server

    # Connect
    sock.bind(server_address)                                       # bind socket with IP and port
    sock.listen(1)                                                  # set listening on chosen IP and port

    if "show" in kwargs.keys() and kwargs["show"]:
        print('Server: Waiting for connection')
    
    connection, client_address = sock.accept()                      # wait for connection with client

    if "show" in kwargs.keys() and kwargs["show"]:
        print('Server: Connected with IP', client_address[0])

    received = 1

    # Communication loop
    while True:
        try:
            data_frame = connection.recv(64)                               # receive data (2 floats)
            if data_frame:
                data = data_frame.decode("utf-8")
                data_split = data.split()
                
                # if "debug" in kwargs.keys() and kwargs["debug"]:
                #     print(data_split)

                # Unpack data
                data0 = float(data_split[0])    # w rample
                data1 = float(data_split[1])    # w_ref sample
                data2 = float(data_split[2])    # measurement time

                # Send data forward
                data_tuple = (data0, data1, data2)
                q_s2cm.put(data_tuple)

                if "debug" in kwargs.keys() and kwargs["debug"]:
                    print("Server: Received", received)
                    received += 1

        except socket.error:
            connection.close()
            break
