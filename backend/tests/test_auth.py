"""Test authentication endpoints."""
from src.core.security import get_password_hash
from src.models.user import User


def test_login(client, db):
    """Test login endpoint."""
    # Create test user
    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword")
    )
    db.add(test_user)
    db.commit()
    
    # Test login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"