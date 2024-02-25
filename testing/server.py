import socket
import select

socks = []

def handle_client(client_socket, client_address):
    # Respond to the client
    data = client_socket.recv(64)
    if data.decode() != "Receiver":
        print(f"Received data '{data.decode()}' from client2")
        for sock in socks:
            if sock != client_socket:
                sock.sendall(data)
    else:
        print(f"receiver joined server.")


# Function to initialize server
def initialize_server():
    # Create a list to hold available sockets
    global socks

    # Create 10 sockets and bind them to the same address
    for _ in range(2):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        sock.bind(("0.0.0.0", 8090))
        sock.listen()
        socks.append(sock)

    while True:
        # Use select to handle multiple sockets
        readable, _, _ = select.select(socks, [], [])

        if not readable:
            print("No sockets ready for reading. Waiting...")
            break

        for sock in readable:
            client_socket, client_address = sock.accept()
            print(f"Connection established with {client_address}")

            handle_client(client_socket, client_address)

initialize_server()
