import socket
import threading
import struct
import json

import sys
sys.path.insert(1, './offline_substitution_modules')


def convert_to_bytes(data, safe_string_length):
    data_frame = ""
    for d in data:
        data_frame += str(d)+" "

    padding_length = safe_string_length-len(data_frame)
    data_frame += '\0'*padding_length
    data_frame = data_frame.encode('utf-8')
    return data_frame


def send(connection, **kwargs):
    sended = 1
    # Communication loop
    while True:
        try:
            print("Prompt desired DC motor speed ([rad/s]):")
            data = input()
            print()

            # Convert data to bytes and send to client
            data_frame = convert_to_bytes([data], 64)

            # Send data to client
            connection.sendall(data_frame)

            if "debug" in kwargs.keys() and kwargs["debug"]:
                print("Server: Sended", sended)
                sended += 1

        except socket.error:                                            # end if socket error
            print('Server: Disconnected with Client!')
            exit()
            break


def receive(connection, q_s2cm, **kwargs):
    received = 1
    # Communication loop
    while True:
        try:
            data_frame = connection.recv(64)                               # receive data (2 floats)
            if data_frame:
                data = data_frame.decode("utf-8")
                data_split = data.split()
                
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

    send_thread    = threading.Thread(target=send, args=(connection,))
    receive_thread = threading.Thread(target=receive, args=(connection,q_s2cm,))
    send_thread.start()
    receive_thread.start()