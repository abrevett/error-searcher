from serpapi import GoogleSearch    # SerpAPI import
from bs4 import BeautifulSoup       # BeautifulSoup import
import requests                     # Import for StackExchange use
import json
import re

STACKX_SITES = {}

stackx_query = {
    "pagesize": 100, # Maximum Size per page
    "order": "desc",
    "sort": "activity",
    "filter": "!.kZ-f.vMXeIXqR48NteY"
}

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

def stackx_search(payload: dict) -> dict:
    req = requests.get("https://api.stackexchange.com/2.3/search/advanced", params=payload)
    print(req.url)
    if(req.status_code != requests.codes.ok):
        print("ERROR: Status code " + str(req.status_code) )
        print( req.json() )
        return None
    return req.json()

def stackx_run(query):
    key = ""
    with open("stackx.key", "r") as keyfile:
        key = keyfile.read().strip()
    forums = [ "serverfault", "stackoverflow", "unix", "askubuntu", "superuser" ]
    resp = {}
    for site in forums:
        pagenum = 1
        payload = dict(stackx_query) 
        payload.update({"key": key, "page": pagenum, "q": query, "site": site})
        print(stackx_query)
        print(payload)
        resp[site] = {}

        resp[site][pagenum] = stackx_search(payload)
        while( resp[site][pagenum]["has_more"] == True ):
            print("getting more!")
            pagenum += 1
            payload.update({ "page": pagenum })
            resp[site][pagenum] = stackx_search(payload)

    return resp

def main():
    # Gather query terms and regex patterns:
    user = input("Enter StackExchange query terms: ")
    regex_str = input("Search Regex of your error: ")

    
    regex = re.compile( r".*" + regex_str + r".*")

#    result = stackx_run(user.strip())
#    with open("result_dump.json", "w+") as jsdump:
#        jsdump.write( json.dumps(result, indent=2) )
#    print("results written to result_dump.json")

    result = {}
    with open("result_dump.json", "r") as jsdump:
        result = json.loads(jsdump.read())
    
    # We now iterate through each response and search for our regex pattern
    relevant = []
    for forum in result.keys():
        site = result[forum]
        for page in site.values():
            items = page["items"]
            for item in items:
                if regex.match(item["body"]):
                    relevant.append(item)

    print(len(relevant))


#    urls = {}
#    for item in result.values():
#        items = item["items"]
#        i=0
#        for r in items:
#            urls[i] = { "link": r["link"], "question_id": r["question_id"] }
#            i +=1

#    regex = r'[a-z]'
#    # Use BeautifulSoup to iterate over links
#    for url in urls.values():
#        link = url["link"]
#        html = requests.get( link ).text
#        soup = BeautifulSoup(html, "html.parser")
#        match = print(soup.body.get_text("\n"))


main()
