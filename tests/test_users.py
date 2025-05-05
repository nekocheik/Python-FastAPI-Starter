from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.services import user as user_service
from app.schemas.user import UserCreate


def test_read_users_superuser(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    """
    Test that a superuser can read all users.
    """
    response = client.get("/api/v1/users/", headers=superuser_token_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0
    for user in users:
        assert "id" in user
        assert "email" in user


def test_read_users_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test that a normal user cannot read all users.
    """
    response = client.get("/api/v1/users/", headers=normal_user_token_headers)
    assert response.status_code == 400  # Bad request - not a superuser


def test_create_user_superuser(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    """
    Test that a superuser can create a new user.
    """
    data = {
        "email": "new_user@example.com",
        "password": "password",
        "full_name": "New User",
    }
    response = client.post("/api/v1/users/", headers=superuser_token_headers, json=data)
    assert response.status_code == 200
    new_user = response.json()
    assert new_user["email"] == data["email"]
    assert new_user["full_name"] == data["full_name"]
    assert "id" in new_user


def test_create_user_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test that a normal user cannot create a new user.
    """
    data = {
        "email": "new_user2@example.com",
        "password": "password",
        "full_name": "New User 2",
    }
    response = client.post("/api/v1/users/", headers=normal_user_token_headers, json=data)
    assert response.status_code == 400  # Bad request - not a superuser


def test_read_user_me(client: TestClient, normal_user_token_headers: Dict[str, str], normal_user: Dict[str, str]) -> None:
    """
    Test that a user can read their own information.
    """
    response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == normal_user["email"]
    assert "id" in user


def test_update_user_me(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test that a user can update their own information.
    """
    data = {"full_name": "Updated Name"}
    response = client.put("/api/v1/users/me", headers=normal_user_token_headers, json=data)
    assert response.status_code == 200
    user = response.json()
    assert user["full_name"] == data["full_name"]


def test_read_user_by_id_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], normal_user: Dict[str, str]
) -> None:
    """
    Test that a superuser can read any user by ID.
    """
    response = client.get(f"/api/v1/users/{normal_user['id']}", headers=superuser_token_headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == normal_user["email"]


def test_update_user_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], normal_user: Dict[str, str]
) -> None:
    """
    Test that a superuser can update any user.
    """
    data = {"full_name": "Super Updated"}
    response = client.put(
        f"/api/v1/users/{normal_user['id']}", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    user = response.json()
    assert user["full_name"] == data["full_name"]


def test_delete_user_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test that a superuser can delete a user.
    """
    # Create a user to delete
    user_in = UserCreate(
        email="to_delete@example.com",
        password="password",
        full_name="User to Delete",
    )
    user = user_service.create_user(db, user_in=user_in)
    
    response = client.delete(f"/api/v1/users/{user.id}", headers=superuser_token_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    
    # Check that the user is really deleted
    response = client.get(f"/api/v1/users/{user.id}", headers=superuser_token_headers)
    assert response.status_code == 404  # Not found 