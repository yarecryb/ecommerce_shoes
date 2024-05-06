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

@router.post("/create_users")
def create_user(new_users: list[User]):
    """Create new users only if their usernames don't already exist."""

    print(new_users)
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
                {
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'full_name': user.full_name
                }
            )
        return "User(s) created!"

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

router = APIRouter()

class LoginCredentials(BaseModel):
    username: str
    password: str

@router.post("/users/login")
def login_user(credentials: LoginCredentials):
    """Authenticate users by checking their username and password."""
    username = credentials.username
    password = credentials.password

    with db.engine.begin() as connection:
        # Execute SQL to get the password associated with the username
        result = connection.execute(
            text("SELECT password FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()
        # Check if result is not None and passwords match
        if result and result[0] == password:
            return {"message": "Login successful!"}
        else:
            # If no result or passwords do not match, return error
            raise HTTPException(status_code=401, detail="Invalid username or password.")

# Example usage of router would be to include it in your FastAPI application setup
