import json
import socket
import struct
import threading
import sys


def convert_to_bytes(data, safe_string_length):
    data_frame = ""
    for d in data:
        data_frame += str(d)+" "

    padding_length = safe_string_length-len(data_frame)
    data_frame += '\0'*padding_length
    data_frame = data_frame.encode('utf-8')
    return data_frame


def receive(sock, q_cli2ss, **kwargs):
    received = 1
    # Communication loop
    while True:
        try:
            data_frame = sock.recv(64)                               # receive data (2 floats)
            if data_frame:
                data = data_frame.decode("utf-8")
                data_split = data.split()
                
                try:
                    data0 = float(data_split[0])    # w rample
                except ValueError:
                    continue

                q_cli2ss.put(data0)

                if "debug" in kwargs.keys() and kwargs["debug"]:
                    print("Client: Received", received, data0)
                    received += 1

        except socket.error:
            break


def send(sock, q_ss2cli, **kwargs):
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

            # Send data to server
            sock.sendall(data_frame)
            if "debug" in kwargs.keys() and kwargs["debug"]:
                print("Client: Sended", sended, data_sample, round(data_sample_time, 3))
                sended += 1
                
        except socket.error:                                            # end if socket error
            print('Client: Disconnected with server!')
            exit()
            break


def client(q_ss2cli, q_cli2ss, dc_motor_driver_data, **kwargs):
    if "show" in kwargs.keys() and kwargs["show"]:
        print("Client: Running")

    # Get connection data
    client_data = dc_motor_driver_data["client"]
    server_ip   = client_data["server_ip"]
    server_port = client_data["server_port"]

    # Initial connection data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (server_ip, server_port)                           # IP and port of server

    # Try to connect
    try:
        sock.connect(server_address)
        print('Client: Connected with server ' + str(server_address[0]) + '!')
    except socket.error:                                                # if server is not active
        print('Client: Run server', server_address[0], 'in order to connect!')
        exit()

    if "show" in kwargs.keys() and kwargs["show"]:
        print("Client: Main loop start")


    send_thread    = threading.Thread(target=send,    args=(sock, q_ss2cli,))
    receive_thread = threading.Thread(target=receive, args=(sock, q_cli2ss,))
    send_thread.start()
    receive_thread.start()
