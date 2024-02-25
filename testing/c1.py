import socket, time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientsocket.connect(('localhost', 5555))

clientsocket.send(b'hello1')
time.sleep(5)
clientsocket.send(b'hello2')
