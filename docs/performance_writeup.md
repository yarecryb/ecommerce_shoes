## Fake Data Modeling
Should contain a link to the python file you used to construct the million rows of data for your service. Should also contain a writeup explaining how many final rows of data you have in each of your table to get to a million rows AND a justification for why you think your service would scale in that way. There is no single right answer to this, but your reasoning must be justifiable.

https://github.com/yarecryb/ecommerce_shoes/blob/main/generate_fake_data.py
env.:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=127.0.0.1
POSTGRES_PORT=54322
POSTGRES_DB=postgres


There are 100,000 rows in the User Table for each unique user.
There are 100,000 rows of unique shoe listings by users.
There are 500,000 rows of transactions where each user interacts with each different shoe posts. 
There are 100,000 carts created by each user.
There are 1,000,000 items added to carts by users.

These values for each data point are accurate to how a shoe selling service would realistically scale in the real world. 100,000 users is a solid amount of users, not too little and not too big. This value allows us to test a generous amount with plenty of room to grow. Having 100,000 listings in the catalogue simulates a shoe list per each user which is a moderate to large size. Having this amount lets us properly look at serach, information gathering and inventory management. For Catalogue ledger we had about 5 interactiions for each user on average. This allows us to test the platforms high interactions. We had 100,000 Carts one cart for each user. Finally we had 1,000,000 rows for cart items. We averaged 10 items per cart purely because shoppers love to add items to their cart to compare different things and remove listings from theri cart all the time. Having this at a high amount will allow us to test, adding items to carts, removing and buying things.

## Performance results of hitting endpoints
For each endpoint, list how many ms it took to execute. State which three endpoints were the slowest.

  1. End Point 1

  2. End Point 2

  3. Endpoint 3 

## Performance tuning
For each of the three slowest endpoints, run explain on the queries and copy the results of running explain into the markdown file. Then describe what the explain means to you and what index you will add to speed up the query. Then copy the command for adding that index into the markdown and rerun explain. Then copy the results of that explain into the markdown and say if it had the performance improvement you expected. Continue this process until the three slowest endpoints are now acceptably fast (think about what this means for your service).

