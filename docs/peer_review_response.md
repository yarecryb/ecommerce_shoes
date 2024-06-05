# All Peer Review Feedback

## Jessica Luu

**Code Review Comments (Jessica Luu)**

1. In create_cart, if there are simultaneous requests or if the auth_token is somehow changed since you do a select first, there could be race conditions. Consider either changing the isolation level or doing like a select for update so you can lock it.

_Thank you for the feedback on the `create_cart` method. We will definitely add this to our implementation._

2-7. In set_cart_item, similar to above you do a select first then do an update. You can do this in a single query or you can change isolation level/lock. This is the same for the checkout, add_item, list_items, and delete_items.

_Thank you for the feedback on the 4 listed method. We understand the concern regarding performing a select first and then an update, which can lead to race conditions. We will implement the necessary adjustments to improve the concurrency handling and overall stability of our application._

8-11. Also in create_user it's recommended to store passwords as a hash rather than the password directly for security.

\_Thank you for the feedback. We've implemented this by hashing our passwords.\_\_

12. Also since username is not UNIQUE in the schema, update_passwords can fail if there are multiple users with the same username (though your create_username does attempt to handle creating only unique usernames)

_Thank you for the feedback. Username IS unique since our implementation doesn't allow other users to create an account using a username already created._

13-14. Deposit and Withdraw should handle concurrency.

_Thank you for the feedback. We've handled concurrency now._

**Schema/API Design comments (Jessica Luu)**
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

1. The auth. check on line 96 within carts.py is redundant with the above. The difference in response messages aren't great enough to warrant a two-stage check.

This has been fixed. Now only doing one auth check per endpoint.

2. The user email should be unique within the schema, not due to rules in the code as this could lead to race conditions bypassing this check.

Fixed. Changes should be reflected in schema.sql

3. The user id should be used to seek user carts, not the username, as that's the identifier that's hard-coded to each user uniquely.

Fixed. Username now uniquely identifies each user.

4. Calls to fetch user_info before accessing the table with that data may fail if the user changes there data between queries. This should either be collapsed into a single query or protected against concurrency in some other fashion.

A user changing their data inbetween queries would only matter when changing their username as the user_id will not change. Currently, our only endpoint using the username within the same query is /portfolio/vendor_leaderboard/ which has a conslidated query to fetch the username.

5. User data like passwords, emails, usernames, etc. should be encrypted within the database -- not stored as raw data.

Emails and usernames will still be stored as raw data. Passwords have been encrypted now and salted with bcrypt.

6. The user email should be unique within the schema, not due to rules in the code as this could lead to race conditions bypassing this check.

Fixed.

7. With how carts are setup, it allows for users to create multiple carts at once. Same as above, if this is intended then go for it, but it seems like it adds needless functionality that is more likely to generate issues than assistance.

This is intended as users can add different items to different carts to save them then check out the carts with the items that they want.

8. More concurrency issues exist within the cart process between the four update calls that should be resolved with collapse or high isolation levels.
   Will implement.

9. Any validation or handling of credit cards (or any sensitive info) should be abstracted out of the package containing the database handling. It introduces a number of security risks when putting them here.
   Credit cards have been removed.

10. On line 108 of wallet.py, the following appears: current_wallet_balance = update_wallet =. Is there a reason for this as it seems to be a mistake given the code following it?
    Fixed. This was a mistake.

11. Deleting items from one's portfolio should clear it from any existing carts. Currently, users can still buy deleted items if it exists within their cart.
    Fixed.

12. Currently, user wallets can go negative when purchasing. There should be a check for sufficient balance that is able to divert a call to refill the wallet should this check fail.
    Fixed.

Schema/API comments

1. Make the user email field unique.

Fixed.

2. Make all id fields unique. Even though they are auto-generated, it doesn't hurt to have additional security on that.

Fixed.

3. User auth. tokens should be unique to each user and enforced as such within the table.

fixed.

4. Add validation to ensure that the user wallet can't go below 0.

Fixed.

5. Possibly add a Boolean "private" field that allows for sellers to not delete items from their catalog but simply hide them.

Will implement.

6. Price should be constrained to double precision like the wallet within catalog.

will implement.

7. Cart should store the price at time of adding instead of referencing the catalog to prevent concurrency issues.

No, if the price increases after the user adds to cart, the price increase should be reflected at checkout.

8. The Boolean bought within carts should default to False, not null, as the default creation state of a cart is not bought.

Fixed.

9. The cart table should be renamed to cart_items potentially, as each entry only supports a single item

Fixed.

