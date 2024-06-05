import pytest
import sqlalchemy
from .info_test import (
    db, example_user, example_user_login, example_item, 
    multiple_example_items, create_user, login_user, add_item, 
    list_items, delete_items
)

@pytest.fixture
def cleanup_db():
    yield
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                DELETE FROM catalog WHERE user_id IN (
                    SELECT id FROM users WHERE username = :username_original
                );
                DELETE FROM users WHERE username = :username_original;
            """),
            {
                'username_original': example_user["username"]
            }
        )

def test_add_one_item(cleanup_db):
    create_user(example_user)
    response = login_user(example_user_login)
    auth_token = response.json()["auth_token"]
    auth = {
        "username": example_user["username"],
        "auth_token": auth_token,
    }
    item_info = {
        "username": example_user["username"],
        "auth_token": auth_token,
        "items": [example_item]
    }
    
    item_response = add_item(item_info)
    assert item_response.status_code == 200
    item_response_data = item_response.json()
    added_item_id = item_response_data["List of Catalog Id's:"][0]

    example_item_with_id = example_item.copy()
    example_item_with_id["id"] = added_item_id

    user_items = list_items( auth)
    assert user_items.status_code == 200

    user_items_data = user_items.json()
    assert len(user_items_data) > 0 

    assert example_item_with_id == user_items_data[0]

# # Test adding multiple items
# def test_add_multiple_items(cleanup_db):
#     create_user(example_user)
#     response = login_user(example_user_login)
#     auth_token = response.json()["auth_token"]
#     auth = {
#         "username": example_user["username"],
#         "auth_token": auth_token,
#     }
#     item_info = {
#         "username": example_user["username"],
#         "auth_token": auth_token,
#         "items": multiple_example_items
#     }
#     # Add items
#     item_response = add_item(item_info)
#     assert item_response.status_code == 200
#     item_response_data = item_response.json()
#     added_item_ids = item_response_data["List of Catalog Id's:"]

#     example_items_with_ids = []
#     for i, item in enumerate(multiple_example_items):
#         item_with_id = item.copy()
#         item_with_id["id"] = added_item_ids[i]
#         example_items_with_ids.append(item_with_id)

#     # List items
#     user_items_response = list_items(auth)
#     assert user_items_response.status_code == 200

#     user_items_data = user_items_response.json()
#     assert len(user_items_data) > 0

#     # Compare the items with IDs with the response items
#     for expected_item, actual_item in zip(example_items_with_ids, user_items_data):
#         assert expected_item == actual_item

# def test_delete_item(cleanup_db):
#     create_user(example_user)
#     response = login_user(example_user_login)
#     auth_token = response.json()["auth_token"]
#     auth = {
#         "username": example_user["username"],
#         "auth_token": auth_token,
#     }
#     item_info = {
#         "username": example_user["username"],
#         "auth_token": auth_token,
#         "items": multiple_example_items
#     }
#     # Add items
#     item_response = add_item(item_info)
#     assert item_response.status_code == 200
#     item_response_data = item_response.json()
#     added_item_ids = item_response_data["List of Catalog Id's:"]

#     # Delete items
#     item_info["items"] = added_item_ids
#     response = delete_items(item_info)
#     assert response.status_code == 200

#     # List items, make sure response is empty
#     list_items_response = list_items(auth)
#     assert list_items_response.json() == []
