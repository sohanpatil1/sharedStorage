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

def encrypt_file(file_with_extension, chunk=64*1024):
    key = Fernet.generate_key()  
    encrypted_filename = encrypt_filename(file_with_extension, key)
    encrypted_content = b""
    cipher_suite = Fernet(key)
    with open(file_with_extension, 'rb') as file:
        while True:
            plaintext = file.read(chunk)
            if not plaintext:
                break
            encrypted_data = cipher_suite.encrypt(plaintext)
            encrypted_content += encrypted_data
    return encrypted_filename, encrypted_content, key


def decrypt_file(encrypted_filename, key, chunk=64*1024):
    parts = encrypted_filename.split(".")
    file = parts[0]
    file_with_extension = decrypt_filename(file, key)
    cipher_suite = Fernet(key)
    with open(encrypted_filename, 'r') as file:
        with open(file_with_extension, 'wb') as decrypted_file:
            while True:
                enctext = file.read(chunk)
                if not enctext:
                    break
                decrypted_data = cipher_suite.decrypt(enctext)
                decrypted_file.write(decrypted_data)

    return file_with_extension

def decrypt_content(encrypted_content, key, chunk=64*1024):
    cipher_suite = Fernet(key)
    decrypted_data = b''
    while True:
        enctext = encrypted_content.read(chunk)
        if not enctext:
            break
        decrypted_data += cipher_suite.decrypt(enctext)
    return decrypted_data


def generateKey():
    return Fernet.generate_key()    

def file_processor(func):
    def wrapper(file_path):
        if os.path.exists(file_path):
            # If it's a file, apply the function to the file
            if os.path.isfile(file_path):
                func(file_path)
            # If it's a directory, recursively apply the decorator to each item in the directory
            elif os.path.isdir(file_path):
                for item in os.listdir(file_path):
                    item_path = os.path.join(file_path, item)
                    wrapper(item_path)
        else:
            print(f"File or directory '{file_path}' does not exist.")
    return wrapper

def write_to_file(data, filename):
    with open(filename, 'w') as file:
        file.write(data)
    print("Data written to", filename)
    
# key = generateKey()
# encrypted_filename = encrypt_file("Professional_Photo.jpg", key)
# decrypted_filename = decrypt_file(encrypted_filename=encrypted_filename, key=key)

# with open("NewProfessional_Photo.jpg", 'wb') as file:
#     file.write(decrypted_filename)