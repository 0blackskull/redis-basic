import sys
import selectors 
import socket

# HOST = "127.0.0.1" # Server's hostname or IP address
# PORT = 65432 # The port used by the server

try:
    # argv[0] is the script itself
    host = sys.argv[1]
    port = int(sys.argv[2]) # ValueError due to int() if argv[1] is like "abc"
except IndexError:
    print("Usage: python multiconn-server.py <host> <port>")
    sys.exit(1)
except ValueError:
    print("Port must be an integer. Usage: python multiconn-server.py <host> <port>")
    sys.exit(1)

sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")

lsock.setblocking(False) 
# Read events for the listening socket
sel.register(lsock, selectors.EVENT_READ, data=None) # arbitary data

"""
Accept connection on a listening socket ready for read
"""
def accept_connection(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_WRITE | selectors.EVENT_READ
    sel.register(conn, selectors.EVENT_WRITE, data=data)

"""
Process event from a connection socket
"""
def service_connection(event):
    mask = event.mask
    conn = event.key.fileobj
    data = event.key.data

    # Ready for Read
    if mask & selectors.EVENT_READ:
        recv_data = conn.recv(1024)

        if recv_data:
            data += recv_data
        else:
            print(f"Closing connection to addr: {data.addr}")
            # Cleanup
            sel.unregister(conn)
            conn.close()

    # Ready for write
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            bytes_sent = conn.send(data.outb)
            data.outb = data.outb[bytes_sent:]


"""
Event Loop setup
"""
try:
    while True:
        # Blocks till I/O ready sockets available
        events = sel.select(timeout=None) # returns tuple list

        for event in events:

            # Event from listening socket
            if event.key.data is None:
                # Accept new connection
                accept_connection(event.key.fileobj) # The server side lsock we registered earlier
            else:
                # Event from connection socket
                service_connection(event)


except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()