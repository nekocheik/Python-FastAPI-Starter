from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.services import item as item_service
from app.schemas.item import ItemCreate


def test_create_item(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test creating an item.
    """
    data = {"title": "Test Item", "description": "This is a test item"}
    response = client.post("/api/v1/items/", headers=normal_user_token_headers, json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content
    assert "created_at" in content
    return content


def test_read_item(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test reading an item.
    """
    # First create an item
    item = test_create_item(client, normal_user_token_headers)
    
    # Now try to read it
    response = client.get(f"/api/v1/items/{item['id']}", headers=normal_user_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item["title"]
    assert content["id"] == item["id"]


def test_read_items(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test reading all items.
    """
    # Create an item first
    item = test_create_item(client, normal_user_token_headers)
    
    # Now get all items
    response = client.get("/api/v1/items/", headers=normal_user_token_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    # Check that our created item is in the list
    found = False
    for i in items:
        if i["id"] == item["id"]:
            found = True
            break
    assert found


def test_update_item(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test updating an item.
    """
    # First create an item
    item = test_create_item(client, normal_user_token_headers)
    
    # Update it
    update_data = {"title": "Updated Item", "description": "This is an updated item"}
    response = client.put(
        f"/api/v1/items/{item['id']}", headers=normal_user_token_headers, json=update_data
    )
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["title"] == update_data["title"]
    assert updated_item["description"] == update_data["description"]
    assert updated_item["id"] == item["id"]


def test_delete_item(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test deleting an item.
    """
    # First create an item
    item = test_create_item(client, normal_user_token_headers)
    
    # Delete it
    response = client.delete(f"/api/v1/items/{item['id']}", headers=normal_user_token_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    
    # Check it's really gone
    response = client.get(f"/api/v1/items/{item['id']}", headers=normal_user_token_headers)
    assert response.status_code == 404


def test_read_other_user_item(
    client: TestClient, 
    normal_user_token_headers: Dict[str, str],
    superuser_token_headers: Dict[str, str]
) -> None:
    """
    Test that a normal user cannot read another user's item.
    """
    # Create an item as normal user
    item = test_create_item(client, normal_user_token_headers)
    
    # Create another item as superuser
    data = {"title": "Superuser Item", "description": "This is a superuser item"}
    response = client.post("/api/v1/items/", headers=superuser_token_headers, json=data)
    superuser_item = response.json()
    
    # Normal user should not be able to read superuser's item
    response = client.get(f"/api/v1/items/{superuser_item['id']}", headers=normal_user_token_headers)
    assert response.status_code == 403  # Forbidden 