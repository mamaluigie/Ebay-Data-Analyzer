import requests
import json
import base64

def get_ebay_authorization_url(item_id):
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Basic {base64.b64encode(f"{json.load(open("credentials.json"))["client_id"]}:{json.load(open("credentials.json"))["client_secret"]}".encode()).decode()}'
    }

    payload = {
        "grant_type": "client_credentials",
        "scope": ,
    }
    
    response = requests.get(url, headers=headers)
    return response.json()