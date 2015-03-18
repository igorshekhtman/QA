#=========================================================================================
#========================== failedJobsList.py ============================================
#=========================================================================================
#
# PROGRAM:         failedJobsList.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    17-Mar-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of retrieving list
#			of failed Hadoop Job(s).
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
import readline
import tabulate
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
STATUS = ""
ORG = ""
ACTIVITY = ""
JOB = ""

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

def output(data):
	columns = sorted(reduce(lambda x, y: set(x) | set(y), [set(x.keys()) for x in data]))
	odata = [[x.split('_')[-1] for x in columns]]
	for row in data:
		odata.append([row.get(x) if type(row.get(x)) != float else '%.2f' % row.get(x) for x in columns])
	print tabulate.tabulate(odata, headers='firstrow', missingval='')

#=========================================================================================

def outputMissingArgumentsandAbort():
	print ("----------------------------------------------------------------------------")
	print (">>> MISSING REQUIRED PARAMETERS: ENVIRONMENT & ORGID <<<")
	print ("----------------------------------------------------------------------------")
	print ("* Usage:")
	print ("* python2.7 failedJobsList.py arg1 arg2 arg3 arg4")
	print ("*")
	print ("* Required paramaters:")
	print ("* --------------------")
	print ("* arg1 - environment (staging or production) / help")
	print ("*")
	print ("* Optional paramaters:")
	print ("* --------------------")
	print ("* arg2 - status (limit list to jobs with given status)")
	print ("* arg3 - org (limit list to jobs for given orgID)")
	print ("* arg4 - activity (limit list to jobs for given activity)")
	print ("* arg5 - job (limit list to jobs of the given job IDs)")
	print ("----------------------------------------------------------------------------")
	print ("\n")
	quit()

#=========================================================================================

def checkForPassedArguments():
	# Arg1 - environment (required)  / help
	# Arg2 - status (optional)
	# Arg3 - org (optional)
	# Arg4 - activity (optional)
	# Arg5 - job (optional)

	global EMAIL, PASSW, AUTHHOST, TOKEHOST, PIPEHOST
	global STATUS, ORG, ACTIVITY, JOB
	global ENVIRONMENT
	
	
	if (len(sys.argv) < 2) or (str(sys.argv[1]).upper() == "HELP") or \
		(str(sys.argv[1]).upper() == "--HELP") or (str(sys.argv[1]).upper() == "-H") or \
		(str(sys.argv[1]).upper() == "-HELP") or (str(sys.argv[1]).upper() == "--H"):
		outputMissingArgumentsandAbort()
	else:
		ENVIRONMENT=str(sys.argv[1])
		if (len(sys.argv) > 2):
			STATUS=str(sys.argv[2])
			if (len(sys.argv) > 3):
				ORG=str(sys.argv[3])
				if (len(sys.argv) > 4):
					ACTIVITY=str(sys.argv[4])
					if (len(sys.argv) > 5):
						JOB=str(sys.argv[5])
		

	if (ENVIRONMENT.upper() == "P") or (ENVIRONMENT.upper() == "PROD") or (ENVIRONMENT.upper() == "PRODUCTION"):
		ENVIRONMENT = "production"
		EMAIL="system_qa@apixio.com"
		PASSW="8p1qa19.."
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
	print ("* STATUS                   = %s" % STATUS)
	print ("* ORG                      = %s" % ORG)
	print ("* ACTIVITY                 = %s" % ACTIVITY )
	print ("* JOB                      = %s" % JOB)	
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

def getFailedJobsList():
	global TOKEN
	
	print ("----------------------------------------------------------------------------")
	print (">>> SUBMIT A JOB <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/coord/jobs/failed"
	if (STATUS > "") or (ORG > "") or (ACTIVITY > "") or (JOB > ""):
		url = url + "?"
	if STATUS > "":
		url = url + "&status="+STATUS+""
	if ORG > "":
		url = url + "&org="+ORG+""
	if ACTIVITY > "":
		url = url + "&activity="+ACTIVITY+""
	if JOB > "":
		url = url + "&job="+JOB+""	

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
  	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	jobs = response.json()
	
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
	print ("* STATUS                   = %s" % STATUS)
	print ("* ORG                      = %s" % ORG)
	print ("* ACTIVITY                 = %s" % ACTIVITY )
	print ("* JOB                      = %s" % JOB)	
	print ("*")
	print ("* RECEIVED STATUS CODE     = %s" % statuscode)
	print ("****************************************************************************")
	print ("*                    LIST OF AVAILABLE FAILED JOBS                         *")
	print ("****************************************************************************")
	
	# ----------- List of Available fields -----------------
	#"activityDisabled": false,
	#----"activityName": "loadAPO",
	#"createdAt": 1426201926233,
	#"dataSize": 0,
	#"effectivePriority": 7,
	#"fromJob": null,
	#"hadoopJob": null,
	#"hdfsDir": "/user/apxqueue/queue-location-3/work/32265/input",
	#"initiator": null,
	#----"jobID": 32268,
	#"launchedAt": null,
	#"orgDisabled": false,
	#----"orgID": "407",
	#----"origJob": 32268,
	#"slotAlloc": "1;1;7;loadAPO;1;0;",
	#"slotCount": 0,
	#"trackingURL": null

	print ("Number:\tJob ID:\tOrig ID:\tOrg ID:\tActivity Name:")
	print ("=======\t=======\t========\t=======\t===============")
	cntr = 0
	for job in sorted(jobs):
		#print json.dumps(job, sort_keys=True, indent=0)
		cntr += 1
		if (ENVIRONMENT.upper() == "STAGING"):
			print ("%d\t%s\t%s\t\t%s\t%s" % (cntr, job['jobID'], job['origJob'], job['orgID'][:3], job['activityName'] ))
		else:
			print ("%d\t%s\t%s\t\t%s\t%s" % (cntr, job['jobID'], job['origJob'], job['orgID'][:8], job['activityName'] ))		
	print ("\n\nTotal of %d failed jobs are available" % cntr)	
			

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)

#quit()
getFailedJobsList()

print ("----------------------------------------------------------------------------")
print ("Exiting resubmitJobTool ...")
#============================ THE END ====================================================