10. Size should be changed to text as sizes often are not purely numerical in representation

Fixed.

11. Should quantity be defaulted to 1? The field should be required with no default as the seller must enter a quantity I feel.

Default is 0 now.

12. Possibly add a reviews table to support seller review functionality (mentioned within my feature comments issue post).

Will implement

## Gabe Riedel

1. Your authentication checks in create_cart seem redundant, you only need one if-else block with the else containing the HTTPException

fixed, one if else block

2. In create_cart you handle invalid_auth errors with a raise exception, but you do not handle that with an exception in set_cart_item

fixed, now raising exception.

3. In list_items in portfolio.py, instead of doing SELECT \*, identify in the query which columns you will actually use so you can save some time and not "over-query" than what is necessary

Fixing this to only query what we need

4. In wallet.py, the luhn_check function is defined and used two different times, you could just make it once as its own helper function and call it in deposit and and withdraw

luhn_check has been removed

5. In withdraw in wallet.py, when setting the variable current_wallet_balance you set it equal to update_wallet and a SQLAlchemy statement simultaneously

fixed to remove redundant variables

6. The SQLAlchemy statement I referred to in 5 has a typo, you refer to the users tables twice

Thanks, fixed the typo. Removed redundant users

7. The SQLAlchemy statement I referred to in 5 just stores the text of the query but does not form a connection so no query will be executed

Fixed, now executes the query

8. In login_user in users.py, remove the debug print statement when you push this to prod so that auth_tokens are not leaked

print statement has been removed

9. The logic for checking username and password is duplicated in your two update functions; you can move this logic out to a helper method

Fixed.

10. In users.py be more consistent in returning just JSON statements not strings

Fixed, now only returning json for consistency

11. In users.py, handle errors not by returning strings but with HTTPException handling

Fixed, now raising 401 exception for invalid username or password

12. Add some error handling in listings.py in case of connection failure

Added.

Schema/API comments

1. Username and email in Users should not be nullable

Fixed.

2. For better normalization, you may want to add a cart_items table and move some of the data in carts there

Done

3. For better normalization, split users into account details with username, email, etc. and authentication details with password, auth, etc.

This seems unnecessary since the users table just has all information about the user already.

4. Update the API endpoint testing site to include your project name instead of Central Coast Cauldrons

Fixed.

5. Make sure the API endpoint responses all take comparable JSON forms

Fixed

6. Could add a ledger system for updating users' wallets instead of updating one variable that could cause concurrency issues

Will implement

7. You might not want to delete rows from the catalog, you can truncate instead or add a column to know if that item has been purchased

Will implement

8. Make IDs unique in schema

Fixed

9. Make username unique

Fixed

10. Make email unique

Fixed

11. Make auth. keys unique

Fixed

12. Default 'bought' boolean variable to False

Fixed

## Sean Hershey

**Code Review Comments (Sean Hershey)**

1. in cart.py there is a redundant if str(user_info.auth_token) == data.auth_token:
   Fixed
2. in cart.py 'bought': False value insert is redundant if you let it be false by default and don't supply it
   Fixed
3. in cart.py your invalid username/auth token handling is different either do return {"message": "Invalid username or auth token!"} or raise HTTPException(status_code=401, detail="Invalid auth")
   Will Implement
4. in cart.py 'Catalog_id' and 'Cart_id' in parameters should match the case of text for readability
   Will Implement
5. in cart.py add_item should be renamed to set_item as only one item can exist or changed to add multiple items
   Will Implement
6. in cart.py add_item should check if bought or otherwise clarify the purpose of the bought boolean logic
   Fixed
7. in cart.py no auth message fail in checkout
   Will Implement
8. in users.py check if change username is changing the username into one that already exists
   Already works
9. in wallet.py no auth verification exists for deposits
   Will Implement
10. in wallet.py current_wallet_balance has table typo "users users" instead of "users"
    Fixed
11. in listings.py add error messages or codes for a retrieving listing failure
    Will Implement
12. inconsistent new lines in SQL statements throughout effect readability
    Will Implement

**Schema/API Design comments (Sean Hershey)**

1. responses should be labbelled message and be reflected that way in code
   Fixed
2. in cases of returning auth_token no additional message is needed
   Fixed
3. created_at should be a time_stamp not string
   Will Implement
4. in cart schema bought boolean defaults to null not false
   Removed whole "bought" idea
5. in users id is not unique
   It is unique
6. in users username is not unique
   Will Implement
7. in users email is not unique
   Will Implement
8. in users auth_token is not unique
   Will Implement
9. in catalog id is not unique
   Will Implement
