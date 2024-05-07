from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class User(BaseModel):
    full_name: str
    username: str

    email: str
    password: str


class LoginCredentials(BaseModel):
    username: str
    password: str

class UsernameUpdateRequest(BaseModel):
    current_username: str
    new_username: str
    password: str
    auth_token: str

class PasswordUpdateRequest(BaseModel):
    username: str
    current_password: str
    new_password: str
    auth_token: str


@router.post("/create_users")
def create_user(new_users: list[User]):
    """Create new users only if their usernames don't already exist."""

    with db.engine.begin() as connection:
        for user in new_users:
            # Check if the username already exists
            result = connection.execute(
                sqlalchemy.text("SELECT * FROM users WHERE username = :username"),
                {'username': user.username}
            ).fetchone()
            if result:
                return {"error": f"The username '{user.username}' is already taken, please choose a different one."}
            
            # If username does not exist, insert new user
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO users (username, email, password, full_name) VALUES (:username, :email, :password, :full_name)"
                ),
                [{
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'full_name': user.full_name
                }]
            )
    return "User(s) created!"

@router.post("/login")
def login_user(credentials: LoginCredentials):
    """Authenticate users by checking their username and password."""
    username = credentials.username
    password = credentials.password

    with db.engine.begin() as connection:
        # Execute SQL to get the password associated with the username
        result = connection.execute(
            sqlalchemy.text("SELECT password FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()
        # Check if result is not None and passwords match
        if result and result[0] == password:
            auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()
            print(auth_token[0])
            return {"message": "Login successful!","Authentication Token": auth_token[0]}
        else:
            return {"message": "Invalid username or password."}

# Example usage of router would be to include it in your FastAPI application setup

@router.post("/update_username")
def update_username(usernameRequest: UsernameUpdateRequest):
    with db.engine.begin() as connection:
        password = connection.execute(
            sqlalchemy.text("SELECT password FROM users WHERE username = :username"),
            {'username': usernameRequest.current_username}
        ).fetchone()
        if password and password[0] == usernameRequest.password:
            usersUpdate = sqlalchemy.text(
                "UPDATE users SET username = :new_username WHERE username = :current_username"
            )
            # Execute the update
            connection.execute(usersUpdate, {
                'new_username': usernameRequest.new_username, 
                'current_username': usernameRequest.current_username
            })

            usersUpdate = sqlalchemy.text(
                "UPDATE catalog SET username = :new_username WHERE username = :current_username"
            )
            # Execute the update
            connection.execute(usersUpdate, {
                'new_username': usernameRequest.new_username, 
                'current_username': usernameRequest.current_username
            })
            return "Username changed!"
        else:
            return "Invalid username or password."

@router.post("/update_password")
def update_password(passwordRequest: PasswordUpdateRequest):
    with db.engine.begin() as connection:
        password = connection.execute(
            sqlalchemy.text("SELECT password FROM users WHERE username = :username"),
            {'username': passwordRequest.username}
        ).fetchone()
        auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
            {'username': passwordRequest.username}
        ).fetchone()
        if password and password[0] == passwordRequest.current_password and auth_token and str(auth_token[0]) == passwordRequest.auth_token:
            usersUpdate = sqlalchemy.text(
                "UPDATE users SET password = :new_password WHERE username = :current_username"
            )
            # Execute the update
            connection.execute(usersUpdate, {
                'new_password': passwordRequest.new_password, 
                'current_username': passwordRequest.username
            })

            return "Password changed!"
        else:
            return "Invalid username or password."

