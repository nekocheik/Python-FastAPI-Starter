import os
import pytest
from typing import Dict, Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


# SQLite URL for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)  # Create the tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Create a FastAPI TestClient with DB overrides for testing.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def normal_user(db) -> Dict[str, str]:
    """
    Create a normal user for testing.
    """
    user_in = UserCreate(
        email="user@example.com",
        password="password",
        full_name="Test User",
    )
    user = create_user(db, user_in=user_in)
    return {"id": user.id, "email": user.email}


@pytest.fixture(scope="function")
def superuser(db) -> Dict[str, str]:
    """
    Create a superuser for testing.
    """
    user_in = UserCreate(
        email="admin@example.com",
        password="password",
        full_name="Super User",
        is_superuser=True,
    )
    user = create_user(db, user_in=user_in)
    return {"id": user.id, "email": user.email}


@pytest.fixture(scope="function")
def normal_user_token_headers(client, normal_user) -> Dict[str, str]:
    """
    Get token headers for normal user.
    """
    login_data = {
        "username": normal_user["email"],
        "password": "password",
    }
    r = client.post("/api/v1/auth/login", data=login_data)
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
def superuser_token_headers(client, superuser) -> Dict[str, str]:
    """
    Get token headers for superuser.
    """
    login_data = {
        "username": superuser["email"],
        "password": "password",
    }
    r = client.post("/api/v1/auth/login", data=login_data)
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"} 