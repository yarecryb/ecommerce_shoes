from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import bcrypt

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
                sqlalchemy.text("""
                    SELECT username, email
                    FROM users 
                    WHERE username = :username OR email = :email
                """),
                {'username': user.username, 'email': user.email}
            ).fetchone()
            if result:
                if result.username == user.username:
                    return {"error": f"The username '{user.username}' is already taken, please choose a different one."}
                else:
                    return {"error": f"The email '{user.email}' is already taken, please choose a different one."}
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # If username does not exist, insert new user
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO users (username, email, password, full_name) 
                    VALUES (:username, :email, :password, :full_name)
                """),
                [{
                    'username': user.username,
                    'email': user.email,
                    'password': hashed_password,
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
            sqlalchemy.text("""
                SELECT password
                FROM users 
                WHERE username = :username
            """),
            {'username': username}
        ).fetchone()
        # Check if result is not None and passwords match
        if result and bcrypt.hashpw(password.encode('utf-8'), result.password.encode('utf-8')):
            token = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token
                FROM users
                WHERE username = :username
            """),
            {'username': username}
            ).fetchone()
            print(token.auth_token)
            return {"message": "Login successful!", "auth_token": token.auth_token}
        else:
            return {"message": "Invalid username or password."}

@router.post("/update_username")
def update_username(usernameRequest: UsernameUpdateRequest):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                SELECT password, auth_token
                FROM users
                WHERE username = :username
            """),
            {'username': usernameRequest.current_username}
        ).fetchone()

        # auth_token is type uuid so needs cast to string
        if result and result.password == usernameRequest.password and str(result.auth_token) == usernameRequest.auth_token:
            usersUpdate = sqlalchemy.text("""
                UPDATE users 
                SET username = :new_username 
                WHERE username = :current_username
            """)
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
        result = connection.execute(
            sqlalchemy.text("""
                SELECT password, auth_token
                FROM users
                WHERE username = :username
            """),
            {'username': passwordRequest.username}
        ).fetchone()

        # auth_token is type uuid so needs cast to string
        if result and result.password == passwordRequest.current_password and str(result.auth_token) == passwordRequest.auth_token:
            usersUpdate = sqlalchemy.text("""
                UPDATE users 
                SET password = :new_password 
                WHERE username = :username
            """)
            # Execute the update
            connection.execute(usersUpdate, {
                'new_password': passwordRequest.new_password, 
                'username': passwordRequest.username
            })
            return "Password changed!"
        else:
            return "Invalid username or password."

