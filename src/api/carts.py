from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import logging

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
    quantity: int

class CheckoutCart(Auth):
    cart_id: int

@router.post("/")
def create_cart(data: Auth):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()
        if user_info and str(user_info.auth_token) == data.auth_token:
            cart_result = connection.execute(
                sqlalchemy.text("""
                    INSERT INTO carts (user_id, bought)
                    VALUES (:user_id, :bought) 
                    RETURNING cart_id
                """),
                {
                    'user_id': user_info.id,
                    'bought': False
                }
            ).fetchone()

            return {"Cart ID": str(cart_result.cart_id)}
        else:
            return {"message": "Invalid username or auth token!"}

@router.post("/{cart_id}/add_item")
def set_cart_item(cart_id: int, cart_item: CartItem = Body(...)):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': cart_item.username}
        ).fetchone()

        if user_info and str(user_info.auth_token) == cart_item.auth_token:
            catalog_quantity = connection.execute(
                sqlalchemy.text("""
                    SELECT quantity
                    FROM catalog
                    WHERE id = :catalog_id
                """),
                {'catalog_id': cart_item.catalog_id}
            ).scalar()

            if catalog_quantity is None or catalog_quantity < cart_item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock for item {}".format(cart_item.catalog_id))

            cart_item_quantity = connection.execute(
                sqlalchemy.text("""
                    SELECT SUM(quantity)
                    FROM cart_items
                    WHERE cart_id = :cart_id AND catalog_id = :catalog_id
                """),
                {'cart_id': cart_id, 'catalog_id': cart_item.catalog_id}
            ).scalar() or 0

            total_quantity = cart_item_quantity + cart_item.quantity

            if total_quantity > catalog_quantity:
                raise HTTPException(status_code=400, detail="Total quantity for item {} exceeds available stock".format(cart_item.catalog_id))

            connection.execute(sqlalchemy.text("""
                INSERT INTO cart_items (catalog_id, cart_id, quantity) 
                                         VALUES (:catalog_id, :cart_id, :quantity)
            """),
            {"catalog_id": cart_item.catalog_id, "cart_id": cart_id, "quantity": cart_item.quantity })

            return {"message": "Item added successfully"}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or auth token")

@router.post("/checkout/")
def checkout(data: CheckoutCart):
    try:
        with db.engine.begin() as connection:
            user_info = connection.execute(
                sqlalchemy.text("""
                    SELECT auth_token, id, wallet
                    FROM users WHERE username = :username
                """),
                {'username': data.username}
            ).fetchone()
            
            if not user_info or str(user_info.auth_token) != data.auth_token:
                raise HTTPException(status_code=400, detail="Invalid user credentials")
            
            items = connection.execute(
                sqlalchemy.text("""
                    SELECT catalog_id, SUM(quantity) as total_quantity
                    FROM cart_items
                    WHERE cart_id = :cart_id
                    GROUP BY catalog_id
                """),
                {'cart_id': data.cart_id}
            ).fetchall()

            total_cost = 0

            for item in items:
                shoe_info = connection.execute(
                    sqlalchemy.text("""
                        SELECT price, quantity
                        FROM catalog
                        WHERE id = :catalog_id
                    """),
                    {'catalog_id': item.catalog_id}
                ).fetchone()

                if shoe_info.quantity < item.total_quantity:
                    raise HTTPException(status_code=400, detail="Not enough stock for item {}".format(item.catalog_id))

                total_cost += shoe_info.price * item.total_quantity

            if user_info.wallet < total_cost:
                raise HTTPException(status_code=400, detail="Insufficient balance. Please refill your wallet.")

            for item in items:
                connection.execute(
                    sqlalchemy.text("""
                        UPDATE catalog SET quantity = quantity - :quantity
                        WHERE id = :id
                    """), 
                    {'id': item.catalog_id, 'quantity': item.total_quantity}
                )

                shoe_info = connection.execute(
                    sqlalchemy.text("""
                        SELECT price, user_id
                        FROM catalog
                        WHERE id = :catalog_id
                    """), 
                    {'catalog_id': item.catalog_id}
                ).fetchone()

                connection.execute(
                    sqlalchemy.text("""
                        UPDATE users SET wallet = wallet - :price
                        WHERE id = :id
                    """), 
                    {'id': user_info.id, 'price': shoe_info.price * item.total_quantity}
                )

                connection.execute(
                    sqlalchemy.text("""
                        UPDATE users SET wallet = wallet + :price
                        WHERE id = :id
                    """), 
                    {'id': shoe_info.user_id, 'price': shoe_info.price * item.total_quantity}
                )

            connection.execute(
                sqlalchemy.text("""
                    UPDATE carts SET bought = :bought 
                    WHERE cart_id = :cart_id
                    RETURNING cart_id, user_id
                """), 
                {'bought': True, 'cart_id': data.cart_id}
            ).fetchone()

            return {"message": "Checkout successful"}
    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"OperationalError: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")