#=========================================================================================
#========================== resubmitJobComplete.py =======================================
#=========================================================================================
#
# PROGRAM:         resubmitJobComplete.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com, Lilith Scneider lschneider@apixio.com
# DATE CREATED:    18-Mar-2015
# INITIAL VERSION: 1.1.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of listing failed
#            and re-submitting previously failed Hadoop Job(s) from the list.
#          New feature for 1.1.0: ignoring jobs
#
#=========================================================================================
import requests
requests.packages.urllib3.disable_warnings() # was getting this : InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
import time
import datetime
import csv
import operator
import random
import re
import sys, os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from time import gmtime, strftime, localtime
import calendar
import mmap
#============================ GLOBAL VARIABLES ===========================================
# Assigning default values
EMAIL="ishekhtman@apixio.com"
PASSW="apixio.123"
AUTHHOST="https://useraccount-stg.apixio.com:7076"
TOKEHOST="https://useraccount-stg.apixio.com:7075"
PIPEHOST="http://coordinator-stg.apixio.com:8066"

# Required paramaters:
ENVIRONMENT = "staging" # default value is staging
ORGID = ""
JOBID = ""


ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
requestdenied = 400
forbidden = 403
notfound = 404
intserveror = 500
servunavail = 503

#============================ FUNCTIONS ==================================================
def outputMissingArgumentsandAbort():
    print ("----------------------------------------------------------------------------")
    print (">>> MISSING REQUIRED PARAMETERS: ENVIRONMENT & JOB-NUMBER(S) <<<")
    print ("----------------------------------------------------------------------------")
    print ("* Usage:")
    print ("* python2.7 resubmitJobComplete.py arg1 arg2")
    print ("*")
    print ("* Required paramaters:")
    print ("* --------------------")
    print ("* arg1 - environment (staging or production) / help")
    print ("*")
    print ("* Optional paramaters:")
    print ("* --------------------")
    print ("* arg2 - orgID (ex. 370)")    
    print ("----------------------------------------------------------------------------")
    print ("\n")
    
    quit()

#=========================================================================================

def checkForPassedArguments():
    # Arg1 - environment (required) / help
    # Arg2 - orgID (optional), comma separated list of jobIDs


    global EMAIL, PASSW, AUTHHOST, TOKEHOST, PIPEHOST
    global JOBID, ENVIRONMENT, ORGID

    #print     len(sys.argv)
    #print str(sys.argv[1])
    #quit()
    
    if (len(sys.argv) < 2) or (str(sys.argv[1]).upper() == "HELP") or \
        (str(sys.argv[1]).upper() == "--HELP") or (str(sys.argv[1]).upper() == "-H") or \
        (str(sys.argv[1]).upper() == "-HELP") or (str(sys.argv[1]).upper() == "--H"):
        outputMissingArgumentsandAbort()
    else:
        ENVIRONMENT=str(sys.argv[1])
        if (len(sys.argv) > 2):
            ORGID=str(sys.argv[2])
    

    if (ENVIRONMENT.upper() == "P") or (ENVIRONMENT.upper() == "PROD") or (ENVIRONMENT.upper() == "PRODUCTION"):
        ENVIRONMENT = "production"
        EMAIL="ishekhtman@apixio.com"
        PASSW="apixio.123"
        AUTHHOST="https://useraccount-prd.apixio.com:7076"
        TOKEHOST="https://tokenizer-prd.apixio.com:7075"
        PIPEHOST="http://coordinator-prd.apixio.com:8066"
    else:  # STAGING ENVIRONMENT
        ENVIRONMENT = "staging"
        EMAIL="ishekhtman@apixio.com"
        PASSW="apixio.123"
        AUTHHOST="https://useraccount-stg.apixio.com:7076"
        TOKEHOST="https://tokenizer-stg.apixio.com:7075"
        PIPEHOST="http://coordinator-stg.apixio.com:8066"

#=========================================================================================

