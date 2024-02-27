import socket
import select

clients = {}  # Dictionary to store client sockets with unique identifiers

def handle_client(client_socket, client_address, data):
    for sock, address in clients.items():
        if client_socket != sock and (address!="server"):
            print(f"Sent for {address[1]}")
            sock.send(data)

# Function to initialize server
def initialize_server():
    # Create a list to hold available sockets
    global clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    server_socket.bind(("0.0.0.0", 8090))
    server_socket.listen(90)
    clients[server_socket] = "server"

    while True:
        sockets_to_monitor = list(clients.keys())
        readable, _, _ = select.select(sockets_to_monitor, [], [])
        print(f"len(sockets_to_monitor): {len(sockets_to_monitor)}")

        for triggered_socket in readable:
            if triggered_socket == server_socket:   # New request
                client_socket, client_address = server_socket.accept()
                clients[client_socket] = client_address
                print(f"New connection from {client_address}")

            else:   # received data
                data = triggered_socket.recv(1024)
                if data:
                    print(f"Received data from {clients[triggered_socket]}: {data.decode()}")
                    handle_client(triggered_socket, clients[triggered_socket], data)
                else:
                    print(f"Connection closed by {clients[triggered_socket]}")
                    triggered_socket.close()
                    del clients[triggered_socket]



# Initialize the server
initialize_server()
