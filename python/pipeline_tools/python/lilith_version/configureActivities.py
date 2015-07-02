#=========================================================================================
# configure activities tool
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

DEBUG = False

tool_name = "configure activities"
actions = {}

#=========================================================================================

def list_activities(environment, external_token):
    print ("\nGetting a list of currently configured activities on " + environment + "...")
    
    endpoint = "/pipeline/coord/activities"
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

    activities = response.json()

    print ("Activity Name:\t\t\t\tEnabled:\tPriority:\tSlots:\tBorrowable:\tMax:")
    print ("==============\t\t\t\t========\t=========\t======\t===========\t====")
    for activity in sorted(activities, key=lambda k: k['name']):
        print ("%s\t%s\t\t%s\t\t%s\t%s\t%s" % (activity['name'].ljust(32),
                                               activity['enabled'],
                                               activity['priority'],
                                               activity['totalSlots'],
                                               str(activity['borrowableSlots']).ljust(10),
                                               activity['slotMax']))

actions['list'] = list_activities

#=========================================================================================

def put_activity_config(environment, external_token, config):
    endpoint = "/pipeline/coord/activity/" + config['name']
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
        print ("Activity Name:\t\t\t\tEnabled:\tPriority:\tSlots:\tBorrowable:\tMax:")
        print ("==============\t\t\t\t========\t=========\t======\t===========\t====")
        print ("%s\t%s\t\t%s\t\t%s\t%s\t%s" % (config['name'].ljust(32),
                                               config['enabled'],
                                               config['priority'],
                                               config['totalSlots'],
                                               str(config['borrowableSlots']).ljust(10),
                                               config['slotMax']))

#=========================================================================================

def get_activity_config(environment, external_token, name):
    endpoint = "/pipeline/coord/activity/" + name
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

def set_activity_state(environment, external_token, disable_or_enable):
    act = raw_input("What is the name of the activity you would like to " + disable_or_enable + "?\n>>> ")
    while act == "": act = raw_input(">>> ")
    if act > "" and act.upper() == "Q": quit()
    act = act.strip()

    config = get_activity_config(environment, external_token, act)
    config['enabled'] = (disable_or_enable == "enable")
    put_activity_config(environment, external_token, config)

def disable_activity(environment, external_token):
    set_activity_state(environment, external_token, "disable")

def enable_activity(environment, external_token):
    set_activity_state(environment, external_token, "enable")

actions['disable'] = disable_activity
actions['enable'] = enable_activity

#=========================================================================================

def set_activity_priority(environment, external_token):
    act = raw_input("What is the name of the activity you would like to reprioritize?\n>>> ")
    while act == "": act = raw_input(">>> ")
    if act > "" and act.upper() == "Q": quit()
    act = act.strip()
    
    pri = raw_input("What priority [1-9] would you like to assign to " + act + "?\n>>> ")
    while pri == "": pri = raw_input(">>> ")
    if pri > "" and pri.upper()[0] == "Q": quit()
    pri = int(pri.strip())
    if pri < 1 or pri > 9: print ("ERROR: bad priority"); quit()

    config = get_activity_config(environment, external_token, act)
    config['priority'] = pri
    
    put_activity_config(environment, external_token, config)

actions['priority'] = set_activity_priority

#=========================================================================================

def set_activity_slots(environment, external_token):
    act = raw_input("What is the name of the activity you would like to configure slots for?\n>>> ")
    while act == "": act = raw_input(">>> ")
    if act > "" and act.upper() == "Q": quit()
    act = act.strip()

    new_config = {}
    config = get_activity_config(environment, external_token, act)

    if "Y" in raw_input("Would you like to like to change the total slots allocated for " + act + "? (y/n)\n>>> ").upper():
        t = raw_input("To how many total slots?\n>>> ")
        while t == "": t = raw_input(">>> ")
        if t > "" and t.upper()[0] == "Q": quit()
        t = int(t.strip())
        if t < 0: print ("ERROR: bad slot input"); quit()
        
        new_config['totalSlots'] = t
    
    if "Y" in raw_input("Would you like to like to change the borrowable slots for " + act + "? (y/n)\n>>> ").upper():
        b = raw_input("To how many total slots?\n>>> ")
        while b == "": b = raw_input(">>> ")
        if b > "" and b.upper()[0] == "Q": quit()
        b = int(b.strip())
        if ((b < 0) or ('totalSlots' in new_config.keys() and b > new_config['totalSlots']) or ("%" not in config['totalSlots'] and b > int(config['totalSlots']))):
            print ("ERROR: bad slot input"); quit()
                
        new_config['borrowableSlots'] = b

    if "Y" in raw_input("Would you like to like to change the max slots for " + act + "? (y/n)\n>>> ").upper():
       m = raw_input("To how many total slots?\n>>> ")
       while m == "": m = raw_input(">>> ")
       if m > "" and m.upper()[0] == "Q": quit()
       m = int(m.strip())
       if m < 0: print ("ERROR: bad slot input"); quit()
       
       new_config['slotMax'] = m

    for key in new_config.keys():
        config[key] = str(new_config[key])

    put_activity_config(environment, external_token, config)

actions['slots'] = set_activity_slots

#=========================================================================================

if __name__ == "__main__":
    action_loop(actions, tool_name)

#=========================================================================================