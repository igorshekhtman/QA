#=========================================================================================
#====================================== push_event.py ====================================
#=========================================================================================
#
# PROGRAM:         push_event.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    19-Oct-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for Pushing individual events 
#			through Data Orchestrator
#
# NOTES / COMMENTS:  python2.7 push_event.py
#
#
#
#=========================================================================================
#
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
import token
#=========================================================================================
#============= Initialization of the UserAccountsConfig file =============================
#=========================================================================================
#	
ok 				= 200
created 		= 201
accepted 		= 202
nocontent 		= 204
movedperm 		= 301
redirect 		= 302
requestdenied 	= 400
unauthorized 	= 401
forbidden 		= 403
notfound 		= 404
intserveror 	= 500
servunavail 	= 503
#
#=========================================================================================
#===================== Helper Functions ==================================================
#=========================================================================================
#
def printGlobalParamaterSettings():
#with optional batch id: ?batch_id={batchId} if you want to limit bundling to a particular run of events

	print ("\n")
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* ACL URL                = %s"%UA_URL)
	print ("* HCC URL                = %s"%HCC_URL)
	print ("* User Name              = %s"%USERNAME)
	print ("* Password               = %s"%PASSWORD)

#=========================================================================================	
	
def checkEnvironmentandReceivers():
	
	
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS, PROJECTID, BATCHID, BUNDL_URL
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global UA_URL, HCC_URL, ACLUSERNAME, ACLPASSWORD, BUNDL_URL, DO_URL
	global USERNAME, PASSWORD
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		ENVIRONMENT = "production"
		ACL_DOMAIN="acladmin.apixio.com"
		UA_URL="https://useraccount.apixio.com"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		USERNAME="root@api.apixio.com"
		PASSWORD="thePassword"
		BUNDL_URL="http://cmp.apixio.com:8087"
		DO_URL="https://dataorchestrator-stg.apixio.com:7085"
	else:
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://useraccount-stg.apixio.com:7076"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		USERNAME="ishekhtman@apixio.com"
		PASSWORD="apixio.123"
		BUNDL_URL="http://cmp-stg2.apixio.com:8087"
		DO_URL="https://dataorchestrator-stg.apixio.com:7085"
	
				
	# overwite any previous ENVIRONMENT settings
	#ENVIRONMENT = "Production"
	print ("ENVIRONMENT = %s\n") % ENVIRONMENT
	print ("Completed setting of enviroment and report receivers ...\n")		

			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def obtainExternalToken(un, pw):

	external_token = ""
	url = UA_URL+'/auths'
	#url = 'https://useraccount-stg.apixio.com:7076/auths'
	referer = UA_URL  	
	#token=$(curl -v --data email=$email --data password="$passw" "http://localhost:8076/auths?int=true" | cut -c11-49)
	
	DATA =    {'Referer': referer, 'email': un, 'password': pw} 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
	
	response = requests.post(url, data=DATA, headers=HEADERS) 

	statuscode = response.status_code

	userjson = response.json()
	if userjson is not None:
		external_token = userjson.get("token") 
		print ("* USERNAME               = %s" % un)
		print ("* PASSWORD               = %s" % pw)
		print ("* URL                    = %s" % url)
		print ("* EXTERNAL TOKEN         = %s" % external_token)
		print ("* RECEIVED STATUS CODE   = %s" % statuscode)
		print ("****************************************************************************")
			
	return (external_token)

#=========================================================================================
def obtainInternalToken(un, pw):
	global TOKEN, APIXIO_TOKEN
	
	print ("----------------------------------------------------------------------------")
	print (">>> ACL - OBTAIN EXTERNAL AND EXCHANGE FOR INTERNAL TOKEN <<<")
	print ("----------------------------------------------------------------------------")
	
	
	TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
	external_token = obtainExternalToken(un, pw)
	url = TOKEN_URL
  	referer = TOKEN_URL  				
  	DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + external_token} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + external_token}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
  	userjson = response.json()
  	if userjson is not None:
  		TOKEN = userjson.get("token")
  		APIXIO_TOKEN = 'Apixio '+str(TOKEN)
  	else:
  		TOKEN = "Not Available"	
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % un)
	print ("* PASSWORD               = %s" % pw)
	print ("* TOKENIZER URL          = %s" % url)
	print ("* EXTERNAL TOKEN         = %s" % external_token)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)

