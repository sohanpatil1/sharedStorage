from fastapi import FastAPI, Request, Response
import uvicorn
import uuid

app = FastAPI()

@app.get("/transferCreds")
def transferCreds(request: Request):
    data = {
        'topic': "receiver"
    }
    return Response(content=str(data), status_code=200)

@app.get("/login")
def login():
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    # Store uuid in postgreSQL
    return Response(content=uuid_str, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)