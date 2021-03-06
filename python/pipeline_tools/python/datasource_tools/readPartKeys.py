#=========================================================================================
#========================== readPartKeys.py ==============================================
#=========================================================================================
#
# PROGRAM:         readPartKeys.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    19-Mar-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for the purpose of translating
#			partial keys.
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
#import MySQLdb
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
ORGID = ""
KEYTYPE = "patientUUID"
AUTHORITY = ""
STARTKEY = ""
#[externalID, partialPatientKey, patientUUID, documentUUID]
KEYTYPE_DICT = {"1": "partialPatientKey", "2": "patientUUID", "3": "documentUUID", "4": "externalID"} 

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
	print ("------------------------------------------------------------------------------------------------------------")
	print (">>> MISSING REQUIRED PARAMETERS: ENVIRONMENT & ORGID <<<")
	print ("------------------------------------------------------------------------------------------------------------")
	print ("* Usage:")
	print ("* python2.7 readPartKeys.py arg1 arg2 arg3 arg4")
	print ("*")
	print ("* Required paramaters:")
	print ("* --------------------")
	print ("* arg1 - environment (staging or production) / help")
	print ("* arg2 - orgID (ex. 370)")
	print ("* arg3 - keyType (ex. 1-partialPatientKey, 2-patientUUID, 3-documentUUID, 4-externalID)")
	print ("*")
	print ("* Optional paramaters:")
	print ("* --------------------")	
	print ("* arg4 - authority (optional)")
	print ("------------------------------------------------------------------------------------------------------------")
	print ("\n")
	quit()

#=========================================================================================

def checkForPassedArguments():
	# Arg1 - environment (required) / help
	# Arg2 - orgID (required))
	# Arg3 - filter (required)


	global EMAIL, PASSW, AUTHHOST, TOKEHOST, PIPEHOST
	global ORGID, CATEGORY, OPERATION, BATCH, PRIORITY
	global ENVIRONMENT, KEYTYPE, AUTHORITY, KEYTYPE_KEY

	#print ("Setting environment varibales ...\n")
	
	
	if (len(sys.argv) < 4) or (str(sys.argv[1]).upper() == "HELP") or \
		(str(sys.argv[1]).upper() == "--HELP") or (str(sys.argv[1]).upper() == "-H") or \
		(str(sys.argv[1]).upper() == "-HELP") or (str(sys.argv[1]).upper() == "--H"):
		outputMissingArgumentsandAbort()
	else:
		ENVIRONMENT=str(sys.argv[1])
		if (len(sys.argv) > 2):
			ORGID = str(sys.argv[2])
			if (len(sys.argv) > 3):
				KEYTYPE_KEY = str(sys.argv[3]) 
			 	if (len(sys.argv) > 4):
  					AUTHORITY = str(sys.argv[4])
		

	if (ENVIRONMENT.upper() == "P") or (ENVIRONMENT.upper() == "PROD") or (ENVIRONMENT.upper() == "PRODUCTION"):
		ENVIRONMENT = "production"
		EMAIL="ishekhtman@apixio.com"
		PASSW="apixio.123"
		AUTHHOST="https://useraccount-prd.apixio.com:7076"
		TOKEHOST="https://tokenizer-prd.apixio.com:7075"
		PIPEHOST="http://coordinator-prd.apixio.com:8066"
		MYSQLDOM = "10.198.2.97"
		MYSQPW = "J3llyF1sh!"
	else:  # STAGING ENVIRONMENT
		ENVIRONMENT = "staging"
		EMAIL="ishekhtman@apixio.com"
		PASSW="apixio.123"
		AUTHHOST="https://useraccount-stg.apixio.com:7076"
		TOKEHOST="https://tokenizer-stg.apixio.com:7075"
		PIPEHOST="http://coordinator-stg.apixio.com:8066"
		MYSQLDOM = "mysqltest-stg1.apixio.net"
		MYSQPW = "M8ng0St33n!"	

#=========================================================================================
def connectToMySQL():
	print ("Connecing to MySQL ...\n")
	global mss_cur, mss_conn, msp_cur, msp_conn
	print ("Connection to MySQL established ...\n")
#=========================================================================================
def closeMySQLConnection():
	global mss_cur, mss_conn, msp_cur, msp_conn
