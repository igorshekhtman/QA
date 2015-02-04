#=========================================================================================
#========================== ussanity.py ==================================================
#=========================================================================================
#
# PROGRAM:         uasanity.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    15-Oct-2014
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Grinder for testing User Accounts functionality:
#			* Log into User Accounts
#			* Obtain and save token
#			* Create new unique Coding Org(s) and save org_uuid(s)
#				- Multiple Coding Orgs allowed (NUMBER_OF_ORGS_TO_CREATE) 
#			* Create new unique HCC user(s) and save user_uuid(s) 
#				- Multiple HCC Users allowed (NUMBER_OF_USERS_TO_CREATE)
#			* Create new unique UA Group and save GRP_UUID
#				- Multiple UA Groups are allowed (NUMBER_OF_GRPS_TO_CREATE)
#			* Activate newly created HCC user
#			* Deactivate a specific HCC user
#			* Assign newly created user pre-defined password (HCC_PASSWORD)
#			* Assign newly created HCC user coding org
#				- Either pre-defined coding org or newly created coding org
#			* Assign specific or newly created coding org to a user
#			* Add list of members to a newly created Group
#			* Remove specific member(s) from a Group
#			* Add specific rules to a Group
#			* Delete specific rules from a Group
#			* Log into HCC with newly created user/org
#			* Store each of the newly created users in an array (HCCUSERSLIST[])
#			* Store each of the newly created coding orgs in an array (HCCORGLIST[])
#			* Report total number of retries, failures and successes
#
# SETUP:
#          * Assumes a User Accounts and HCC environments are available
#
# USAGE:
#          * Ensure Grinder is configured to execute acl_complete_test.py
#          * Set the global variables, see below (Global Test Environment Selection)
#          * Run acl_complete_test.py
#          * Results will be printed on Grinder Agent and in Grinder Console log files
#
#=========================================================================================
# Global Paramaters descriptions and possible values:
# These are defined in CSV_CONFIG_FILE_NAME = "uasanity.csv", 
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
#=========================================================================================
# Revision 1: 1.0.1
# Author: Igor Shekhtman ishekhtman@apixio.com 
# Specifics: Introduction of Program Flow Control
#=========================================================================================
# Revision 2: 1.0.2
# Author: Igor Shekhtman ishekhtman@apixio.com
# Specifics: Introduction of external uasanity.csv configuration file
#=========================================================================================
# Revision 3:
# Author:
# Specifics:
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
#=== CODING ORG MAP: ORG_NAME - ORG_UUID =================================================
#=========================================================================================
CDGORGMAP = { \
	"AE & Associates":"UO_7ffb36bb-26c1-439e-b259-9a6db503aa11", \
	"Scripps":"UO_609aa5c3-4bff-4aec-a629-1da4f0be144e", \
	"Coding Org 1":"UO_5c83fcf7-d216-42ca-859d-9908e74049e5", \
	"Coding Org 2":"UO_c2fee803-b169-4bfb-9e46-137295379b46", \
	"Coding Org 3":"UO_fb540446-a07d-4e2f-b2a2-6caf1179d455", \
	"HealthCare Partners":"UO_62eb7683-e42b-4cf4-a7cf-e91dcaf68bbb", \
	"Apixio Coders":"UO_059c7bbd-7ecc-4172-8d81-6ea2dadb6e76", \
	"CCHCA":"UO_6cbe9df5-cdfb-414f-b1f0-f44c7b519bcb", \
	"Load Test Coders":"UO_149af107-1ef7-49a0-923e-be4b2de174b3", \
	"org0420":"UO_7c6cf5ea-b35c-4ecf-866f-915f70269d34", \
	"test Coding org":"UO_ee2a6959-bc38-40c3-813b-d3e7a9cc681b", \
	"Test Org2":"UO_8f2082b8-5060-4e90-bd6e-3db8f97659a6", \
	"Test Org 1000":"UO_45dcce68-47a8-4e0f-9cf4-467476021337", \
	"Test Org 1000":"UO_1296f532-2605-4e63-9d09-e5e992bd07ea", \
	"Test Org 1000":"UO_6add7125-0eb0-472c-9840-47e24867f5ea", \
	"test org1":"UO_9010f837-0ac7-41fa-abbf-16c82b1c9032", \
	}

