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
import webbrowser

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt
import uvicorn

MQTT_HOST = "localhost"
FASTAPI_HOST = "localhost"
CLIENT_ID = "temp"


def on_message(client, userdata, message):
    logging.info(f"Received message {sys.getsizeof(str(message.payload.decode()))}")    
    output = json.loads(message.payload.decode())
    # if "topic" in output.keys():
    if output['destination'] == message.topic:
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
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(MQTT_HOST, 1883)
    client.loop_start()
    return app, client


app, client = Initialize(on_message, on_connect, on_publish)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/publish")
async def publish(request: Request):
    body = await request.json()
    logging.info("Client Publishing")

    if body['isEncrypted']:
        key = logic.generateKey()
    else: 
        key = None

    if not os.path.exists("tempcookie.json"):
        raise FileNotFoundError(f"You need to register first!")
    else:
        logging.info("Publishing since registered")

    with open("tempcookie.json", "r") as file:
        data = json.load(file)

    params = {
        'sourceUID' : data['cookie'],
        'filename': body.get("filename", None),
        'destination': body.get('destination', None),
    }

    if key:
        params['encryptionKey'] = key.decode()

    if body.get("isEncrypted", True):
        response = requests.post(f"http://{FASTAPI_HOST}:8080/upload", json=params)
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
        response = requests.post(f"http://{FASTAPI_HOST}:8080/upload", json=params)
        if response.ok:
            logging.info("Received topic for sending encrypted file")
            with open(body['filename'], "rb") as file:
                file_content = base64.b64encode(file.read())    # file content of the file being shared.
            topic = eval(response.text) # Topic for sending content
            content = {
                'filename': body.get("filename"),
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
        'path': body["path"],   # Could be none. When only one folder has been pushed.
    }
    response = requests.get(f"http://{FASTAPI_HOST}:8080/download", json=body)
    if response.ok:
        topic = response.text
        logging.info("Made request to server for topic.")
        # Send information through mqtt
        client.subscribe(topic=topic)
        return Response(status_code=200)
    else:
        return Response(content="Could not make request to server for topic.", status_code=500)


@app.post("/register")
def register():
    if os.path.exists("tempcookie.json"):
        logging.info("Rejoining session")
        with open("tempcookie.json", "r") as file:
            data = json.load(file)
        if not len(data):   #Empty file
            os.remove("tempcookie.json")
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
        response = requests.get(f"http://{FASTAPI_HOST}:8080/register", json=body)
        if response.ok:
            cookie = eval(response.text)
            logging.info("Received cookie:", cookie)
            data = {
                'cookie': cookie,
                'key': key.decode(),
            }
            with open('tempcookie.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            client.subscribe(cookie)
        else:
            logging.info("Registration request failed with status code:", response.status_code)
            sys.exit(0)
        return Response(status_code=200)

if __name__ == "__main__":
    # webbrowser.open('file:///Users/sohanpatil/Documents/VSWorkspace/storage/src/frontend/index.html',new=2)
    uvicorn.run(app=app, host="0.0.0.0", port=8060)