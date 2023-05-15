from serpapi import GoogleSearch    # SerpAPI import
from bs4 import BeautifulSoup       # BeautifulSoup import
import requests                     # Import for StackExchange use
import json
import re
import itertools

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

def regex_weights(regex):
    # Split on GNU error standards
    regex_tok = regex.split(r": ")
    count_delim = (len(regex_tok)-1)*2
    if(count_delim < 0):
        return None
    # we now calculate the weights for each regex token:
    weight_d = float( len(regex) - count_delim )
    weights = [ len(tok)/weight_d for tok in regex_tok ]
    # and now the weights for each regex combination:
    combos = list()
    for i in range( len(regex_tok)+1 ):
        combos += list(itertools.combinations(regex_tok, i))
    combos.remove( () )

    # We create a mapping from regex to scoring weight
    weight_map = {}
    for comb in combos:
        weight_sum = 0
        for c in comb:
            ind = regex_tok.index(c)
            weight_sum += weights[ind]
        weight_map[': '.join(comb)] = weight_sum
    return weight_map




def main():
    # Gather query terms and regex patterns:
    user = input("Enter StackExchange query terms: ")
    regex_str = input("Search Regex of your error: ")

    # Created mapping from regex combinations to relative weights
    mapping = regex_weights(regex_str)

    mapping_ind = [ rx for rx in mapping.keys() ]
    regexs = [ re.compile( r".*" + rx + r".*", flags=re.I) for rx in mapping_ind ]

    result = stackx_run(user.strip())
    with open("result_dump.json", "w+") as jsdump:
        jsdump.write( json.dumps(result, indent=2) )
    print("results written to result_dump.json")

#    result = {}
#    with open("result_dump.json", "r") as jsdump:
#        result = json.loads(jsdump.read())
    
    # We now iterate through each response and search for our regex pattern
    relevant = []
    for forum in result.keys():
        site = result[forum]
        for page in site.values():
            items = page["items"]
            for item in items:
                i=0
                weight=0
                for regex in regexs:
                    if regex.search(item["body"]) and mapping[mapping_ind[i]] > weight:
                        weight = mapping[mapping_ind[i]]
                    item["weight"] = weight
                    relevant.append(item)
                    i += 1
    
    relevant = [ it for it in relevant if it["weight"] > 0.3 ]
    relevant.sort( key=lambda x: x["weight"])
    rel_links = set([ it["link"] for it in relevant ])
    print(rel_links)
    print( "StackExchange: " + str(len(rel_links)) )

main()
