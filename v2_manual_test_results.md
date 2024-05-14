# Example workflow

1. User registers by sending their details to `POST /users/create_user`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/users/create_user' \
  -H 'Content-Type: application/json' \
  -d '{
    "full_name": "someoneelse",
    "email": "idk",
    "password": "10",
    "username": "someonelese"
  }'

Response:
{
    "message": "User created successfully!"
}

2. User logs in by sending their username and password to `POST /auth/login`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "someonelese",
    "password": "10"
  }'

Response:
{
    "message": "Login successful!",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

3. User updates their username by sending their current username, new username, password, and authentication token to `POST /auth/update_username`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/auth/update_username' \
  -H 'Content-Type: application/json' \
  -d '{
    "current_username": "someonelese",
    "new_username": "newusername",
    "password": "10",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

Response:
{
    "message": "Username Changed!"
}

4. User updates their password by sending their current username, current password, new password, and authentication token to `POST /auth/update_password`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/auth/update_password' \
  -H 'Content-Type: application/json' \
  -d '{
    "current_username": "newusername",
    "current_password": "10",
    "new_password": "newsecurepassword",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

Response:
{
    "message": "Password Changed!"
}

5. User deposits money into their wallet by sending their username, authentication token, card details, and amount to `POST /wallet/deposit`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/wallet/deposit' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "newusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "card_number": "1234567890123456",
    "expiration_date": "12/24",
    "cvs": 123,
    "amount": 100.00
  }'

Response:
{
    "message": "Deposit successful!"
}

6. User withdraws money from their wallet by sending their username, authentication token, card details, and amount to `POST /wallet/withdraw`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/wallet/withdraw' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "newusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "card_number": "1234567890123456",
    "expiration_date": "12/24",
    "cvs": 123,
    "amount": 50.00
  }'

Response:
{
    "message": "Withdrawal successful!"
}

7. User gets all listings by sending a GET request to `GET /listings`.

# Testing results

curl -X 'GET' \
  'https://ecommerce-shoes-vz56.onrender.com/listings' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'

Response:
[
    {
        "id": 1,
        "username": "sellerusername",
        "title": "Shoe Title",
        "brand": "Nike",
        "size": 10,
        "price": 100.00,
        "created_at": "2022-05-27T00:00:00Z"
    },
    {
        "id": 2,
        "username": "sellerusername",
        "title": "Another Shoe",
        "brand": "Adidas",
        "size": 9,
        "price": 80.00,
        "created_at": "2022-05-27T00:00:00Z"
    }
]

8. User creates a cart by sending their username and authentication token to `POST /carts`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/carts' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -d '{
    "username": "newusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

Response:
{
    "Cart ID": "abc123"
}

9. User adds an item to their cart by sending their username, authentication token, and catalog ID to `POST /carts/{cart_id}/add_item`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/carts/abc123/add_item' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -d '{
    "username": "newusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "catalog_id": 1
  }'

Response:
{
    "Catalog ID": "1",
    "Cart ID": "abc123"
}

10. User checks out their cart by sending their username, authentication token, and cart ID to `POST /carts/{cart_id}/checkout`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/carts/abc123/checkout' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -d '{
    "username": "newusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "cart_id": "abc123"
  }'

Response:
{
    "message": "Checkout successful!"
}

11. Seller adds items to the catalog by sending the item details, username, and authentication token to `POST /portfolio/add_items`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/portfolio/add_items' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -d '{
    "title": "New Shoe",
    "brand": "Nike",
    "size": 10,
    "price": "150.00",
    "quantity": 5,
    "username": "sellerusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

Response:
{
    "List of Catalog Id's": [1, 2, 3]
}

12. Seller lists their items by sending their username and authentication token to `POST /portfolio/list_items`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/portfolio/list_items' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -d '{
    "username": "sellerusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

Response:
[
    {
        "id": 1,
        "title": "New Shoe",
        "brand": "Nike",
        "size": 10,
        "price": "150.00"
    },
    {
        "id": 2,
        "title": "Another Shoe",
        "brand": "Adidas",
        "size": 9,
        "price": "80.00"
    }
]

13. Seller deletes an item from their listing by sending their username, authentication token, and item ID to `POST /portfolio/delete_item`.

# Testing results

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/portfolio/delete_item' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -d '{
    "username": "sellerusername",
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "items": [1, 2]
  }'

Response:
{
    "message": "Items deleted successfully"
}
