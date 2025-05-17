#!/usr/bin/env python3
"""Manual test script to diagnose server issues."""

import subprocess
import time
import requests
import sys

def test_server():
    """Test if the server is responding correctly."""
    print("Starting server test...")
    
    # Start server in background
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(3)
    
    try:
        # Test endpoints
        endpoints = [
            ("http://localhost:8001/docs", "API Documentation"),
            ("http://localhost:8001/api/v1/health", "Health Check"),
        ]
        
        for url, name in endpoints:
            try:
                response = requests.get(url, timeout=5)
                print(f"\n{name} ({url}):")
                print(f"Status: {response.status_code}")
                print(f"Content: {response.text[:200]}...")
            except Exception as e:
                print(f"\n{name} ({url}):")
                print(f"Error: {e}")
        
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()
        
        # Print any server errors
        stdout, stderr = server_process.communicate()
        if stderr:
            print("\nServer errors:")
            print(stderr)

if __name__ == "__main__":
    test_server()