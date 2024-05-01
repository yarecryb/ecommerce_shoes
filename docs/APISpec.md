# API Specification for CSC Project 

## 1. Customer Purchasing

The API calls are made in this sequence when making a purchase:
1. `Get Listings`
2. `Create Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`

### 1.1. Get Listings - `/listings` (GET)

Retrieves the list of available shoe listings based on optional filters like size, brand, and price.

**Query Parameters**:
- `size` (optional): Shoe size to filter by.
- `brand` (optional): Brand name to filter by.
- `max_price` (optional): Maximum price to filter by.

**Response**:

```json
[
    {
        "listing_id": "integer",
        "title": "string",
        "brand": "string",
        "size": "integer",
        "price": "integer",
        "images": ["string"]
    }
]
```

### 1.2. Create Cart - `/carts` (POST)

Creates a new shopping cart for the customer.

**Response**:

```json
{
    "cart_id": "string" /* This ID will be used for future calls to add items and checkout */
}
```

### 1.3. Add Item to Cart - `/carts/{cart_id}/items/{listing_id}` (PUT)

Adds a specific shoe listing to the customer's cart or updates the quantity of an existing item in the cart.

**Request**:

```json
{
  "quantity": "integer"
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

### 1.4. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Processes the checkout of the cart, including payment handling and order confirmation.

**Request**:

```json
{
  "payment_method": "string",
  "shipping_address": "string"
}
```

**Response**:

```json
{
    "total_items": "integer",
    "total_amount": "integer"
}
```
## 2. User Login and Signup

The API calls are made in this sequence when signing up:
1. `Users`
2. `Auth Login`

### 2.1. Get Listings - `/users` (POST)

Sends user data needed to create an account.

**Query Parameters**:
- `username`: Username used for login.
- `email`: Email used for login.
- `password`: Used for login.

**Response**:

```json
[
    "Account created"
]
```

### 2.2. Get Listings - `/auth/login` (POST)

Used for user to login once account is crated.

**Query Parameters**:
- `username`: Username used for login.
- `password`: Used for login.

**Response**:

```json
{
    "auth_token": "string"
}
```

## 3. Posting as Seller

The API calls are made in this sequence when making a purchase:
1. `Make Portfolio`
2. `Add Shoes`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`

### 3.1. Make Portfolio - `/portfolio` (POST)
Used for seller to create a seller portfolio once account is crated.

**Query Parameters**:
- `username`: Username used for login.

**Response**:

```json
{

    "portfolio_id": "int"
}
```

### 3.3. Add Shoes - `/portfolio/add_item` (POST)
Used for seller to create a seller portfolio once account is crated.

**Query Parameters**:
- `portfolio_id`: ID tied to the user's shoe portfolio.
- `shoe_id`: ID tied to the shoe that will be added.
- `quantity`: How many of those shoes will be sold.

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
