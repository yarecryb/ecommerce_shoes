# API Specification for CSC Project 

The API calls are made in this sequence when using the shop:
1. `User Login and Signup`
2. `Customer Purchasing`
3. `Posting as Seller`

## 1. User Login and Signup

The API calls are made in this sequence when signing up:
1. `Create Account`
2. `Auth Login`
3. `Update Username`
4. `Update Password`
5. `Deposit Money to Wallet`
6. `Withdraw Money from Wallet`

### 1.1. Create Account - `/users/create_user` (POST)

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

### 1.2. User Login - `/users/login` (POST)

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

### 1.3. Change Username - `/users/update_username` (POST)

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

### 1.4. Change Password - `/users/update_password` (POST)

Used for user to change their username

**Request**:
```json
{
    "username": "string",
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

### 1.5. Add Money to Wallet - `/wallet/deposit` (POST)

The user can add money to the wallet to buy shoes

**Request**:
```json
{
    "username": "string",
    "auth_token": "string",
    "card_number": "string",
    "expiration_date": "string",
    "cvs": "integer",
    "amount": "float"
}
```

**Response**:

```json
{
    "Deposit successful!"
}
```

### 1.6. Withdraw Money from Wallet - `/wallet/withdraw` (POST)

The user can withdraw money from the wallet

**Request**:
```json
{
    "username": "string",
    "auth_token": "string",
    "card_number": "string",
    "expiration_date": "string",
    "cvs": "integer",
    "amount": "float"
}
```

**Response**:

```json
{
    "Withdrawal successful!"
}
```

## 2. Customer Purchasing

The API calls are made in this sequence when making a purchase:
1. `Get Listings`
2. `Create Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`


### 2.1. Get All Listings - `/listings` (GET)

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

### 2.2. Create Cart - `/carts` (POST)

Creates a new shopping cart for the customer.

**Request**:

```json
{
    "username": "integer",
    "auth_token": "string"  # Once user has been logged in, a authentication token will be given
}
```

**Response**:

```json
{
    "Cart ID": "string"
}
```

### 2.3. Add Item to Cart - `/carts/{cart_id}/add_item` (POST)

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

### 2.4. Checkout Cart - `/carts/checkout` (POST)

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


## 3. Posting as Seller

The API calls are made in this sequence when making a purchase:
1. `Add Item`
2. `List Items`
3. `Delete Items`

### 3.1. Add Items - `/portfolio/add_items` (POST)
Used for seller to add an item to the catalog

**Response**:
```json
{
    "username": "string",
    "auth_token": "string",
    [
        {
            "title": "string",
            "brand": "string",
            "size": "float",
            "price": "string",
            "quantity": "integer"
        }
    ]
}
```

**Response**:

```json
{
    "List of Catalog Id's:": "list(integers)"
}
```

### 3.2. List Portfolio - `/portfolio/list_items` (POST)
Used for seller to show what items they have listed


```json
{
  "username": "string",
  "auth_token": "string",
}
```

**Response**:

```json
[
    {
        "id": "integer",
        "title": "string",
        "brand": "string",
        "size": "float",
        "price": "string",
        "quantity": "integer"
    }
]
```

### 3.3. Delete Item - `/portfolio/delete_item` (POST)
Used for seller to remove an item from their listing

**Query Parameters**:

```json
{
  "username": "string",
  "auth_token": "string",
  "items": "List of integers"
}
```

**Response**:

```json
{
    "Items deleted successfully"
}
```