#	mss_cur.close()
#	mss_conn.close()
#	msp_cur.close()
#	msp_conn.close()	
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
	print ("* ORG ID                   = %s" % ORGID)
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
def updateOrgConfig(input_string):
	#print ("updateActivityConfig")
	delimiter = ','
  	input_string = input_string.split(delimiter)
  	#input_string = json.dumps(input_string)
	#print input_string
	#quit()
	name = input_string[0]
	enabled = input_string[1]
	priority = input_string[2]
	
	update_string = {"name": input_string[0], "enabled": input_string[1], "priority": input_string[2]}
	update_string = json.dumps(update_string)
	#print update_string
	#quit()
	
	#sample json
	#{"name":"370","enabled":true,"priority":"5"}
	
	print ("----------------------------------------------------------------------------")
	print (">>> UPDATE ORG PRIORITY <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/coord/org/"+name+""
  	referer = PIPEHOST  				
  	
  	#DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + TOKEN} 
  	HEADERS = {	'Connection': 'keep-alive', \
  				'Content-Type': 'application/json', \
  				'Content-Length': '48', \
  				'Referer': referer, \
  				'Accept': '*/*', \
  				'Authorization': 'Apixio ' + TOKEN}	
  	DATA = update_string			
			
  	response = requests.put(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	if statuscode == ok:
		print statuscode
	else:
		print ("Failure occured with %s status code received back from server" % statuscode)
		quit()
	
#=========================================================================================
def validateUpdateString(input_string):
	global KEYTYPE, ORGID, AUTHORITY, KEYTYPE_KEY, STARTKEY
	
	delimiter = ','
  	input_string = input_string.split(delimiter)
  	#input_string = json.dumps(input_string)
  	#print input_string
  	#print len(input_string)
  	
  	
  	if len(input_string) < 2:
  		validation_string = "Some of the required paramaters are missing, please try again ..."
  	else:
  		validation_string = "success" 		
  		ORGID = input_string[0]
  		KEYTYPE_KEY = input_string[1]
  		KEYTYPE = KEYTYPE_DICT[KEYTYPE_KEY]
  		#if len(input_string) > 2:
  		#	AUTHORITY = input_string[2]
  		if len(input_string) > 2:
  			STARTKEY = input_string[2]
  		else:
  			STARTKEY = ""	
  		
  		
  		#print ORGID
  		#print KEYTYPE
  		#print AUTHORITY
  		#quit()	
  			
  	
  	return(validation_string)
  	
  	
#=========================================================================================

def getListOfPartialKeys(orgid, filter):
	global TOKEN, INPUT_STRING, ORG_DICT, FILTER, STARTKEY
	
	ORG_DICT = {}
	#STARTKEY = "" #this is a temp setting
	
	print ("----------------------------------------------------------------------------")
	print (">>> GET LIST OF PARTIAL KEYS <<<")
	print ("----------------------------------------------------------------------------")

	url = PIPEHOST+"/pipeline/datasource/"+orgid+"/keys?filter="+filter+""
	if STARTKEY > "":
		url = url + "&startkey="+STARTKEY+"" 
	
	

  	referer = PIPEHOST  				
  	DATA =    { 'Referer': referer, 'Authorization': 'Apixio ' + TOKEN} 
  	HEADERS = {	'Connection': 'keep-alive', \
  				'Content-Type': 'text/plain', \
  				'Content-Length': '48', \
  				'Referer': referer, \
  				'Authorization': 'Apixio ' + TOKEN} 			
  	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	if statuscode == ok:
		keys = response.text
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
	print ("* SUBMIT PARTIAL KEYS URL  = %s" % url)
	print ("*")
	print ("* ORG ID                   = %s" % ORGID)
	print ("* FILTER / KEY TYPE        = %s" % filter)
	print ("* START KEY                = %s" % STARTKEY)
	print ("*")
	print ("* RECEIVED STATUS CODE     = %s" % statuscode)
	print ("****************************************************************************")
	print ("----------------------------------------------------------------------------")

	#print keys
	
	return (keys)

#=========================================================================================	

def readListOfPartialKeys():
	global TOKEN, INPUT_STRING, ORG_DICT, KEYTYPE, AUTHORITY, KEYTYPE_KEY
	
	ORG_DICT = {}
	
	print ("----------------------------------------------------------------------------")
	print (">>> READ OR TRANSLATE PARTIAL KEY(S) <<<")
	print ("----------------------------------------------------------------------------")

	#url = PIPEHOST+"/pipeline/datasource/"+ORGID+"/keys?filter="+KEYTYPE+""
	#if AUTHORITY > "":
	#	url = url + "&startkey="+AUTHORITY+"" 
	
	
	#------------------------------
	# Obtain list of patientUUIDs
	#-------------------------------
	
	
	
	#sample patientUUID for ORG-370 - "pat_af339ba3-faab-4660-9fb1-72855468ced5"
	#pat_554ac7f2-e512-4439-ab13-a2041fb8fb3a
	#pat_c4eef6a2-429b-4591-a15c-a30058f2f711
	#pat_f7fcc246-c8ec-4411-91bb-9496ab303fe3
	#pat_8698b558-0333-4b74-8b1e-30213fdf864a
	#pat_023aa984-de91-40ce-9453-1139fda2b36d
	#pat_4c3baa8f-5ae8-488c-b7a6-1e988245c3f8
	#pat_99828dd2-cb86-46e8-b9d1-5744d98faab6
	#pat_f9d90866-f589-4cca-b957-a674f7a07b33
	#pat_1aa02475-3866-435b-b357-11f4eacebeca
	
	#url = PIPEHOST+"/pipeline/datasource/"+ORGID+"/keys?keyType="+KEYTYPE+""
	
	
	KEYTYPE = KEYTYPE_DICT[KEYTYPE_KEY]	
	
	ids_list = getListOfPartialKeys(ORGID, KEYTYPE)
	
	
	url = PIPEHOST+"/pipeline/datasource/370/keys?keyType="+KEYTYPE+""	
  	referer = PIPEHOST  
  	HEADERS = {	'Connection': 'keep-alive', \
  				'Content-Type': 'text/plain', \
  				'Content-Length': '48', \
  				'Referer': referer, \
  				'Authorization': 'Apixio ' + TOKEN} 
  	
	#ids_list = ("pat_af339ba3-faab-4660-9fb1-72855468ced5", "pat_554ac7f2-e512-4439-ab13-a2041fb8fb3a", "pat_c4eef6a2-429b-4591-a15c-a30058f2f711", "pat_f7fcc246-c8ec-4411-91bb-9496ab303fe3")
  	
#  	ids_list = json.dumps(ids_list)
  				
  	#DATA = '\n'.join(ids_list)
  	DATA = ids_list
  	#print DATA
  	#quit()					

  	response = requests.post(url, data=DATA, headers=HEADERS) 

	statuscode = response.status_code


	if statuscode == ok:
		output_data = response.text
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
	print ("* SUBMIT PARTIAL KEYS URL  = %s" % url)
	print ("*")
	print ("* ORG ID                   = %s" % ORGID)
	print ("* KEYTYPE                  = %s" % KEYTYPE)
	print ("* AUTHORITY                = %s" % AUTHORITY)
	print ("*")
	print ("* RECEIVED STATUS CODE     = %s" % statuscode)
	print ("****************************************************************************")
	print ("----------------------------------------------------------------------------")
					
	print output_data
	
	print ("-------------------------------------------------------------------------------------------------------------")
	print ("Possible keyTypes are: 1-partialPatientKey, 2-patientUUID, 3-documentUUID, 4-externalID")
	print ("-------------------------------------------------------------------------------------------------------------")
	INPUT_STRING = raw_input("To re-list enter: orgID,keyType,startkey or just enter Q to Quit: ")
	if INPUT_STRING.upper() != "Q":
		validation = validateUpdateString(INPUT_STRING)
		if validation.upper() == "SUCCESS":
			#updateOrgConfig(INPUT_STRING)
			obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)
			readListOfPartialKeys()
		else:
			print (validation)
			#quit()
			raw_input("Press Enter to continue...")
			

#============================ MAIN PROGRAM BODY ==========================================
os.system('clear')

checkForPassedArguments()

outputGlobalVariableSettings()

#connectToMySQL()


INPUT_STRING=""
while INPUT_STRING.upper() != "Q":
	obtainInternalToken(EMAIL, PASSW, {ok, created}, 0, 0)
	readListOfPartialKeys()

#closeMySQLConnection()
#============================ THE END ====================================================
