# All Peer Review Feedback

## Jessica Luu
__Code Review Comments (Jessica Luu)__
1. In create_cart, if there are simultaneous requests or if the auth_token is somehow changed since you do a select first, there could be race conditions. Consider either changing the isolation level or doing like a select for update so you can lock it.

_Thank you for the feedback on the `create_cart` method. We will definitely add this to our implementation._

2-7. In set_cart_item, similar to above you do a select first then do an update. You can do this in a single query or you can change isolation level/lock. This is the same for the checkout, add_item, list_items, and delete_items.

_Thank you for the feedback on the 4 listed method. We understand the concern regarding performing a select first and then an update, which can lead to race conditions. We will implement the necessary adjustments to improve the concurrency handling and overall stability of our application._

8-11. Also in create_user it's recommended to store passwords as a hash rather than the password directly for security.

_Thank you for the feedback. We've implemented this by hashing our passwords._

12. Also since username is not UNIQUE in the schema, update_passwords can fail if there are multiple users with the same username (though your create_username does attempt to handle creating only unique usernames)

_Thank you for the feedback. Username IS unique since our implementation doesn't allow other users to create an account using a username already created._ 

13-14. Deposit and Withdraw should handle concurrency.

_Thank you for the feedback. We've handled concurrency now._

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

3. In list_items in portfolio.py, instead of doing SELECT *, identify in the query which columns you will actually use so you can save some time and not "over-query" than what is necessary

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


## Arthur Umerov

## Liam Hyde

