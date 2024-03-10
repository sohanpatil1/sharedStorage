import psycopg2
from psycopg2.extras import Json, DictCursor
import config

###############################
connection = psycopg2.connect(
    dbname=config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=str(config.DB_PORT)
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

async def uploadToDest(request):
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