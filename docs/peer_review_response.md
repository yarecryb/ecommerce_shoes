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

## Asa Levine

## Sean Hershey 

## Gabe Riedel

## Arthur Umerov

## Liam Hyde

