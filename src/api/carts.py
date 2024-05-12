from fastapi import APIRouter, Depends, Request
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


class Customer(BaseModel):
    username: str
    auth_token: str


@router.post("/")
def create_cart(new_cart: Customer):
    """ Create a new cart for a user if authentication succeeds. """
    with db.engine.begin() as connection:
        # Get the authentication token from the users table
        auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
            {'username': new_cart.username}
        ).fetchone()
        
        # Compare the fetched token with the provided one in the request
        if str(auth_token[0]) == new_cart.auth_token:
            # Insert a new cart entry into the carts table
            cart_result = connection.execute(
                sqlalchemy.text(
                    "INSERT INTO carts (username, bought) VALUES (:username, :bought) RETURNING cart_id"
                ),
                {
                    'username': new_cart.username,
                    'bought': False  # Use Python's boolean False instead of string "False"
                }
            ).fetchone()  # Fetch the result of the query which includes the cart_id

            # Print the cart_id from the result
            return {"Cart ID": str(cart_result[0])}
        else:
            return {"message": "Invalid username or auth token!"}



class CartItem(BaseModel):
    username: str
    auth_token: str
    catalog_id: int

@router.post("/{cart_id}/add_item")
def set_cart_item(cart_id: int, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        # Get the authentication token from the users table
        auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
            {'username': cart_item.username}
        ).fetchone()
        
        # Compare the fetched token with the provided one in the request
        if str(auth_token[0]) == cart_item.auth_token:
            # Insert a new cart entry into the carts table
            title = connection.execute(
            sqlalchemy.text("SELECT title FROM catalog WHERE id = :id"),
            {'id': cart_item.catalog_id}
        ).fetchone()
            price = connection.execute(
            sqlalchemy.text("SELECT price FROM catalog WHERE id = :id"),
            {'id': cart_item.catalog_id}
        ).fetchone()
            
            usersUpdate = sqlalchemy.text(
                "UPDATE carts SET title = :title, price = :price, catalog_id = :catalog_id WHERE cart_id = :cart_id"
            )
            # Execute the update
            connection.execute(usersUpdate, {
                'title': str(title[0]),
                'price': float(price[0]),
                'cart_id': cart_id,
                'catalog_id': cart_item.catalog_id
            })
            return "OK"
        else:
            return {"message": "Invalid username or auth token!"}

class CheckoutCart(BaseModel):
    username: str
    auth_token: str
    cart_id: int

@router.post("/{cart_id}/checkout")
def checkout(checkoutCart: CheckoutCart):
    """ """
    with db.engine.begin() as connection:
        # Get the authentication token from the users table
        auth_token = connection.execute(
            sqlalchemy.text("SELECT auth_token FROM users WHERE username = :username"),
            {'username': checkoutCart.username}
        ).fetchone()
        cart_username = connection.execute(
            sqlalchemy.text("SELECT username FROM carts WHERE cart_id = :cart_id"),
            {'cart_id': checkoutCart.cart_id}
        ).fetchone()
        
        # Compare the fetched token with the provided one in the request
        if str(auth_token[0]) == checkoutCart.auth_token and str(cart_username[0]) == checkoutCart.username:
            # Insert a new cart entry into the carts table
            title = connection.execute(
            sqlalchemy.text("SELECT title FROM carts WHERE cart_id = :id"),
            {'id': checkoutCart.cart_id}
                ).fetchone()
            price = connection.execute(
            sqlalchemy.text("SELECT price FROM carts WHERE cart_id = :id"),
            {'id': checkoutCart.cart_id}
                ).fetchone()
            
            usersUpdate = sqlalchemy.text(
                "UPDATE carts SET bought = :bought WHERE cart_id = :cart_id")
                # Execute the update
            connection.execute(usersUpdate, {
                    'bought': True,
                    'cart_id': checkoutCart.cart_id
                })

                #give buyer money:
            usersUpdate = sqlalchemy.text(
                "UPDATE carts SET bought = :bought WHERE cart_id = :cart_id")
                # Execute the update
            connection.execute(usersUpdate, {
                    'bought': True,
                    'cart_id': checkoutCart.cart_id
                })

                #Give Seller the Money
            catalogid = connection.execute(
                        sqlalchemy.text("SELECT catalog_id FROM carts WHERE cart_id = :id"),
                        {'id': checkoutCart.cart_id}
                            ).fetchone()
            print(catalogid)
            return catalogid

