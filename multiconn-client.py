import sys
import selectors 
import socket
import types

try:
    # argv[0] is the script itself
    host = sys.argv[1]
    port = int(sys.argv[2]) # ValueError due to int() if argv[1] is like "abc"
    num_connections = int(sys.argv[3]) if len(sys.argv) > 3 else 1
except IndexError:
    print("Usage: python multiconn-server.py <host> <port> <num-connections>")
    sys.exit(1)
except ValueError:
    print("Port must be an integer. Usage: python multiconn-server.py <host> <port> <num-connections>")
    sys.exit(1)

sel = selectors.DefaultSelector()

messages = [b"1st from client", b"2nd from client", b"3rd from client"]

def start_connections(host, port, num_conns):
    server_addr = (host, port)

    for i in range(num_conns):
        conn_id = i + 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

        # connect_ex instead of connect
        # Non blocking mode so connection not completed instantly
        # connect raises BlockingIOError in this case
        # connect_ex just returns errno.EINPROGRESS
        sock.connect_ex(server_addr)

        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        data = types.SimpleNamespace(
            conn_id=conn_id,
            msg_total=sum(len(m) for m in messages),
            recv_total=0, # Track how much recieved, number of bytes
            messages=messages.copy(), # Each connection sends a separate list
            outb=b"" # Track how much sent
        )
        sel.register(sock, events, data=data)

def service_connection(event):
    key, mask = event
    sock = key.fileobj
    data = key.data

    # Read ready (data received from server)
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"Received from server: {recv_data!s}")
            # Update receive tracking
            data.recv_total += len(recv_data)

        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection for {data.conn_id}")
            sel.unregister(sock)
            sock.close()

    # Write ready (send data to server)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop()

        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.conn_id}")
            bytes_sent = sock.send(data.outb)
            data.outb = data.outb[bytes_sent:]


try:
    start_connections(host, port, num_connections)
    while True:
        events = sel.select(timeout=None)
        for event in events:
            # if event.key.data:
            service_connection(event)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
    sys.exit(1)
# except Exception as e:
#     print(f"Exiting due to: {e!r}")
#     sys.exit(1)
finally:
    sel.close()

