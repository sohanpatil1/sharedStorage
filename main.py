from fastapi import FastAPI, Request, Response
from logger import logger
import psycopg2
from psycopg2.extras import Json, DictCursor
import uvicorn
# from cryptography.fernet import Fernet

###############################
connection = psycopg2.connect(
    dbname="storagedb",
    user="postgres",
    password="my_password",
    host="localhost",
    port="54320"
)
connection.autocommit = True
cursor = connection.cursor(cursor_factory=DictCursor)

# Check if the database exists
cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'storagedb';")
exists = cursor.fetchone()

# If the database doesn't exist, create it
if not exists:
    cursor.execute("CREATE DATABASE storagedb;")

# Commit the transaction
connection.commit()

cursor.execute("CREATE TABLE if not exists tracker ( \
                sourceUID VARCHAR(30),  \
                spaceRemaining INT, \
                destinations JSONB );")
"""
destinations = {
        }
"""
###############################

app = FastAPI()

# def generateKey():
#     return Fernet.generate_key()    

@app.post("/upload")
async def uploadToDest(request: Request):
    client_ip = request.client.host
    sourceUID = request.query_params['sourceUID']
    spaceRequired = request.query_params['spaceRequired']
    pathToDirectory = request.query_params['pathToDirectory']
    key = request.query_params['encryptionKey']

    if 'destination' in request.query_params:
        destination = request.query_params['destination']
    else:
        destination = None
        # Check for any empty destination.
        query = "SELECT destinations FROM tracker WHERE sourceUID = %s;"
        cursor.execute(query, (sourceUID,))
        results = cursor.fetchone()
    
    if len(results) == 0:   # First upload
        query = f"INSERT sourceKey FROM tracker WHERE sourceUID = {sourceUID};"
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)