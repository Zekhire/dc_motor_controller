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


def remove_defective_prefix(data):
    data = data.replace("\x00", "")
    return data


def receive(sock, q_cli2ss, **kwargs):
    received = 1
    # Communication loop
    while True:
        try:
            data_frame = sock.recv(64)
            print(received, data_frame)
            if data_frame:
                # print("", end="")
                data = data_frame.decode("utf-8")
                
                # print("Client: Received", received, data)
                # data = remove_defective_prefix(data)
                # print(data)
                # print()
                data_split = data.split()
                
                # Unpack data
                try:
                    data0 = float(data_split[0])    # w rample
                    data1 = float(data_split[1])    # w_ref sample
                    data2 = float(data_split[2])    # measurement time
                except IndexError:
                    print("received", received, data_split)

                # Send data forward
                data_tuple = (data0, data1, data2)
                q_cli2ss.put(data_tuple)
                received += 1

                if "debug" in kwargs.keys() and kwargs["debug"]:
                    print("Client: Received", received)
                    received += 1
            else:
                print("dupa")

        except socket.error:
            break


def send(sock, **kwargs):
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
            sock.sendall(data_frame)
            if "debug" in kwargs.keys() and kwargs["debug"]:
                print("Server: Sended", sended)
                sended += 1
    
        except socket.error:                                            # end if socket error
            print('Client: Disconnected with server!')
            exit()
            break


def client(q_s2cm, monitor_data, **kwargs):
    if "show" in kwargs.keys() and kwargs["show"]:
        print("Client: Running")

    # Get connection data
    client_data = monitor_data["client"]
    server_ip   = client_data["server_ip"]
    server_port = client_data["server_port"]

    # Initial connection data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (server_ip, server_port)                           # IP and port of server

    # Try to connect
    while True:
        try:
            sock.connect(server_address)
            print('Client: Connected with server ' + str(server_address[0]) + '!')
            break
        except socket.error:                                                # if server is not active
            print('Client: Run server', server_address[0], 'in order to connect!')

    if "show" in kwargs.keys() and kwargs["show"]:
        print("Client: Main loop start")


    send_thread    = threading.Thread(target=send, args=(sock,))
    receive_thread = threading.Thread(target=receive, args=(sock, q_s2cm,))
    send_thread.start()
    receive_thread.start()
