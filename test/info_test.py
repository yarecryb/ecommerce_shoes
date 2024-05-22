from fastapi.testclient import TestClient
import sys
import os
import pytest
import sqlalchemy
from src import database as db

sys.path.append("..")

from src.api.server import app

client = TestClient(app)

api_header = {
    "access_token": os.environ.get("API_KEY")
}

example_user = {
    "full_name": "John Doe",
    "username" : "john",
    "email" : "john@calpoly.edu",
    "password" : "123"
}

new_user = {
    "full_name": "Mark Doe",
    "username" : "mark",
    "email" : "mark@calpoly.edu",
    "password" : "thisis a new password"
}

example_user_login = {
    "username" : "john",
    "password" : "123"
}

def create_user(user):
    return client.post("/users/create_users", 
        headers=api_header,
        json=[user])

def login_user(user_info):
    return client.post("/users/login", 
        headers=api_header,
        json=user_info)