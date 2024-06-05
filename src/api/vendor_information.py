from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum

router = APIRouter(
    prefix="/vendor",
    tags=["vendor"],
    dependencies=[Depends(auth.get_api_key)],
)

class Auth(BaseModel):
    username: str
    auth_token: str

class VendorMetrics(BaseModel):
    total_customers: int
    avg_spent_per_customer: float
    brands_sold: int
    recurring_customers: int
    total_money_spent: float

class SortBy(str, Enum):
    TOTAL_CUSTOMERS = "total_customers"
    AVG_SPENT_PER_CUSTOMER = "avg_spent_per_customer"
    BRANDS_SOLD = "brands_sold"
    RECURRING_CUSTOMERS = "recurring_customers"
    TOTAL_MONEY_SPENT = "total_money_spent"

class VendorRanking(BaseModel):
    full_name: str
    username: str
    total_money_sold: float
    rank: int

@router.post("/")
def vendor_leaderboard(
    data: Auth,
    sort_by: SortBy = Query(SortBy.TOTAL_CUSTOMERS, description="Sort by")
):
    valid_sort_fields = [
        "total_customers", "avg_spent_per_customer",
        "brands_sold", "recurring_customers", "total_money_spent"
    ]
    
    if sort_by not in valid_sort_fields:
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
                    (SELECT SUM(cart_items.quantity * catalog.price) FROM cart_items JOIN catalog ON cart_items.catalog_id = catalog.id JOIN carts ON cart_items.cart_id = carts.cart_id WHERE catalog.user_id = :user_id AND carts.bought = TRUE) as total_money_spent
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
                    SUM(cart_items.quantity * catalog.price) as total_money_sold
                FROM catalog
                JOIN users ON catalog.user_id = users.id
                JOIN cart_items ON catalog.id = cart_items.catalog_id
                JOIN carts ON cart_items.cart_id = carts.cart_id
                WHERE carts.bought = TRUE
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
                sort_by.value: metrics_dict[sort_by.value],
                "user_rank": user_rank,
                "top_5": top_5
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid auth")
