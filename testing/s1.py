from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()

# Define a route for the root endpoint "/"
@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

# Define a route for "/items/{item_id}" where item_id is a path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# Run the FastAPI application using uvicorn server on port 8080
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
