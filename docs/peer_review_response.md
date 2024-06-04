# All Peer Review Feedback

## Jessica Luu
__Code Review Comments (Jessica Luu)__
1. In create_cart, if there are simultaneous requests or if the auth_token is somehow changed since you do a select first, there could be race conditions. Consider either changing the isolation level or doing like a select for update so you can lock it.

_Thank you for the feedback on the `create_cart` method. We will definitely add this to our implementation._

2-7. In set_cart_item, similar to above you do a select first then do an update. You can do this in a single query or you can change isolation level/lock. This is the same for the checkout, add_item, list_items, and delete_items.

_Thank you for the feedback on the 4 listed method. We understand the concern regarding performing a select first and then an update, which can lead to race conditions. We will implement the necessary adjustments to improve the concurrency handling and overall stability of our application._

8-11. Also in create_user it's recommended to store passwords as a hash rather than the password directly for security.

_Thank you for the feedback. We've implemented this by hashing our passwords.__

12. Also since username is not UNIQUE in the schema, update_passwords can fail if there are multiple users with the same username (though your create_username does attempt to handle creating only unique usernames)

_Thank you for the feedback. Username IS unique since our implementation doesn't allow other users to create an account using a username already created._ 

13-14. Deposit and Withdraw should handle concurrency.

_Thank you for the feedback. We've handled concurrency now._

__Schema/API Design comments (Jessica Luu)__
1-4. Split the user table into two separate tables: one for user data and one for authentication details, and enforce a UNIQUE constraint on email and username. This normalization up to 3NF improves your create_users endpoint by eliminating the need for a select query, as insert failures will be handled by the UNIQUE constraint.

_Split the user table into two separate tables: one for user data and one for authentication details, and enforce a UNIQUE constraint on email and username. This normalization up to 3NF improves your create_users endpoint by eliminating the need for a select query, as insert failures will be handled by the UNIQUE constraint._

5. It should be the case that a user should have a username, email, password, etc. They shouldn't default to NULL, rather it should be NOT NULL since these seem like required attributes of an ecommerce store.

_This has been fixed and implemented._

6. I suggest changing the design of the catalog and carts tables. Instead of having a catalog that has a foreign key reference to a user_id, you should create a catalog with a list of items, then split your cart table into two for the cart and cart_items, similar to the potion shop to handle the many-to-many relationship.

_The suggestion to change the design of the catalog and carts tables by creating a catalog with a list of items and splitting the cart table into two for cart and cart_items is not suitable for our system. Having a catalog with a foreign key reference to user_id ensures that each user has their personalized catalog, simplifying queries and data management. Splitting the cart table adds unnecessary complexity, as our current design efficiently handles the relationships and operations needed. Moreover, our existing schema is optimized for performance and scalability, making the proposed changes redundant and potentially introducing more points of failure._

7. You could also split up the catalog table into a brands table, then a separate brand_items table too, to keep track of the brands that exist in your store and the items that belong to the brand.

_We already track brand and item name in catalog._

8. You can ledgerize the catalog items or another form of auditing so you can track changes over time.

_We've started, but haven't ulitilize it's functionality._

9. Instead of POST for delete_item, it should be labeled as a DELETE, just for better understanding

_Implemented_

10. Also rather than a delete, perhaps you might want to do a soft delete and update the table in case you wanted to still save the information rather than deleting the entire row. Up to you if the information is important.

_We may delete this because, but it will still show on the ledger, for info for us_

11. list_items is labeled as POST, but you're only querying the database, it should labeled as a GET request

_Implemented_

12. The wallet attribute in the users table could be changed to a integer. You can store the money as cents and do the calculation yourself. This is helpful when it comes down to having to compare numbers.

_We prefer to use it as a string, so we can compare it for a one liner in a stampt statement_

## Asa Levine

## Sean Hershey 

## Gabe Riedel

## Arthur Umerov

## Liam Hyde

