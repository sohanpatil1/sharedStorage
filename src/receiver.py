# Client2 sends to server which sends to client1
import socket
import time

def main():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client_socket.connect(('0.0.0.0', 8090))

    while True:
        try:
            data = client_socket.recv(64)
            if data:
                print(f"receiver.py : {data.decode()}")
            time.sleep(1)

        except KeyboardInterrupt:
            # Clean up
            client_socket.close()

if __name__ == "__main__":
    main()