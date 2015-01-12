#=========================================================================================
#========================== aclsanity.py =================================================
#=========================================================================================
#
# PROGRAM:         aclsanity.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    15-Oct-2014
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Grinder for testing ACL functionality:
#			* Log into ACL
#			* Obtain and save token
#			* Create new unique Coding Org(s) and save org_uuid(s)
#				- Multiple Coding Orgs allowed (NUMBER_OF_ORGS_TO_CREATE) 
#			* Create new unique HCC user(s) and save user_uuid(s) 
#				- Multiple HCC Users allowed (NUMBER_OF_USERS_TO_CREATE)
#			* Create new unique ALC Group and save GRP_UUID
#				- Multiple ACL Groups are allowed (NUMBER_OF_GRPS_TO_CREATE)
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
#          * Assumes a ACL and HCC environments are available
#          * Assumes a Grinder environment is available
#          * For further details, see http://grinder.sourceforge.net
#
# USAGE:
#          * Ensure Grinder is configured to execute acl_complete_test.py
#          * Set the global variables, see below (Global Test Environment Selection)
#          * Run acl_complete_test.py
#          * Results will be printed on Grinder Agent and in Grinder Console log files
#
#=========================================================================================
# Global Paramaters descriptions and possible values:
# These are defined in CSV_CONFIG_FILE_NAME = "aclsanity.csv", 
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
# Specifics: Introduction of external ACLConfig.csv configuration file
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
from time import gmtime, strftime, localtime
import calendar
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
#===================== Initialization of the ACLConfig file ==============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/sanity_test/"
CSV_CONFIG_FILE_NAME = "aclsanity.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "ACL Sanity Test"
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
SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp; %s</b></font></td></tr></table>"

MODULES = {	"login":"0", \
			"create new coding organization":"1", \
			"create and delete new group":"2", \
			"add and delete group permissions":"3", \
			"add delete activate assign new user":"4", \
			"log into hcc":"5", \
			"log into acl":"6", \
			"create new user":"7", \
			"activate new user":"8", \
			"deactivate existing user":"9", \
			"set password":"10", \
			"create new group":"11", \
			"delete existing group":"12", \
			"add group permission":"13", \
			"delete group permission":"14", \
			"add coder to a group":"15", \
			"remove coder from a group":"16", \
			"assign coding organization":"17", \
			"connection to hcc host":"18", \
			"hcc login page":"19", \
			"hcc user login":"20", \
			"user/password/group/org creation/deletion/assignment": "21" \
			}
FAILED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
SUCCEEDED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
RETRIED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
for i in range (0, 22):
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
forbidden = 403
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
	print ("* ACL URL                = %s"%ACL_URL)
	print ("* HCC URL                = %s"%HCC_URL)
	print ("* ACL Admin User Name    = %s"%ACLUSERNAME)
	print ("* Coding Organization    = %s"%CODING_ORGANIZATION)
	print ("* HCC Users to Create    = %s"%str(NUMBER_OF_USERS_TO_CREATE))
	print ("* HCC Orgs to Create     = %s"%str(NUMBER_OF_ORGS_TO_CREATE))
	print ("* HCC Groups to Create   = %s"%str(NUMBER_OF_GRPS_TO_CREATE))
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
def ListUserGroupOrg():
	print ("\n")
	if int(NUMBER_OF_USERS_TO_CREATE) > 0:
		print ("=================================")
		print ("List of newly created HCC Users:")
		print ("=================================")
		for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
			print (HCCUSERSLIST[i])
	print ("=================================")
	print ("List of newly created HCC Orgs:")
	print ("=================================")
	for i in range (0, int(NUMBER_OF_ORGS_TO_CREATE)):
		print (HCCORGLIST[i])
	print ("=================================")
	print ("List of newly created HCC Groups:")
	print ("=================================")
	for i in range (0, int(NUMBER_OF_GRPS_TO_CREATE)):
		print (HCCGRPLIST[i])	
	print ("=================================")
	print ("Test execution results summary:")
	print ("=================================")	
	print ("* RETRIED:    = %s" % RETRIED)			
	print ("* FAILED:     = %s" % FAILED)
	print ("* SUCCEEDED:  = %s" % SUCCEEDED)
	print ("* TOTAL:      = %s" % (RETRIED+FAILED+SUCCEEDED)) 							
	print ("=================================")		

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
	else:
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
	
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
	REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	REPORT = REPORT + HTML_RECEIVERS
	REPORT = REPORT + """MIME-Version: 1.0\n"""
	REPORT = REPORT + """Content-type: text/html\n"""
	REPORT = REPORT + """Subject: ACL %s Sanity Test Report - %s\n\n""" % (ENVIRONMENT, START_TIME)

	REPORT = REPORT + """<h1>Apixio ACL Sanity Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """ACL user name: <b>%s</b><br>\n""" % (ACLUSERNAME)
	REPORT = REPORT + """ACL app url: <b>%s</b><br>\n""" % (ACL_URL)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s%s</font></b><br><br>\n""" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + """<table align="left" width="800" cellpadding="1" cellspacing="1"><tr><td>"""
	print ("End writing report header ...\n")

