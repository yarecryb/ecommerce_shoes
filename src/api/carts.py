from fastapi import APIRouter, Depends, Request, HTTPException
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

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


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
def set_cart_item(cart_id: int, cart_item: CartItem):
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
            itemUpdate = sqlalchemy.text("""
                UPDATE carts SET catalog_id = :catalog_id
                WHERE cart_id = :cart_id
            """)
            # Execute the update
            connection.execute(itemUpdate, {
                'catalog_id': cart_item.catalog_id,
                'cart_id': cart_id
            })

            return "OK"
        else:
            return {"message": "Invalid username or auth token!"}

@router.post("/checkout/")
def checkout(data: CheckoutCart):
    """ """
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()
        

        if user_info and str(user_info.auth_token) == data.auth_token:
            
            cart_update = connection.execute(
                sqlalchemy.text("""
                    UPDATE carts SET bought = :bought 
                    WHERE cart_id = :cart_id
                    RETURNING user_id, catalog_id
                """), 
                {
                    'bought': True,
                    'cart_id': data.cart_id
                }
            ).fetchone()


            shoe_info = connection.execute(
                sqlalchemy.text("""
                    UPDATE catalog SET quantity = quantity - 1
                    WHERE id = :id
                    RETURNING *
                """), 
                { 'id': cart_update.catalog_id}
            ).fetchone()
            sold_info = connection.execute(
                sqlalchemy.text("""
                    UPDATE catalog SET sold = quantity + sold
                    WHERE id = :id
                    RETURNING *
                """), 
                { 'id': cart_update.catalog_id}
            ).fetchone()

            #Take money from buyer
            buyer_update = connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet - :price
                    WHERE id = :id
                """), 
                {
                    'id': user_info.id,
                    'price': shoe_info.price
                })

            seller_update = connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet + :price
                    WHERE id = :id
                """), {
                    'id': shoe_info.user_id,
                    'price': shoe_info.price
                })
            print(shoe_info.user_id)
            return cart_update.catalog_id

