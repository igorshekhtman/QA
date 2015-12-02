#=========================================================================================
#====================================== bundle_non_es.py =================================
#=========================================================================================
#
# PROGRAM:         bundle.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    28-May-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for Bundle specific data set:
#
# NOTES / COMMENTS:  python2.7 bundle.py staging projectID
#
#
#
#
# COVERED TEST CASES:
#
#
# SETUP:
#          * Assumes Meta ACLs and HCC environments are available
#		   * Assumes that Python2.7 is available 
#
# USAGE:
#          * Set the global variables, see below (Global Test Environment Selection)
#          * Run: python2.7 useraccountsregressiontest.py staging eng@apixio.com ops@apixio.com
#          * Results can be accessed through Apixio Reports portal: https://reports.apixio.com/html/user_accounts_regression_reports_staging.html
#			s.cmpmsvc.bundle("CP_84cffb11-bbda-41ae-a0ec-0e9693f9459c", user_annotation="Reject")
#			s.cmpmsvc.bundle("CP_84cffb11-bbda-41ae-a0ec-0e9693f9459c", user_annotation="Accept")
#			s.cmpmsvc.bundle("CP_84cffb11-bbda-41ae-a0ec-0e9693f9459c", user_annotation="None")
#
# MISC: 
#
#=========================================================================================
#
# Global Paramaters descriptions and possible values:
# These are defined in CSV_CONFIG_FILE_NAME = "bundle.csv", 
# Which is located in CSV_CONFIG_FILE_PATH folder
#
# ENVIRONMENT - "Staging" or "Production"
# NUMBER_OF_USERS_TO_CREATE - integer (0 through x) - total number of HCC users to create
# NUMBER_OF_ORGS_TO_CREATE - integer (0 through x) - total number of coding orgs to create
# CODINGORGANIZATION - any organization from CDGORGMAP list below
# HCCPASSWORD - default password to be assigned to every HCC user
#
# CSV_FILE_PATH - path for output csv file (content: environment, username, password)
# CSV_FILE_PATH - name for output csv file 
#
# MAX_NUM_RETRIES - global limit for number of retries (statuscode = 500)
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
import token
requests.packages.urllib3.disable_warnings()
#=========================================================================================
#============= Initialization of the UserAccountsConfig file =============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/bundling_tool/"
CSV_CONFIG_FILE_NAME = "bundle.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "User Accounts Regression Test"
SENDER="donotreply@apixio.com"
CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
START_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
TIME_START=time.time()
END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
DURATION_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR=strftime("%Y", gmtime())
CURDAY=strftime("%d", gmtime())
CURMONTH=strftime("%m", gmtime())
CURYEAR=strftime("%Y", gmtime())

PASSED_STAT="<table width='100%%'><tr><td bgcolor='#00A303' align='center'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED_STAT="<table width='100%%'><tr><td bgcolor='#DF1000' align='center'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<br><table width='100%%'><tr><td bgcolor='#4E4E4E' align='left'><font size='3' color='white'><b>&nbsp;&nbsp; %s</b></font></td></tr></table>"

#=========================================================================================
#================== Global variable declaration, initialization ==========================
#=========================================================================================
#
# Author: Igor Shekhtman ishekhtman@apixio.com
#
# Creation Date: 23-Oct-2014
#
# Description: Global configuration variables are read from "CSV_CONFIG_FILE_NAME" 
# defined above which is located in "CSV_CONFIG_FILE_PATH".  All values are read into 
# a "result" dictionary, which is later parsed one row at a time, filling values for 
# each of the global variables.
#
#
def ReadConfigurationFile(filename):
	result={ }
	csvfile = open(filename, 'rb')
	reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
	for row in reader:
		if (str(row[0])[0:1] <> '#') and (str(row[0])[0:1] <> ' '):	
			result[row[0]] = row[1]
	globals().update(result)
	return result    	
#=========================================================================================
#================= Global Variable Initialization Section ================================
#=========================================================================================
	
ok 				= 200
created 		= 201
accepted 		= 202
nocontent 		= 204
movedperm 		= 301
redirect 		= 302
requestdenied 	= 400
unauthorized	= 401
forbidden 		= 403
notfound 		= 404
intserveror 	= 500
servunavail 	= 503

STATUS_CODES = {	200: "OK", 201: "CREATED", 202: "ACCEPTED", 204: "NO CONTENT", 301: "MOVED PERM", \
				302: "REDIRECT", 400: "REQUEST DENIED", 401: "UNAUTHORIZED", 403: "FORBIDDEN", \
				404: "NOT FOUND", 500: "INT SERVER ERROR", 503: "SERVER UNAVAILABLE" } 


#=========================================================================================
#===================== Helper Functions ==================================================
#=========================================================================================

def printGlobalParamaterSettings():

	print ("\n")
	print ("* Version                = %s"%VERSION)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* UA URL                 = %s"%UA_URL)
	print ("* BUNDLER URL            = %s"%BUNDL_URL)
	print ("* User Name              = %s"%USERNAME)
	print ("* Project ID             = %s"%PROJECTID)
	print ("* Batch ID               = %s"%BATCHID)

#=========================================================================================
	
