from cryptography.fernet import Fernet
import hashlib
import os

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
    
    return md5_hash, md5_hash.hexdigest()

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

key = generateKey()
encrypted_filename = encrypt_file("Professional_Photo.jpg", key)
decrypted_filename = decrypt_file(encrypted_filename=encrypted_filename, key=key)

with open("NewProfessional_Photo.jpg", 'wb') as file:
    file.write(decrypted_filename)