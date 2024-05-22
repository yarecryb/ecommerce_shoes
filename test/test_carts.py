from .info_test import *

def test_read_listings():
    response = client.get("/listings/")
    assert response.status_code == 200
