from .info_test import *

@pytest.fixture
def cleanup_db():
    yield
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                DELETE FROM users WHERE username IN (:username_original, :username_new)
            """),
            {'username_original': example_user["username"], 'username_new': new_user["username"]}
        )

def test_wallet_deposit(cleanup_db):
    response = create_user(example_user)
    assert response.status_code == 200
    assert response.json()["message"] == "User(s) created!"

    response = login_user(example_user_login)
    assert response.status_code == 200

    response_data = response.json()
    assert "auth_token" in response.json()
    assert "message" in response.json()
    auth_token = response_data["auth_token"]
    assert  response_data["message"] == "Login successful!"

    deposit_info = {
        "username": example_user["username"],
        "auth_token": auth_token,
        "amount": 10
    }
    
    response = wallet_deposit(deposit_info)
    response_data = response.json()
    assert response.status_code == 200
    assert  response_data["message"] == "Deposit successful!"

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                SELECT wallet FROM users WHERE username = :username
            """),
            {'username': example_user["username"]}
        ).fetchone()

        assert result.wallet == 10

    withdraw_info = {
        "username": example_user["username"],
        "auth_token": auth_token,
        "amount": 10
    }

    response = wallet_withdraw(withdraw_info)
    response_data = response.json()
    assert response.status_code == 200
    assert  response_data["message"] == "Withdrawal successful!"

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                SELECT wallet FROM users WHERE username = :username
            """),
            {'username': example_user["username"]}
        ).fetchone()

        assert result.wallet == 0
