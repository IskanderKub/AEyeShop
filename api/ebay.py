import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

async def get_ebay_access_token() -> str: # Get ebay access token
    credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}" # Combine client ID and secret
    encoded = base64.b64encode(credentials.encode()).decode() # Encode to base64 it is required by ebay api (OAuth2.0)
    async with httpx.AsyncClient() as client: # Create an asynchronous HTTP client
        response = await client.post( # Make a POST request to eBays OAuth2 token endpoint
            "https://api.ebay.com/identity/v1/oauth2/token",
            headers={ # Set the required headers for the request
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={ # Set the required data for the request
                "grant_type": "client_credentials", # Use client credentials to take token
                "scope": "https://api.ebay.com/oauth/api_scope" # Set link to data in ebay api
            }
        )
    data = response.json()
    print("eBay response:", data)
    return data["access_token"]

async def search_ebay(query: str) -> list: # Search items on eBay
    token = await get_ebay_access_token() # Get the access token
    async with httpx.AsyncClient() as client: # Create link with HTTP client ebay
        response = await client.get( # GET request to eBay search endpoint
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            headers={"Authorization": f"Bearer {token}"}, # Set authorization header with access token
            params={
                "q": query, # text from user to search in ebay
                "limit": 5  # maximum number of items in response
            }
        )
    data = response.json() # get response from eBay in JSON format
    items = data.get("itemSummaries", []) # get list of items, if empty return empty list
    results = [] # create empty list for results
    for item in items: # loop through each item
        results.append({ # add formatted item to results
            "title": item.get("title", "No title"), # item title
            "price": item.get("price", {}).get("value", "N/A") + " " + item.get("price", {}).get("currency", ""), # price with currency
            "condition": item.get("condition", "N/A"), # item condition
            "url": item.get("itemWebUrl", "https://ebay.com") # link to item on eBay
        })
    return results # return formatted list of items to router