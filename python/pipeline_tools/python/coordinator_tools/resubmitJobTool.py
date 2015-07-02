#=========================================================================================
#========================== resubmitJobTool.py ===========================================
#=========================================================================================
#
# PROGRAM:         resubmitJobTool.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    17-Mar-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of re-submitting
#			Hadoop Job(s).
#
#=========================================================================================
import requests
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

# Optional paramaters:
CATEGORY = "standard"
OPERATION = "pipeline"
BATCH = ""
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
	print (">>> MISSING REQUIRED PARAMETERS: ENVIRONMENT & ORGID <<<")
	print ("----------------------------------------------------------------------------")
	print ("* Usage:")
	print ("* python2.7 resubmitJobTool.py arg1 arg2 arg3 arg4 arg5 arg6")
	print ("*")
	print ("* Required paramaters:")
	print ("* --------------------")
	print ("* arg1 - environment (staging or production) / help")
	print ("* arg2 - orgID (ex. 10000289)")
	print ("*")
	print ("* Optional paramaters:")
	print ("* --------------------")
	print ("* arg3 - category (ex. standard, default - standard)")
	print ("* arg4 - operation (ex. pipeline, default - pipeline)")
	print ("* arg5 - priority (ex. 1-10, default - 5)")
	print ("* arg6 - batch (ex. 370_PipelineSanityTestStaging_03162015170339, default - none)")
	print ("----------------------------------------------------------------------------")
	print ("\n")
	quit()

#=========================================================================================

def checkForPassedArguments():
	# Arg1 - environment (required) / help
	# Arg2 - orgID (required)
	# Arg3 - category (optional)
	# Arg4 - operation (optional)
	# Arg5 - priority (optional)	
	# Arg6 - batch (optional)


	global EMAIL, PASSW, AUTHHOST, TOKEHOST, PIPEHOST
	global ORGID, CATEGORY, OPERATION, BATCH, PRIORITY
	global ENVIRONMENT

	#print ("Setting environment varibales ...\n")
	
	
	if (len(sys.argv) < 3) or (str(sys.argv[1]).upper() == "HELP") or \
		(str(sys.argv[1]).upper() == "--HELP") or (str(sys.argv[1]).upper() == "-H") or \
		(str(sys.argv[1]).upper() == "-HELP") or (str(sys.argv[1]).upper() == "--H"):
		outputMissingArgumentsandAbort()
	else:
		ENVIRONMENT=str(sys.argv[1])
		ORGID=str(sys.argv[2])
		if (len(sys.argv) > 3):
			CATEGORY=str(sys.argv[3])
			if (len(sys.argv) > 4):
				OPERATION=str(sys.argv[4])
				if (len(sys.argv) > 5):
					PRIORITY=str(sys.argv[5])
					if (len(sys.argv) > 6):
						BATCH=str(sys.argv[6])

		

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
	print ("* ORG ID                   = %s" % ORGID)
	print ("* CATEGORY                 = %s" % CATEGORY)
	print ("* OPERATION                = %s" % OPERATION)
	print ("* PRIORITY                 = %s" % PRIORITY)	
	print ("* BATCH                    = %s" % BATCH)
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

def submitJob():
	global TOKEN
	
	print ("----------------------------------------------------------------------------")
	print (">>> SUBMIT A JOB <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/coord/jobs?orgID="+ORGID+""
	if CATEGORY > "":
		url = url + "&category="+CATEGORY+""
	if OPERATION > "":
		url = url + "&operation="+OPERATION+""
	if PRIORITY > "":
		url = url + "&priority="+PRIORITY+""
	if BATCH > "":
		url = url + "&batch="+BATCH+""	

  	referer = PIPEHOST  				
  	#print url
  	#print referer
  	#quit()
  	#Content-Type header in your request, or it's incorrect. In your case it must be application/xml
  	DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + TOKEN} 
  	HEADERS = {	'Connection': 'keep-alive', \
  				'Content-Type': 'application/octet', \
  				'Content-Length': '48', \
  				'Referer': referer, \
  				'Authorization': 'Apixio ' + TOKEN}
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
	print ("* ORG ID                   = %s" % ORGID)
	print ("* CATEGORY                 = %s" % CATEGORY)
	print ("* OPERATION                = %s" % OPERATION)
	print ("* PRIORITY                 = %s" % PRIORITY)
	print ("* BATCH                    = %s" % BATCH)	
	print ("*")
	print ("* RECEIVED STATUS CODE     = %s" % statuscode)
	print ("****************************************************************************")

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)

submitJob()

print ("----------------------------------------------------------------------------")
print ("Exiting resubmitJobTool ...")
#============================ THE END ====================================================