def getOrgName(id):
    try:
        idString = str(id).strip()
        blankUUID = 'O_00000000-0000-0000-0000-000000000000'
        url = AUTHHOST+"/customer/"+blankUUID[0:-(len(idString))]+idString

        referer = AUTHHOST
        HEADERS = { 'Content-Type': 'application/json', \
                    'Referer': referer, \
                    'Authorization': 'Apixio ' + TOKEN}
        response = requests.get(url, data={}, headers=HEADERS)
        statuscode = response.status_code

        customerOrg = response.json()

        return (customerOrg['name'])
    except:
        return (id)
    
#=========================================================================================        

def outputGlobalVariableSettings():

    print ("----------------------------------------------------------------------------")
    print (">>> GLOBAL VARIABLE SETTINGS <<<")
    print ("----------------------------------------------------------------------------")
    print ("* ENVIRONMENT              = %s" % ENVIRONMENT)
    print ("* ROOT USERNAME            = %s" % EMAIL)
    print ("* PASSWORD                 = %s" % PASSW)
    print ("* AUTHENTICATION HOST URL  = %s" % AUTHHOST)
    print ("* TOKENIZER HOST URL       = %s" % TOKEHOST)
    print ("* COORDINATOR HOST URL     = %s" % PIPEHOST)
    print ("*")
    print ("* ORGID(S)                 = %s" % ORGID)
    print ("****************************************************************************")

#=========================================================================================

def obtainExternalToken(un, pw, exp_statuscode, tc, step):

    #print ("\n----------------------------------------------------------------------------")
    #print (">>> OBTAIN EXTERNAL TOKEN <<<")
    #print ("----------------------------------------------------------------------------")

    #8076
    #7076
    external_token = ""
    url = AUTHHOST+"/auths"
    #url = 'https://useraccount-stg.apixio.com:7076/auths'
    referer = AUTHHOST      
    #token=$(curl -v --data email=$email --data password="$passw" ${authhost}/auths | cut -c11-49)
    
    DATA =    {'Referer': referer, 'email': EMAIL, 'password': PASSW} 
    HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
    
    response = requests.post(url, data=DATA, headers=HEADERS) 

    statuscode = response.status_code
    #print statuscode
    #quit()

    userjson = response.json()
    if userjson is not None:
        external_token = userjson.get("token") 
        print ("* USERNAME                 = %s" % un)
        print ("* PASSWORD                 = %s" % pw)
        print ("* URL                      = %s" % url)
        print ("* EXTERNAL TOKEN           = %s" % external_token)
        print ("* EXPECTED STATUS CODE     = %s" % exp_statuscode)
        print ("* RECEIVED STATUS CODE     = %s" % statuscode)
        print ("****************************************************************************")
            
    return (external_token)

#=========================================================================================
def obtainInternalToken(un, pw, exp_statuscode, tc, step):
    global TOKEN
    
    print ("----------------------------------------------------------------------------")
    print (">>> OBTAIN EXTERNAL AND EXCHANGE FOR INTERNAL TOKEN <<<")
    print ("----------------------------------------------------------------------------")
    
    
    #TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
    external_token = obtainExternalToken(un, pw, exp_statuscode, tc, step)
    url = TOKEHOST+"/tokens"
    referer = TOKEHOST
    DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + external_token} 
    HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + external_token}
    response = requests.post(url, data=DATA, headers=HEADERS) 
    userjson = response.json()
    if userjson is not None:
        TOKEN = userjson.get("token")
    else:
        TOKEN = "Not Available"
    statuscode = response.status_code
    print ("* USERNAME                 = %s" % un)
    print ("* PASSWORD                 = %s" % pw)
    print ("* TOKENIZER URL            = %s" % url)
    print ("* EXTERNAL TOKEN           = %s" % external_token)
    print ("* INTERNAL TOKEN           = %s" % TOKEN)
    print ("* EXPECTED STATUS CODE     = %s" % exp_statuscode)
    print ("* RECEIVED STATUS CODE     = %s" % statuscode)


#=========================================================================================
def validateUpdateString(input_string):
    
    if "=" in input_string:
        input_string = input_string.split("=")
        if len(input_string) == 2:
            validation_string = "filter"
        else:
            validation_string = "Filter must contain one key=value pair, please try again ..."

    else:
        delimiter = ','
        input_string = input_string.split(delimiter)
        if input_string == ['']:
            validation_string = "Some of the required paramaters are missing, please try again ..."
        else:
            validation_string = "success"
            for i in input_string:
                if i not in AV_JOBS:
                    validation_string = "Invalid line number '%s', please try again ..." % i

    return(validation_string)
