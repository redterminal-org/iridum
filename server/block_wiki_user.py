"""
    block_user.py

    MediaWiki API Demos
    Demo of `Block` module: sending POST request to block user
    MIT license
"""

import requests
from evennia import settings

def block_wiki_user(username):
    S = requests.Session()
    
    URL = "https://iridum.redterminal.org/api.php"
    
    # Step 1: GET request to fetch login token
    PARAMS_0 = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }
    
    R = S.get(url=URL, params=PARAMS_0)
    DATA = R.json()
    
    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
    
    # Step 2: POST request to log in. Use of main account for login is not
    # supported. Obtain credentials via Special:BotPasswords
    # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
    PARAMS_1 = {
        "action": "login",
        "lgname": "BlockBot",
        "lgpassword": settings.PASS_WIKI_BLOCKBOT,
        "lgtoken": LOGIN_TOKEN,
        "format": "json"
    }
    
    R = S.post(URL, data=PARAMS_1)
    
    # Step 3: GET request to fetch CSRF token
    PARAMS_2 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }
    
    R = S.get(url=URL, params=PARAMS_2)
    DATA = R.json()
    
    CSRF_TOKEN = DATA['query']['tokens']['csrftoken']
    
    # Step 4: POST request to block user
    PARAMS_3 = {
        "action": "block",
        "user": username,
        "expiry": "never",
        "reason": "Blocked from Wiki Usage",
        "token": CSRF_TOKEN,
        "format": "json"
    }
    
    R = S.post(URL, data=PARAMS_3)
    DATA = R.json()
    
    try:
        _ = DATA["block"]
        return True
    except KeyError:
        return False

def unblock_wiki_user(username):
    S = requests.Session()
    
    URL = "https://iridum.redterminal.org/api.php"
    
    # Step 1: GET request to fetch login token
    PARAMS_0 = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }
    
    R = S.get(url=URL, params=PARAMS_0)
    DATA = R.json()
    
    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
    
    # Step 2: POST request to log in. Use of main account for login is not
    # supported. Obtain credentials via Special:BotPasswords
    # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
    PARAMS_1 = {
        "action": "login",
        "lgname": "BlockBot",
        "lgpassword": settings.PASS_WIKI_BLOCKBOT,
        "lgtoken": LOGIN_TOKEN,
        "format": "json"
    }
    
    R = S.post(URL, data=PARAMS_1)
    
    # Step 3: GET request to fetch CSRF token
    PARAMS_2 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }
    
    R = S.get(url=URL, params=PARAMS_2)
    DATA = R.json()
    
    CSRF_TOKEN = DATA['query']['tokens']['csrftoken']
    
    # Step 4: POST request to block user
    PARAMS_3 = {
        "action": "unblock",
        "user": username,
        "reason": "unblocked from Wiki usage",
        "token": CSRF_TOKEN,
        "format": "json"
    }
    
    R = S.post(URL, data=PARAMS_3)
    DATA = R.json()
    
    try:
        _ = DATA["unblock"]
        return True
    except KeyError:
        return False
