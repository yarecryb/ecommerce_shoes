from fastapi import APIRouter
from fastapi import APIRouter, Depends,Query
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
router = APIRouter()


@router.get("/listings/", tags=["listings"])
def get_catalog(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    with db.engine.connect() as connection:
        # Define the specific column order in the SELECT statement
        query = sqlalchemy.text("""
            SELECT id, username, title, brand, size, price, created_at FROM catalog
            ORDER BY id ASC
            OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """)
        offset = (page - 1) * page_size
        result = connection.execute(query, {'offset': offset, 'limit': page_size})
        catalog_items = [row._asdict() for row in result]
        return catalog_items