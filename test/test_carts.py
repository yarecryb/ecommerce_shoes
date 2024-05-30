from .info_test import client  # Import only the 'client' name from info_test

def test_read_listings():
    response = client.get("/listings/")
    assert response.status_code == 200
