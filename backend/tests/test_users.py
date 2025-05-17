"""Test user endpoints."""
from src.models.user import User


def test_create_user(client, db):
    """Test user creation."""
    user_data = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "newpassword",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "password" not in data
    assert "hashed_password" not in data


def test_read_users(client, db):
    """Test reading users."""
    # Create test users
    test_user1 = User(
        email="user1@example.com",
        username="user1",
        hashed_password="hashedpw1"
    )
    test_user2 = User(
        email="user2@example.com",
        username="user2",
        hashed_password="hashedpw2"
    )
    db.add_all([test_user1, test_user2])
    db.commit()
    
    response = client.get("/api/v1/users/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2