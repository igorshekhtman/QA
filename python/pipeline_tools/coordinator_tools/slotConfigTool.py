#=========================================================================================
#========================== slotConfigTool.py ============================================
#=========================================================================================
#
# PROGRAM:         slotConfigTool.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    18-Mar-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of re-configuring
#			number of slots in a Hadoop cluster.
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

# Optional paramaters:
ACTIVITYID = ""


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
	print ("* python2.7 clusterConfigTool.py arg1 arg2")
	print ("*")
	print ("* Required paramaters:")
	print ("* --------------------")
	print ("* arg1 - environment (staging or production) / help")
	print ("*")
	print ("* Optional paramaters:")
	print ("* --------------------")
	print ("* arg2 - activityID")
	print ("----------------------------------------------------------------------------")
	print ("\n")
	quit()

#=========================================================================================

def checkForPassedArguments():
	# Arg1 - environment (required) / help
	# Arg2 - activityID (optional)


	global EMAIL, PASSW, AUTHHOST, TOKEHOST, PIPEHOST
	global ORGID, CATEGORY, OPERATION, BATCH, PRIORITY
	global ENVIRONMENT

	#print ("Setting environment varibales ...\n")
	
	
	if (len(sys.argv) < 2) or (str(sys.argv[1]).upper() == "HELP") or \
		(str(sys.argv[1]).upper() == "--HELP") or (str(sys.argv[1]).upper() == "-H") or \
		(str(sys.argv[1]).upper() == "-HELP") or (str(sys.argv[1]).upper() == "--H"):
		outputMissingArgumentsandAbort()
	else:
		ENVIRONMENT=str(sys.argv[1])
		if (len(sys.argv) > 2):
			ACTIVITYID=str(sys.argv[2])
		

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
	print ("* ACTIVITY ID              = %s" % ACTIVITYID)
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

def getListOfActivities():
	global TOKEN
	
	print ("----------------------------------------------------------------------------")
	print (">>> GET LIST OF HADOOP CLUSTER ACTIVITIES <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/coord/activities"


  	referer = PIPEHOST  				
  	DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + TOKEN} 
  	HEADERS = {	'Connection': 'keep-alive', \
  				'Content-Type': 'application/octet', \
  				'Content-Length': '48', \
  				'Referer': referer, \
  				'Authorization': 'Apixio ' + TOKEN}
  	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	if statuscode == ok:
		activities = response.json()
	else:
		print ("Failure occured with %s status code received back from server" % statuscode)
		quit()
				
	print ("* ENVIRONMENT              = %s" % ENVIRONMENT)
	print ("* ROOT USERNAME            = %s" % EMAIL)
	print ("* PASSWORD                 = %s" % PASSW)
	print ("* INTERNAL TOKEN           = %s" % TOKEN)
	print ("* AUTHENTICATION HOST URL  = %s" % AUTHHOST)
	print ("* TOKENIZER HOST URL       = %s" % TOKEHOST)
	print ("* COORDINATOR HOST URL     = %s" % PIPEHOST)
	print ("* SUBMIT JOB COMPLETE URL  = %s" % url)
	print ("*")
	print ("* ACTIVITY ID              = %s" % ACTIVITYID)
	print ("*")
	print ("* RECEIVED STATUS CODE     = %s" % statuscode)
	print ("****************************************************************************")
	# Available fields:
	#    "borrowableSlots": "0",
    #    "enabled": true,
    #    "name": "docUUIDLinkCheckAndRecovery",
    #    "priority": 5,
    #    "slotMax": "1",
    #    "slotMin": "0",
    #    "totalSlots": "1"

	print ("Nmbr:\tBS:\tEnabled:\tPriority:\tSl-Max:\tSl-Min:\tSl-Tot:\tName:")
	print ("=====\t===\t========\t=========\t=======\t=======\t=======\t=====")
	cntr = 0
	for activity in sorted(activities):
		#print json.dumps(job, sort_keys=True, indent=0)
		cntr += 1
		print ("%d\t%s\t%s\t\t%s\t\t%s\t%s\t%s\t%s" % (cntr, activity['borrowableSlots'], \
			activity['enabled'], activity['priority'], activity['slotMax'], activity['slotMin'], \
			activity['totalSlots'], activity['name'] ))	
	print ("\nTotal of %d activities available" % cntr)	
	
	#print json.dumps(activities, sort_keys=True, indent=4)

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)

getListOfActivities()

print ("----------------------------------------------------------------------------")
print ("Exiting slotConfigTool ...")
#============================ THE END ====================================================