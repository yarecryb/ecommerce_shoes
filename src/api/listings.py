from fastapi import APIRouter
from fastapi import Query
import sqlalchemy
from src import database as db
router = APIRouter()


@router.get("/listings/", tags=["listings"])
def get_catalog(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    with db.engine.connect() as connection:
        # Define the specific column order in the SELECT statement
        query = sqlalchemy.text("""
            SELECT catalog.id, user_info.username, title, brand, size, price, catalog.created_at
            FROM catalog
            JOIN users AS user_info ON catalog.user_id = user_info.id
            ORDER BY catalog.id ASC
            OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """)
        offset = (page - 1) * page_size
        result = connection.execute(query, {'offset': offset, 'limit': page_size})
        catalog_items = [row._asdict() for row in result]
        return catalog_items