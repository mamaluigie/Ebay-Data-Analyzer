import requests
import json
import base64
import time
import os

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
            return auth_code
    else:
        print("Creating a new auth_code.json file.")
        auth_code = get_ebay_authorization_code()

        # Saving the authorization code json to a json file for reference
        with open("auth_code.json", "w") as f:
            json.dump(auth_code, f)

        return auth_code

# Function to call the eBay Browse API and retrieve the data that is requested
def browse_api_call(auth_code, query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {auth_code['access_token']}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "Content-Type": "application/json"
    }

    payload = {
        "q" : query,
        "limit" : 200
    }

    response = requests.get(url, headers=headers, params=payload)
    return response.json()

# An idea for tomorrow is to save the queried search results to a sqllite database
# then connect an ai model to this to analyze the data to see if it is fake based
# on the images that are provided with each post descriptions
if __name__ == "__main__":

    # Am just going to test out doing gaming consoles for now
    queries = ["Playstation 5", "Xbox Series X", "Nintendo Switch 2", "Steam Deck"]
    auth_code = update_authorization_code()
    for query in queries:

        data = browse_api_call(auth_code, query)

        # Check if the folder exists, if not create it
        if not os.path.exists("./data"):
            os.makedirs("./data")

        # check if there is a folder for that item
        if not os.path.exists(f"./data/{query}"):
            os.makedirs(f"./data/{query}")

            # going to save all of the data into json files in the data drop folder.
            with open(f"./data/{query}/{query}_{time.time()}_item_file.json", "w") as f:
                json.dump(data, f)

    # After saving all of the data into the data drop folders there will be another 
    # program that will be run to process the data and insert it into a mysql database