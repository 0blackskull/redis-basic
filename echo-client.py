import socket

HOST = "127.0.0.1" # Server's hostname or IP address
PORT = 65432 # Teh port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((HOST, PORT))

    # b creates a bytes object
    s.send(b"1")

    while True:
        data = s.recv(1024)

        if data == b"close":
            break
        
        print(f"Received: {data}")

    # data = s.recv(1024)