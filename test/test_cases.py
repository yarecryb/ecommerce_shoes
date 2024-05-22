from fastapi.testclient import TestClient
import sys
sys.path.append("..")

from src.api.server import app

client = TestClient(app)


def test_create_user():
    response = client.post("/users/create_users/")
    assert response.status_code == 200

def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200

def test_update_user():
    response = client.put("/users/1", json={"name": "John Doe"})
    assert response.status_code == 200

def test_delete_user():
    response = client.delete("/users/1")
    assert response.status_code == 200

def test_create_listing():
    response = client.post("/listings/create_listing/", json={"name": "Shoes", "price": 50.99})
    assert response.status_code == 200

def test_get_listing():
    response = client.get("/listings/1")
    assert response.status_code == 200

def test_update_listing():
    response = client.put("/listings/1", json={"name": "Updated Shoes", "price": 59.99})
    assert response.status_code == 200

def test_delete_listing():
    response = client.delete("/listings/1")
    assert response.status_code == 200
    
# # def test_create_user():
# #     response = client.post("/users/create_users/")
# #     assert 