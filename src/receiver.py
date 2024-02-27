# Client2 sends to server which sends to client1
import socket
import hashlib
import os
import time


def getChecksum(data):
    md5_hash = hashlib.md5()
    if isinstance(data, str) and os.path.isfile(data):
        with open(data, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
    else:
        # If the input is not a filename or the file does not exist, assume it's a string
        md5_hash.update(data.encode('utf-8'))
    
    return md5_hash.hexdigest()

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