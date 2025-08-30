import requests
import json
import base64
import time
import os

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

if __name__ == "__main__":

    if os.path.exists("auth_code.json"):
        with open("auth_code.json", "r") as f:
            auth_code = json.load(f)

            # Check if the code is expired in the current file. If so generate a new authorization code with the client secret and client id
            if auth_code["expires_in"] + auth_code["timestamp"] > time.time():
                print("Using saved auth code file.")
            else:
                auth_code = get_ebay_authorization_code()
        print(auth_code)
    else:
        auth_code = get_ebay_authorization_code()
        # Saving the authorization code json to a json file for reference
        with open("auth_code.json", "w") as f:
            json.dump(auth_code, f)

        print("Saved a new authcode to the auth_code.json file.")
