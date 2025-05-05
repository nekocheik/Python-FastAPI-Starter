from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.services import user as user_service
from app.schemas.user import UserCreate


def test_login(client: TestClient, normal_user: Dict[str, str]) -> None:
    """
    Test that a user can login.
    """
    login_data = {
        "username": normal_user["email"],
        "password": "password",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, normal_user: Dict[str, str]) -> None:
    """
    Test that login fails with incorrect password.
    """
    login_data = {
        "username": normal_user["email"],
        "password": "wrong_password",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401  # Unauthorized


def test_login_nonexistent_user(client: TestClient) -> None:
    """
    Test that login fails with nonexistent user.
    """
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401  # Unauthorized


def test_test_token(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test that a token can be used to access a protected endpoint.
    """
    response = client.post("/api/v1/auth/test-token", headers=normal_user_token_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert "user_id" in result


def test_access_without_token(client: TestClient) -> None:
    """
    Test that access is denied without a token.
    """
    response = client.post("/api/v1/auth/test-token")
    assert response.status_code == 401  # Unauthorized
    
    
def test_access_with_invalid_token(client: TestClient) -> None:
    """
    Test that access is denied with an invalid token.
    """
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/api/v1/auth/test-token", headers=headers)
    assert response.status_code == 403  # Forbidden 