#=========================================================================================	
	
def writeReportDetails(module):	
	global REPORT
	global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
	
	REPORT = REPORT + SUBHDR % module.upper()
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
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/aclsanity/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/aclsanity/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="ACL Sanity "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/aclsanity/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="acl_sanity_reports_"+ENVIRONMENT.lower()+".txt"
		# Old location 
		#REPORTXTFILEFOLDER="/usr/lib/apx-reporting/html/assets"
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
		REPORTFILETXT = open(REPORTXTFILENAME, 'a')
		REPORTFILETXT.write(REPORTXTSTRING)
		REPORTFILETXT.close()
		os.chdir("/mnt/automation/python/sanity_test")
		print ("Finished archiving report ... \n")

#=========================================================================================	

def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2
	print ("Emailing report ...\n")
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, RECEIVERS, REPORT)	
	s.sendmail(SENDER, RECEIVERS2, REPORT)
	print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)	
			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def logInToACL():
	global TOKEN, ACL_URL, SESSID, DATA, HEADERS
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - OBTAIN AUTHORIZATION <<<")
	print ("----------------------------------------------------------------------------")
	print ("* ACL URL                = %s" % ACL_URL)
	statuscode = 500
	# repeat until successful login is reached
	while statuscode != 200:
  		url = ACL_URL+'/auth'
  		referer = ACL_URL  				
  		DATA =    {'Referer': referer, 'email': ACLUSERNAME, 'password': ACLPASSWORD} 
  		HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
  		response = requests.post(url, data=DATA, headers=HEADERS) 
  		SESSID = TOKEN = response.cookies["session"]
  		print ("* LOG IN USER            = %s" % response.status_code)
		print ("* ACL USERNAME           = %s" % ACLUSERNAME)
		print ("* ACL PASSWORD           = %s" % ACLPASSWORD)
		print ("* ACL SESSION ID         = %s" % SESSID)
		print ("* ACL TOKEN              = %s" % TOKEN)
		statuscode = response.status_code
		print ("* STATUS CODE            = %s" % statuscode)
		IncrementTestResultsTotals("log into acl", statuscode)	
#=========================================================================================
def ACLCreateNewUser(retries):
	global USR_UUID, HCCUSERNAME, TOKEN, ACL_URL
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - CREATE NEW USER <<<")
	print ("----------------------------------------------------------------------------")
	HCCUSERNAME = get_new_hcc_user()	
	url = ACL_URL+'/access/user'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'email': HCCUSERNAME, 'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	userjson = response.json()
	if userjson is not None:
		USR_UUID = userjson.get("id")
		#print ("User UUID: " + USR_UUID)	
	print ("* HCC USERNAME           = %s" % HCCUSERNAME)
	print ("* HCC USER UUID          = %s" % USR_UUID)
	print ("* ACL TOKEN:             = %s" % TOKEN)	
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", statuscode)
	if (statuscode == 500) and (retries <= int(MAX_NUM_RETRIES)):
		print (">>> Failure occured: username already exists <<<")
		retries = retries + 1
		ACLCreateNewUser(retries)				
