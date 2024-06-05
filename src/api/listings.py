from fastapi import APIRouter, Query, HTTPException
import sqlalchemy
from src import database as db
from sqlalchemy.exc import OperationalError
import time

router = APIRouter()

@router.get("/listings/", tags=["listings"])
def get_catalog(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    retry_count = 3  # Number of times to retry the database connection in case of failure
    while retry_count > 0:
        try:
            with db.engine.connect() as connection:  # Establish a connection to the database
                # Define the specific column order in the SELECT statement
                query = sqlalchemy.text("""
                    SELECT catalog.id, user_info.username, title, brand, size, price, catalog.created_at, SUM(quantity) AS quantity
                    FROM catalog
                    JOIN catalog_ledger ON catalog.id = catalog_id
                    JOIN users AS user_info ON catalog.user_id = user_info.id
                    WHERE quantity > 0
                    GROUP BY catalog.id, user_info.username, title, brand, size, price, catalog.created_at
                    ORDER BY catalog.id ASC
                    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
                """)
                offset = (page - 1) * page_size  # Calculate the offset for pagination
                result = connection.execute(query, {'offset': offset, 'limit': page_size})  # Execute the query
                catalog_items = [row._asdict() for row in result]  # Convert the result to a list of dictionaries
                return catalog_items  # Return the catalog items
        except OperationalError as e:  # Handle database connection errors
            retry_count -= 1  # Decrement the retry count
            if retry_count == 0:  # If no retries left, raise an HTTP exception
                raise HTTPException(status_code=500, detail="Database connection failed")
            time.sleep(1)  # Wait for 1 second before retrying
