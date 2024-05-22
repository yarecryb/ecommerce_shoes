from .info_test import *
import pytest

@pytest.fixture
def cleanup_user():
    yield
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                DELETE FROM users WHERE username IN (:username_original, :username_new)
            """),
            {'username_original': example_user["username"], 'username_new': new_user["username"]}
        )

def test_read_listings():
    response = client.get("/listings/")
    assert response.status_code == 200

def test_create_login_user(cleanup_user):
    response = create_user(example_user)
    assert response.status_code == 200
    assert response.json() == "User(s) created!"

    response = login_user(example_user_login)
    assert response.status_code == 200

    response_data = response.json()
    assert "auth_token" in response.json()
    assert "message" in response.json()
    assert  response_data["message"] == "Login successful!"

def test_change_username_password(cleanup_user):
    create_user(example_user)
    response = login_user(example_user_login)
    response_data = response.json()
    auth_token = response_data["auth_token"]

    new_user_info = {
        "current_username": example_user["username"],
        "new_username": new_user["username"],
        "password": example_user["password"],
        "auth_token": auth_token
    }

    update_response = client.post("/users/update_username",
        headers=api_header,
        json=new_user_info)
    
    assert update_response.status_code == 200
    update_response_data = update_response.json()
    assert  update_response_data == "Username changed!"

    new_password_info = {
        "username": new_user["username"],
        "current_password": example_user["password"],
        "new_password": new_user["password"],
        "auth_token": auth_token
    }

    update_password_response = client.post("/users/update_password",
        headers=api_header,
        json=new_password_info)
    
    assert update_password_response.status_code == 200
    update_password_response_data = update_password_response.json()
    assert  update_password_response_data == "Password changed!"

    new_user_login = {
        "username": new_user["username"],
        "password": new_user["password"]
    }

    response = login_user(new_user_login)
    assert response.status_code == 200
    response_data = response.json()
    assert "auth_token" in response.json()
    assert "message" in response.json()
    assert  response_data["message"] == "Login successful!"