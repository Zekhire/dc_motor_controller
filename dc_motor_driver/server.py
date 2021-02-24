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


def send(connection, q_ss2cli, **kwargs):
    # Set helping variables
    safe_string_length = 64
    sended = 1

    # Communication loop
    while True:
        try:
            # Get data from AD converter
            data_sample      = q_ss2cli.get()
            data_sample_ref  = q_ss2cli.get()
            data_sample_time = q_ss2cli.get()

            data = [data_sample, data_sample_ref, data_sample_time]

            # Convert data to bytes and send to server
            data_frame = convert_to_bytes(data, safe_string_length)
            # print(data_frame, end="")
            # Send data to server
            connection.sendall(data_frame)
            if "debug" in kwargs.keys() and kwargs["debug"]:

                print("Server: Sended", sended, data_frame)
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
                
                try:
                    data0 = float(data_split[0])    # w rample
                except ValueError:
                    continue

                q_s2cm.put(data0)

                if "debug" in kwargs.keys() and kwargs["debug"]:
                    print("Server: Received", received, data0)
                    received += 1

        except socket.error:
            connection.close()
            break


def server(q_ss2cli, q_cli2ss, dc_motor_driver_data, **kwargs):
    if "show" in kwargs.keys() and kwargs["show"]:
        print("Server: Running")

    # Get connection data
    server_data = dc_motor_driver_data["server"]
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

    if "key" in kwargs.keys() and kwargs["key"]:
        kwargs["key"].put(0)

    send_thread    = threading.Thread(target=send,    args=(connection, q_ss2cli,), kwargs=kwargs)
    receive_thread = threading.Thread(target=receive, args=(connection, q_cli2ss,), kwargs=kwargs)
    send_thread.start()
    receive_thread.start()
