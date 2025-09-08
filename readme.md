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

To get the description data for each item I have to make a request to the getitem endpoint for each item and update the data with the description.
with the getitems api endpoint I am able to provide 20 items at a time per request with a rate limit of 5000 items a day it seems like since it is apart of the browse api, this makes it so each request is twice as long since I will have to wait like 18 seconds before going to the next also
so something that will take 4 hours to process will now take around 8 hours.

It seems like I have to use trading api to see if the item sold or not since the browse api is only for active items.


* brain storming *
to optimize the obtaining of the data with adding descriptions it might be best to have paralell processing of the data for 
* brain storming *

to get data without using the feed api since I have restricted access to the feed api I will have to utilize the finding api (aparently it is depricated) or the shopping api GetSingleItem api call. With the shopping api call it will only have ~90 days to check and see if the listing is active or not before not being able to access that data anymore.

transformers library help:

It looks like the zero-shot -classification libraries are going to be the most useful for my use case. 
It takes in a list of candidate labels and a sentence and classfies on one of the candidate labels it based on that