PERIMISSION_TYPES = [ \
	"canAnnotate", \
	"viewDocuments", \
	"viewReportsAnnotatedFor", \
	"viewReportsAnnotatedBy", \
	"viewAllAnnotations", \
	"canRelease" \
	]
	
#=========================================================================================
#===================== Initialization of the UAConfig file ==============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/sanity_test/"
CSV_CONFIG_FILE_NAME = "uasanity.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "User Accounts Sanity Test"
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

PASSED_STAT="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED_STAT="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp; %s (%s)</b></font></td></tr></table>"

MODULES = {	"log into user accounts":"0", \
			"password reminder":"1", \
			"log into hcc":"2" \
			}
FAILED_TOT = [0,1,2]
SUCCEEDED_TOT = [0,1,2]
RETRIED_TOT = [0,1,2]
for i in range (0, 3):
	FAILED_TOT[i] = 0
	SUCCEEDED_TOT[i] = 0
	RETRIED_TOT[i] = 0

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
badrequest = 400
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
    print "cookies = [%s]" % cookies
    return cookies    
#=========================================================================================    
def get_new_hcc_user():
	global HCC_USERNAME_PREFIX, HCC_USERNAME_POSTFIX
	hccusernumber = str(int(time.time()))
	hccusername = HCC_USERNAME_PREFIX + hccusernumber + HCC_USERNAME_POSTFIX
	return hccusername
#=========================================================================================
def PrintGlobalParamaterSettings():
	print ("\n")
	print ("* Version                = %s"%VERSION)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* UA URL                = %s"%UA_URL)
	print ("* HCC URL                = %s"%HCC_URL)
	print ("* UA Admin User Name    = %s"%UAUSERNAME)
	print ("* Coding Organization    = %s"%CODING_ORGANIZATION)
	print ("* HCC Users to Create    = %s"%str(NUMBER_OF_USERS_TO_CREATE))
	print ("* HCC Orgs to Create     = %s"%str(NUMBER_OF_ORGS_TO_CREATE))
	print ("* HCC Groups to Create   = %s"%str(NUMBER_OF_GRPS_TO_CREATE))
#=========================================================================================
def IncrementTestResultsTotals(module, code, testype):
	global FAILED, SUCCEEDED, RETRIED
	global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
	if testype == "positive":
		accepted_codes = {ok, nocontent}
	else:
		accepted_codes = {unauthorized, forbidden, badrequest, notfound}	
	if code in accepted_codes:
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
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
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
		UA_DOMAIN="acladmin.apixio.com"
		UA_URL="https://acladmin.apixio.com"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		UAUSERNAME="root@api.apixio.com"
		UAPASSWORD="thePassword"
	else:
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
		UA_DOMAIN="accounts-stg.apixio.com"
		UA_URL="https://accounts-stg.apixio.com"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		UAUSERNAME="abeyk6@apixio.net"
		UAPASSWORD="apixio.123"
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS2=str(sys.argv[3])
		HTML_RECEIVERS="""To: Eng <%s>,Ops <%s>\n""" % (str(sys.argv[2]), str(sys.argv[3]))
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS2="abeyk@apixio.com"
		HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""
				
	# overwite any previous ENVIRONMENT settings
	#ENVIRONMENT = "Production"
	print ("Version %s\n") % VERSION
	print ("ENVIRONMENT = %s\n") % ENVIRONMENT
	print ("Completed setting of enviroment and report receivers ...\n")		

#=========================================================================================	
	
def writeReportHeader ():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Begin writing report header ...\n")
	# REPORT = MIMEMultipart()
	#REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	#REPORT = REPORT + HTML_RECEIVERS
	#REPORT = REPORT + """MIME-Version: 1.0\n"""
	#REPORT = REPORT + """Content-type: text/html\n"""
	#REPORT = REPORT + """Subject: OppRouter %s Optimization Test Report - %s\n\n""" % (ENVIRONMENT, START_TIME)
	REPORT = """ """
	REPORT = REPORT + """<h1>Apixio User Accounts Sanity Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """UA user name: <b>%s</b><br>\n""" % (UAUSERNAME)
	REPORT = REPORT + """UA app url: <b>%s</b><br>\n""" % (UA_URL)
	#REPORT = REPORT + """Maximum # of Opps to serve: <b>%s</b><br>\n""" % (CODE_OPPS_MAX)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s%s</font></b><br><br>\n""" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + """<table align="left" width="800" cellpadding="1" cellspacing="1"><tr><td>"""
	print ("End writing report header ...\n")

