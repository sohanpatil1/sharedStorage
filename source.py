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

def encrypt_file(filename, key):
    cipher_suite = Fernet(key)
    with open(filename, 'rb') as file:
        plaintext = file.read()
    encrypted_data = cipher_suite.encrypt(plaintext)
    return encrypted_data

def decrypt_file(encrypted_data, key):
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data

def encrypt_filename(filename, key):
    cipher_suite = Fernet(key)
    encrypted_filename = cipher_suite.encrypt(filename.encode())
    return encrypted_filename

def decrypt_filename(encrypted_filename, key):
    cipher_suite = Fernet(key)
    decrypted_filename = cipher_suite.decrypt(encrypted_filename).decode()
    return decrypted_filename

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
encrypted_file_name = encrypt_filename("Professional_Photo.jpg", key)
decrypted_data = decrypt_file(encrypted_data=encrypted_data, key=key)
decrypted_file_name = decrypt_filename(encrypted_file_name, key)

with open("NewProfessional_Photo.jpg", 'wb') as file:
    file.write(decrypted_data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8040)