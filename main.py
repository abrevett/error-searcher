from serpapi import GoogleSearch    # SerpAPI import
from bs4 import BeautifulSoup       # BeautifulSoup import
import requests                     # Import for StackExchange use
import json

STACKX_SITES = {}

def serp_search():
    key = ""
    with open("serpapi.key", "r") as keyfile:
        key = keyfile.read()

    search = GoogleSearch({
            "q": "alpine linux",
            "serp_api_key": key
        })

    return search.get_dict()

def google_search():
    key = ""
    eid = ""
    with open("googleapi.key") as keyfile:
        key = keyfile.read()
    with open("googleapi.id") as idfile:
        eid = idfile.read()
    # TODO: Key is valid, but cx parameter not working
#    r = requests.get("https://www.googleapis.com/customsearch/v1?key=" + key + "&cx=" + eid + "&q=alpine", )
#    r = requests.get("https://www.googleapis.com/customsearch/v1?key=" + key +"&cx=017576662512468239146:omuauf_lfve&q=lectures")
    return r.json()


def printJSON( val: dict ):
    print( json.dumps(val, indent=2) )


def init_stackx():
    payload = {
        "pagesize": "360"
    }
    req = requests.get("https://api.stackexchange.com/2.3/search/advanced", params=payload)
    print(req.url)
    if(req.status_code != 200):
        print("ERROR: Status code " + str(req.status_code) )
        return None
    STACKX_SITES = req.json()

def stackx_search():

    payload = {
        "site": "unix",
        "q": "alpine linux",
#        "body": "",
        "pagesize": 100, # Maximum Size per page
        "order": "desc",
        "sort": "activity"
    }
    req = requests.get("https://api.stackexchange.com/2.3/search/advanced", params=payload)
    print(req.url)
    if(req.status_code != 200):
        print("ERROR: Status code " + str(req.status_code) )
        print( req.json() )
        return None
    return req.json()


#result = google_search()
#print(result)

#print("\n\n")

#result = serp_search()
#organic = result["organic_results"]

#init_stackx()
result = stackx_search()

if(result): 
    printJSON( result["items"] )
