## Example Flows

### Example Flow 1: New User Registration and First Purchase

1. User registers by sending their details to `POST /users`.
2. User logs in via `POST /auth/login` and receives a token.
3. User browses shoes by calling `GET /listings` with filters applied.
4. User creates a cart via `POST /carts`.
5. User adds shoes to the cart by calling `PUT /carts/{cart_id}/items/{listing_id}` multiple times.
6. User checks out by calling `POST /carts/{cart_id}/checkout`.

### Example Flow 2: Repeat Customer Purchase

1. Returning user logs in via `POST /auth/login` to retrieve their session token.
2. User retrieves the latest shoe listings via `GET /listings`.
3. User reuses an existing cart or creates a new one via `POST /carts`.
4. User adds multiple shoes to their cart.
5. Completes the purchase with `POST /carts/{cart_id}/checkout`.

### Example Flow 3: Admin Adding New Listings

1. Admin logs in to obtain a session token.
2. Admin posts new shoe listings via `POST /listings`.
3. Admin views all listings to verify new entries via `GET /listings`.

### Example Flow 4: User adds a New Listing

1. User logs in via `POST /auth/login`
2. User creates a listing via POST /listings
3. User can view all their listings via `GET /listings/{user_id}`.
