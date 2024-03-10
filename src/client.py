"""
This is the standard code used by sender/receiver. Not for testing purposes.
"""

import requests
import uuid
import os
import logic
import sys
import msgpack
import paho.mqtt.client as mqtt
import time
from fastapi import FastAPI, Request
import uvicorn
from logger import logging

def get_mac_address():
    # Get the MAC address of the first network interface
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    mac_address = ':'.join([mac[e:e+2] for e in range(0, 12, 2)])
    return mac_address

def on_message(client, userdata, message):
    logging.info("Received message")
    output = eval(message.payload)
    """
    output = {
        'filename': encrypted_filename,
        'data': encrypted_content,
        'key' : key,
    }
    """
    decrypted_data = logic.decrypt_content(output['data'], output['key'])
    filename = logic.decrypt_filename(output['encypted_filename'])
    logic.write_to_file(data=decrypted_data, filename=filename)

def on_connect(client, userdata, flags, rc, properties):
    logging.info("Connected to broker!")

def on_publish(client, userdata, mid, reason_codes, properties):
    logging.info("Message published correctly")

def on_disconnect(client, userdata, rc, properties):
    if rc != 0:
        logging.info(f"Unexpected disconnection. Reconnecting...")

def Initialize(on_message, on_connect, on_publish):
    app = FastAPI()
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect("localhost", 1883)
    client.loop_start()
    client.enable_logger(logger=logging)
    return app, client

app, client = Initialize(on_message, on_connect, on_publish)


@app.post("/publish")
def publish(request: Request):
    # Access file structure and publish
    # Reach out to server to get topic name.
    # response = requests.get("http://localhost:8080/transferCreds")
    # response = eval(response.text)
    global client
    encrypted_filename, encrypted_content, key = logic.encrypt_file(file_with_extension="Professional_Photo.png")
    content={
        'filename': encrypted_filename,
        'data': encrypted_content,
        'key' : key,
    }
    client.publish('receiver', str(content))

@app.post("/register")
def register(request: Request):
    global client
    if os.path.exists("cookie.txt"):
        logging.info("Rejoining")
    else:
        cookie = None
        logging.info("New registration")
    
    if not cookie:
        response = requests.get("http://localhost:8080/login")
        if response.ok:
            cookie = response.text
            logging.info("Received cookie:", cookie)
            logic.write_to_file(cookie, "~/cookie.txt")
        else:
            logging.info("Request failed with status code:", response.status_code)
            sys.exit(0)
    
if __name__ == "__main__":
    pass
    # uvicorn.run(app=app, host="0.0.0.0", port=8050)