# This is the program that will parse through all of the un read data in the data drop folder
# and insert it into the sqllilte database that will be located in this directory.

# Making sure that no duplicate data is inserted and that all of the data is parsed through and
# Categorized correctly with the proper standardized names for each item.
# This categorization of the data could potentially be done with ai processing by feeding in the 
# name of the listing and ask the ai how many GB does it have, What edition is it, etc depending 
# on the type of listing. 

# Depending on the type of listing that I am searching for will depend on what the prompt will be
# inserted into the ai model for processing.

# After I categorize the data into sub category I can query those in order to get 100 percent of the dtaa

# At first though I am not going to be able to get 100 percent of the data due to the 10k limit on items
# that can be paginated through

import sqlite3 
import os 
import json
from tqdm import tqdm

def process_data(queries, time_for_data_pull):
    # This function will process the data and insert it into the SQLite database

    
    # go through each item and collect a list of categories created with ai
        # Now we are going to go through each of the categories, 
    # Check if there is an associated database for each, 
    # then create the database if it does not exist or update it if it does 
    # based on the timestamp that is associated with that particular datapull

    # Check if there is a database folder and if there is not one then create it
    if os.path.exists("./databases") == False:
        os.makedirs("./databases")

    # Go through the list of queries and create a database based on the query list

    for query in queries:
        conn = sqlite3.connect(f"./databases/{query}.db")
        print(f"Updating database for {query} at timestamp {time_for_data_pull}")

        cursor = conn.cursor()

        # Explanation of the table attributes
        # itemId: Unique identifier for each item that is stored as a string
        #         Example: 
        #         "v1|254654754368|0"
        # title: Title of the item
        # Description: Description of the item that will be added in later on
        #              since I have to use a different api, the shopping api
        #              to get the descriptions of each item referencing the itemId prob
        # price: Price of the item in USD
        # timestamp: Timestamp of when the data was pulled
        # itemWebUrl: URL of the item's webpage
        # imageUrl: URL of the item's image
        # sellerUsername: Username of the seller
        # sellerFeedbackPercentage: Feedback percentage of the seller 
        # sellerFeedbackScore: Feedback score of the seller in an integer
        # categories: Categories the item belongs to in a json looking list
        # condition: Condition of the item
        # buyingOptions: Buying options available for the item
        # itemLocation: Location of the item represented as a form of postal code.
        #               Might only be the first 3 or so digits of the postal code.

        # Since there is no item upload date available I will have to calculate this 
        # by getting checking the previous data pull and seeing what new items have been
        # added every time I do a data pull, if there is no matches from the previous data
        # pull then that means that the item is new and I can input the item creation date
        # as the datetime that was originally recorded.

        cursor.execute(
            f'''CREATE TABLE IF NOT EXISTS "{query}"(
                itemId TEXT PRIMARY KEY,
                title TEXT,
                price REAL,
                timestampOfDataPull INTEGER,
                timestampOfItemSold TEXT DEFAULT NULL,
                itemWebUrl TEXT,
                imageUrl TEXT,
                sellerUsername TEXT,
                sellerFeedbackPercentage REAL,
                sellerFeedbackScore INTEGER,
                categories TEXT,
                condition TEXT,
                buyingOptions TEXT,
                itemLocation TEXT,
                shippingCost REAL,
                minEstimatedDeliveryDate TEXT,
                maxEstimatedDeliveryDate TEXT,
                soldStatus BOOLEAN DEFAULT 0)
                ''')

        # going to initially make a table for the overall data
        # later on going to separate that table into separate ones based on
        # the subcategory that is decided with ai and populate it with the data

        # Going thorugh each item in the itemsummaries for each file for the associated 
        # timestamp
        for file in tqdm(os.listdir(f"./data/{query}")):
            if file.endswith(".json") and file.startswith(f"{query}_{time_for_data_pull}"):
                with open(f"./data/{query}/{file}", "r") as f:
                    print(f"Processing file {file} for {query} database.")
                    data = json.load(f)

                    # Organizing all of the data from file a dictionary for each item
                    # to make easier to go through and input

                    for itemUnprocessed in data["itemSummaries"]:
                        item = {}

                        item["itemId"] = itemUnprocessed["itemId"]
                        item["title"] = itemUnprocessed["title"]
                        item["price"] = itemUnprocessed["price"]["value"]
                        item["timestampOfDataPull"] = time_for_data_pull
                        item["itemWebUrl"] = itemUnprocessed["itemWebUrl"]
                        if itemUnprocessed.get("image"):
                            item["imageUrl"] = itemUnprocessed["image"]["imageUrl"]
                        else:
                            item["imageUrl"] = "NoImage"
                        item["sellerUsername"] = itemUnprocessed["seller"]["username"]
                        item["sellerFeedbackPercentage"] = itemUnprocessed["seller"]["feedbackPercentage"]
                        item["sellerFeedbackScore"] = itemUnprocessed["seller"]["feedbackScore"]
                        item["categories"] = str(itemUnprocessed["categories"])
                        item["condition"] = itemUnprocessed["condition"]
                        item["buyingOptions"] = str(itemUnprocessed["buyingOptions"])

                        # Checking if item is in USA or not
                        if itemUnprocessed.get("itemLocation"):
                            if itemUnprocessed["itemLocation"].get("country") == "US":
                                if itemUnprocessed["itemLocation"].get("postalCode"):
                                    item["itemLocation"] = itemUnprocessed["itemLocation"]["postalCode"]
                                else:
                                    item["itemLocation"] = "NoPostalCode"
                            else:
                                item["itemLocation"] = "NoPostalCode"
                        else:
                            print("Item has no location?")
                            print(itemUnprocessed)
                            item["itemLocation"] = "NoPostalCode"

                        # Checking if shipping cost exists
                        if "shippingOptions" not in itemUnprocessed.keys():
                            item["shippingCost"] = "noShipping"
                            item["minEstimatedDeliveryDate"] = "noShipping"
                            item["maxEstimatedDeliveryDate"] = "noShipping"
                        elif "shippingCost" in itemUnprocessed["shippingOptions"][0]:
                            item["shippingCost"] = itemUnprocessed["shippingOptions"][0]["shippingCost"]["value"] 
                            # Check if there are delivery dates
                            if itemUnprocessed["shippingOptions"][0].get("minEstimatedDeliveryDate") and itemUnprocessed["shippingOptions"][0].get("maxEstimatedDeliveryDate"):
                                item["minEstimatedDeliveryDate"] = itemUnprocessed["shippingOptions"][0]["minEstimatedDeliveryDate"] 
                                item["maxEstimatedDeliveryDate"] = itemUnprocessed["shippingOptions"][0]["maxEstimatedDeliveryDate"] 
                            else:
                                item["minEstimatedDeliveryDate"] = "noDeliveryDate"
                                item["maxEstimatedDeliveryDate"] = "noDeliveryDate"

                        # Now that we have all the data organized, we can insert it into the database
                        columns = ', '.join(item.keys())
                        placeholders = ', '.join(['?' for _ in item])
                        sql = f'INSERT OR REPLACE INTO "{query}" ({columns}) VALUES ({placeholders})'
                        cursor.execute(sql, tuple(item.values()))

                        # Must commit the changes to the database
                        conn.commit()
        print(f"Committing all updates to the {query} database.")
    print("Finished uploading all data to each respective database.")


# This is for testing
if __name__ == "__main__":
    # This is only going to do the playstation 5 data
    process_data(["Playstation 5"], 1757138356.2579854)