#=========================================================================================	
	
def writeReportDetails(module, testype):	
	global REPORT
	global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
	
	REPORT = REPORT + SUBHDR % (module.upper(), testype)
	#obtainFailedJobs("summary_coordinator_jobfinish"+POSTFIX)
	REPORT = REPORT + "<table spacing='1' padding='1'><tr><td>Succeeded:</td><td>"+str(SUCCEEDED_TOT[int(MODULES[module])])+"</td></tr>"
	REPORT = REPORT + "<tr><td>Retried:</td><td>"+str(RETRIED_TOT[int(MODULES[module])])+"</td></tr>"
	REPORT = REPORT + "<tr><td>Failed:</td><td>"+str(FAILED_TOT[int(MODULES[module])])+"</td></tr></table>"
	if (FAILED_TOT[int(MODULES[module])] > 0) or (RETRIED_TOT[int(MODULES[module])] > 0):
		REPORT = REPORT+FAILED_STAT
	else:
		REPORT = REPORT+PASSED_STAT
	print ("Completed writeReportDetails ... \n")

#=========================================================================================			
	
def writeReportFooter():
	global REPORT
	print ("Write report footer ...\n")
	#REPORT = REPORT+"</td></tr></table>"
	REPORT = REPORT+"<table>"
	END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	REPORT = REPORT+"<tr><td><br>Start of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, START_TIME)
	REPORT = REPORT+"<tr><td>End of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, END_TIME)
	TIME_END = time.time()
	TIME_TAKEN = TIME_END - TIME_START
	hours, REST = divmod(TIME_TAKEN,3600)
	minutes, seconds = divmod(REST, 60)
	REPORT = REPORT+"<tr><td>Test Duration: <b>%s hours, %s minutes, %s seconds</b><br></td></tr>" % (hours, minutes, seconds)
	REPORT = REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr>"
	REPORT = REPORT+"</table>"
	REPORT = REPORT+"</td></tr></table>"
	print ("Finished writing report ...\n")

#=========================================================================================	

def archiveReport():
	global DEBUG_MODE, ENVIRONMENT, CURMONTH, CURDAY
	if not DEBUG_MODE:
		print ("Archiving report ...\n")
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/uasanity/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/uasanity/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="UA Sanity "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/uasanity/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="ua_sanity_reports_"+ENVIRONMENT.lower()+".txt"
		# New location 
		REPORTXTFILEFOLDER="/usr/lib/apx-reporting/assets"
		os.chdir(BACKUPREPORTFOLDER)
		REPORTFILE = open(REPORTFILENAME, 'w')
		REPORTFILE.write(REPORT)
		REPORTFILE.close()
		os.chdir(REPORTFOLDER)
		REPORTFILE = open(REPORTFILENAME, 'w')
		REPORTFILE.write(REPORT)
		REPORTFILE.close()		
		os.chdir(REPORTXTFILEFOLDER)
		f = open(REPORTXTFILENAME)
		s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
		if s.find(REPORTXTSTRING) != -1:
			print "Report entry found, skipping append ...\n"
		else:
			print "Report entry not found, appending new entry ...\n"
			REPORTFILETXT = open(REPORTXTFILENAME, 'a')
			REPORTFILETXT.write(REPORTXTSTRING)
			REPORTFILETXT.close()
		os.chdir("/mnt/automation/python/sanity_test")
		print ("Finished archiving report ... \n")

#=========================================================================================	

