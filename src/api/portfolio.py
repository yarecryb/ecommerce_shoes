from fastapi import APIRouter, Depends, HTTPException
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
class UserDetails(BaseModel):
    username: str
    auth_token: str


class ItemDetail(BaseModel):
    title: str
    brand: str
    size: float
    price: str
    quantity: int

class ItemDetailWithID(ItemDetail):
    id: int

class ItemListing(UserDetails):
    items: list[ItemDetail]

class ItemIDs(UserDetails):
    items: list[int]


@router.post("/add_item")
def add_item(data: ItemListing):
    catalog_id = []
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()

        # Check if user auth_token is valid before inserting items
        if user_info and str(user_info.auth_token) == data.auth_token:
            for item in data.items:
                portfolio_id = connection.execute(
                    sqlalchemy.text("""
                        INSERT INTO catalog (user_id, title, brand, size, price, quantity)
                        VALUES (:user_id, :title, :brand, :size, :price, :quantity) 
                        RETURNING id
                    """),
                        {
                            'user_id': user_info.id,
                            'title': item.title,
                            'brand': item.brand,
                            'size': item.size,
                            'price': item.price,
                            'quantity': item.quantity
                        }
                )
                catalog_id.append(portfolio_id.fetchone().id)
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")
        
    return {
        "List of Catalog Id's:": catalog_id
    }

# returns all listings that belong to the user logged in
@router.post("/list_items")
def list_items(user: UserDetails):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': user.username}
        ).fetchone()

        if user_info and str(user_info.auth_token) == user.auth_token:
            items = connection.execute(
                sqlalchemy.text("""
                    SELECT *
                    FROM catalog
                    WHERE user_id = :user_id
                """),
                {'user_id': user_info.id}
            ).fetchall()
            item_list = [
                ItemDetailWithID(
                    id=item.id,
                    title=item.title,
                    brand=item.brand,
                    size=item.size,
                    price=item.price,
                    quantity=item.quantity
                )
                for item in items
            ]

            return item_list
    raise HTTPException(status_code=401, detail="Invalid auth")


@router.post("/delete_item")
def delete_item(data: ItemIDs):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()
        if user_info and str(user_info.auth_token) == data.auth_token:
            for item in data.items:
                # Delete the item if auth_token is valid
                connection.execute(
                    sqlalchemy.text("""
                        DELETE FROM catalog 
                        WHERE id = :item_id AND user_id = :user_id
                    """),
                    {'item_id': item, 'user_id': user_info.id}
                )
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")
        
    return {"message": "Items deleted successfully"}



if __name__ == "__main__":
    print(add_item())