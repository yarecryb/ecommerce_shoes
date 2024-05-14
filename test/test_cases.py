from fastapi.testclient import TestClient
import sys
sys.path.append("..")

from src.api.server import app

client = TestClient(app)


def test_read_listings():
    response = client.get("/listings/")
    assert response.status_code == 200
    
# def test_create_user():
#     response = client.post("/users/create_users/")
#     assert 