def checkEnvironmentandReceivers():
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - project ID
	# Arg3 - batch ID
	
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS, PROJECTID, BATCHID, BUNDL_URL
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global ACLUSERNAME, ACLPASSWORD, BUNDL_URL, UA_URL, HCC_URL, TOKEN_URL
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT[:1].upper() == "P"): #Production
		ENVIRONMENT = "production"
		ACL_DOMAIN="acladmin.apixio.com"
		UA_URL="https://useraccount.apixio.com:7076"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		USERNAME="system_qa@apixio.com"
		PASSWORD="9p2qa20.."
		BUNDL_URL="http://cmp-2.apixio.com:8087"
		TOKEN_URL = "https://tokenizer.apixio.com:7075/tokens"
	elif (ENVIRONMENT[:1].upper() == "D"): #Development
		ENVIRONMENT = "development"
		UA_URL="https://useraccount-dev.apixio.com:7076"
		USERNAME="ishekhtman@apixio.com"
		PASSWORD="apixio.321"
		BUNDL_URL="http://cmp-dev.apixio.com:8087"
		TOKEN_URL = "https://tokenizer-dev.apixio.com:7075/tokens"	
	elif (ENVIRONMENT[:1].upper() == "E"):  #Engineering
		ENVIRONMENT = "engineering"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://useraccount-stg.apixio.com:7076"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		USERNAME="ishekhtman@apixio.com"
		PASSWORD="apixio.321"
		#BUNDL_URL="http://cmp-stg.apixio.com:8087"
		#BUNDL_URL="http://cmp-stg2.apixio.com:8087"
		BUNDL_URL="http://cmp-stg2.apixio.com:8087"
		TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"		
	else:  #Staging
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://useraccount-stg.apixio.com:7076"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		USERNAME="ishekhtman@apixio.com"
		PASSWORD="apixio.321"
		#BUNDL_URL="http://cmp-stg.apixio.com:8087"
		#BUNDL_URL="http://cmp-stg2.apixio.com:8087"
		BUNDL_URL="http://cmp-stg2.apixio.com:8087"
		TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
	
	
	if (len(sys.argv) > 2):
		PROJECTID=str(sys.argv[2])
	else:
		print "Missing project ID, aborting now ..."
		print "Proper use instructions:"
		print "python2.7 bundle.py <environment> <projectID (required)> <batchID (optional)>"
		print ""
		print "environment: production, engineering, dev, staging"
		quit()

	if (len(sys.argv) > 3):
		BATCHID=str(sys.argv[3])
	else:
		BATCHID=""
	
				
	# overwite any previous ENVIRONMENT settings
	#ENVIRONMENT = "Production"
	print ("Version %s\n") % VERSION
	print ("ENVIRONMENT = %s\n") % ENVIRONMENT
	print ("Completed setting of enviroment and report receivers ...\n")		

#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def obtainExternalToken(un, pw):

	external_token = ""
	url = UA_URL+'/auths'
	referer = UA_URL  	
	#token=$(curl -v --data email=$email --data password="$passw" "http://localhost:8076/auths?int=true" | cut -c11-49)
	
	DATA =    {'Referer': referer, 'email': un, 'password': pw} 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
	
	print ("* USERNAME               = %s" % un)
	print ("* PASSWORD               = %s" % pw)
	print ("* URL                    = %s" % url)
	
	response = requests.post(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* EXT. TOKEN STATUS CODE = %s" % statuscode)
	if (statuscode != ok) and (statuscode != created):
		print ("Failure occured obtaining ext. token: %s, exiting now ..." % STATUS_CODES[statuscode])
		quit()

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
	print (">>> UA / TOKENIZER - OBTAIN EXTERNAL AND EXCHANGE FOR INTERNAL TOKEN <<<")
	print ("----------------------------------------------------------------------------")
	
	
	external_token = obtainExternalToken(un, pw)
	
	url = TOKEN_URL
  	referer = TOKEN_URL  				
  	DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + external_token} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + external_token}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
  	statuscode = response.status_code
  	print ("* INT. TOKEN STATUS CODE = %s" % statuscode)
  	if (statuscode != ok) and (statuscode != created):
		print ("Failure occured obtaining int. token: %s, exiting now ..." % STATUS_CODES[statuscode])
		quit()
  	
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
	print ("* STATUS CODE            = %s" % statuscode)


#=========================================================================================

def bundleDataSet():
	print ("\n----------------------------------------------------------------------------")
	print (">>> CMP - BUNDLE DATA SET FOR %s PROJECT <<<" % PROJECTID)
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = BUNDL_URL+"/cmp/v1/project/"+PROJECTID+"/bundle?user_annotation=None"
	#URL = BUNDL_URL+"/cmp/v1/project/"+PROJECTID+"/bundle"
	if BATCHID > "":
		URL = BUNDL_URL+"/cmp/v1/project/"+PROJECTID+"/bundle?batch_id="+BATCHID
		#URL = BUNDL_URL+"/cmp/v1/project/"+PROJECTID+"/bundle?user_annotation=None&batch_id="+BATCHID
	
	print ("\n")
	print ("* URL                    = %s"%URL)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* Admin User Name        = %s"%USERNAME)
	print ("* Project ID             = %s"%PROJECTID)	
	print ("* Internal Token         = %s"%TOKEN)
	print ("* Apixio Token           = %s"%APIXIO_TOKEN)
	#URL = "https://authentication-stg.apixio.com:7076/customer/projects"
	#print ("* URL                    = %s"%URL)
	
	
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.post(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code

	print ("* Status Code            = %s"%statuscode)


	if (statuscode == ok) or (statuscode == nocontent):
		print "Successfully bundling ..."
	else:
		print ("Failure occured bundling: %s, exiting now ..." % STATUS_CODES[statuscode])
		quit()		

	return()	

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

checkEnvironmentandReceivers()

printGlobalParamaterSettings()

obtainInternalToken(USERNAME, PASSWORD)

bundleDataSet()
	

print ("\n============================================================================")	
print ("============================= End of Bundler =================================")
print ("============================================================================")
#=========================================================================================