#=========================================================================================
def ACLActivateNewUser():
	global USR_UUID, TOKEN, ACL_URL
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Activate New User <<<")
	print ("----------------------------------------------------------------------------")	
	#print ("User UUID: " + USR_UUID)
	url = ACL_URL+'/access/user/'+USR_UUID
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.put(url, data=DATA, headers=HEADERS) 
	print ("* HCC USER UUID          = %s" % USR_UUID)
	print ("* ACL TOKEN              = %s" % TOKEN) 	
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", response.status_code)
#=========================================================================================
def ACLDectivateUser(uuid):
	global USR_UUID, TOKEN, ACL_URL
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Deactivate User <<<")
	print ("----------------------------------------------------------------------------")		
	#print ("User UUID: " + USR_UUID)
	url = ACL_URL+'/access/user/'+uuid
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.delete(url, data=DATA, headers=HEADERS)	
	print ("* HCC USER UUID          = %s" % uuid)
	print ("* ACL TOKEN              = %s" % TOKEN) 
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", response.status_code)					
#=========================================================================================
def ACLSetPassword():
	global USR_UUID, HCC_PASSWORD, TOKEN, ACL_URL
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Assign New User Password <<<")
	print ("----------------------------------------------------------------------------")		
	url = ACL_URL+'/access/user/'+USR_UUID+'/password'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'password': HCC_PASSWORD}
	HEADERS = { 'Origin': ACL_URL, 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.put(url, data=DATA, headers=HEADERS) 
	print ("* HCC PASSWORD           = %s" % HCC_PASSWORD)
	print ("* HCC User UUID          = %s" % USR_UUID)
	print ("* ACL TOKEN              = %s" % TOKEN) 				
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", response.status_code)
#=========================================================================================
def ACLCreateNewCodingOrg():
	global ACL_URL, TOKEN, ORG_UUID, ACL_CODNG_ORG_PREFIX, CODING_ORGANIZATION
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Create New Coding Org <<<")
	print ("----------------------------------------------------------------------------")		
	conumber = str(int(time.time()))
	coname = ACL_CODNG_ORG_PREFIX + conumber
	CODING_ORGANIZATION = coname									
	#print ("Coding Org Name: "+coname)		
	url = ACL_URL+'/access/userOrganization'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'name': coname, 'key': conumber, 'description': coname}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	userjson = response.json()
	if userjson is not None:
		ORG_UUID = userjson.get("id")				
	print ("* CODING ORG NAME        = %s" % coname)
	print ("* CODING ORG UUID        = %s" % ORG_UUID)
	print ("* ACL TOKEN              = %s" % TOKEN)			
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("create new coding organization", response.status_code)
#=========================================================================================
def ACLCreateNewGroup():
	global ACL_URL, TOKEN, ACL_GROUP_PREFIX, GRP_UUID, ACLGROUPNAME
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Create New Group <<<")
	print ("----------------------------------------------------------------------------")		
	gnumber = str(int(time.time()))
	gname = ACL_GROUP_PREFIX + gnumber
	ACLGROUPNAME = gname									
	#print ("Group Name: "+gname)
	url = ACL_URL+'/access/group'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'name': gname}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	grpjson = response.json()
	if grpjson is not None:
		GRP_UUID = grpjson.get("id").get("id")
	print ("* GROUP NAME             = %s" % gname)	
	print ("* GROUP UUID             = %s" % GRP_UUID)
	print ("* ACL TOKEN              = %s" % TOKEN)						
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("create and delete new group", response.status_code)
#=========================================================================================
def ACLDeleteExistingGroup(group_uuid):									
	global ACL_URL, TOKEN
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Delete Existing Group <<<")
	print ("----------------------------------------------------------------------------")		
	url = ACL_URL+'/access/group/'+group_uuid
  	referer = ACL_URL+'/admin/'  				
	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer} 
  	response = requests.delete(url, data=DATA, headers=HEADERS) 			
	print ("* GROUP UUID             = %s" % group_uuid)
	print ("* ACL TOKEN              = %s" % TOKEN)				
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("create and delete new group", response.status_code)
#=========================================================================================
def ACLAddGroupPermission(per_type, group_uuid, org_uuid):
	global HCCGRPEMISSIONS
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Add "+per_type+" Group Permission <<<")
	print ("----------------------------------------------------------------------------")	
	url = ACL_URL+'/access/permission/'+group_uuid+'/'+org_uuid+'/'+per_type
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	#grpjson = response.json()
	print ("* GROUP UUID             = %s" % group_uuid)
	print ("* ORG UUID               = %s" % org_uuid)
	print ("* PERMISSION TYPE        = %s" % per_type)		
	print ("* ACL TOKEN              = %s" % TOKEN)					
	statuscode = response.status_code	
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("add and delete group permissions", statuscode)
	if (statuscode == ok) or (statuscode == nocontent):
		if per_type == "canAnnotate":
			HCCGRPEMISSIONS[0] = "1"
		elif per_type == "viewDocuments":
			HCCGRPEMISSIONS.append(1)
			HCCGRPEMISSIONS[1] = "1"
		elif per_type == "viewReportsAnnotatedFor":
			HCCGRPEMISSIONS.append(2)
			HCCGRPEMISSIONS[2] = "1"
		elif per_type == "viewReportsAnnotatedBy":
			HCCGRPEMISSIONS.append(3)
			HCCGRPEMISSIONS[3] = "1"
		elif per_type == "viewAllAnnotations":
			HCCGRPEMISSIONS.append(4)
			HCCGRPEMISSIONS[4] = "1"
		elif per_type == "canRelease":
			HCCGRPEMISSIONS.append(5)
			HCCGRPEMISSIONS[5] = "1"	
