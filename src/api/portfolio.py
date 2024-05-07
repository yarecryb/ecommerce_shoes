from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
    dependencies=[Depends(auth.get_api_key)],
)

class ItemListing(BaseModel):
    username: str
    title: str
    brand: str
    size: int
    price: int
    auth_token: str

class Item(BaseModel):
    username: str
    auth_token: str
    portfolio_id: int

@router.post("/add_item")
def add_item(items: list[ItemListing]):
    catalog_id = []
    with db.engine.begin() as connection:
        for item in items:
            auth_token = connection.execute(
                sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
                {'username': item.username}
            ).fetchone()
            if str(auth_token[0]) == item.auth_token:
                portfolio_id = connection.execute(
                sqlalchemy.text(
                    "INSERT INTO catalog (username, title, brand, size, price, auth_token) VALUES (:username, :title, :brand, :size, :price, :auth_token) RETURNING id"),
                        {
                            'username': item.username,
                            'title': item.title,
                            'brand': item.brand,
                            'size': item.size,
                            'price': item.price,
                            'auth_token': item.auth_token
                        }
                    )
                catalog_id.append(portfolio_id.fetchone()[0])
                
        return {
            "List of Catalog Id's:": catalog_id
        }

@router.post("/delete_item")
def delete_item(items: list[Item]):
    with db.engine.begin() as connection:
        for item in items:
            # Check auth_token
            auth_token = connection.execute(
                sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
                {'username': item.username}
            ).fetchone()
            if not auth_token or str(auth_token[0]) != item.auth_token:
                return "Unauthorized: Invalid auth_token for user {item.username}"
            
            # Delete the item if auth_token is valid
            connection.execute(
                sqlalchemy.text("DELETE FROM catalog WHERE id = :item_id AND username = :username"),
                {'item_id': item.portfolio_id, 'username': item.username}
            )
    return {"message": "Items deleted successfully"}



if __name__ == "__main__":
    print(add_item())