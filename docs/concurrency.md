# Concurrency issues for ecommerce shoes

1. In /carts/checkout/, had we first got the price of the wallet and updated the wallet before running update then the code would have encountered a lost update anomaly.

Example issue
![Example1](./concurrency1.png)

Updating wallet within a single update statement for each transaction.
```
            connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet - :price
                    WHERE id = :id
                """), 
                {
                    'id': user_info.id,
                    'price': shoe_info.price
                })

            connection.execute(
                sqlalchemy.text("""
                    UPDATE users SET wallet = wallet + :price
                    WHERE id = :id
                """), {
                    'id': shoe_info.user_id,
                    'price': shoe_info.price
                })
```