#=========================================================================================
def ACLDelGroupPermission(per_type, group_uuid, org_uuid):
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Del "+per_type+" Group Permission <<<")
	print ("----------------------------------------------------------------------------")	
		
	url = ACL_URL+'/access/permission/'+group_uuid+'/'+org_uuid+'/'+per_type
  	referer = ACL_URL+'/admin/'  				
	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer} 
  	response = requests.delete(url, data=DATA, headers=HEADERS) 		
	print ("* GROUP UUID             = %s" % group_uuid)
	print ("* ORG UUID:              = %s" % org_uuid)
	print ("* PERMISSION TYPE        = %s" % per_type)		
	print ("* ACL TOKEN              = %s" % TOKEN)				
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("add and delete group permissions", response.status_code)			
#=========================================================================================
def ACLAddMemberToGroup():
	global USR_UUID, GRP_UUID, ACL_URL
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Add Member to Group <<<")
	print ("----------------------------------------------------------------------------")		
	print ("* USER UUID              = %s" % USR_UUID)
	print ("* GROUP UUID             = %s" % GRP_UUID)
	url = ACL_URL+'/access/groupMembership/'+GRP_UUID+'/'+USR_UUID
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	print ("* ACL GROUP UUID         = %s" % GRP_UUID)
	print ("* HCC USER UUID          = %s" % USR_UUID)		
	print ("* ACL TOKEN              = %s" % TOKEN)						
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", response.status_code)
#=========================================================================================
def ACLDelMemberFromGroup(group_uuid, usr_uuid):	
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Del Member from Group <<<")
	print ("----------------------------------------------------------------------------")		
	url = ACL_URL+'/access/groupMembership/'+group_uuid+'/'+usr_uuid
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.delete(url, data=DATA, headers=HEADERS) 	
	print ("* HCC USER UUID:         = %s" % usr_uuid)
	print ("* ACL GROUP UUID:        = %s" % group_uuid)				
	print ("* ACL TOKEN:             = %s" % TOKEN)			
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", response.status_code)
#=========================================================================================
def ACLAssignCodingOrg():
	global USR_UUID, ORG_UUID, ACL_URL
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - Assign Coding Organization <<<")
	print ("----------------------------------------------------------------------------")			
	#print ("User UUID: " + USR_UUID)
	#print ("Org UUID: " + ORG_UUID)
	url = ACL_URL+'/access/userOrganization/'+ORG_UUID+'/'+USR_UUID
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 	
	print ("* HCC USER UUID          = %s" % USR_UUID)
	print ("* ACL ORG UUID           = %s" % ORG_UUID)				
	print ("* ACL TOKEN              = %s" % TOKEN)								
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("user/password/group/org creation/deletion/assignment", response.status_code)
#=========================================================================================
def logInToHCC(): 
	global TOKEN, SESSID, DATA, HEADERS
	global HCCUSERNAME, HCC_PASSWORD, HCC_URL
	global HCC_TOKEN, HCC_SESSID
	HCC_HOST_DOMAIN = 'hccstage.apixio.com'
	HCC_HOST_URL = 'https://%s' % HCC_HOST_DOMAIN
	response = requests.get(HCC_URL+'/')
	IncrementTestResultsTotals("log into hcc", response.status_code)
	print ("\n----------------------------------------------------------------------------")
	print (">>> HCC - CONNECT TO HOST <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RESPONSE CODE          = %s" % response.status_code)
	url = referer = HCC_URL+'/account/login/?next=/'
	response = requests.get(url)
	IncrementTestResultsTotals("log into hcc", response.status_code)
	print ("\n----------------------------------------------------------------------------")
	print (">>> HCC - LOGIN PAGE <<<")
	print ("----------------------------------------------------------------------------")	
	print ("* RESPONSE CODE          = %s" % response.status_code)
	HCC_TOKEN = response.cookies["csrftoken"]
	HCC_SESSID = response.cookies["sessionid"]
	DATA =    {'csrfmiddlewaretoken': HCC_TOKEN, 'username': HCCUSERNAME, 'password': HCC_PASSWORD } 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '115', \
				'Cookie': 'csrftoken='+HCC_TOKEN+'; sessionid='+HCC_SESSID+' ', \
				'Referer': referer}			
	response = requests.post(url, data=DATA, headers=HEADERS) 
	print ("\n----------------------------------------------------------------------------")
	print (">>> HCC - LOGIN USER <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RESPONSE CODE          = %s" % response.status_code)
	print ("* HCC Username           = %s" % HCCUSERNAME)
	print ("* HCC Password           = %s" % HCC_PASSWORD)
	print ("* HCC Token              = %s" % HCC_TOKEN)
	print ("* HCC Session ID         = %s" % HCC_SESSID)
	print ("* STATUS CODE            = %s" % response.status_code)
	IncrementTestResultsTotals("log into hcc", response.status_code)	
				
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
os.system('clear')

