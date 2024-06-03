from fastapi import APIRouter, Query, HTTPException
import sqlalchemy
from src import database as db
from sqlalchemy.exc import OperationalError
import time

router = APIRouter()

@router.get("/listings/", tags=["listings"])
def get_catalog(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    retry_count = 3
    while retry_count > 0:
        try:
            with db.engine.connect() as connection:
                # Define the specific column order in the SELECT statement
                query = sqlalchemy.text("""
                    SELECT catalog.id, user_info.username, title, brand, size, price, catalog.created_at
                    FROM catalog
                    JOIN users AS user_info ON catalog.user_id = user_info.id
                    WHERE catalog.quantity > 0
                    ORDER BY catalog.id ASC
                    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
                """)
                offset = (page - 1) * page_size
                result = connection.execute(query, {'offset': offset, 'limit': page_size})
                catalog_items = [row._asdict() for row in result]
                return catalog_items
        except OperationalError as e:
            retry_count -= 1
            if retry_count == 0:
                raise HTTPException(status_code=500, detail="Database connection failed")
            time.sleep(1)  # Wait before retrying
