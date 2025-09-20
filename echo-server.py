import socket

HOST = "127.0.0.1"
PORT = 65432

# socket object implements context manager protocol in python, no explicit .close() needed
# IPv4 address family, TCP socket type
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen() # optional backlog param

    # accept call blocks execution
    conn, addr = s.accept()

    with conn:
        print(f"Connected by {addr}")

        while True:
            # read max 1024 bytes from servers TCP receive buffer 
            data = conn.recv(1024)

            # exit 
            if not data:
                break
            
            print(data)
            # Just sending back all received data as a sample
            conn.sendall(data)

    # .close() called automatically in cleanup (__exit__ in context manager)

            