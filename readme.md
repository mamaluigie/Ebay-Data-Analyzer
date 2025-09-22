# Ebay Data Analyzer

This project is to test the functionality for obtaining all data from a specified ebay query. Doing so is difficult due to the access restrictions that ebay has put on the Feed API. Since there are strict restrictions on the feed api I am required to go through the alternative route on obtaining the data via the browse api.


After getting all the data pulled from an original query I can then run data analysis on it to determine interesting things about the data like outliers, time to sell, and other stuff.

### Limitations of the browse api

Some limitations to the browse api are that you can only pull the queried data with 200 item pages at a time limited to a total of 10,000 entries that can be pulled altogether. Rate limits are also set so that you have to wait about 17 seconds in between each data pull or risk getting throttled/ip banned from the api.

### Workaround

Due to this limitation I have to be creative on how I am to pull all of the data. The idea behind how to do this I came up with is to pull 10,000 records and insert them into a sqllite database. 

Retrieve the embeddings for each of the titles of each entry utilizing a transformer encoder based model.

After getting the embeddings for each of the titles I will then be able to cluster each of the titles into categories that each fall in.

Then use a llm model to see a category that each of these would most likely fit in then run a new query with that category name that the llm suggests. 

Repeat on each subcategory until I have like at least 90% of the original query results.

Example:

- Query (Playstation 5) will pull everything that has to do with playstation 5. This is about 1 million records in NA region. 
- I can only obtain 10,000 records so will feed this data through the embedding model, cluster it, then utilize an llm for detecting what proper category names would be. Like if it is video games or etc.

### Potential issues:

*Will determine if these are actually issues after the testing period is finished*

- (Potential problem): This method could cluster things that are alike to well potentially. Like if there is a kirby game it will only cluster based on if it is a kirby thing. but maybe not. just have to do the kmeans clustering and check output in testing first.

- (Potential problem) I might not be able to obtain all of the categories and will be limited by the number of categories that get pulled in the original 10k 

- (Potential problem) Another thing that I thought of is that there is not really a way to see if a new query was apart of the original set that was pulled in the original query at the beginning. That is why it is important to probably get a fine tuned category to start with and not something that is super broad.

        Example:
        - Pulling "Playstation 5" might not be good since that will pull so many things that are not directly related to the playstation 5. all depends on the size of the original query.

    - (Potential Fix) I think that a good rule of thumb would be that if the original query is greater than 100k then it probably should not be used. Or if the amount of data that I can actually pull is less than 10% of the overall query. This will ensure that the data quality, number of clusters, and quality of clusters are greater for the data pull.

### Steps to acomplish this

*The basic idea is to pull, then pull subsets until the majority of the original major set is obtained.*

- [x] Pull all the 10k records for the original query of greater than 10k records.
- [x] Insert this data into a sqlite database.
- [x] Run this data through an embedding model of choice. *(finished in testing)*
- [ ] Run the embedded text through a clusetering algorithm.
- [ ] Run the clustered sorted data through an llm to get the cluster titles.
- [ ] Use the clustered titles that are output from the llm to get an additional query of 10k records
- [ ] Run this loop until there is at least 90% of the data obtained from the original query.

## Notes

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