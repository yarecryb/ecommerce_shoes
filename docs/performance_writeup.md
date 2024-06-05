## Fake Data Modeling
Should contain a link to the python file you used to construct the million rows of data for your service. Should also contain a writeup explaining how many final rows of data you have in each of your table to get to a million rows AND a justification for why you think your service would scale in that way. There is no single right answer to this, but your reasoning must be justifiable.

## Performance results of hitting endpoints
For each endpoint, list how many ms it took to execute. State which three endpoints were the slowest.

## Performance tuning
For each of the three slowest endpoints, run explain on the queries and copy the results of running explain into the markdown file. Then describe what the explain means to you and what index you will add to speed up the query. Then copy the command for adding that index into the markdown and rerun explain. Then copy the results of that explain into the markdown and say if it had the performance improvement you expected. Continue this process until the three slowest endpoints are now acceptably fast (think about what this means for your service).

## Prepare for final presentation
Plan to present for 15 minutes. You will be interrupted during your presentation for questions. Your final presentations MUST be a live demo. No powerpoint or slides are needed. I will ask you to demo certain things in your presentation. Make sure you handle normal edge cases otherwise I will find them live during your presentation.