def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2, REPORT, REPORT_EMAIL
	
	print ("Emailing report ...\n")
	REPORT_EMAIL = REPORT
	IMAGEFILENAME=str(CURDAY)+".png" 
	message = MIMEMultipart('related')
	message.attach(MIMEText((REPORT_EMAIL), 'html'))
	#code removed since no image is being attached
	#======================================================
	#with open(IMAGEFILENAME, 'rb') as image_file:
	#	image = MIMEImage(image_file.read())
	#image.add_header('Content-ID', '<picture@example.com>')
	#image.add_header('Content-Disposition', 'inline', filename=IMAGEFILENAME)
	#message.attach(image)
	#=======================================================

	message['From'] = 'Apixio QA <QA@apixio.com>'
	message['To'] = 'To: Eng <eng@apixio.com>,Ops <ops@apixio.com>'
	message['Subject'] = 'User Accounts %s Sanity Test Report - %s\n\n' % (ENVIRONMENT, START_TIME)
	msg_full = message.as_string()
		
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, [RECEIVERS, RECEIVERS2], msg_full)	
	s.quit()
	# Delete graph image file from stress_test folder
	#os.remove(IMAGEFILENAME)
	print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)
	
	#print ("Emailing report ...\n")
	#s=smtplib.SMTP()
	#s.connect("smtp.gmail.com",587)
	#s.starttls()
	#s.login("donotreply@apixio.com", "apx.mail47")	        
	#s.sendmail(SENDER, RECEIVERS, REPORT)	
	#s.sendmail(SENDER, RECEIVERS2, REPORT)
	#print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)	
			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def logInToUA(testype):
	global TOKEN, UA_URL, SESSID, DATA, HEADERS, UAPASSWORD
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - LOGIN TEST (%s) <<<") % testype
	print ("----------------------------------------------------------------------------")

	url = UA_URL+'/auth'
	referer = UA_URL  

	#Corrupt user password for negative test purposes
	if testype == "negative":
		password = "123.apixio"
	else:
		password = 	UAPASSWORD		
  	DATA =    {'Referer': referer, 'email': UAUSERNAME, 'password': password} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS)
  	statuscode = response.status_code
  	print ("* SERVER RESPONSE CODE  = %s" % statuscode)
  	print ("* UA LOGIN TEST         = %s" % testype.upper())
  	if statuscode == ok:
  		SESSID = TOKEN = response.cookies["session"]
		print ("* UA SESSION ID         = %s" % SESSID)
		print ("* UA TOKEN              = %s" % TOKEN)
	print ("* UA URL                = %s" % url)
  	print ("* UA REFERER            = %s" % referer)
	print ("* UA USERNAME           = %s" % UAUSERNAME)
	print ("* UA PASSWORD           = %s" % password)
	IncrementTestResultsTotals("log into user accounts", statuscode, testype)	
	print ("\nUA Login Test Completed ...\n")	
	#quit()
		
#=========================================================================================		
def passwordReminder(testype):
	global TOKEN, UA_URL, SESSID, DATA, HEADERS, UAPASSWORD, UAUSERNAME
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - PASSWORD REMINDER TEST (%s) <<<") % testype
	print ("----------------------------------------------------------------------------")
	
	url = UA_URL+'/auth/forgot'
	referer = UA_URL  

	#Corrupt user password for negative test purposes
	if testype == "negative":
		username = "abeyk999999@apixio.net"
	else:
		username = 	UAUSERNAME					
  	DATA =    {'Referer': referer, 'emailAddress': username} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS)
  	statuscode = response.status_code
  	print ("* SERVER RESPONSE CODE  = %s" % statuscode)
  	print ("* UA LOGIN TEST         = %s" % testype.upper())
  	if statuscode == ok:
  		SESSID = TOKEN = response.cookies["session"]
  		#print ("* LOG IN USER            = %s" % response.status_code)
		print ("* UA SESSION ID         = %s" % SESSID)
		print ("* UA TOKEN              = %s" % TOKEN)
	print ("* UA URL                = %s" % url)
  	print ("* UA REFERER            = %s" % referer)
	print ("* UA USERNAME           = %s" % username)
	
	IncrementTestResultsTotals("password reminder", statuscode, testype)	
	print ("\nUA password reminder test completed ...\n")
	#quit()
