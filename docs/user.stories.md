# User Stories and Exceptions for ShoeMarket

This document outlines the user stories and exceptions/error scenarios for the ShoeMarket e-commerce platform. The user stories detail the primary functions and goals of our users, while the exceptions cover potential error scenarios and our planned responses to ensure a smooth user experience.

## User Stories

User stories describe the interactions and goals of the users within the ShoeMarket platform. They follow the format: As a [persona], I [want to], [so that].

1. As a sneaker enthusiast, I want to filter shoe listings by size, so that I can quickly find shoes that fit me.
2. As a collector, I want to filter by brand and release date, so that I can find specific collectible shoes.
3. As a bargain hunter, I want to sort listings by price, so that I can find the best deals available.
4. As a runner, I want to be able to easily find good running shoes, so that I can buy the best shoes for running.
5. As a seller, I want to be able to easily list shoes that I have for sale, so that I can reach customers to make money selling shoes.
6. As a student, I want to see what other kinds of shoes people are buying, so I can see what kinds of styles are popular.
7. As a reseller, I want to see how the shoe market is fluctuating.
8. As a parent, I want to know what shoes are the most popular to buy for my kids.
9. As somebody in a relationship, I want to see what shoes I can get my partner, and pick out the best colorways. 
10. As a Hiker, I want to see what shoes are good for hiking, and pick out the best hiking shoes.
11. As a reseller, I want to see the average prices for the shoe I'm looking to sell, and sell at an optimal price.
12. As a Female, I want to see shoes that are made for me, and buy shoes that are for woman.
 
## Exceptions

Exceptions detail the error scenarios we anticipate and how the system is designed to handle them to maintain usability and user satisfaction.

1. Exception: Search/filter yields no results.
 - The system will suggest broadening search criteria and offer to notify the user when products matching their criteria are listed.
2. Exception: A listed item is sold out or no longer available.
 - The listing will be automatically removed or updated, and users who have shown interest will be notified.
3. Exception: User attempts to register with an already used email.
 - The system will inform the user that the email is already in use and suggest they log in or reset their password.
4. Exception: A listed item that is not good for running but is listed as a good running shoe.
  - The system will have a review system so users can see how good a certain shoe is for a certain task.
5. Exception: Two users have the same item in their cart and try to checkout.
  - The system will check to be sure an item is available even if the item is already in a user's cart.
6. Exception: A user makes multiple failed login attempts within a few minutes.
- The system will make the user wait before trying again and notify the email attached to that account about the multiple login attempts.
7. Exception: A user intends to make a search but they spell it wrong
  - The system will yield results for products that are similar to user input
8. Exception : A user's payment does not go through or has pending status. 
  - The system will notify the user, so that they do not make the same payment twice. 
9. Exception: User enters invalid data format in a form field (e.g., entering letters in a numerical field).
The system will display an error message highlighting the specific field(s) with invalid input and provide guidance on the expected format, enabling the user to correct the information and proceed with the form submission.
10. Expection: A user posts a shoe that is not on the catalog
 - The system will allow the user to add their shoe as a new model.
11. Exception: The user tries to sell a shoe at a negative price
   - The system will force the user to sell the shoe inside a proper range.
12. Exception: A user spam posts the same shoe listing multiple times.
  - The system will notify the user and will only allow one posting for each entry of shoe in the catalog.
