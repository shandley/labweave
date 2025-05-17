#!/usr/bin/env python3
"""Simple test to check if FastAPI app starts correctly."""

from src.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting LabWeave test server on port 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002)