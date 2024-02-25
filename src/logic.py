from cryptography.fernet import Fernet
import requests
import uvicorn
from fastapi import FastAPI, Request, Response
import hashlib

app = FastAPI()

def getChecksum(filename):
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def encrypt_filename(filename, key):
    cipher_suite = Fernet(key)
    encrypted_filename = cipher_suite.encrypt(filename.encode())
    return encrypted_filename

def decrypt_filename(encrypted_filename, key):
    cipher_suite = Fernet(key)
    decrypted_filename = cipher_suite.decrypt(encrypted_filename).decode()
    return decrypted_filename

def encrypt_file(file_with_extension, key, chunk=64*1024):
    encrypted_filename = encrypt_filename(file_with_extension)
    parts = file_with_extension.split(".")
    cipher_suite = Fernet(key)

    with open(file_with_extension, 'rb') as file:
        with open(f"{encrypted_filename}.enc", 'wb') as encrypted_file:
            while True:
                plaintext = file.read(chunk)
                if not plaintext:
                    break
                encrypted_data = cipher_suite.encrypt(plaintext)
                encrypted_file.write(encrypted_data)

    return f"{encrypted_filename}.enc"

def decrypt_file(encrypted_filename, key, chunk=64*1024):
    parts = encrypted_filename.split(".")
    file = parts[0]
    file_with_extension = decrypt_filename(file)
    cipher_suite = Fernet(key)
    with open(encrypted_filename, 'rb') as file:
        with open(file_with_extension, 'wb') as decrypted_file:
            while True:
                enctext = file.read(chunk)
                if not enctext:
                    break
                decrypted_data = cipher_suite.decrypt(enctext)
                decrypted_file.write(decrypted_data)

    return file_with_extension

def generateKey():
    return Fernet.generate_key()    

@app.post("/upload")
def uploadToMachine(request: Request):
    return

@app.get("/download")
def downloadFromMachine(request: Request):
    return

key = generateKey()
encrypted_data = encrypt_file("Professional_Photo.jpg", key)
decrypted_data = decrypt_file(encrypted_data=encrypted_data, key=key)

with open("NewProfessional_Photo.jpg", 'wb') as file:
    file.write(decrypted_data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8040)