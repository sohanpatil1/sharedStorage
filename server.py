import socket


def start_echo_server(host, port):
    socks = []
    count = 1

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((host, port))
    server_socket.listen(1)

    print("Echo server started. Listening for connections...")
    for i in range(600000):
        # print(f"waiting for accept")
        client_socket, client_address = server_socket.accept()
        socks.append(client_address[1])
        print(f"{count}: appended socket number: {client_address[1]}")
        count += 1
        pass
        if count % 100 == 0:
            print(f"count = {count}")
    pass

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to client: {client_address}")


        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.sendall(data)


        print(f"Client {client_address} disconnected.")
        client_socket.close()


    server_socket.close()


# Start the Echo Server
start_echo_server('localhost', 8000)