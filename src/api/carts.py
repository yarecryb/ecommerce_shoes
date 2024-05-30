from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    dependencies=[Depends(auth.get_api_key)],
)

class Auth(BaseModel):
    username: str
    auth_token: str

class CartItem(Auth):
    catalog_id: int

class CheckoutCart(Auth):
    cart_id: int

@router.post("/")
def create_cart(data: Auth):
    """ Create a new cart for a user if authentication succeeds. """
    with db.engine.begin() as connection:
        # Get the authentication token from the users table
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()
        if user_info and str(user_info.auth_token) == data.auth_token:
            # Compare the fetched token with the provided one in the request
            if str(user_info.auth_token) == data.auth_token:
                # Insert a new cart entry into the carts table
                cart_result = connection.execute(
                    sqlalchemy.text("""
                        INSERT INTO carts (user_id, bought)
                        VALUES (:user_id, :bought) 
                        RETURNING cart_id
                    """),
                    {
                        'user_id': user_info.id,
                        'bought': False  # Use Python's boolean False instead of string "False"
                    }
                ).fetchone()  # Fetch the result of the query which includes the cart_id

                # Print the cart_id from the result
                return {"Cart ID": str(cart_result.cart_id)}
            else:
                return {"message": "Invalid username or auth token!"}
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")


#TODO : update to one to many, add multiple items to cart
@router.post("/{cart_id}/add_item")
def set_cart_item(cart_id: int, cart_item: CartItem, quantity: int):
    """ """
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': cart_item.username}
        ).fetchone()

        if user_info and str(user_info.auth_token) == cart_item.auth_token:
            connection.execute(sqlalchemy.text("""
                INSERT INTO cart_items (catalog_id, cart_id, quantity) 
                                         VALUES (:catalog_id, :cart_id, :quantity)
            """),
            [{"catalog_id": cart_item.catalog_id,"cart_id": cart_id, "quantity": quantity  }])

            return "OK"
        else:
            return {"message": "Invalid username or auth token!"}

@router.post("/checkout/")
def checkout(data: CheckoutCart):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()
        
        if not user_info or str(user_info.auth_token) != data.auth_token:
            raise HTTPException(status_code=400, detail="Invalid user credentials")
        
        items = connection.execute(
            sqlalchemy.text("""
                SELECT catalog_id, quantity
                FROM cart_items
                WHERE cart_id = :cart_id
            """),
            {'cart_id': data.cart_id}
        ).fetchall()

        for item in items:
            stock = connection.execute(
                sqlalchemy.text("""
                    SELECT quantity
                    FROM catalog
                    WHERE id = :catalog_id
                """),
                {'catalog_id': item.catalog_id}
            ).scalar()

            if stock < item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock for item {}".format(item.catalog_id))

            shoe_info = connection.execute(
                sqlalchemy.text("""
                    UPDATE catalog SET quantity = quantity - :quantity
                    WHERE id = :id
                    RETURNING id, user_id, price
                """), 
                {'id': item.catalog_id, 'quantity': item.quantity}
            ).fetchone()

            # Take money from buyer
            connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet - :price
                    WHERE id = :id
                """), 
                {'id': user_info.id, 'price': shoe_info.price * item.quantity}
            )

            # Add money to seller
            connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet + :price
                    WHERE id = :id
                """), 
                {'id': shoe_info.user_id, 'price': shoe_info.price * item.quantity}
            )

        cart_update = connection.execute(
            sqlalchemy.text("""
                UPDATE carts SET bought = :bought 
                WHERE cart_id = :cart_id
                RETURNING cart_id, user_id
            """), 
            {'bought': True, 'cart_id': data.cart_id}
        ).fetchone()

        return {"message": "Checkout successful", "cart_id": cart_update.cart_id}