print ("\n\nStarting ACL-Admin New User Creation...\n")

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

writeReportHeader()

PrintGlobalParamaterSettings()

logInToACL()
writeReportDetails("log into acl")

# Org related testing
ACLCreateNewCodingOrg()
writeReportDetails("create new coding organization")

# Group related testing
ACLCreateNewGroup()
ACLDeleteExistingGroup(GRP_UUID)
ACLCreateNewGroup()
writeReportDetails("create and delete new group")
		
for permission in PERIMISSION_TYPES:
	ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
	ACLDelGroupPermission(permission, GRP_UUID, ORG_UUID)
	ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
writeReportDetails("add and delete group permissions")	
			
# User related testing			
for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
	ACLCreateNewUser(0)
	HCCUSERSLIST.append(i)
	HCCUSERSLIST[i] = HCCUSERNAME
	ACLActivateNewUser()
	ACLDectivateUser(USR_UUID)
	ACLActivateNewUser()
	ACLSetPassword()
	ACLAssignCodingOrg()
	ACLAddMemberToGroup()
	ACLDelMemberFromGroup(GRP_UUID, USR_UUID)
	ACLAddMemberToGroup()
	logInToHCC()	
writeReportDetails("user/password/group/org creation/deletion/assignment")

logInToHCC()
writeReportDetails("log into hcc")
	
ListUserGroupOrg()

writeReportFooter()

archiveReport()

emailReport()	
	
print ("==== End of ACL Sanity Test =====")
print ("=================================")
#=========================================================================================