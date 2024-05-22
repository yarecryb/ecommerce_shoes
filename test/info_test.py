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

example_item = {
    "title": "Panda Dunks",
    "brand": "Nike",
    "size": 14,
    "price": "110",
    "quantity": 1
}

multiple_example_items = [
    example_item,
    {
        "title": "Superstar something",
        "brand": "Adidas",
        "size": 600,
        "price": "50",
        "quantity": 20000
    },
    {
        "title": "Another type of shoe",
        "brand": "something",
        "size": 6,
        "price": "30",
        "quantity": 5
    },
    {
        "title": "More types of shoes",
        "brand": "something",
        "size": 6,
        "price": "30",
        "quantity": 5
    }
]

def create_user(user):
    return client.post("/users/create_users", 
        headers=api_header,
        json=[user])

def login_user(user_info):
    return client.post("/users/login", 
        headers=api_header,
        json=user_info)

def add_item(item):
    return client.post("/portfolio/add_item",
        headers=api_header,
        json=item)

def list_items(user_info):
    return client.post("/portfolio/list_items",
        headers=api_header,
        json=user_info)