#=========================================================================================
def logInToHCC(testype): 
	global TOKEN, SESSID, DATA, HEADERS
	global HCCUSERNAME, HCC_PASSWORD, HCC_URL
	global HCC_TOKEN, HCC_SESSID
	
	#Corrupt user password for negative test purposes
	if testype == "negative":
		url = HCC_URL+'/test/'
	else:
		url = HCC_URL+'/'	
	print ("\n----------------------------------------------------------------------------")
	print (">>> HCC - CONNECT TO HOST (%s) <<<") % testype
	print ("----------------------------------------------------------------------------")
	response = requests.get(url)
	statuscode = response.status_code
  	print ("* SERVER RESPONSE CODE  = %s" % statuscode)
  	print ("* UA CONNECT TO HOST    = %s" % testype.upper())
	IncrementTestResultsTotals("log into hcc", response.status_code, testype)
	print ("\nHCC connect to host test completed ...\n")	
	#quit()
	
	#Corrupt user password for negative test purposes
	if testype == "negative":
		url = HCC_URL+'/account/logins/?previous=/'
	else:
		url = HCC_URL+'/account/login/?next=/'
	print ("\n----------------------------------------------------------------------------")
	print (">>> HCC - LOGIN PAGE (%s) <<<") % testype
	print ("----------------------------------------------------------------------------")	
	response = requests.get(url)
	statuscode = response.status_code
	print ("* SERVER RESPONSE CODE  = %s" % statuscode)
	print ("* UA LOGIN PAGE TEST    = %s" % testype.upper())
	if statuscode == ok:
		HCC_TOKEN = response.cookies["csrftoken"]
		HCC_SESSID = response.cookies["sessionid"]
		print ("* HCC SESSION ID        = %s" % HCC_SESSID)
		print ("* HCC TOKEN             = %s" % HCC_TOKEN)
	print ("* HCC URL               = %s" % url)		
	IncrementTestResultsTotals("log into hcc", response.status_code, testype)
	print ("\nHCC login page test completed ...\n")
	#quit()
	
	
	#Corrupt user password for negative test purposes
	url = HCC_URL+'/account/login/?next=/'
	response = requests.get(url)
	HCC_TOKEN = response.cookies["csrftoken"]
	HCC_SESSID = response.cookies["sessionid"]
	
	if testype == "negative":
		token = '245624564526-2456245624562-245624562456'
	else:
		token = HCC_TOKEN	
	print ("\n----------------------------------------------------------------------------")
	print (">>> HCC - LOGIN USER (%s) <<<") % testype
	print ("----------------------------------------------------------------------------")	
	url = HCC_URL+'/account/login/?next=/'
	referer = HCC_URL+'/account/login/?next=/'
	DATA =    {'csrfmiddlewaretoken': token, 'username': UAUSERNAME, 'password': UAPASSWORD } 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '115', \
				'Cookie': 'csrftoken='+HCC_TOKEN+'; sessionid='+HCC_SESSID+' ', \
				'Referer': referer}			
	response = requests.post(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* SERVER RESPONSE CODE  = %s" % statuscode)
	print ("* HCC LOGIN USER TEST   = %s" % testype.upper())
	if statuscode == ok:
		print ("* HCC Username           = %s" % UAUSERNAME)
		print ("* HCC Password           = %s" % UAPASSWORD)
		print ("* HCC Token              = %s" % HCC_TOKEN)
		print ("* HCC Session ID         = %s" % HCC_SESSID)

	IncrementTestResultsTotals("log into hcc", response.status_code, testype)	
	print ("\nHCC login user test completed ...\n")
				
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
os.system('clear')

print ("\n\nStarting User Accounts - Admin New User Creation...\n")

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

writeReportHeader()

PrintGlobalParamaterSettings()

logInToUA("positive")
writeReportDetails("log into user accounts", "positive")

logInToUA("negative")
writeReportDetails("log into user accounts", "negative")

passwordReminder("positive")
writeReportDetails("password reminder", "positive")

passwordReminder("negative")
writeReportDetails("password reminder", "negative")

logInToUA("positive")
writeReportDetails("log into user accounts", "positive")

logInToHCC("positive")
writeReportDetails("log into hcc", "positive")

logInToHCC("negative")
writeReportDetails("log into hcc", "negative")
	
writeReportFooter()

archiveReport()

emailReport()	
	
print ("==== End of User Accounts Sanity Test =====")
print ("===========================================")
#=========================================================================================