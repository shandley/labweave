"""Simple test to verify basic setup."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create a simple app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Test it
client = TestClient(app)
response = client.get("/")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

assert response.status_code == 200
assert response.json() == {"message": "Hello World"}
print("Test passed!")