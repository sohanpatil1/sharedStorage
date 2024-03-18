import config
from fastapi import FastAPI, Request, Response
import json
import logging
import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import Json, DictCursor
import time
import uvicorn
import uuid

###############################
connection = psycopg2.connect(
    dbname=config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=str(config.DB_PORT),
)
connection.autocommit = True
cursor = connection.cursor(cursor_factory=DictCursor)

# Check if the database exists
cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'storagedb';")
exists = cursor.fetchone()

# If the database doesn't exist, create it
if not exists:
    cursor.execute("CREATE DATABASE storagedb;")
    logging.info("Creating new database")

# Commit the transaction
connection.commit()

cursor.execute(
    "CREATE TABLE if not exists tracker ( \
                sourceUID VARCHAR(100),  \
                spaceRemaining INT, \
                destinations JSONB );"
)
"""
destinations = {
        }
"""
def on_connect(client, userdata, flags, rc, properties):
    logging.info("Connected to broker!")


def on_publish(client, userdata, mid, reason_codes, properties):
    logging.info("Message published correctly")


client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="Server")
client.on_connect = on_connect
client.on_publish = on_publish
client.connect("localhost", 1883)
client.loop_start()

###############################

app = FastAPI()

@app.post("/upload")
async def uploadToDest(request):
    sourceUID = request.query_params["sourceUID"]
    pathToDirectory = request.query_params["path"]
    key = request.query_params["encryptionKey"]
    destination= request.query_params.get('destination', None),

    if not destination:
        # Check for any empty destination the source already has their information in.
        query = "SELECT destinations FROM tracker WHERE sourceUID = %s;"
        cursor.execute(query, (sourceUID,))
        results = cursor.fetchone()
    else:
        # Reach out to same destination
        generated_uuid = uuid.uuid4()
        topic = str(generated_uuid)
        client.publish(topic="sourceUID", content=topic)    # Share topic with source
        client.publish(topic="destination", content=topic)    # Share topic with destination
        pass
    return topic


@app.get("/register")
async def login(request: Request):
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    body = await request.json()
    spaceOffered = body["spaceOffered"]
    destinations = json.dumps({})
    # Store uuid in postgreSQL
    query = f"INSERT INTO tracker (sourceUID, spaceremaining, destinations) VALUES ('{uuid_str}', {spaceOffered}, '{destinations}');"
    cursor.execute(query=query)
    return Response(content=uuid_str, status_code=200)


@app.get("/download")
def requestDownload(request: Request):
    """ """


if __name__ == "__main__":
    try:
        uvicorn.run(app=app, host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        exit(0)
