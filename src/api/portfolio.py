from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
    dependencies=[Depends(auth.get_api_key)],
)

from typing import Optional

class SearchParams(BaseModel):
    brand: Optional[str] = None
    title: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class Auth(BaseModel):
    username: str
    auth_token: str

class ItemDetail(BaseModel):
    title: str
    brand: str
    size: float
    price: float
    quantity: int

class ItemDetailWithID(ItemDetail):
    id: int

class ItemListing(Auth):
    items: list[ItemDetail]

class ItemIDs(Auth):
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

        if user_info and str(user_info.auth_token) == data.auth_token:
            for item in data.items:
                if item.quantity > 0:
                    portfolio_id = connection.execute(
                        sqlalchemy.text("""
                            INSERT INTO catalog (user_id, title, brand, size, price)
                            VALUES (:user_id, :title, :brand, :size, :price) 
                            RETURNING id
                        """),
                            {
                                'user_id': user_info.id,
                                'title': item.title,
                                'brand': item.brand,
                                'size': item.size,
                                'price': item.price,
                            }
                    ).fetchone()

                    connection.execute(
                        sqlalchemy.text("""
                            INSERT INTO catalog_ledger (catalog_id, quantity)
                            VALUES (:catalog_id, :quantity)
                        """),
                            {
                                'catalog_id': portfolio_id.id,
                                'quantity': item.quantity
                            }
                    )
                    catalog_id.append(portfolio_id.id)
                else:
                    raise HTTPException(status_code=401, detail="Invalid item amount")
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")
        
    return {
        "List of Catalog Id's:": catalog_id
    }

@router.post("/list_items")
def list_items(auth: Auth):
    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id
                FROM users WHERE username = :username
            """),
            {'username': auth.username}
        ).fetchone()

        if user_info and str(user_info.auth_token) == auth.auth_token:
            items = connection.execute(
                sqlalchemy.text("""
                    SELECT catalog.id, title, brand, size, price, SUM(quantity) AS quantity
                    FROM catalog
                    JOIN catalog_ledger ON catalog.id = catalog_id
                    WHERE user_id = :user_id
                    GROUP BY catalog.id, title, brand, size, price
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
                connection.execute(
                    sqlalchemy.text("""
                        INSERT INTO catalog_ledger (catalog_id, customer_id, quantity)
                        VALUES (:item_id, :user_id, (
                            SELECT -1 * COALESCE(SUM(quantity), 0)
                            FROM catalog_ledger
                            WHERE catalog_id = :item_id
                            GROUP BY catalog_id
                        ));
                        UPDATE cart_items SET quantity = 0
                        WHERE catalog_id = :item_id;
                    """),
                    {'item_id': item, 'user_id': user_info.id}
                )
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")
        
    return {"message": "Items deleted successfully"}

class VendorMetrics(BaseModel):
    total_customers: int
    avg_spent_per_customer: float
    brands_sold: int
    recurring_customers: int
    total_money_spent: float

class VendorLeaderboardRequest(Auth):
    sort_by: str

class VendorRanking(BaseModel):
    full_name: str
    username: str
    total_money_sold: float
    rank: int

@router.post("/vendor_leaderboard")
def vendor_leaderboard(data: VendorLeaderboardRequest):
    valid_sort_fields = ["total_customers", "avg_spent_per_customer", "brands_sold", "recurring_customers", "total_money_spent"]
    
    if data.sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort_by value")

    with db.engine.begin() as connection:
        user_info = connection.execute(
            sqlalchemy.text("""
                SELECT auth_token, id, full_name, username
                FROM users WHERE username = :username
            """),
            {'username': data.username}
        ).fetchone()

        if user_info and str(user_info.auth_token) == data.auth_token:
            metrics_query = """
                WITH customer_totals AS (
                    SELECT carts.user_id, SUM(catalog.price * cart_items.quantity) as total_amount
                    FROM carts
                    JOIN cart_items ON carts.cart_id = cart_items.cart_id
                    JOIN catalog ON cart_items.catalog_id = catalog.id
                    WHERE catalog.user_id = :user_id AND carts.bought = TRUE
                    GROUP BY carts.user_id
                ),
                recurring_customers AS (
                    SELECT carts.user_id
                    FROM carts
                    JOIN cart_items ON carts.cart_id = cart_items.cart_id
                    WHERE cart_items.catalog_id IS NOT NULL AND carts.bought = TRUE
                    GROUP BY carts.user_id
                    HAVING COUNT(*) > 1
                )
                SELECT
                    (SELECT COUNT(DISTINCT carts.user_id) FROM carts JOIN cart_items ON carts.cart_id = cart_items.cart_id JOIN catalog ON cart_items.catalog_id = catalog.id WHERE catalog.user_id = :user_id AND carts.bought = TRUE) as total_customers,
                    (SELECT AVG(total_amount) FROM customer_totals) as avg_spent_per_customer,
                    (SELECT COUNT(DISTINCT brand) FROM catalog WHERE user_id = :user_id) as brands_sold,
                    (SELECT COUNT(*) FROM recurring_customers) as recurring_customers,
                    (SELECT SUM(price * quantity) FROM catalog WHERE user_id = :user_id) as total_money_spent
            """

            metrics = connection.execute(
                sqlalchemy.text(metrics_query),
                {'user_id': user_info.id}
            ).fetchone()

            metrics_dict = {
                "total_customers": metrics.total_customers,
                "avg_spent_per_customer": metrics.avg_spent_per_customer,
                "brands_sold": metrics.brands_sold,
                "recurring_customers": metrics.recurring_customers,
                "total_money_spent": metrics.total_money_spent,
            }

            # Ranking Query
            ranking_query = """
                SELECT 
                    users.full_name,
                    users.username,
                    SUM(price * quantity) as total_money_sold
                FROM catalog
                JOIN users ON catalog.user_id = users.id
                GROUP BY users.id
                ORDER BY total_money_sold DESC
            """

            rankings = connection.execute(
                sqlalchemy.text(ranking_query)
            ).fetchall()

            user_rank = None
            top_5 = []

            for rank, row in enumerate(rankings, start=1):
                if rank <= 5:
                    top_5.append(VendorRanking(
                        full_name=row.full_name,
                        username=row.username,
                        total_money_sold=row.total_money_sold,
                        rank=rank
                    ))
                if row.username == user_info.username:
                    user_rank = VendorRanking(
                        full_name=row.full_name,
                        username=row.username,
                        total_money_sold=row.total_money_sold,
                        rank=rank
                    )

            return {
                data.sort_by: metrics_dict[data.sort_by],
                "user_rank": user_rank,
                "top_5": top_5
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")

@router.post("/search_items")
def search_items(params: SearchParams):
    with db.engine.begin() as connection:
        query = """
            SELECT catalog.id, title, brand, size, price, SUM(catalog_ledger.quantity) AS quantity
            FROM catalog
            JOIN catalog_ledger ON catalog.id = catalog_ledger.catalog_id
        """
        filters = []
        if params.brand:
            filters.append("brand ILIKE :brand")
        if params.title:
            filters.append("title ILIKE :title")
        if params.min_price is not None:
            filters.append("price >= :min_price")
        if params.max_price is not None:
            filters.append("price <= :max_price")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " GROUP BY catalog.id, title, brand, size, price HAVING SUM(catalog_ledger.quantity) > 0"

        items = connection.execute(
            sqlalchemy.text(query),
            {
                'brand': f"%{params.brand}%" if params.brand else None,
                'title': f"%{params.title}%" if params.title else None,
                'min_price': params.min_price,
                'max_price': params.max_price
            }
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