10. in carts id is not unique
    Will Implement
11. in catalog price should be the same as price in wallet
    Will Implement
12. in catalog price should be stored when added not referencing catalog
    Will Implement

## Arthur Umerov

**Code Review Comments (Arthur Umerov)**

1. In create_cart, if there are simultaneous requests or if the auth_token is changed, consider either changing the isolation level or using a select for update to avoid race conditions
Fixed
2. In create_user, store passwords as hashes rather than plaintext for security
Fixed
3. Ensure the email and username fields in the user table have a UNIQUE constraint to avoid duplicate entries and race conditions
Fixed
4. In set_cart_item, handle concurrency issues by performing a single query or by using locking mechanisms
Fixed
5. In listings.py, add indexing to frequently queried columns like brand and price to speed up searches
Will implement
6. In portfolio.py, ensure the quantity of items being added is a positive integer
Fixed
7. User data such as passwords, emails, and usernames should be encrypted in the database, not stored as raw data
Fixed
8. In wallet.py, ensure all credit card handling is abstracted out (use libraries or frameworks instead)
Fixed
9. In list_items in portfolio.py, specify the columns needed in the SELECT query to future proof
Fixed
10. Deleting items from one's portfolio should also remove them from any existing carts to prevent users from purchasing deleted items
Fixed - instead of removing items, more checks were added to checkout
11. Make sure user wallets cannot go below 0
Fixed
12. In carts.py, consider logging activity when adding items to the cart and checking out for reference/tracability
Fixed

**Schema/API Design comments (Arthur Umerov)**

1. Split the user table into user details (username, email, ...) and authentication details (password, auth tokens)
Fixed
2. Ensure the email and username fields in the user table are unique
Fixed
3. Set NOT NULL constraints for essential fields like username, email, and password in the user table
Fixed
4. Use clear HTTP methods for API endpoints (DELETE for delete_item and GET for list_items)
Fixed
5. Change the wallet amount to an int and store cents instead of dollar floats

6. Ensure all IDs (user, catalog, ...) are unique
Fixed
7. Use a timestamp data type for the created_at field instead of a string
Fixed
8. Set default values for Boolean fields
Fixed
9. Implement soft deletes for items (add a Boolean 'deleted' field to the items table)
Fixed
10. Split the catalog into a brands table and a brand_items table

11. Split the cart table into a cart and cart_items table
Fixed
12. Add a Boolean 'private' field to allow sellers to hide an item from the catalog instead of deleting it


**Code Review Comments (Liam Hyde)**
1. on line 93 of creating a cart, why do you compare the provided and expected auth token twice?
fixed.
2. I think a lot of the string casting is unnecessary
fixed.
3. In checkout can you only buy one item at a time? that seems weird, given there is no restriction on adding multiple items to carts
fixed.
4. listings does not function as defined in the spec, there are parameters where there shouldn't be
listings can vary as each listing will vary based on seller.
5. Encrypt all private user data (passwords, emails, wallets) etc in the database instead of storing the raw data
Encrypted passwords, usernames etc. we found not needed.
6. you should probably use a library to handle wallets
We found this was not neccesary.
7. removing items from a portfolio should remove them from all carts
Fixed. 
8. when handling checkouts, make sure customer balance does not go below 0
Fixed.
9. handling is inconsistent when requests/posts fail, should either all raise errors or all return error json
Errors are raised as HTTP exceptions now.
10. I don't think you can do normal subtraction with money values
Fixed.
12. you can run into race conditions with how you implement auth_token, consider adding an isolation level change
fixed
13. you can run into these same race conditions with how you handle wallets
fixed

**Schema/API Design comments (Liam Hyde)**
1. in users username should be unique
Fixed
2. in users email should be unique
Fixed.
3. in users auth_token should be unique (idk if random guarantees this)
They are unique.
4. fullname, username, email, and password should not be nullable
Fixed.
5. authentication info like passwords and personal info should probably be in different tables
We found that it was fine for now, but could be done later on. 
6. catalog can be split into catalog and items tables with catalog pointing to data on specific items
We found that it was fine for now, but could be done later on. 
7. in new items table title, brand, price, etc per item should not be nullable
As sellers can post sellings with limited information this should be fine.
8. carts and cart items should be two separate tables
we found this was unnecessary. 
9. wallet should also be a separate table from users
10. id should be unique in all tables
All IDS are unique.
11. when returning messages from the api make sure its json formatted as a field of "message": ""
Fixed for most.
12. auth_token should expire after a certain amount of time and require a new login
auth token resets after everytime.


