# Group Project: V5 - Performance Tuning

## Fake Data Modeling
[Generate Fake Data File](https://github.com/yarecryb/ecommerce_shoes/blob/main/generate_fake_data.py)

env.:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=127.0.0.1
POSTGRES_PORT=54322
POSTGRES_DB=postgres

There are 100,000 rows in the User Table for each unique user.
There are 100,000 rows of unique shoe listings by users.
There are 300,000 rows for ledgers representing transactions.
There are 200,000 carts created by each user.
There are 100,000 items added to carts by users.
There are 500,000 rows of transactions where each user interacts with each different shoe posts.
There are 100,000 carts created by each user.
There are 1,000,000 items added to carts by users.

These values for each data point are accurate to how a shoe selling service would realistically scale in the real world. 100,000 users is a solid amount of users, not too little and not too big. This value allows us to test a generous amount with plenty of room to grow. Having 100,000 listings in the catalogue simulates a shoe list per each user which is a moderate to large size. Having this amount lets us properly look at serach, information gathering and inventory management. For catalog ledger we had about 5 interactions for each user on average. This allows us to test the platforms high interactions. We had 200,000 Carts one cart for each user. Finally we had 300,000 rows for cart items. We averaged 10 items per cart purely because shoppers love to add items to their cart to compare different things and remove listings from theri cart all the time. Having this at a high amount will allow us to test, adding items to carts, removing and buying things.


## Performance results of hitting endpoints

For each endpoint, list how many ms it took to execute. State which three endpoints were the slowest.
1. Deposit - 0.109 ms
2. Withdraw - 0.099 ms
3. Balance - 0.070 ms

4. Create_cart - 0.747 ms
5. View cart - 0.077 ms
6. Add item in cart 0.737 ms
7. Checkout - 0.427 ms

8. Listings - 43.073 ms

9. Add Item - 1.363 ms
10. List Items - 0.169 ms
11. Delete Items - 1.46 ms
12. Vendor - 21.43 ms
13. Search - 12.424 ms

14. Create_users - 0.247 ms
15. Login - 0.124 ms
16. Change username - 0.524 ms
17. Change password - 0.451 ms

18. Topten - 0.852 ms


## Slowest Endpoints: 
1. '/listings'

2. '/vendor'

3. '/search'

## Performance tuning

For each of the three slowest endpoints, run explain on the queries and copy the results of running explain into the markdown file. Then describe what the explain means to you and what index you will add to speed up the query. Then copy the command for adding that index into the markdown and rerun explain. Then copy the results of that explain into the markdown and say if it had the performance improvement you expected. Continue this process until the three slowest endpoints are now acceptably fast (think about what this means for your service).


1. /listings
EXPLAIN ANALYZE
SELECT catalog.id, title, brand, size, price, SUM(quantity) AS quantity
FROM catalog
JOIN catalog_ledger ON catalog.id = catalog_ledger.catalog_id
WHERE user_id = :user_id
GROUP BY catalog.id, title, brand, size, price;

Execution Time: 43.073 ms

Proposed Index: 
CREATE INDEX catalog_user_id_idx ON catalog(user_id);
CREATE INDEX catalog_ledger_catalog_id_idx ON catalog_ledger(catalog_id);

EXPLAIN ANALYZE
SELECT catalog.id, title, brand, size, price, SUM(quantity) AS quantity
FROM catalog
JOIN catalog_ledger ON catalog.id = catalog_ledger.catalog_id
WHERE user_id = 123
GROUP BY catalog.id, title, brand, size, price;

Planning Time: 0.092 ms
Execution Time: 0.025 ms

2. Vendor Endpoint
EXPLAIN ANALYZE
WITH customer_totals AS (
    SELECT carts.user_id, SUM(catalog.price * cart_items.quantity) as total_amount
    FROM carts
    JOIN cart_items ON carts.cart_id = cart_items.cart_id
    JOIN catalog ON cart_items.catalog_id = catalog.id
    WHERE catalog.user_id = :user_id AND carts.bought = TRUE
    GROUP BY carts.user_id
),
recurring_customers AS (
    SELECT carts.user_id
    FROM carts
    JOIN cart_items ON carts.cart_id = cart_items.cart_id
    WHERE cart_items.catalog_id IS NOT NULL AND carts.bought = TRUE
    GROUP BY carts.user_id
    HAVING COUNT(*) > 1
)
SELECT
    (SELECT COUNT(DISTINCT carts.user_id) FROM carts JOIN cart_items ON carts.cart_id = cart_items.cart_id JOIN catalog ON cart_items.catalog_id = catalog.id WHERE catalog.user_id = :user_id AND carts.bought = TRUE) as total_customers,
    (SELECT AVG(total_amount) FROM customer_totals) as avg_spent_per_customer,
    (SELECT COUNT(DISTINCT brand) FROM catalog WHERE user_id = :user_id) as brands_sold,
    (SELECT COUNT(*) FROM recurring_customers) as recurring_customers,
    (SELECT SUM(price * quantity) FROM catalog WHERE user_id = :user_id) as total_money_spent;

Execution time - 21.43 ms

Proposed Index:
CREATE INDEX carts_user_id_idx ON carts(user_id);
CREATE INDEX cart_items_cart_id_idx ON cart_items(cart_id);
CREATE INDEX cart_items_catalog_id_idx ON cart_items(catalog_id);
CREATE INDEX catalog_user_id_idx ON catalog(user_id);

EXPLAIN ANALYZE
WITH customer_totals AS (
    SELECT carts.user_id, SUM(catalog.price * cart_items.quantity) as total_amount
    FROM carts
    JOIN cart_items ON carts.cart_id = cart_items.cart_id
    JOIN catalog ON cart_items.catalog_id = catalog.id
    WHERE catalog.user_id = 123 AND carts.bought = TRUE
    GROUP BY carts.user_id
),
recurring_customers AS (
    SELECT carts.user_id
    FROM carts
    JOIN cart_items ON carts.cart_id = cart_items.cart_id
    WHERE cart_items.catalog_id IS NOT NULL AND carts.bought = TRUE
    GROUP BY carts.user_id
    HAVING COUNT(*) > 1
)
SELECT
    (SELECT COUNT(DISTINCT carts.user_id) FROM carts JOIN cart_items ON carts.cart_id = cart_items.cart_id JOIN catalog ON cart_items.catalog_id = catalog.id WHERE catalog.user_id = 123 AND carts.bought = TRUE) as total_customers,
    (SELECT AVG(total_amount) FROM customer_totals) as avg_spent_per_customer,
    (SELECT COUNT(DISTINCT brand) FROM catalog WHERE user_id = 123) as brands_sold,
    (SELECT COUNT(*) FROM recurring_customers) as recurring_customers,
    (SELECT SUM(price * quantity) FROM catalog WHERE user_id = 123) as total_money_spent;

Execution Time - 1.432 ms

3. Search Endpoint
EXPLAIN ANALYZE
SELECT catalog.id, title, brand, size, price, SUM(catalog_ledger.quantity) AS quantity
FROM catalog
JOIN catalog_ledger ON catalog.id = catalog_ledger.catalog_id
WHERE (brand ILIKE :brand OR :brand IS NULL)
AND (title ILIKE :title OR :title IS NULL)
AND (price >= :min_price OR :min_price IS NULL)
AND (price <= :max_price OR :max_price IS NULL)
GROUP BY catalog.id, title, brand, size, price
HAVING SUM(catalog_ledger.quantity) > 0;

Execution time - 12.434 ms

Proposed Index:

CREATE INDEX catalog_brand_idx ON catalog(brand);
CREATE INDEX catalog_title_idx ON catalog(title);
CREATE INDEX catalog_price_idx ON catalog(price);
CREATE INDEX catalog_ledger_catalog_id_idx ON catalog_ledger(catalog_id);

EXPLAIN ANALYZE
SELECT catalog.id, title, brand, size, price, SUM(catalog_ledger.quantity) AS quantity
FROM catalog
JOIN catalog_ledger ON catalog.id = catalog_ledger.catalog_id
WHERE (brand ILIKE '%Nike%' OR :brand IS NULL)
AND (title ILIKE '%Shoe%' OR :title IS NULL)
AND (price >= 50 OR :min_price IS NULL)
AND (price <= 200 OR :max_price IS NULL)
GROUP BY catalog.id, title, brand, size, price
HAVING SUM(catalog_ledger.quantity) > 0;


Execution time - 5.439 ms