import socket

HOST = "127.0.0.1"
PORT = 65432

# id to name
users = {
    1: "Utkarsh Bajpai",
    2: "Sky Carter"
}

# socket object implements context manager protocol in python, no explicit .close() needed
# IPv4 address family, TCP socket type
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen() # optional backlog param

    # accept call blocks execution
    conn, addr = s.accept()

    with conn:
        print(f"Connected by {addr}")

        counter = 20 * 1000

        # read max 1024 bytes from servers TCP receive buffer 
        data = conn.recv(1024)

        print(type(data), data)

        while True:
            # exit 
            # if not data:
            #     break
            
            # print(type(data), data)

            if counter <= 0:
                conn.send(b"close")
                break
            else:
                ping = ("PING" + str(21 - counter / 1000)).encode('utf-8')
                conn.send(ping)
                counter -= 1000
            

            # Just sending back all received data as a sample

    # .close() called automatically in cleanup (__exit__ in context manager)

            