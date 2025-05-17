"""Test script for verifying all endpoints are working."""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_health():
    """Test health endpoint."""
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Health Check: {response.status_code} - {response.json()}")
    
def test_auth():
    """Test authentication."""
    # Create a test user first
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpass123",
        "is_active": True,
        "is_superuser": False
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Create User: {response.status_code}")
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Token received: {token[:20]}...")
        return token
    return None

def test_endpoints(token):
    """Test CRUD endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Projects
    project_data = {"name": "Test Project", "description": "Test Description"}
    response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
    print(f"Create Project: {response.status_code}")
    
    # Test Experiments
    experiment_data = {
        "name": "Test Experiment",
        "description": "Test Description",
        "project_id": 1,
        "creator_id": 1
    }
    response = requests.post(f"{BASE_URL}/experiments/", json=experiment_data, headers=headers)
    print(f"Create Experiment: {response.status_code}")
    
    # Test Protocols
    protocol_data = {
        "name": "Test Protocol",
        "description": "Test Description",
        "author_id": 1
    }
    response = requests.post(f"{BASE_URL}/protocols/", json=protocol_data, headers=headers)
    print(f"Create Protocol: {response.status_code}")
    
    # Test Samples
    sample_data = {
        "name": "Test Sample",
        "description": "Test Description",
        "experiment_id": 1,
        "collected_by": 1
    }
    response = requests.post(f"{BASE_URL}/samples/", json=sample_data, headers=headers)
    print(f"Create Sample: {response.status_code}")
    
    # Test Documents (without file upload)
    response = requests.get(f"{BASE_URL}/documents/", headers=headers)
    print(f"List Documents: {response.status_code}")

if __name__ == "__main__":
    print("Testing LabWeave API Endpoints...")
    print("-" * 30)
    
    test_health()
    token = test_auth()
    
    if token:
        test_endpoints(token)
    else:
        print("Authentication failed, skipping other tests")