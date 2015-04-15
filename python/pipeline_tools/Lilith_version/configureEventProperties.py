#=========================================================================================
# configure event properties tool
#
# author: lschneider
# created: Apr 13, 2015
#=========================================================================================

import sys, os
import getpass
import json
import requests
requests.packages.urllib3.disable_warnings() # was getting this : InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

from apxadmin import *

DEBUG = False

tool_name = "configure event properties"

#=========================================================================================

def list_versions(environment, external_token):
    org_id = ask_for_org_id()

    endpoint = "/pipeline/event/versions"
    referer = pas(environment)
    url = referer + endpoint
    if org_id > "": url += "?orgID=" + org_id
    
    if DEBUG: print ("DEBUG: calling GET "+ url);

    token = token_swap(environment, external_token)
    
    DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + token}
    HEADERS = {	'Connection': 'keep-alive', 'Referer': referer, 'Authorization': 'Apixio ' + token}
    response = requests.get(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    
    if statuscode is not 200:
        print ("Error getting versions.")

    version_list = str(response.text).strip().split("\n")

    width = 6
    for i in range(len(version_list)%width, width):
        version_list.append(" ")
    height = len(version_list)/width

    print("\nAvailable " + org_id + " property versions:")
    for c1,c2,c3,c4,c5,c6 in zip(version_list[:height],
                                 version_list[height:2*height],
                                 version_list[2*height:3*height],
                                 version_list[3*height:4*height],
                                 version_list[4*height:5*height],
                                 version_list[5*height:]):
        print '{:<15}{:<15}{:<15}{:<15}{:<15}{:<}'.format(c1,c2,c3,c4,c5,c6)

#=========================================================================================

def view_properties(environment, external_token):
    org_id = ask_for_org_id()

    version = raw_input("Enter the properties version you would like to view ('current' for the latest version).\n>>> ")
    endpoint = "/pipeline/event/properties/" + version.strip()
    referer = pas(environment)
    url = referer + endpoint
    if org_id > "": url += "?orgID=" + org_id
    
    if DEBUG: print ("DEBUG: calling GET "+ url);
    
    token = token_swap(environment, external_token)

    DATA    = { 'Referer': referer, 'Authorization': 'Apixio ' + token}
    HEADERS = {	'Connection': 'keep-alive',
                'Referer': referer,
                'Authorization': 'Apixio ' + token}
    response = requests.get(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))

    print "\n"
    print response.text

#=========================================================================================

def read_properties():
    filename = raw_input("What is the name of the file to read the new properties from?\n>>> ")
    if len(filename) == 0: read_properties()
    if filename.upper()[0] == "Q": quit()

    model_filename = ""
    properties = []

    print("Reading file " + filename + "...")
    properties_file = open(filename, 'rb')
    for line in properties_file:
        if line[0] != "#" and "$modelFile" in line:
            model_filename = line.strip().split("=")[1]
        if line[0] != "#" and len(line.split("=")) == 2:
            properties.append(line.strip())

    return properties, model_filename

#=========================================================================================

def upload_config(environment, external_token, save_or_update):
    org_id = ask_for_org_id()
    properties, model = read_properties()
    
    print ("Are these properties correct? (y/n)\n")
    for p in properties: print p
    if "Y" not in raw_input("\n>>> ").upper(): quit()
    
    FILES = {}

    endpoint = "/pipeline/event/properties/" + save_or_update
    if model > "":
        endpoint += "/" + model
        FILES = {'file': open(model, 'rb')}
    referer = pas(environment)
    url = referer + endpoint + "?"
    if org_id > "": url += "orgID=" + org_id
    for p in properties: url += "&" + p

    if DEBUG: print ("DEBUG: calling POST "+ url);
    
    token = token_swap(environment, external_token)

    HEADERS = {	'Connection': 'keep-alive',
                'Referer': referer,
                'Content-Type': 'application/octet-stream',
                'Content-Length': '48',
                'Authorization': 'Apixio ' + token}
    response = requests.post(url, files=FILES, headers=HEADERS)
    statuscode = response.status_code
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    if statuscode != 200: print ("ERROR: could not " + save_or_update + " properties. Check your file and try again.")

#=========================================================================================

def update_config(environment, external_token):
    upload_config(environment, external_token, "update")

def save_config(environment, external_token):
    upload_config(environment, external_token, "save")

#=========================================================================================

def delete_config(environment, external_token):
    org_id = ask_for_org_id()
    
    version = raw_input("Enter the properties version you would like to delete.\n>>> ")
    endpoint = "/pipeline/event/properties/" + version.strip()
    referer = pas(environment)
    url = referer + endpoint
    if org_id > "": url += "?orgID=" + org_id
    
    if DEBUG: print ("DEBUG: calling DELETE "+ url);
    
    token = token_swap(environment, external_token)
    
    DATA    = { 'Referer': referer, 'Authorization': 'Apixio ' + token}
    HEADERS = {	'Connection': 'keep-alive',
                'Referer': referer,
                'Authorization': 'Apixio ' + token}
    response = requests.delete(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))
    if statuscode != 200: print ("ERROR: delete failed")

#=========================================================================================

actions = { "list":list_versions,
            "view":view_properties,
            "save":save_config,
            "update":update_config,
            "delete":delete_config }

if __name__ == "__main__":
    action_loop(actions, tool_name)

#=========================================================================================