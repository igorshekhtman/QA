#=========================================================================================
#========================== eventConfigCompleteTool.py ===================================
#=========================================================================================
#
# PROGRAM:         eventConfigCompleteTool.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    21-Mar-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of viewing and 
#			updating of any given version of event model configuration for any one specific 
#			organization.
#
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
import MySQLdb
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


#===== MySQL Authentication============
STDOM = "mysqltest-stg1.apixio.net" 
STPW = "M8ng0St33n!"
PRDOM = "10.198.2.97"
PRPW = "J3llyF1sh!"
#======================================

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
	print ("* python2.7 eventConfigCompleteTool.py arg1 arg2")
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

	#print 	len(sys.argv)
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
def connectToMySQL():
	print ("Connecing to MySQL ...\n")
	global mss_cur, mss_conn, msp_cur, msp_conn
	mss_conn = MySQLdb.connect(host=STDOM, \
		user='qa', \
		passwd=STPW, \
		db='apixiomain')		
	mss_cur = mss_conn.cursor() 
	msp_conn = MySQLdb.connect(host=PRDOM, \
		user='qa', \
		passwd=PRPW, \
		db='apixiomain')		
	msp_cur = msp_conn.cursor()
	print ("Connection to MySQL established ...\n")
#=========================================================================================
def closeMySQLConnection():
	global mss_cur, mss_conn, msp_cur, msp_conn
	mss_cur.close()
	mss_conn.close()
	msp_cur.close()
	msp_conn.close()	
#=========================================================================================
def getOrgName(id):
	global mss_cur, mss_conn, msp_cur, msp_conn
	mss_cur.execute("SELECT org_name FROM apixiomain.ldap_org where ldap_org_id=%s" % id)
	for row in mss_cur.fetchall():
		orgname = str(row[0])
		env = "Staging"
		break	
	else:	
		msp_cur.execute("SELECT org_name FROM apixiomain.ldap_org where ldap_org_id=%s" % id)
		for row in msp_cur.fetchall():
			orgname = str(row[0])
			env = "Production"
			break
		else:
			orgname = id
			env = "N/A"	
	#print env+" Orgname: "+orgname
	#print ""
	return (orgname)
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
def getOrgSpecificProperties(org, version):
	  	
	print ("----------------------------------------------------------------------------")
	print (">>> GET ORG SPECIFIC SET OF PROPERTIES <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/event/properties/"+version+"?orgID="+org+""
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
  		print response.text
  		result = response.text
  	else:
  		print ("Bad server response %s received.  Exiting application ..." % statuscode)
  		result = "Event model properties not available"		
	return (result)
#=========================================================================================	

def getEventConfigVersionNumbers():
	global TOKEN, AV_JOBS, INPUT_STRING
	
	print ("----------------------------------------------------------------------------")
	print (">>> GET EVENT CONFIG VERSION NUMBERS <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/event/versions"
	#if (ORGID > ""):
	#	url = url + "?"
	#if ORGID > "":
	#	url = url + "&org="+ORGID+""
	
	#1405126119695
	#1406595348574

	
	
	#url = PIPEHOST+"/pipeline/event/properties/1405126119695"
	
	#url = PIPEHOST+"/pipeline/event/properties/1405126119695?orgID=370"
	
	
	AV_JOBS = {}
  	referer = PIPEHOST  				

  	DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + TOKEN} 
  	HEADERS = {	'Connection': 'keep-alive', \
  				'Content-Type': 'application/octet', \
  				'Content-Length': '48', \
  				'Referer': referer, \
  				'Authorization': 'Apixio ' + TOKEN}
  	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	
	versions_list = []
	cntr = 0
	version = ""
	if statuscode == ok:
		versions = response.text
		for item in versions:
			if item != "\n":
				version = version + item
			else:
				versions_list.append(version)
				version = ""					
		print versions_list 
		print len(versions_list)
	else:
		print ("Bad server response %s received.  Exiting application ..." % statuscode)	
	#quit()
	
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
	print ("* VERSIONS LIST            = %s" % versions_list)
	print ("*")
	print ("* RECEIVED STATUS CODE     = %s" % statuscode)
	print ("****************************************************************************************")
	print ("*                           LIST OF AVAILABLE FAILED JOBS                              *")
	print ("****************************************************************************************")
	

	for version in versions_list:
		specific_properties = getOrgSpecificProperties(ORGID, version)

	
	print ("-------------------------------------------------------------------------------------------")
	print ("Enter line number(s), comma separated, of the job(s) to resubmit or just enter Q to Quit")
	print ("-------------------------------------------------------------------------------------------")
	INPUT_STRING = raw_input("Line number(s): ")
	if INPUT_STRING.upper() != "Q":
		validation = validateUpdateString(INPUT_STRING)
		if validation.upper() == "SUCCESS":
			submitJob(INPUT_STRING)
		else:
			print (validation)
			#quit()
			raw_input("Press Enter to continue...")	

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)

#connectToMySQL()

INPUT_STRING=""
while INPUT_STRING.upper() != "Q":
	obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)
	getEventConfigVersionNumbers()

#closeMySQLConnection()

#============================ THE END ====================================================