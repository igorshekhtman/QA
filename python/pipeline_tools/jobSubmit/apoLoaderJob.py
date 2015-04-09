#=========================================================================================
#========================== apoLoaderJob.py ==============================================
#=========================================================================================
#
# PROGRAM:         apoLoaderJob.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    24-Mar-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of imitating
#			"submit work" coordinator functionality.
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
APO_FILENAME = ""
CATEGORY = "standard"
OPERATION = "pipeline"
BATCH = "apoLoaderJob"
PRIORITY = "5"


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
    print (">>> MISSING REQUIRED PARAMETERS: ENVIRONMENT, ORGID and APO FILE-NAME <<<")
    print ("----------------------------------------------------------------------------")
    print ("* Usage:")
    print ("* python2.7 apoLoaderJob.py arg1 arg2 arg3 arg4 arg5 arg6 arg7")
    print ("*")
    print ("* Required paramaters:")
    print ("* --------------------")
    print ("* arg1 - environment (staging or production) / help")
    print ("* arg2 - orgID (ex. 370)")
    print ("* arg3 - APO filename (ex. document13.APO)")
    print ("*")
    print ("* Optional paramaters:")
    print ("* --------------------")
    print ("* arg4 - category")
    print ("* arg5 - operation")
    print ("* arg6 - batch")
    print ("* arg7 - priority")
    print ("----------------------------------------------------------------------------")
    print ("\n")
    quit()
#=========================================================================================

def checkForPassedArguments():
    # Arg1 - environment (required) / help
    # Arg2 - orgID (required)
    # Arg3 - APO filename
    
    
    global EMAIL, PASSW, AUTHHOST, TOKEHOST, PIPEHOST
    global JOBID, ENVIRONMENT, ORGID
    global APO_FILENAME, CATEGORY, OPERATION, BATCH, PRIORITY
    
    
    if (len(sys.argv) < 4) or (str(sys.argv[1]).upper() == "HELP") or \
        (str(sys.argv[1]).upper() == "--HELP") or (str(sys.argv[1]).upper() == "-H") or \
        (str(sys.argv[1]).upper() == "-HELP") or (str(sys.argv[1]).upper() == "--H"):
        outputMissingArgumentsandAbort()
    else:
        ENVIRONMENT = str(sys.argv[1])
        ORGID = str(sys.argv[2])
        APO_FILENAME = str(sys.argv[3])
        if (len(sys.argv) > 4):
            CATEGORY = str(sys.argv[4])
            if (len(sys.argv) > 5):
                OPERATION = str(sys.argv[5])
                if (len(sys.argv) > 6):
                    BATCH = str(sys.argv[6])
                    if (len(sys.argv) > 7):
                        PRIORITY = str(sys.argv[7])


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
    # TODO: hit a customer endpoint on the user account service for the customer org name
    idString = str(id)
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
    delimiter = ','
    input_string = input_string.split(delimiter)
    #input_string = json.dumps(input_string)
    #print input_string
    #print len(input_string)
    #print len(input_string)
    #print input_string
    
    #if len(input_string) < 2:
    if input_string == ['']:
        validation_string = "Some of the required paramaters are missing, please try again ..."
    else:
        validation_string = "success"
    #for i in range (0,len(input_string)):
    #	print AV_JOBS[input_string[i]]
    #quit()
    
    return(validation_string)
#=========================================================================================

def submitWorkToCoordinator():
    global TOKEN
        
    print ("----------------------------------------------------------------------------")
    print (">>> SUBMIT WORK TO COORDINATOR <<<")
    print ("----------------------------------------------------------------------------")
    
    url = PIPEHOST+"/pipeline/coord/jobs?orgID="+ORGID+""
    if CATEGORY > "":
        url = url + "&category="+CATEGORY+""
    if OPERATION > "":
        url = url + "&operation="+OPERATION+""
    if BATCH > "":
        url = url + "&batch="+BATCH+""
    if PRIORITY > "":
        url = url + "&priority="+PRIORITY+""

    referer = PIPEHOST
    
    HEADERS = {	'Connection': 'keep-alive', \
                'Content-Type': 'application/octet-stream', \
                'Content-Length': '48', \
                'Referer': referer, \
                'Accept': '*/*', \
                'Authorization': 'Apixio ' + TOKEN}

    FILES = {'file': open(APO_FILENAME, 'rb')}

    response = requests.post(url, files=FILES, headers=HEADERS)
    
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
    print ("* ORGID                    = %s" % ORGID)
    print ("* APO_FILENAME             = %s" % APO_FILENAME)
    print ("* CATEGORY                 = %s" % CATEGORY)
    print ("* OPERATION                = %s" % OPERATION)
    print ("* BATCH                    = %s" % BATCH)
    print ("* PRIORITY                 = %s" % PRIORITY)
    print ("*")
    print ("* RECEIVED STATUS CODE     = %s" % statuscode)
    print ("****************************************************************************")

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)

submitWorkToCoordinator()

#============================ THE END ====================================================