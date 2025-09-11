import requests
import json
import base64
import time
import os
import sqlite3
from tqdm import tqdm

from data_processing import upload_database
from data_processing import create_table
from data_processing import clean_item

# Gets the authorization code and saves it to the auth_code.json file
def get_ebay_authorization_code():
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    # Reading the credentials json file in read only to load into an object
    with open("credentials.json", "r") as cred_file:
        creds = json.load(cred_file)

    # Extracting client_id and client_secret
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    credentials = f"{client_id}:{client_secret}"

    # Base64 encoding the credentials
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Saving the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}"
    }

    # Saving the payload information
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    response = requests.post(url, headers=headers, data=payload)

    # Saving the current time in utc so we can compare to see if the token is expired
    data = response.json()
    data["timestamp"] = time.time()
    return data

# Checks to see if the authorization code is expired and returns the original or updated authorization code
def update_authorization_code():
    if os.path.exists("auth_code.json"):
        print("Found existing auth code file.")
        with open("auth_code.json", "r") as f:
            print("reading the authcode.json")
            auth_code = json.load(f)

            # Check if the code is expired in the current file. If so generate a new authorization code with the client secret and client id
            if auth_code["expires_in"] + auth_code["timestamp"] > time.time():
                print("Using saved auth code file.")
            else:
                print("Auth code expired. Generating a new one.")
                auth_code = get_ebay_authorization_code()

                # Update the authcode file
                with open("auth_code.json", "w") as f:
                    json.dump(auth_code,f)
                    return auth_code
            return auth_code
    else:
        print("Creating a new auth_code.json file.")
        auth_code = get_ebay_authorization_code()

        # Saving the authorization code json to a json file for reference
        with open("auth_code.json", "w") as f:
            json.dump(auth_code, f)

        return auth_code

# Function to call the eBay Browse API and retrieve the data that is requested
def browse_api_call(query, limit=200, offset=0, category_ids=[]):
    # Have to continuously check to see if the auth code is expired or not or will error out
    auth_code = update_authorization_code()

    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {auth_code['access_token']}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "Content-Type": "application/json"
    }

    payload = {
        "q" : query,
        "limit" : limit,
        "offset" : offset,
        # Going to only pull data from USA with shipping option and new items only due to
        # data cap of 10k items per query
        "filter" : f"deliveryCountry:{{US}},deliveryOptions:{{SHIP_TO_HOME}},conditions:{{NEW}},maxDeliveryCost:0",
        "sort" : "newlyListed",
        "category_ids" : f"{",".join(category_ids)}"
    }

    response = requests.get(url, headers=headers, params=payload)

    # waiting for a third of a second since I am allotted 5000 queries/day, 208 per hour, about 1 every 17.4 seconds
    time.sleep(18)
    return response.json()

# Function to pull the data and save it to a json file
# Returns the timestamp for the data pull
# All data is stored in the data directory in the query folder
def pull_data(query):

    # Need to create the data directory if it does not exist
    if not os.path.exists("./data"):
        os.makedirs("./data")
        print("created data directory")

    # This is to see how many pages there are
    data = browse_api_call(query, limit=1, category_ids=["139971"])

    # See how many 200 item pages there are
    total_items = data["total"]
    total_pages = (total_items // 200) + 1
    if total_pages > 50:
        total_pages = 50
    
    # Check to see if the data is 100% of the data, else skip pulling the data comletely and uploading to the database
    # Data is not accurate if the data is not 100%
    if total_items > 9500:
        # Skip pulling the data completely and uploading to the database
        print(f"Skipping data pull for {query} as total items exceed 9500")
        return None

    time_for_data_pull = time.time()

    # check if there is a folder for that item
    if not os.path.exists(f"./data/{query}"):
        os.makedirs(f"./data/{query}")
        print(f"created data directory for {query}")

    # Adding functinoality for pulling 10% of the data by seeing how many search results there are
    # And going through and pulling 10% of the data.
    print(f"Saving data for {query}")
    print([x.upper() if x == query else x for x in queries])

    
    # Going through all of the pages and pulling the data for testing
    for page in tqdm(range(total_pages)):
        print(f"Pulling page {page+1} of {total_pages} for {query}")
        data = browse_api_call(query, limit=200, offset=page*200, category_ids=["139971"])
        with open(f"./data/{query}/{query}_{time_for_data_pull}_item_file_page_{page+1}.json", "w") as f:
            json.dump(data, f)
        
    return time_for_data_pull

# Returns a timestamp and query for each successful datapull for a list of tuples
def pull_all_data(queries):

    timestamps = []
    for query in queries:
        time = pull_data(query)
        print(f"Data pulling complete for {query} at time {time}")
        if time:
            timestamps.append((query, time))

    return timestamps

# function to go through and all the data pulled and check if the item does not exist in the initial database
# if it doesnt then add it to the new database with a timestamp associated with time the item was caught
# This pulls out all of the fresh data that was actually added to ebay.
def check_and_upload_database(old_dbname, new_dbname, query, timestamp):
    
    # Connect to the old database and create a cursor
    old_conn = sqlite3.connect(f"./databases/{old_dbname}.db")
    old_cursor = old_conn.cursor()

    # Connect to the new item database 
    new_conn = sqlite3.connect(f"./databases/{new_dbname}.db")

    for file in os.listdir(f"./data/{query}/"):
        if timestamp in file:
            with open(f"./data/{query}/{file}") as f:
                data = json.load(f)
                for item in data["itemSummaries"]:
                    # Check if item in database
                    sql = "SELECT * FROM '{query}' WHERE itemId = ?"
                    result = old_cursor.execute(sql, item["itemId"])
                    if not result.fetchone():
                        # Fill new database with item with new timestamp at the current moment this is found out.
                        # Need to update the data processing library with something better to create a database 
                        # and to upload data to it with a basic insert so I can use it here.
                        create_table(new_conn, query)
                        item = clean_item({}, item)

                    else:
                        # Skip if the item is not in the database
                        pass
                            
# An idea for tomorrow is to save the queried search results to a sqllite database
# then connect an ai model to this to analyze the data to see if it is fake based
# on the images that are provided with each post descriptions
if __name__ == "__main__":
    # Am just going to test out doing gaming consoles for now
    # Will have to update this based on what the ai suggests for the categories for search
    queries = ["Playstation 5", "Xbox Series X", "Nintendo Switch 2", "Steam Deck"]
    queries_timestamps = pull_all_data(queries)

    # If the initial database exists create one
    for query, timestamp in queries_timestamps:
        if not os.path.exists(f"./databases/initial_{query}.db"):
            # Uploading the initial database infromation from the query and timestamp named 
            upload_database(f"initial_{query}", query, timestamp)
        else:
            # Else look into each of the original database entries and check to see if there are any new items
            # This is to create the new item database so we can have more accurate time information.
            # In the new database include the description for each item also utilizing the shopping api I think.
            check_and_upload_database(f"initial_{query}", f"new_{query}", query, timestamp)
        