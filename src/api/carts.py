from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
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

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
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

            return {"cart_id": str(cart_result.cart_id)}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or auth token!")

@router.post("/{cart_id}/view_cart", response_model=dict, status_code=status.HTTP_200_OK)
def view_cart(cart_id: int, data: Auth):
    with db.engine.begin() as connection:
        # Verify user credentials and cart ownership
        user_cart_info = connection.execute(
            sqlalchemy.text("""
                SELECT users.auth_token, carts.cart_id
                FROM users
                JOIN carts ON users.id = carts.user_id
                WHERE users.username = :username AND carts.cart_id = :cart_id
            """),
            {'username': data.username, 'cart_id': cart_id}
        ).fetchone()

        if not user_cart_info or str(user_cart_info.auth_token) != data.auth_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or auth token")

        # Fetch cart items
        cart_items = connection.execute(
            sqlalchemy.text("""
                SELECT catalog.brand, catalog.title, catalog.size, cart_items.quantity
                FROM cart_items
                JOIN catalog ON cart_items.catalog_id = catalog.id
                WHERE cart_items.cart_id = :cart_id
            """),
            {'cart_id': cart_id}
        ).fetchall()

        if not cart_items:
            return {"message": "Cart is empty"}

        # Construct the response
        items = [{
            "brand": item.brand,
            "title": item.title,
            "size": item.size,
            "quantity": item.quantity
        } for item in cart_items]

        return {"items": items}
        

@router.post("/{cart_id}/add_item", response_model=dict, status_code=status.HTTP_200_OK)
def set_cart_item(cart_id: int, cart_item: CartItem = Body(...)):
    if cart_item.quantity < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be at least 1")

    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, users.id, wallet, cart_id
                FROM users 
                JOIN carts ON users.id = carts.user_id
                WHERE username = :username
                FOR UPDATE
            """),
            {'username': cart_item.username}
        ).fetchone()

        if user_info and str(user_info.auth_token) == cart_item.auth_token and cart_id == user_info.cart_id:
            catalog_item = connection.execute(
                sqlalchemy.text("""
                SELECT price, SUM(quantity) AS quantity
                    FROM catalog
                    JOIN catalog_ledger ON catalog.id = catalog_id
                    WHERE catalog.id = :catalog_id
                    GROUP BY catalog.id, price
                """),
                {'catalog_id': cart_item.catalog_id}
            ).fetchone()

            if catalog_item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No catalog item found with ID {cart_item.catalog_id}")

            if catalog_item.quantity < cart_item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for item {cart_item.catalog_id}")

            cart_items = connection.execute(
                sqlalchemy.text("""
                    SELECT quantity
                    FROM cart_items
                    WHERE cart_id = :cart_id AND catalog_id = :catalog_id
                    FOR UPDATE
                """),
                {'cart_id': cart_id, 'catalog_id': cart_item.catalog_id}
            ).fetchall()

            cart_item_quantity = sum(item.quantity for item in cart_items)

            total_quantity = cart_item_quantity + cart_item.quantity

            if total_quantity > catalog_item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Total quantity for item {cart_item.catalog_id} exceeds available stock")

            # Calculate the total cost of items in the cart
            total_cost_in_cart = connection.execute(
                sqlalchemy.text("""
                    SELECT SUM(ci.quantity * c.price)
                    FROM cart_items ci
                    JOIN catalog c ON ci.catalog_id = c.id
                    WHERE ci.cart_id = :cart_id
                """),
                {'cart_id': cart_id}
            ).scalar() or 0

            # Calculate the cost of the new item
            new_item_cost = catalog_item.price * cart_item.quantity

            # Check if the user has enough balance in their wallet
            if total_cost_in_cart + new_item_cost > user_info.wallet:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough balance in the wallet")

            connection.execute(sqlalchemy.text("""
                INSERT INTO cart_items (catalog_id, cart_id, quantity) 
                VALUES (:catalog_id, :cart_id, :quantity)
            """),
            {"catalog_id": cart_item.catalog_id, "cart_id": cart_id, "quantity": cart_item.quantity })

            return {"message": "Item added successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or auth token")

@router.post("/checkout/", response_model=dict, status_code=status.HTTP_200_OK)
def checkout(data: CheckoutCart):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id, wallet
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()

        if not user_info or str(user_info.auth_token) != data.auth_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user credentials")

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
                    SELECT price, SUM(quantity) AS quantity
                    FROM catalog
                    JOIN catalog_ledger ON catalog.id = catalog_id
                    WHERE catalog.id = :catalog_id
                    GROUP BY price, catalog_id
                """),
                {'catalog_id': item.catalog_id}
            ).fetchone()

            if shoe_info.quantity < item.total_quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for item {item.catalog_id}")

            total_cost += shoe_info.price * item.total_quantity

        if user_info.wallet < total_cost:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance. Please refill your wallet.")

        for item in items:
            # Update catalog quantities
            connection.execute(
                sqlalchemy.text("""                                    
                    INSERT INTO catalog_ledger (catalog_id, customer_id, quantity)
                    VALUES (:id, :customer_id, :quantity)
                """), 
                {'id': item.catalog_id, 'customer_id': user_info.id, 'quantity': -1 * item.total_quantity}
            )

            shoe_info = connection.execute(
                sqlalchemy.text("""
                    SELECT price, user_id
                    FROM catalog
                    WHERE id = :catalog_id
                """), 
                {'catalog_id': item.catalog_id}
            ).fetchone()

            # Deduct from buyer's wallet
            connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet - :price
                    WHERE id = :id
                """), 
                {'id': user_info.id, 'price': shoe_info.price * item.total_quantity}
            )

            # Add to seller's wallet
            connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet + :price
                    WHERE id = :id
                """), 
                {'id': shoe_info.user_id, 'price': shoe_info.price * item.total_quantity}
            )

            # Mark the cart as bought
            connection.execute(
                sqlalchemy.text("""
                    UPDATE carts SET bought = :bought 
                    WHERE cart_id = :cart_id
                """), 
                {'bought': True, 'cart_id': data.cart_id}
            )

        return {"message": "Checkout successful"}
