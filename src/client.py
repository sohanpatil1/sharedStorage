"""
This is the standard code used by sender/receiver. Not for testing purposes.
"""

import json
from logger import logging
import logic
import os
import requests
import sys
import time
import uuid

from fastapi import FastAPI, Request, Response
import msgpack
import paho.mqtt.client as mqtt
import uvicorn


def get_mac_address():
    # Get the MAC address of the first network interface
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    mac_address = ":".join([mac[e : e + 2] for e in range(0, 12, 2)])
    return mac_address


def on_message(client, userdata, message):
    logging.info(f"Received message {sys.getsizeof(str(message.payload.decode()))}")
    output = eval(message.payload.decode())
    """
    output = {
        'filename': encrypted_filename,
        'isEncrypted' : True,
        'data': encrypted_content,
        'key' : key,
        'source' : source,  # Which machine sent it
        'destination': destination, # Which machine received it
    }
    """
    if output['isEncrypted']:
        decrypted_data = logic.decrypt_content(output["data"], output["key"])
        filename = logic.decrypt_filename(output["filename"], key=output["key"])
    else:
        decrypted_data = output['data']
        filename = output['filename']
    logic.write_to_file(data=decrypted_data, filename="test.png")


def on_connect(client, userdata, flags, rc, properties):
    logging.info("Connected to broker!")


def on_publish(client, userdata, mid, reason_codes, properties):
    logging.info("Message published correctly")


def on_disconnect(client, userdata, rc, properties):
    if rc != 0:
        logging.info(f"Unexpected disconnection. Reconnecting...")


def Initialize(on_message, on_connect, on_publish):
    app = FastAPI()
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=get_mac_address())
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect("localhost", 1883)
    client.loop_start()
    return app, client


app, client = Initialize(on_message, on_connect, on_publish)


@app.post("/publish")
def publish(request: Request):
    key = logic.generateKey()
    if not os.path.exists("cookie.json"):
        raise FileNotFoundError(f"You need to register first!")
    
    with open("cookie.json", "r") as file:
        data = json.load(file)
    body = {
        'sourceUID' : data['cookie'],
        'path': request.query_params.get("path", None),
        'encryptionKey' : key,
        'destination': request.query_params.get('destination', None),
    }
    if request.query_params.get("isEncrypted", True):
        response = requests.get("http://localhost:8080/upload", json=body)
        if response.ok:
            topic = response.text
            encrypted_filename, encrypted_content, key = logic.encrypt_file(file_with_extension="Professional_Photo.png", key=key)
            content = {
                "filename": encrypted_filename, # Encrypted filename
                "data": encrypted_content,  # Encrypted content
                "key": key,
            }
            logging.info(sys.getsizeof(str(content)))
            client.publish(topic=topic, payload=json.dumps(content))
            return Response(content="Success", status_code=200)
        else:
            return Response(status_code=500)
    else:   # No need to be encrypted
        response = requests.get("http://localhost:8080/upload", json=body)
        if response.ok:
            with open("filename", "r") as file:
                file_content = file.read()
            topic = response.text
            content = {
                "filename": request.query_params.get("filename"),   # Decrypted Filename
                "data": file_content,
                "key": None,
            }
            logging.info(sys.getsizeof(str(content)))
            client.publish(topic=topic, payload=json.dumps(content))
            return Response(content="Success", status_code=200)
        else:
            return Response(status_code=500)


@app.get("/download")
def downloadBackup(request: Request):
    """
    Requesting client's data currently stored on friend's machine.
    """
    # Request for transfer credentials
    body = {
        'path': request.query_params["path"],   # Could be none. When only one folder has been pushed.
    }
    response = requests.get("http://localhost:8080/download", json=body)
    if response.ok:
        topic = response.text
        # Send information through mqtt
        client.subscribe(topic=topic)
        return Response(status_code=200)
    else:
        return Response(content="Could not make request to server.", status_code=500)


@app.post("/register")
def register():
    if os.path.exists("cookie.json"):
        logging.info("Rejoining session")
        with open("cookie.json", "r") as file:
            data = json.load(file)
        if not len(data):   #Empty file
            os.remove("cookie.json")
        client.subscribe(data['cookie'])
    else:

        cookie = None
        key = logic.generateKey()
        logging.info("New registration")
        if not os.path.exists("sharedStorage"):
            os.makedirs("sharedStorage")
        body = {
            "spaceOffered" : 5368709120, #5 GB
            "location" : "sharedStorage/"
        }
        response = requests.get("http://localhost:8080/register", json=body)
        if response.ok:
            cookie = response.text
            logging.info("Received cookie:", cookie)
            data = {
                'cookie': cookie,
                'key': key.decode(),
            }
            with open('cookie.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            client.subscribe(cookie)
        else:
            logging.info("Registration request failed with status code:", response.status_code)
            sys.exit(0)
# publish()
register()

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8050)