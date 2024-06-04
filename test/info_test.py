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
    "price": 110,
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

def wallet_withdraw(details):
    return client.post("/wallet/withdraw",
        headers=api_header,
        json=details)

def wallet_deposit(details):
    return client.post("/wallet/deposit",
        headers=api_header,
        json=details)

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

def delete_items(items):
    return client.post("/portfolio/delete_item",
        headers=api_header,
        json=items)

def test_create_user_missing_fields():
    incomplete_user = {
        "full_name": "Incomplete User",
        "username": "incomplete"
    }

def test_create_user_invalid_email():
    user_with_invalid_email = {
        "full_name": "Invalid Email User",
        "username": "invalidemail",
        "email": "not-an-email",
        "password": "password123"
    }

# def test_add_item_invalid_price():
#     create_user(example_user)
#     login_response = login_user({"username": example_user['username'], "password": example_user['password']})
#     access_token = login_response.json()["access_token"]
#     invalid_price_item = {
#         "title": "Invalid Price Item",
#         "brand": "BrandX",
#         "size": 10,
#         "price": "not-a-price",  
#         "quantity": 5
#     }