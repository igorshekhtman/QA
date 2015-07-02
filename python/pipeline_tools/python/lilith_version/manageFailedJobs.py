#=========================================================================================
# manage failed jobs tool
#
# author: lschneider
# created: Apr 14, 2015
#=========================================================================================

import sys, os
import getpass
import json
import requests
requests.packages.urllib3.disable_warnings() # was getting this : InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

from apxadmin import *

DEBUG = False

tool_name = "manage failed jobs"
actions = {}

#=========================================================================================

def get_failed_jobs(environment, external_token):
    endpoint = "/pipeline/coord/jobs/failed"
    referer = pas(environment)
    url = pas(environment) + endpoint
    
    if DEBUG: print ("DEBUG: Calling GET " + url)
    
    token = token_swap(environment, external_token)
    HEADERS = { 'Connection': 'keep-alive',
                'Referer': referer,
                'Content-Type': 'application/octet',
                'Content-Length': '48',
                'Authorization': 'Apixio ' + token }
    response = requests.get(url, data={}, headers=HEADERS)
    statuscode = response.status_code
    
    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))

    return response.json()

#=========================================================================================

def list_failed_jobs(environment, external_token):
    print ("Getting list of failed jobs on " + environment + "...")

    jobs = get_failed_jobs(environment, external_token)

    print ("Job ID:\t\tOrg ID:\t\tOrg Name:\t\tBatch ID:\t\t\t\tActivity Name:")
    print ("=======\t\t=======\t\t=========\t\t=========\t\t\t\t==============")
    for job in sorted(jobs, key=lambda k: k['jobID']):
        print ("%s\t%s\t%s\t%s\t%s" % (str(job['jobID']).ljust(10),
                                       job['orgID'].ljust(10),
                                       get_org_name(job['orgID'], environment, external_token).ljust(20),
                                       str(job['batchID']).ljust(35),
                                       job['activityName']))

actions['list'] = list_failed_jobs

#=========================================================================================

def get_job_ids(environment, external_token):
    input = raw_input("Enter a comma separated list of job IDs \n"
                      + "\tor a filter of the form key=value where the key is jobID, orgID, batchID, or acivityName."
                      + "\n>>> ")
    while input == "": input = raw_input(">>> ")
    if input > "" and input.upper()[0] == "Q": quit()
    jobids = []
    
    if "=" in input:
        input = input.split("=")
        if len(input) == 2:
            key, value = input[0].strip(), input[1].strip()
            filtered_jobs = filter(lambda x: key in x and x[key] == value,
                                   get_failed_jobs(environment, external_token))
            for job in sorted(filtered_jobs, key=lambda k: k['jobID']):
                jobids.append(job['jobID'])
        else:
            print ("Filter must contain one key=value pair, please try again ...")
    else:
        input = input.split(",")
        for i in input:
            jobids.append(i.strip())

    return jobids

#=========================================================================================

def submit(environment, external_token, resubmit_or_ignore):
    endpoint = "/pipeline/coord/jobs/" + resubmit_or_ignore
    referer = pas(environment)
    url = pas(environment) + endpoint
    
    if DEBUG: print ("DEBUG: Calling POST " + url)

    jobids = get_job_ids(environment, external_token)
    DATA = json.dumps(jobids)
    
    print ("Are you sure you want to " + resubmit_or_ignore + " these jobs? (y/n)\n")
    print ("Job IDs: " + str(DATA))
    if "Y" not in raw_input("\n>>> ").upper(): quit()
    
    token = token_swap(environment, external_token)
    HEADERS = { 'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Content-Length': '48',
                'Referer': referer,
                'Accept': '*/*',
                'Authorization': 'Apixio ' + token }

    response = requests.post(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code

    if DEBUG: print ("DEBUG: got response code: " + str(statuscode))

#=========================================================================================

def resubmit_jobs(environment, external_token):
    submit(environment, external_token, "resubmit")

def ignore_jobs(environment, external_token):
    submit(environment, external_token, "ignore")

actions['resubmit'] = resubmit_jobs
actions['ignore'] = ignore_jobs

#=========================================================================================

if __name__ == "__main__":
    action_loop(actions, tool_name)

#=========================================================================================