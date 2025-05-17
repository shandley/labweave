#!/usr/bin/env python3
"""Test script to verify the development environment is working properly."""

import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_health():
    """Test if the API is running."""
    try:
        response = requests.get("http://localhost:8000/api/v1/health")
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return False

def test_database_connection():
    """Test if PostgreSQL is accessible."""
    try:
        db_url = os.getenv("DATABASE_URL", "postgresql://labweave_user:labweave_password@localhost/labweave")
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ PostgreSQL connection successful")
            return True
    except OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_api_docs():
    """Test if API documentation is accessible."""
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs not accessible: {e}")
        return False

def test_auth_endpoint():
    """Test if authentication endpoint exists."""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "test", "password": "test"}
        )
        # We expect 401 or 422, not 404
        if response.status_code in [401, 422]:
            print("✅ Auth endpoint exists")
            return True
        else:
            print(f"❌ Auth endpoint issue: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth endpoint not accessible: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🧪 Testing LabWeave Development Environment\n")
    
    tests = [
        ("API Health", test_api_health),
        ("Database Connection", test_database_connection),
        ("API Documentation", test_api_docs),
        ("Auth Endpoint", test_auth_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...")
        results.append(test_func())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your environment is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())