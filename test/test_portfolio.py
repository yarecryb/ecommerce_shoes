from .info_test import *

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
    #Add item
    item_reponse = add_item(item_info)
    assert item_reponse.status_code == 200
    item_response_data = item_reponse.json()
    added_item_id = item_response_data["List of Catalog Id's:"][0]

    example_item_with_id = example_item.copy()
    example_item_with_id["id"] = added_item_id

    #List item 
    user_items = list_items(auth)
    assert user_items.status_code == 200

    user_items_data = user_items.json()
    assert len(user_items_data) > 0 

    assert example_item_with_id == user_items_data[0]

# test adding multiple items
def test_add_multiple_item(cleanup_db):
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
        "items": multiple_example_items
    }
    #Add items
    item_reponse = add_item(item_info)
    assert item_reponse.status_code == 200
    item_response_data = item_reponse.json()
    added_item_ids = item_response_data["List of Catalog Id's:"]

    example_items_with_ids = []
    for i, item in enumerate(multiple_example_items):
        item_with_id = item.copy()
        item_with_id["id"] = added_item_ids[i]
        example_items_with_ids.append(item_with_id)

    # List items
    user_items_response = list_items(auth)
    assert user_items_response.status_code == 200

    user_items_data = user_items_response.json()
    assert len(user_items_data) > 0

    # Compare the items with IDs with the response items
    for expected_item, actual_item in zip(example_items_with_ids, user_items_data):
        assert expected_item == actual_item

