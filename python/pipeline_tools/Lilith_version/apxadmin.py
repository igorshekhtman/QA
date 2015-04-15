#=========================================================================================
# apxadmin module
#
# author: lschneider
# created: Apr 14, 2015
#=========================================================================================

import sys, os
import getpass
import json
import requests
requests.packages.urllib3.disable_warnings() # was getting this : InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

DEBUG = False

#=========================================================================================

auth_stg = "https://useraccount-stg.apixio.com:7076"
token_stg = "https://tokenizer-stg.apixio.com:7075"
pas_stg = "http://coordinator-stg.apixio.com:8066"
auth_prd = "https://useraccount-prd.apixio.com:7076"
token_prd = "https://tokenizer-prd.apixio.com:7075"
pas_prd = "https://coordinator.apixio.com:8066"

prod = "production"
stag = "staging"

def auth(environment): # user account service
    if environment == prod: return auth_prd
    return auth_stg

def tokenizer(environment):
    if environment == prod: return token_prd
    return token_stg

def pas(environment): # pipeline admin service
    if environment == "production": return pas_prd
    return pas_stg

#=========================================================================================

def get_environment():
    i = raw_input("\nAre you logging in to staging or production? \n>>> ")
    
    if len(i) > 0 and i.upper()[0] == "Q":
        quit()
    if "PROD" in i.upper() or "PRD" in i.upper():
        return prod
    if "STAG" in i.upper() or "STG" in i.upper():
        return stag
    
    return get_environment()

#=========================================================================================

def ask_for_org_id():
    org_id = raw_input("\nEnter the ID of the organization or hit return for default.\n>>> ")
    if len(org_id) > 0 and org_id.upper()[0] == "Q": quit()
    return org_id

#=========================================================================================

def login(environment):
    u = raw_input("\nPlease enter your " + environment+ " username...\n>>> ")
    if u > "" and u.upper()[0] == "Q": quit()
    p = getpass.getpass("... and password.\n>>> ")
    if p > "" and p.upper()[0] == "Q": quit()
    
    endpoint = "/auths"
    referer = auth(environment)
    url = referer + endpoint
    
    DATA    = {'Referer': referer, 'email': u, 'password': p}
    HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
    
    response = requests.post(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    
    if statuscode is not 200:
        print ("Error logging in, please try again.")
        return login(environment)
    
    userjson = response.json()
    token = userjson.get("token")

    if DEBUG: print ("DEBUG: got token: " + token)
    return u, token

#=========================================================================================

def token_swap(environment, external_token):
    endpoint = "/tokens"
    referer = tokenizer(environment)
    url = referer + endpoint
    
    DATA    = {'Referer': referer, 'Authorization': 'Apixio ' + external_token}
    HEADERS = { 'Connection': 'keep-alive',
                'Content-Length': '48',
                'Referer': referer,
                'Authorization': 'Apixio ' + external_token}

    response = requests.post(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    
    if statuscode is not 201:
        print ("Error Authenticating. Exiting...")
        quit()

    userjson = response.json()
    token = userjson.get("token")
    
    if DEBUG: print ("DEBUG: got token: " + token)
    return token

#=========================================================================================

def get_org_name(id, environment, external_token):
    try:
        idString = str(id).strip()
        blankUUID = 'O_00000000-0000-0000-0000-000000000000'
        url = auth(environment) + "/customer/" + blankUUID[0:-(len(idString))] + idString
        
        if DEBUG: print ("DEBUG: Calling GET " + url)
        
        token = token_swap(environment, external_token)
        referer = auth(environment)
        HEADERS = { 'Content-Type': 'application/json',
                    'Referer': referer,
                    'Authorization': 'Apixio ' + token}
        response = requests.get(url, data={}, headers=HEADERS)
        statuscode = response.status_code
        
        if DEBUG: print ("DEBUG: Got response code: " + str(statuscode))
        
        customerOrg = response.json()
        
        return (customerOrg['name'])
    except:
        if DEBUG: print("DEBUG: ", sys.exc_info()[0])
        return (id)

#=========================================================================================

def action_loop(actions, tool_name):
    os.system('clear')
    print ("Welcome to the " + tool_name + " tool.\nEnter Q at any time to quit.")

    environment = get_environment()
    print ("Environment set to " + environment + ".")

    username, token = login(environment)
    print ("You are now logged in as " + username + ".")

    available_commands = "\nAvailable commands: " + str(actions.keys())
    i = ""
    print available_commands
    while len(i) == 0 or i.upper()[0] != "Q":
        try:
            actions[i.lower().strip()](environment, token)
            print available_commands
        except:
            if i > "":
                print ("ERROR: Invalid command.")
                if DEBUG: print("DEBUG: ", sys.exc_info()[0])
                print available_commands
        i = raw_input(">>> ")

#=========================================================================================