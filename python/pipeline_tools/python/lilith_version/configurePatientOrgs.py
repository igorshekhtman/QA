#=========================================================================================
# configure organizations tool
#
# author: lschneider
# created: Apr 15, 2015
#=========================================================================================

import sys, os
import getpass
import json
import requests
requests.packages.urllib3.disable_warnings() # was getting this : InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

from apxadmin import *

DEBUG = True

tool_name = "configure organizations"
actions = {}

#=========================================================================================

def list_configured_orgs(environment, external_token):
    print ("\nGetting a list of currently configured organizations on " + environment + "...")
    
    endpoint = "/pipeline/coord/orgs"
    referer = pas(environment)
    url = pas(environment) + endpoint
    
    if DEBUG: print ("DEBUG: Calling GET " + url)

    token = token_swap(environment, external_token)
    HEADERS = {	'Connection': 'keep-alive',
                'Referer': referer,
                'Authorization': 'Apixio ' + token }
    response = requests.get(url, data={}, headers=HEADERS)
    statuscode = response.status_code

    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    
    orgs = response.json()

    print ("OrgID:\t\tOrg Name:\t\t\tEnabled:\tPriority:")
    print ("======\t\t=========\t\t\t========\t=========")
    for org in sorted(orgs, key=lambda k: k['name']):
        print ("%s\t%s\t%s\t\t%s" % (org['name'].ljust(10),
                                     get_org_name(org['name'], environment, external_token).ljust(25),
                                     org['enabled'],
                                     org['priority'] ))

actions['list'] = list_configured_orgs

#=========================================================================================

def put_org_config(environment, external_token, config):
    endpoint = "/pipeline/coord/org/" + config['name'] # 'name' in the org json is the care opt id currently
    referer = pas(environment)
    url = pas(environment) + endpoint
    
    if DEBUG: print ("DEBUG: Calling PUT " + url)
    
    DATA = json.dumps(config)
    token = token_swap(environment, external_token)
    HEADERS = {	'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Content-Length': '48',
                'Referer': referer,
                'Accept': '*/*',
                'Authorization': 'Apixio ' + token }
    response = requests.put(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code

    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    
    if statuscode == 200:
        print ("\nSuccessfully updated... ")
        print ("OrgID:\t\tOrg Name:\t\t\tEnabled:\tPriority:")
        print ("======\t\t=========\t\t\t========\t=========")
        print ("%s\t%s\t%s\t\t%s" % (config['name'].ljust(10),
                                     get_org_name(config['name'], environment, external_token).ljust(25),
                                     config['enabled'],
                                     config['priority'] ))

#=========================================================================================

def get_org_config(environment, external_token, id):
    endpoint = "/pipeline/coord/org/" + id
    referer = pas(environment)
    url = pas(environment) + endpoint
    
    if DEBUG: print ("DEBUG: Calling GET " + url)
    
    token = token_swap(environment, external_token)
    HEADERS = {	'Connection': 'keep-alive',
                'Referer': referer,
                'Authorization': 'Apixio ' + token }
    response = requests.get(url, data={}, headers=HEADERS)
    statuscode = response.status_code
    
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))

    return response.json()

#=========================================================================================

def set_org_state(environment, external_token, disable_or_enable):
    id = raw_input("What is the ID of the organization you would like to " + disable_or_enable + "?\n>>> ")
    while id == "": id = raw_input(">>> ")
    if id > "" and id.upper() == "Q": quit()
    id = id.strip()
    
    config = {}
    try: config = get_org_config(environment, external_token, id)
    except: config = {'enabled':True, 'priority':5, 'name':id}

    config['enabled'] = (disable_or_enable == "enable")
    put_org_config(environment, external_token, config)

def disable_org(environment, external_token):
    set_org_state(environment, external_token, "disable")

def enable_org(environment, external_token):
    set_org_state(environment, external_token, "enable")

actions['disable'] = disable_org
actions['enable'] = enable_org

#=========================================================================================

def set_org_priority(environment, external_token):
    id = raw_input("What is the ID of the organization you would like to reprioritize?\n>>> ")
    while id == "": id = raw_input(">>> ")
    if id > "" and id.upper() == "Q": quit()
    id = id.strip()
    
    pri = raw_input("What priority [1-9] would you like to assign to " + get_org_name(id, environment, external_token) + "?\n>>> ")
    while pri == "": pri = raw_input(">>> ")
    if pri > "" and pri.upper()[0] == "Q": quit()
    pri = int(pri.strip())
    if pri < 1 or pri > 9: print ("ERROR: bad priority"); quit()
    
    config = {}
    try: config = get_org_config(environment, external_token, id)
    except: config = {'enabled':True, 'priority':5, 'name':id}
    
    config['priority'] = pri
    
    put_org_config(environment, external_token, config)

actions['priority'] = set_org_priority

#=========================================================================================

if __name__ == "__main__":
    action_loop(actions, tool_name)

#=========================================================================================