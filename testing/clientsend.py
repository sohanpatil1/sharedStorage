import socket

def main():

    csocks = [] # client sockets
    # Connect the socket to the server address
    # server_address = ('2601:647:5580:9310:18e:7b3d:5991:66b9', 12345)  # Use IPv6 loopback address
    server_address = ('localhost', 8000)
    for i in range(100000):
        # Create a TCP/IP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        t = client_socket.connect(server_address)
        pass
    pass
    breakpoint()

    try:
        # Send data
        message = "Hello, world"
        print(f"Sending '{message}' to the server")
        client_socket.sendall(message.encode())

        # Receive response
        data = client_socket.recv(16)
        print(f"Received '{data.decode()}' from the server")
    finally:
        # Clean up
        client_socket.close()

if __name__ == "__main__":
    main()