#=========================================================================================

def pushEvent(page):
	print ("\n----------------------------------------------------------------------------")
	print (">>> PUSHING EVENT PAGE %d <<<" % page)
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = DO_URL+"/event"
	DATA = { 
  "subject": { 
      "uri": "a8116dbf-0713-4476-b890-f3f694b5a19e", 
      "type": "patient" 
  }, 
  "fact": { 
      "code": { 
          "code": "36201", 
          "codeSystem": "2.16.840.1.113883.6.103", 
          "codeSystemVersion": "9", 
          "displayName": "36201" 
      }, 
      "time": { 
          "startTime": "2014-01-02T00:00:00-0800", 
          "endTime": "2014-12-30T00:00:00-0800" 
      } 
  }, 
  "source": { 
      "uri": "d8d69b4a-4245-45fe-9d1b-fe2a3c1a3acc", 
      "type": "document" 
  }, 
  "evidence": { 
      "inferred": False, 
      "source": { 
          "uri": "casper", 
          "type": "jromero@apexcodemine.com" 
      }, 
      "attributes": { 
          "pageNumber": str(page), 
          "totalPages": "3" 
      } 
  }, 
  "attributes": { 
      "sourceType": "NARRATIVE", 
      "SOURCE_TYPE": "NARRATIVE", 
      "totalPages": "3", 
      "$orgId": "482" 
  } 
}
	
	
	print ("\n")
	print ("* URL                    = %s"%URL)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* User Name              = %s"%USERNAME)
	print ("* Password               = %s"%PASSWORD)
	print ("* Internal Token         = %s"%TOKEN)
	print ("* Apixio Token           = %s"%APIXIO_TOKEN)
	print ("* DATA                   = %s"%DATA)
	
	#quit()
	

	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	
	
	
	
	response = requests.post(URL, data=json.dumps(DATA), headers=HEADERS)
	statuscode = response.status_code

	print ("* Status Code            = %s"%statuscode)


	if (statuscode == ok) or (statuscode == nocontent):
		print "Successfully pushing the event ..."
	else:
		print "Failure occured, exiting now ..."
		quit()		

	return()	
	
#=========================================================================================

def checkEvent(patientID):
	print ("\n----------------------------------------------------------------------------")
	print (">>> CHECKING EVENT <<<")
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = DO_URL+"/event/sequence/patient/"+patientID
	
	DATA = {}
	
	
	print ("\n")
	print ("* URL                    = %s"%URL)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* User Name              = %s"%USERNAME)
	print ("* Password               = %s"%PASSWORD)
	print ("* Internal Token         = %s"%TOKEN)
	print ("* Apixio Token           = %s"%APIXIO_TOKEN)
	print ("* DATA                   = %s"%DATA)
	
	#quit()
	

	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	
	
	
	
	response = requests.get(URL, data=json.dumps(DATA), headers=HEADERS)
	statuscode = response.status_code

	print ("* Status Code            = %s"%statuscode)


	if (statuscode == ok) or (statuscode == nocontent):
		print "Successfully getting the event ..."
		print ("----------------------------------------------------------------------------")
		print json.dumps(response.json())
	else:
		print "Failure occured, exiting now ..."
		quit()		

	return()	
	

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

checkEnvironmentandReceivers()

printGlobalParamaterSettings()

obtainInternalToken(USERNAME, PASSWORD)

#pushEvent(2)

checkEvent("a8116dbf-0713-4476-b890-f3f694b5a19e")
	

print ("\n============================================================================")	
print ("=========================== End of Event Activities ========================")
print ("============================================================================")
#=========================================================================================
