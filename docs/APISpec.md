# API Specification for CSC Project 

## 1. Customer Purchasing

The API calls are made in this sequence when making a purchase:
1. `Get Listings`
2. `Create Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`

### 1.1. Get All Listings - `/listings` (GET)

Retrieves the list of available shoe listings based on optional filters like size, brand, and price.

**Response**:

```json
[
    {
        "id": "integer",
        "username": "string",
        "title": "string",
        "brand": "string",     
        "size": "integer",
        "price": "float",
        "created_at": "string" # technically a time_stamptz
    }
]
```

### 1.2. Create Cart - `/carts` (POST)

Creates a new shopping cart for the customer.

**Request**:

```json
{
    "username": "integer",
    "auth_token": "string  # Once user has been logged in, a authentication token will be given
}
```

**Response**:

```json
{
    "Cart ID": "string"
}
```

### 1.3. Add Item to Cart - `/carts/{cart_id}/add_item` (POST)

Adds a specific shoe listing to the customer's cart

**Request**:

```json
{
    "username": "integer",
    "auth_token": "string",
    "catalog_id": "int"
}
```

**Response**:

```json
{
    "Catalog ID": "string",
    "Cart ID": "string"
}
```

### 1.4. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Processes the checkout of the cart, including payment handling and order confirmation.

**Request**:

```json
{
    "username": "integer",
    "auth_token": "string",
    "cart_id": "int"
}
```

**Response**:

```json
{
    "Catalog ID": "string"
}
```

## 2. User Login and Signup

The API calls are made in this sequence when signing up:
1. `Create Account`
2. `Auth Login`
3. `Update Username`
4. `Update Password`

### 2.1. Create Account - `/users/create_user` (POST)

Sends user data needed to create an account.

**Request**:
```json
[
    {
        "full_name": "string",
        "username": "string",
        "email": "string",
        "password": "string"
    }
]
```

**Response**:

```json
[
    "User(s) created!"
]
```

### 2.2. Get Listings - `/auth/login` (POST)

Used for user to login once account is crated.

**Request**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Response**:

```json
{
    "Login successful!",
    "auth_token": "string"
}
```

### 2.3. Change Username - `/auth/update_username` (POST)

Used for user to change their username

**Request**:
```json
{
    "current_username": "string",
    "new_username": "string",
    "password": "string",
    "auth_token": "string"
}
```

**Response**:

```json
{
    "Username Changed!",
}
```

### 2.4. Change Password - `/auth/update_password` (POST)

Used for user to change their username

**Request**:
```json
{
    "current_username": "string",
    "current_password": "string",
    "new_password": "string",
    "auth_token": "string"
}
```

**Response**:

```json
{
    "Password Changed!",
}
```

## 3. Posting as Seller

The API calls are made in this sequence when making a purchase:
1. `Add Item`
2. `List Items`
3. `Delete Items`

### 3.1. Add Items - `/portfolio/add_items` (POST)
Used for seller to add an item to the catalog

```json
[
    {
        "title": "string",
        "brand": "string",
        "size": "float",
        "price": "string",
        "quantity": "integer"
        "username": "string",
        "auth_token": "string",
    }
]

```

**Response**:

```json
{
    "List of Catalog Id's:": "list(integers)"
}

### 3.3. Add Shoes - `/portfolio/add_item` (POST)
Used for seller to create a seller portfolio once account is crated.


```json
{
  "username": "string",
  "auth_token": "string",
  "items" : [
       {
         "title": "string",
         "brand": "string",
         "size": "number",
         "price": "integer",
         "quantity": "integer"
       }
   ]
}
```

**Response**:

```json
{
    "Item added"
}
```

### 3.4. Add Photos - `/portfolio/add_photo` (POST)
Used for seller to add photos to their post

**Query Parameters**:

- `photo`: What the link of the photo will be

**Response**:

```json
{
    "Item added"
}
```

### 3.5. Get Portfolio Items - `/portfolio/get_items` (GET)
Used for seller to display current listings

**Query Parameters**:
- `portfolio_id`: ID tied to the user's shoe portfolio.

**Response**:

```json
{
    "shoes" : "listof objects"
}
```

## 4. Deleting Posts

The API calls are made in this sequence when deleting:
1. `Get portfolio`
2. `Delete listing`

### 4.1. Get portfolio - `/portfolio/{portfolio_id}` (GET)

Retrieves all user listings based on portfolio ID

Query Parameters:
-`portfolio_id`: Identifier for the seller's portfolio.

**Response**:

```json
{
     "listing_id": "integer",
        "title": "string",
        "brand": "string",
        "size": "integer",
        "price": "integer",
        "images": ["string"]
}
```

### 4.2. Delete Listing - `/portfolio/{portfolio_id}/listing/{listing_id}` (DELETE)

Deletes a specific shoe from a seller's portfolio

Query Parameters:
-`portfolio_id`: Identifier for the seller's portfolio.
-`listing_id`: Identifier for the specific listing to be deleted.

```json
**Response**:
{
    "success": "boolean",
    "message": "Listing deleted successfully"
}
```