#=========================================================================================

def jobsByLineNumber(input_string): # input: comma separated line numbers
    global TOKEN

    jobIds = []
    delimiter = ','
    input_string = input_string.split(delimiter)
    for i in range (0,len(input_string)):
        jobIds.append(AV_JOBS[input_string[i]])

    return(jobIds)

#=========================================================================================

def jobsByFilter(job_filter): # input: key=value
    global TOKEN
    
    job_filter = job_filter.split("=");
    key, value = job_filter[0], job_filter[1]
    
    filtered_jobs = filter(lambda x: key in x and x[key] == value, ALL_JOBS)
    
    jobIds = []
    for job in sorted(filtered_jobs, key=lambda k: k['jobID']):
        jobIds.append(job['jobID'])
    
    return(jobIds)

#=========================================================================================

def resubmit(jobIdList):
    global TOKEN
    
    print ("----------------------------------------------------------------------------")
    print (">>> RE-SUBMIT JOB(s) <<<")
    print ("----------------------------------------------------------------------------")
    
    url = PIPEHOST+"/pipeline/coord/jobs/resubmit"
    referer = PIPEHOST
    
    HEADERS = { 'Connection': 'keep-alive', \
                'Content-Type': 'application/json', \
                'Content-Length': '48', \
                'Referer': referer, \
                'Accept': '*/*', \
                'Authorization': 'Apixio ' + TOKEN}

    JOBIDS = json.dumps(jobIdList)
    
    DATA = JOBIDS
    
    response = requests.post(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    print ("* ENVIRONMENT              = %s" % ENVIRONMENT)
    print ("* ROOT USERNAME            = %s" % EMAIL)
    print ("* PASSWORD                 = %s" % PASSW)
    print ("* INTERNAL TOKEN           = %s" % TOKEN)
    print ("* AUTHENTICATION HOST URL  = %s" % AUTHHOST)
    print ("* TOKENIZER HOST URL       = %s" % TOKEHOST)
    print ("* COORDINATOR HOST URL     = %s" % PIPEHOST)
    print ("* SUBMIT JOB COMPLETE URL  = %s" % url)
    print ("*")
    print ("* JOB ID(S)                = %s" % JOBIDS)
    print ("*")
    print ("* RECEIVED STATUS CODE     = %s" % statuscode)
    print ("****************************************************************************")

#=========================================================================================

def ignore(jobIdList):
    global TOKEN
    
    print ("----------------------------------------------------------------------------")
    print (">>> IGNORE JOB(s) <<<")
    print ("----------------------------------------------------------------------------")
    
    url = PIPEHOST+"/pipeline/coord/jobs/ignore"
    referer = PIPEHOST
    
    HEADERS = { 'Connection': 'keep-alive', \
                'Content-Type': 'application/json', \
                'Content-Length': '48', \
                'Referer': referer, \
                'Accept': '*/*', \
                'Authorization': 'Apixio ' + TOKEN}

    JOBIDS = json.dumps(jobIdList)
    
    DATA = JOBIDS
    
    response = requests.post(url, data=DATA, headers=HEADERS)
    statuscode = response.status_code
    print ("* ENVIRONMENT              = %s" % ENVIRONMENT)
    print ("* ROOT USERNAME            = %s" % EMAIL)
    print ("* PASSWORD                 = %s" % PASSW)
    print ("* INTERNAL TOKEN           = %s" % TOKEN)
    print ("* AUTHENTICATION HOST URL  = %s" % AUTHHOST)
    print ("* TOKENIZER HOST URL       = %s" % TOKEHOST)
    print ("* COORDINATOR HOST URL     = %s" % PIPEHOST)
    print ("* SUBMIT JOB COMPLETE URL  = %s" % url)
    print ("*")
    print ("* JOB ID(S)                = %s" % JOBIDS)
    print ("*")
    print ("* RECEIVED STATUS CODE     = %s" % statuscode)
    print ("****************************************************************************")

#=========================================================================================
    
def getFailedJobsList():
    global TOKEN, AV_JOBS, INPUT_STRING, ALL_JOBS
    
    print ("----------------------------------------------------------------------------")
    print (">>> GET FAILED JOB(S) LIST <<<")
    print ("----------------------------------------------------------------------------")

    url = PIPEHOST+"/pipeline/coord/jobs/failed"
    if (ORGID > ""):
        url = url + "?"
    if ORGID > "":
        url = url + "&org="+ORGID+""
    
    AV_JOBS = {}
    referer = PIPEHOST
    DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + TOKEN} 
    HEADERS = { 'Connection': 'keep-alive', \
                'Content-Type': 'application/octet', \
                'Content-Length': '48', \
                'Referer': referer, \
                'Authorization': 'Apixio ' + TOKEN}
    response = requests.get(url, data=DATA, headers=HEADERS) 
    statuscode = response.status_code
    jobs = response.json()
    ALL_JOBS = jobs
    
    print ("****************************************************************************")
    print ("* ENVIRONMENT              = %s" % ENVIRONMENT)
    print ("* ROOT USERNAME            = %s" % EMAIL)
    print ("* PASSWORD                 = %s" % PASSW)
    print ("* INTERNAL TOKEN           = %s" % TOKEN)
    print ("* AUTHENTICATION HOST URL  = %s" % AUTHHOST)
    print ("* TOKENIZER HOST URL       = %s" % TOKEHOST)
    print ("* COORDINATOR HOST URL     = %s" % PIPEHOST)
    print ("* SUBMIT JOB COMPLETE URL  = %s" % url)
    print ("*")
    print ("* ORGID                    = %s" % ORGID)
    print ("*")
    print ("* RECEIVED STATUS CODE     = %s" % statuscode)
    print ("****************************************************************************************")
    print ("*                           LIST OF AVAILABLE FAILED JOBS                              *")
    print ("****************************************************************************************")

    print ("Line#:\tJob ID:\tOrg ID:\t\tOrg Name:\t\tBatch ID:\t\tActivity Name:")
    print ("======\t=======\t=======\t\t=========\t\t=========\t\t==============")
    cntr = 0
    for job in sorted(jobs, key=lambda k: k['jobID']):
        #print json.dumps(job, sort_keys=True, indent=0)
        cntr += 1
        print ("%d\t%s\t%s\t%s\t%s\t%s" % (cntr, job['jobID'], job['orgID'].ljust(10), getOrgName(job['orgID']).ljust(20), str(job['batchID']).ljust(20), job['activityName']))
        AV_JOBS.update({ str(cntr): str(job['jobID'])})
    
    print ("-------------------------------------------------------------------------------------------")
    print ("Enter line number(s), comma separated, of the job(s) to resubmit ")
    print ("      or a filter of the form key=value where the key is jobID, orgID, batchID, or acivityName")
    print ("      or IGNORE to remove the next specified set of jobs")
    print ("      or just enter Q to Quit")
    print ("-------------------------------------------------------------------------------------------")
    INPUT_STRING = raw_input("Next command: ")
    if INPUT_STRING.upper() == "IGNORE":
        INPUT_STRING = raw_input("Next ignore command: ")
        if INPUT_STRING.upper() != "Q":
            validation = validateUpdateString(INPUT_STRING)
            if validation.upper() == "SUCCESS":
                ignore(jobsByLineNumber(INPUT_STRING))
            if validation.upper() == "FILTER":
                ignore(jobsByFilter(INPUT_STRING))
            else:
                print (validation)
                raw_input("Press Enter to continue...")
    elif INPUT_STRING.upper() != "Q":
        validation = validateUpdateString(INPUT_STRING)
        if validation.upper() == "SUCCESS":
            resubmit(jobsByLineNumber(INPUT_STRING))
        if validation.upper() == "FILTER":
            resubmit(jobsByFilter(INPUT_STRING))
        else:
            print (validation)
            raw_input("Press Enter to continue...")    

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)

INPUT_STRING=""
while INPUT_STRING.upper() != "Q":
    obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)
    getFailedJobsList()
#============================ THE END ====================================================