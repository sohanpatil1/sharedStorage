"""
This is the standard code used by sender/receiver. Not for testing purposes.
"""

import base64
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
    output = json.loads(message.payload.decode())
    if "topic" in output.keys():
        client.subscribe(output["topic"])
        logging.info(f"Client.py subscribed to {output['topic']}")
        return
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
        logging.error("Temp.py File is encrypted.")
        decrypted_data = logic.decrypt_content(output["data"], output["key"])
        filename = logic.decrypt_filename(output["filename"], key=output["key"])
    else:
        decrypted_data = base64.b64decode(output['data'])
        filename = output['filename']
        logging.info("Client.py writing to sharedStorage/test.png file")
    logic.write_to_file(data=decrypted_data, filename=f"sharedStorage/{filename}")


def on_connect(client, userdata, flags, rc, properties):
    logging.info("Client.py connected to broker!")


def on_publish(client, userdata, mid, reason_codes, properties):
    logging.info("Client.py published message correctly")


def on_disconnect(client, userdata, rc, properties):
    if rc != 0:
        logging.info(f"Unexpected disconnection. Reconnecting...")

def on_subscribe(client, userdata, mid, rc, properties):
    logging.info("Temp subscribed to a topic")

def Initialize(on_message, on_connect, on_publish):
    app = FastAPI()
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="client.py")
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect("localhost", 1883)
    client.loop_start()
    return app, client


app, client = Initialize(on_message, on_connect, on_publish)


@app.post("/publish")
def publish(request: Request):
    logging.info("Client Publishing")
    if eval(request.query_params['isEncrypted']):
        key = logic.generateKey()
    else: 
        key = None
    if not os.path.exists("cookie.json"):
        raise FileNotFoundError(f"You need to register first!")
    else:
        logging.info("Publishing since registered")
    with open("cookie.json", "r") as file:
        data = json.load(file)
    body = {
        'sourceUID' : data['cookie'],
        'filename': request.query_params.get("filename", None),
        'destination': request.query_params.get('destination', None),
    }
    if key:
        body['encryptionKey'] = key.decode()
    if eval(request.query_params.get("isEncrypted", True)):
        response = requests.post("http://localhost:8080/upload", json=body)
        if response.ok:
            logging.info("Received topic for sending encrypted file")
            topic = response.text
            encrypted_filename, encrypted_content, key = logic.encrypt_file(file_with_extension="Professional_Photo.png", key=key)
            content = {
                "filename": encrypted_filename, # Encrypted filename
                "data": encrypted_content,  # Encrypted content
                "key": key,
            }
            logging.info(sys.getsizeof(str(content)))
            client.publish(topic=topic, payload=json.dumps(content))
            logging.info("Sent encrypted file")
            return Response(content="Success", status_code=200)
        else:
            return Response(content=response.text, status_code=500)
    else:   # No need to be encrypted
        response = requests.post("http://localhost:8080/upload", json=body)
        if response.ok:
            logging.info("Received topic for sending encrypted file")
            with open(body['filename'], "rb") as file:
                file_content = base64.b64encode(file.read())
            topic = eval(response.text)
            content = {
                'filename': request.query_params.get("filename"),
                'isEncrypted' : False,
                'data': file_content.decode(),
                # 'data': base64.b64decode(file_content),
                'key' : None,
                'source' : "b89422da-ef65-4589-80bd-4f846b17e763",  # Which machine sent it
                'destination': "cab96b10-7e43-42a2-a2e9-0475e71c1423", # Which machine received it
            }
            logging.info(f"Client.py sent the file without encryption at topic {topic}.")
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
# register()

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8050)