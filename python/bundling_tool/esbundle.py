#=========================================================================================
#====================================== bundle_new.py ====================================
#=========================================================================================
#
# PROGRAM:         esbundle.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    13-Aug-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for ES Bundle specific data set:
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
	
ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
requestdenied = 400
unauthorized = 401
forbidden = 403
notfound = 404
intserveror = 500
servunavail = 503

HCCUSERSLIST = [0]
HCCORGLIST = [0]
HCCGRPLIST = [0]
HCCGRPEMISSIONS = [0]
FAILED = 0
SUCCEEDED = 0
RETRIED = 0
#=========================================================================================
#===================== Helper Functions ==================================================
#=========================================================================================
def LogData(data):
	global REPORT
	print (data)
	REPORT = REPORT + str(data) + "<br>"

#=========================================================================================
def create_request(test, headers=None):
    request = HTTPRequest()
    if headers:
        request.headers = headers
        #print "headers = [%s]" % headers
    test.record(request)
    #print "request = [%s]" % request
    return request
#=========================================================================================    
def get_session(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    session = ''
    #print "cookies = [%s]" % cookies
    for cookie in cookies:
        if cookie.getName() == 'session':
            session = cookie.getValue()
            #print "cookie = [%s]" % cookie
    return session
#=========================================================================================    
def get_csrf_token(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    csrftoken = ''
    for cookie in cookies:
        if cookie.getName() == 'csrftoken':
            csrftoken = cookie.getValue()
    return csrftoken    
#=========================================================================================    
def print_all_cookies(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    print ("cookies = [%s]" % cookies)
    return cookies    
#=========================================================================================    
def get_new_hcc_user():
	global HCC_USERNAME_PREFIX, HCC_USERNAME_POSTFIX
	hccusernumber = str(int(time.time()))
	hccusername = HCC_USERNAME_PREFIX + hccusernumber + HCC_USERNAME_POSTFIX
	return hccusername
#=========================================================================================
def printGlobalParamaterSettings():
#with optional batch id: ?batch_id={batchId} if you want to limit bundling to a particular run of events

	print ("\n")
	print ("* Version                = %s"%VERSION)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* UA  URL                = %s"%UA_URL)
	print ("* ACL Admin User Name    = %s"%ACLUSERNAME)
	print ("* PARMFILE               = %s"%PARMFILE)

#=========================================================================================
def IncrementTestResultsTotals(module, code):
	global FAILED, SUCCEEDED, RETRIED
	global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
	if (code == ok) or (code == nocontent):
		SUCCEEDED = SUCCEEDED+1
		SUCCEEDED_TOT[int(MODULES[module])] = SUCCEEDED_TOT[int(MODULES[module])] + 1
	#elif code == intserveror:
	#	RETRIED = RETRIED+1
	else:
		FAILED = FAILED+1
		FAILED_TOT[int(MODULES[module])] = FAILED_TOT[int(MODULES[module])] + 1
#=========================================================================================							
def WriteToCsvFile():
	file_obj = CSV_FILE_PATH + CSV_FILE_NAME
	f = open(file_obj, 'w')
	file_writer=csv.writer(f, delimiter=',')
	# write headers row
	file_writer.writerow (["Status", "Environment", "UserName", "Password", \
		"CodingOrg", "Group", "canAnnotate", "viewDocuments", \
		"viewReportsAnnotatedFor", "viewReportsAnnotatedBy", \
		"viewAllAnnotations"])
	for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
		file_writer.writerow (["1", HCC_DOMAIN, str(HCCUSERSLIST[i]), \
			HCC_PASSWORD, HCCORGLIST[0], HCCGRPLIST[0], HCCGRPEMISSIONS[0], \
			HCCGRPEMISSIONS[1], HCCGRPEMISSIONS[2], \
			HCCGRPEMISSIONS[3], HCCGRPEMISSIONS[4]])
	#f.write('\n')
	f.close()	

#=========================================================================================	
	
def checkEnvironmentandReceivers():
	
	# Environment for ES Bundler is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - parmfile
	
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS, PROJECTID, BATCHID, BUNDL_URL
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global PARMFILE, BNDL_URL, UA_URL, HCC_URL, ACLUSERNAME, ACLPASSWORD, TOKEN_URL
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		#USERNAME="apxdemot0138"
		#PASSWORD="Hadoop.4522"
		ENVIRONMENT = "production"
		ACL_DOMAIN="acladmin.apixio.com"
		UA_URL="https://useraccount.apixio.com:7076"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="system_qa@apixio.com"
		ACLPASSWORD="9p2qa20.."
		BUNDL_URL="http://52.11.138.4:8087"
		BNDL_URL="https://bundler-2.apixio.com:8443/hcc/bundler/bundle"
		TOKEN_URL="https://tokenizer.apixio.com:7075/tokens"
	else:
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://acladmin-stg.apixio.com"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="ishekhtman@apixio.com"
		ACLPASSWORD="apixio.123"
		BUNDL_URL="http://52.11.138.4:8087"
		BNDL_URL="https://bundler-stg2.apixio.com:8443/hcc/bundler/bundle"
		TOKEN_URL="https://tokenizer-stg.apixio.com:7075/tokens"
	
	if (len(sys.argv) > 2):
		PARMFILE=str(sys.argv[2])
	else:
		print "Missing project ID, aborting now ..."
		print "Proper use instructions:"
		print "python2.7 esbundle.py <environment> <parm-file-name (required)>"
		quit()


				
	# overwite any previous ENVIRONMENT settings
	#ENVIRONMENT = "Production"
	print ("Version %s\n") % VERSION
	print ("ENVIRONMENT = %s\n") % ENVIRONMENT
	print ("Completed setting of enviroment and report receivers ...\n")		



			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def obtainExternalToken(un, pw, exp_statuscode, tc, step):

	external_token = ""
	#ACLUSERNAME="lschneider@apixio.com"
	#ACLPASSWORD="ritiyi6!"
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
		print ("* ACL USERNAME           = %s" % un)
		print ("* ACL PASSWORD           = %s" % pw)
		print ("* URL                    = %s" % url)
		print ("* EXTERNAL TOKEN         = %s" % external_token)
		print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
		print ("* RECEIVED STATUS CODE   = %s" % statuscode)
		print ("****************************************************************************")
			
	return (external_token)

#=========================================================================================
def obtainInternalToken(un, pw, exp_statuscode, tc, step):
	global TOKEN, APIXIO_TOKEN
	
	print ("----------------------------------------------------------------------------")
	print (">>> ACL - OBTAIN EXTERNAL AND EXCHANGE FOR INTERNAL TOKEN <<<")
	print ("----------------------------------------------------------------------------")
	
	
	#TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
	external_token = obtainExternalToken(un, pw, exp_statuscode, tc, step)
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
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)

	
#=========================================================================================

def bundleDataSet():
	print ("\n----------------------------------------------------------------------------")
	print (">>> BUNDLE DATA SET FOR %s PARMFILE <<<" % PARMFILE)
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = "https://bundler-stg2.apixio.com:8443/hcc/bundler/bundle"
	URL = BNDL_URL

	
	print ("\n")
	print ("* URL                    = %s"%URL)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* Admin User Name        = %s"%ACLUSERNAME)
	print ("* Parameters File        = %s"%PARMFILE)	
	print ("* Internal Token         = %s"%TOKEN)
	print ("* Apixio Token           = %s"%APIXIO_TOKEN)
	
	DATA = json.load(open(PARMFILE))
	FILES = {'file': (PARMFILE, open(PARMFILE, 'rb'), 'application/json', {'Expires': '0'})}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.put(URL, data=json.dumps(DATA), files={}, headers=HEADERS)
	statuscode = response.status_code

	print ("* Status Code            = %s"%statuscode)


	if statuscode != ok:
		print "Failure occured, exiting now ..."
		quit()
	else:
		print "Successfully bundling ..."		

	return()	

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

#ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

printGlobalParamaterSettings()

obtainInternalToken(ACLUSERNAME, ACLPASSWORD, {ok, created}, 0, 0)

bundleDataSet()
	

print ("\n============================================================================")	
print ("============================= End of Elastic Bundler =========================")
print ("============================================================================")
#=========================================================================================
