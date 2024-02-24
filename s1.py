import socket, threading

# https://stackoverflow.com/questions/10810249/python-socket-multiple-clients
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('', 5555))
serversocket.listen(5)

def client_listener(connection, address):
    print(f"New connection {connection=} {address=}")
    while True:
        buf = connection.recv(64)
        if not buf:
            print(f"Closing connection {connection=} {address=}")
            break
        print(buf)


while True:
    connection, address = serversocket.accept()
    threading.Thread(target=client_listener, args=(connection, address)).start()