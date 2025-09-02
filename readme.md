Sample Size:

The sample size that I am in need of using will update depending on what item is being queried. 

With the browse api I am only able to do 5000 queries per day
https://developer.ebay.com/develop/get-started/api-call-limits

this means that I am able to do 208 calls per hour and 3 calls per minute without hitting the daily threshold

The maximum number of records that I am able to query per request is 200 I think?
have to check on this


Task to complete before going to bed tonight is to have the data imported with getting 10 percent of it utilizing timeouts
to make sure that it is not getting rate limited.

Inserting the unsold data into the database.

Checking the database links to see if it is sold or not.
If it is sold then drop from the database and add to a sold database with the upload date and sold date so we can see how
long it took to sell that item.


Make sure that each item being added to the databases are put into their own individual tables for item. make sure that each table item
for each item is specific like if it is an xbox that is 500GB vs 1TB. Make sure to be that specific. 


I might not have to make it only get 10% if I am only looking at like one item at a time
one with a huge search query like laptop has 1million records which will take like exactly 24 hours to get all of the data for.

Idea for what the ai can do is to have it go through the data and suggest a list of categories that it can use and reference to create the 
tables and then insert the data into after going though it.
