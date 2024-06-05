from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    dependencies=[Depends(auth.get_api_key)],
)

# sort by day, month, or year
@router.get("/top_ten")
def top_ten(
    year: int = "",
    month: int = "",
    day: int = "",
):
    with db.engine.begin() as connection:
        base_query = """
            WITH FilteredSales AS (
                SELECT 
                    c.brand,
                    SUM(ledger.quantity) * -1 AS shoes_sold
                FROM catalog_ledger AS ledger
                JOIN catalog AS c ON ledger.catalog_id = c.id
                WHERE 1=1
                {date_filters}
                GROUP BY c.brand
            ),
            RankedSales AS (
                SELECT 
                    brand,
                    shoes_sold,
                    DENSE_RANK() OVER (ORDER BY shoes_sold DESC) AS shoe_rank
                FROM FilteredSales
            )
            SELECT 
                brand,
                shoes_sold,
                shoe_rank
            FROM RankedSales
            WHERE shoe_rank <= 10
            ORDER BY shoe_rank;
        """

        date_filters = ""
        params = {}
        if year:
            date_filters += " AND EXTRACT(YEAR FROM ledger.created_at) = :year"
            params["year"] = year
        if month:
            date_filters += " AND EXTRACT(MONTH FROM ledger.created_at) = :month"
            params["month"] = month
        if day:
            date_filters += " AND EXTRACT(DAY FROM ledger.created_at) = :day"
            params["day"] = day
        query = base_query.format(date_filters=date_filters)

        results = connection.execute(sqlalchemy.text(query), params)

        json = {
            "results": []
        }
        for row in results:
            json["results"].append(
                {
                    "brand": row.brand,
                    "shoes_sold": row.shoes_sold,
                    "rank": row.shoe_rank
                }
            )
    return json
