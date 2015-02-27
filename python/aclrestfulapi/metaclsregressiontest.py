#=========================================================================================
#========================== metaclsregressiontest.py =====================================
#=========================================================================================
#
# PROGRAM:         metaclsregressiontest.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    23-Feb-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for testing Meta ACLs functionality:
#
# NOTES / COMMENTS:
#			* Based on the 5 specific test cases I outlined in an email last week and that were copied to the JIRA QA ticket, I think it makes 
#				sense to provide the following new RESTful APIs to be added to user-account service:
#
#			* GET /perms/{subject}/{operation}/{object}
#
#			  This API would perform a "has permission" test on the Subject/Operation/Object and return either 200 (has permission) or 403 (doesn't have permission)
#
#			* PUT /perms/{subject}/{operation}/{object}
#
#  				This API would attempt to add the given permission.  If the user linked with the token presented in the Authorization: HTTP header has the ability to add that permission, the 200 status code will be returned, otherwise a 403 will be returned.  There is no HTTP body.
#
#			* DELETE /perms/{subject}/{operation}/{object}
#
#  				This API will undo the effects of the PUT call, if the authenticated user has permission.
#
#			* PUT /grants/{subject}/{operation}
#
#  				This APi will attempt to grant the given subject the rights to add permission on the given operation.  The constraints on the subject and object of that "add permission" operation will be given by a string-ized JSON object that is the HTTP body.
#
#			* DELETE /grants/{subject}/{operation}
#
#  				This API will attempt to undo the effect of the PUT form of this URL.  No HTTP body is required.
#
#			* GET /groups
#
#  				This API will return a list of all UserGroups.  An optional query parameter of "type=role" will restrict the returned groups to those that are role-based UserGroups.  Only ROOT can request this list of groups.
#
#			* GET /groups/{group}/members
#
#  				This API will return the members of the given UserGroup.
#
#
# END POINTS LIST:
#
#			* GET /customer/projects
#			* GET /customer/{customerId}/projects
#			* GET /customer/{customerId}/project/{projectId}
#			* POST /customer/{customerId}/project
#			* POST /customer/{customerId}/project/{projectId}
#
# COVERED TEST CASES:
#
#			* 1.) 	with just initial setup, no User should be able to perform any Operation
#
#			* 2.) 	addPermission(alex, garth, CanCode, Scripps) should return true; Alex(ROOT) can give Garth (in CodeBusters) any permission
#					hasPermission(garth, CanCode, Scripps) should return true
#					hasPermission(garth, CanCode, CHMC) should return false
#					hasPermission(eric, CanCode, Scripps) should return false
#
#			* 3.) 	addPermission(eric, garth, CanCode, <any>) should return false; Eric can't directly give someone permissions
#					grantAddPermission(eric, garth, CanCode, <any>, <any>) should return false; Eric can't delegate permissions either
#
#			* 4.)	grantAddPermission(alex, eric, CanCode, CodeBustersGroup, Scripps) should return true; Alex is granting Eric the ability to addPerm on CanCode
#					addPermission(eric, brooke, CanCode, Scripps) should return true
#					addPermission(eric, brooke, CanCode, CHMC) should return false (constraint failure)
#					grantAddPermission(eric, garth, CanCode, CodeBustersGroup, CHMC) should return false; Eric still has no rights to delegate permissions
#
#			* 5.)	removeAddPermission(alex, eric, CanCode) should return true; after this Eric should not be able to addPermission
#					addPermission(eric, kim, CanCode, CHMC) should return false (no permissions now)
#
# SETUP:
#          * Assumes Meta ACLs and HCC environments are available
#		   * Assumes that Python2.7 is available 
#
# USAGE:
#          * Ensure Grinder is configured to execute metaclsregressiontest.py
#          * Set the global variables, see below (Global Test Environment Selection)
#          * Run: python2.7 metaclsregressiontest.py staging eng@apixio.com ops@apixio.com
#          * Results can be accessed through Apixio Reports portal: https://reports.apixio.com/html/meta_acls_regression_reports_staging.html
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
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/aclrestfulapi/"
CSV_CONFIG_FILE_NAME = "metaclsregressiontest.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "Meta ACLs Regression Test"
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
requestdenied = 400
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
		ACL_DOMAIN="acladmin.apixio.com"
		ACL_URL="https://acladmin.apixio.com"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="root@api.apixio.com"
		ACLPASSWORD="thePassword"
	else:
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		ACL_URL="https://acladmin-stg.apixio.com"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="ishekhtman@apixio.com"
		ACLPASSWORD="apixio.123"
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS2=str(sys.argv[3])
		HTML_RECEIVERS="""To: Eng <%s>,Ops <%s>\n""" % (str(sys.argv[2]), str(sys.argv[3]))
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS2="ishekhtman@apixio.com"
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
	REPORT = ""
	REPORT = REPORT + "<h1>Meta ACLs Regression Test Report</h1>"
	REPORT = REPORT + "Run date & time: <b>%s</b><br>\n" % (CUR_TIME)
	REPORT = REPORT + "Report type: <b>%s</b><br>\n" % (REPORT_TYPE)
	REPORT = REPORT + "ACL user name: <b>%s</b><br>\n" % (ACLUSERNAME)
	REPORT = REPORT + "ACL app url: <b>%s</b><br>\n" % (ACL_URL)	
	REPORT = REPORT + "Enviromnent: <b><font color='red'>%s%s</font></b><br>" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + "<table align='left' width='800' cellpadding='1' cellspacing='1'><tr><td>"	
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
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/metaclsregression/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/metaclsregression/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="Meta ACLs Regression "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/metaclsregression/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="meta_acls_regression_reports_"+ENVIRONMENT.lower()+".txt"
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
		f = open(REPORTXTFILENAME)
		s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
		if s.find(REPORTXTSTRING) != -1:
			print "Report entry found, skipping append ...\n"
		else:
			print "Report entry not found, appending new entry ...\n"
			REPORTFILETXT = open(REPORTXTFILENAME, 'a')
			REPORTFILETXT.write(REPORTXTSTRING)
			REPORTFILETXT.close()
		os.chdir("/mnt/automation/python/aclrestfulapi")
		print ("Finished archiving report ... \n")

#=========================================================================================	

def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2
	
	print ("Emailing report ...\n")
	IMAGEFILENAME=str(CURDAY)+".png" 
	message = MIMEMultipart('related')
	message.attach(MIMEText((REPORT), 'html'))
	#with open(IMAGEFILENAME, 'rb') as image_file:
	#	image = MIMEImage(image_file.read())
	#image.add_header('Content-ID', '<picture@example.com>')
	#image.add_header('Content-Disposition', 'inline', filename=IMAGEFILENAME)
	#message.attach(image)

	message['From'] = 'Apixio QA <QA@apixio.com>'
	message['To'] = 'To: Eng <eng@apixio.com>,Ops <ops@apixio.com>'
	message['Subject'] = 'Meta ACLs %s Regression Test Report - %s\n\n' % (ENVIRONMENT, START_TIME)
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
	
			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def obtainExternalToken(un, pw):

	#print ("\n----------------------------------------------------------------------------")
	#print (">>> ACL - OBTAIN EXTERNAL TOKEN <<<")
	#print ("----------------------------------------------------------------------------")

	#8076
	#7076
	external_token = ""
	#ACLUSERNAME="lschneider@apixio.com"
	#ACLPASSWORD="ritiyi6!"
	url = ACL_URL+'/auths'
	#url = 'https://useraccount-stg.apixio.com:7076/auths'
	referer = ACL_URL  	
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
		print ("* STATUS CODE            = %s" % statuscode)
		print ("****************************************************************************")
			
	return (external_token)

#=========================================================================================
def obtainInternalToken(un, pw):
	global TOKEN
	
	print ("\n----------------------------------------------------------------------------")
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
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % un)
	print ("* PASSWORD               = %s" % pw)
	print ("* TOKENIZER URL          = %s" % url)
	print ("* EXTERNAL TOKEN         = %s" % external_token)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* STATUS CODE            = %s" % statuscode)
		
#=========================================================================================				
def addACLOperation(name, description):

	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - ADD ACL OPERATION <<<")
	print ("----------------------------------------------------------------------------")
	
	url = ACL_URL+'/aclop'
  	referer = ACL_URL 	
  	#print "Internal Token     = %s" % TOKEN
  	apixio_token='Apixio '+str(TOKEN)
  	#print "Apixio token       = %s" % apixio_token		
  	DATA = {'name': name, 'description': description}
	HEADERS = {'Authorization': apixio_token}
	#print url
	#print DATA
	#print HEADERS
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	if statuscode == requestdenied:
		print (">>> Operation %s already exists for user %s <<<" % (name, ACLUSERNAME))
	else:
		print ("* USERNAME               = %s" % ACLUSERNAME)
		print ("* PASSWORD               = %s" % ACLPASSWORD)
		print ("* URL                    = %s" % url)
		print ("* INTERNAL TOKEN         = %s" % TOKEN)
		print ("* OPERATION NAME         = %s" % name)
		print ("* OPERATION DESCRIPTION  = %s" % description)
	print ("* STATUS CODE            = %s" % statuscode)
	return (statuscode)	
#=========================================================================================
def getListOfUserGroups(param, grp_name):
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - GET LIST OF USER GROUPS "+param.upper()+"<<<")
	print ("----------------------------------------------------------------------------")

	group_list = ""
	#url = ACL_URL+'/groups?type=System:Role'
	url = ACL_URL+'/groups'+param
  	referer = ACL_URL 
  	apixio_token='Apixio '+str(TOKEN) 				
  	#DATA =    {'Referer': referer, 'Authorization': apixio_token} 
  	DATA = {'Authorization': apixio_token}
  	#HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': apixio_token}
  	HEADERS = {'Authorization': apixio_token}
  	#response = requests.get(url, data=DATA, headers=HEADERS) 
  	response = requests.get(url, data=DATA, headers=HEADERS)
	  	
  	userjson = response.json()
  	group_list = response.json()
  	#if userjson is not None:
  	#	group_list = userjson.get("grp_name")
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* STATUS CODE            = %s" % statuscode)
	for i in range (0, len(group_list)):
		print json.dumps(group_list[i])
	
	
	#print group_list[1]
	#print group_list[2]
	#print group_list[3]
	
	#grp_list = json.dumps(group_list[0])
	#print grp_list
	
	return json.dumps(group_list)
	
#=========================================================================================	
def getUserRole(userID):
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - GET STATUS AND ROLE OF THE USER <<<")
	print ("----------------------------------------------------------------------------")

	user_name = ""
	#url = ACL_URL+'/users/'+userID+'/firstName'
	url = ACL_URL+'/users/'+userID
  	referer = ACL_URL 
  	apixio_token='Apixio '+str(TOKEN) 				
  	DATA = {'Authorization': apixio_token}
  	HEADERS = {'Authorization': apixio_token}
  	response = requests.get(url, data=DATA, headers=HEADERS)
  	
  	userjson = response.json()
  	user_name = response.json()
  	#if userjson is not None:
  	#	group_member = userjson.get()
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* STATUS / ROLE          = %s" % json.dumps(user_name))
	print ("* STATUS CODE            = %s" % statuscode)
	
	return json.dumps(user_name)
#=========================================================================================
def getListOfGroupMembers(groupID):
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - GET LIST OF MEMBERS FROM A SPECIFIC GROUP <<<")
	print ("----------------------------------------------------------------------------")

	group_member_list = ""
	url = ACL_URL+'/groups/'+groupID+'/members'
  	referer = ACL_URL 
  	apixio_token='Apixio '+str(TOKEN) 				
  	DATA = {'Authorization': apixio_token}
  	HEADERS = {'Authorization': apixio_token}
  	response = requests.get(url, data=DATA, headers=HEADERS)
  	
  	userjson = response.json()
  	group_member_list = response.json()
  	#if userjson is not None:
  	#	group_member = userjson.get()
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* STATUS CODE            = %s" % statuscode)
	for i in range (0, len(group_member_list)):
		print json.dumps(group_member_list[i])
	
	
	return json.dumps(group_member_list)
#=========================================================================================

def getSetDeletePermissions(subject_uuid, op_name, customer, method):

	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - SUBJECT PERMISSIONS - "+method+" <<<")
	print ("----------------------------------------------------------------------------")

	perm_status = ""
	
	url = ACL_URL+'/perms/'+subject_uuid+'/'+op_name+'/'+customer
  	referer = ACL_URL 
  	apixio_token='Apixio '+str(TOKEN) 				
  	DATA = {'Authorization': apixio_token}
  	HEADERS = {'Authorization': apixio_token}
  	if method.upper() == "GET":
	  	response = requests.get(url, data=DATA, headers=HEADERS)
	elif method.upper() == "PUT":
		response = requests.put(url, data=DATA, headers=HEADERS)
	elif method.upper() == "DELETE":
		response = requests.delete(url, data=DATA, headers=HEADERS)
	  	
	statuscode = response.status_code	
	if statuscode == ok:
		print ("* USERNAME               = %s" % ACLUSERNAME)
		print ("* PASSWORD               = %s" % ACLPASSWORD)
		print ("* URL                    = %s" % url)
		print ("* INTERNAL TOKEN         = %s" % TOKEN)
		print ("* USER / GROUP UUID      = %s" % subject_uuid)
		print ("* OPERATION NAME         = %s" % op_name)
		print ("* CUSTOMER               = %s" % customer)
		print ("* METHOD                 = %s" % method)
		perm_status = "successfully %s" % method
	else:
		perm_status = "failed %s" % method
	print ("* STATUS CODE            = %s" % statuscode)


	return (statuscode)
	
	
#=========================================================================================

def addAndDeleteGrants(subject_uuid, op_name, method):

	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - SUBJECT GRANTS - "+method+" <<<")
	print ("----------------------------------------------------------------------------")

	grant_status = ""
	
	url = ACL_URL+'/grants/'+subject_uuid+'/'+op_name
  	referer = ACL_URL
  	apixio_token="Apixio "+str(TOKEN)
  	SUBJECT = {"type": "All"}
  	OBJECT = {"type": "All"}				
  	DATA = {"subject": SUBJECT, "object": OBJECT}
  	HEADERS = {"Content-Type": "application/json", "Authorization": apixio_token}
	# this is a requirement to convert single quotes to double quotes in order for dropwizard to work
  	DATA = json.dumps(DATA)
  	
	if method.upper() == "PUT":
		response = requests.put(url, data=DATA, headers=HEADERS)
	elif method.upper() == "DELETE":
		response = requests.delete(url, data=DATA, headers=HEADERS)
	  	
	statuscode = response.status_code	
	if statuscode == ok:
		grant_status = "successfully %s" % method
	else:
		grant_status = "failed %s" % method
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* USER / GROUP UUID      = %s" % subject_uuid)
	print ("* OPERATION NAME         = %s" % op_name)
	print ("* METHOD                 = %s" % method)	
	print ("* STATUS CODE            = %s" % statuscode)


	return (statuscode)

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
# Groups:
# "ROOT role" - "G_6b0f5c37-a6e3-49a3-b3cc-e0b77edc1cb0"
#
# "USER role" - "G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"
#
# Users:
# "ROOT role" 
#{"type": "U", "id": "U_05c5dfa1-710c-4010-8dcd-4301c0c667b3"}
#{"type": "U", "id": "U_2357bb19-07cf-4a68-a5b2-2dff1811e253"}
#{"type": "U", "id": "U_2862e12a-d000-41ac-87dd-a1824afc827a"}
#{"type": "U", "id": "U_46056d96-1253-4e49-8eef-f05399d428ac"}
#{"type": "U", "id": "U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"}
#{"type": "U", "id": "U_8eaf3a36-2438-4c77-87a9-4ba9bb7773da"}
#{"type": "U", "id": "U_9db1b15b-0789-4f43-80b7-9f6cc95cb9c7"}
#{"type": "U", "id": "U_a84c2790-94d8-4c97-bbf6-0b4bb7e00931"}
#{"type": "U", "id": "U_b3529884-0a91-4211-b9ae-4f3b62de1ede"}
#{"type": "U", "id": "U_dd132911-fa53-473e-bf1f-67b579e0e4f1"}
#{"type": "U", "id": "U_e77e3280-948b-4b16-b69c-010493a7f886"}
#
# "USER role"
#{"type": "U", "id": "U_fd92c9ef-a5cf-451f-b741-a816e044faf7"}
#{"type": "U", "id": "U_fde77955-bf6b-4763-aa43-bcd5f35ef058"}
#{"type": "U", "id": "U_fecfa42b-1a78-44fb-a2e7-6699891b763d"}
#{"type": "U", "id": "U_ff19f00f-5770-4225-ab7e-dee3325d9547"}
#{"type": "U", "id": "U_ff55cacc-45e7-4ed3-a1d8-63336c346a38"}
#{"type": "U", "id": "U_ff794257-548c-42cc-9cdd-9797b2f97575"}
#{"type": "U", "id": "U_ffb9d112-f6a3-4f2e-a9df-509313571c3e"}
#{"type": "U", "id": "U_ffba21dd-5661-4539-b8c0-b9ced8a0fbb1"}
#{"type": "U", "id": "U_ffd18f65-0dce-4086-a930-a70e1223e16b"}
#{"type": "U", "id": "U_fff77145-4bb0-43b4-9788-3e4d05b0c8eb"}
#
# addACLOperation("CanCode", "Can Code Things")

os.system('clear')

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

#writeReportHeader()

#Then the test code can do the same verification (via GET:/perms/{sub}/{op}/{obj}) 

PrintGlobalParamaterSettings()
#obtainInternalToken()

#========================================================================================================
#addACLOperation("CanCode100", "Can Code Things100")
#quit()
#========================================================================================================
#getListOfUserGroups("", "ROOT Users")
#getListOfUserGroups("?type=System:Role", "ROOT Users")
#getListOfGroupMembers("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45")
#getUserRole("U_e77e3280-948b-4b16-b69c-010493a7f886")
#========================================================================================================
#getSetDeletePermissions("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanAnnotate6", "IHC", "PUT")
############## to verify permissions #################
#getSetDeletePermissions("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanAnnotate6", "IHC", "GET")
######################################################
#getSetDeletePermissions("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanAnnotate6", "IHC", "DELETE")
#========================================================================================================
#addAndDeleteGrants("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanAnnotate6", "PUT")
#addAndDeleteGrants("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanAnnotate6", "DELETE")
#========================================================================================================
#=================================
#List of newly created HCC Users:
#=================================
#sanitytest001@apixio.net -        U_76ceeff8-9319-4f6f-a14b-b45152ac6417
#opprtroptusr0001@apixio.net -     U_e36b03f4-57d8-4ab6-b955-2e6f217113a6
#grinderUSR1416591626@apixio.net - U_f8d8d099-8512-44df-83af-216f0140e758 - Eric
#grinderUSR1416591631@apixio.net - U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c - Garth
#grinderUSR1416591636@apixio.net - U_ee7a0cf3-8111-4277-b5ff-d3793159697e - Brooke
#grinderUSR1416591640@apixio.net - U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6 - Kim
#grinderUSR1416591644@apixio.net - U_a5647e32-78f2-4e91-bd86-080e8dfc29fb
# pw: apixio.123
#=================================
#List of newly created HCC Orgs:
#=================================
#grinderORG1416591623
#=================================
#List of newly created HCC Groups:
#=================================
#grinderGRP1416591623
#=================================
#
# ROOT:
# Alex / Igor - "U_e77e3280-948b-4b16-b69c-010493a7f886" / "U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"
# USERS:
# Garth -  grinderUSR1416591631@apixio.net - "U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c"
# Eric -   grinderUSR1416591626@apixio.net - "U_f8d8d099-8512-44df-83af-216f0140e758"
# Brooke - grinderUSR1416591636@apixio.net - "U_ee7a0cf3-8111-4277-b5ff-d3793159697e"
# Kim -    grinderUSR1416591640@apixio.net - "U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6"
# GROUPS:
# grinderGRP1416591623 - "G_766e9de6-a9a4-40b0-a82d-8414be97953f"
# CodeBusters          - "G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"

#========================================================================================================

def testCase2():
# TEST CASE 2:
#	addPermission(alex, garth, CanCode, Scripps) should return true; Alex(ROOT) can give Garth (in CodeBusters) any permission
#	hasPermission(garth, CanCode, Scripps) should return true
#	hasPermission(garth, CanCode, CHMC) should return false
#	hasPermission(eric, CanCode, Scripps) should return false

	# Login as a ROOT user
	obtainInternalToken("ishekhtman@apixio.com", "apixio.123")
	
	if (addACLOperation("CanCode101", "Can Code Things101") == ok) or (addACLOperation("CanCode101", "Can Code Things101") == requestdenied):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")	
		raw_input("Press Enter to continue...")		
	
	if (getSetDeletePermissions("U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c", "CanCode101", "Scripps", "PUT") == ok):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")			
	
	if (getSetDeletePermissions("U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c", "CanCode101", "Scripps", "GET") == ok):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")		
		
	if (getSetDeletePermissions("U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c", "CanCode101", "CHMC", "GET") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")		

	if (getSetDeletePermissions("U_f8d8d099-8512-44df-83af-216f0140e758", "CanCode101", "Scripps", "GET") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	


#========================================================================================================

# TEST CASE 3:
#	addPermission(eric, garth, CanCode, <any>) should return false; Eric can't directly give someone permissions
#	grantAddPermission(eric, garth, CanCode, <any>, <any>) should return false; Eric can't delegate permissions either
def testCase3():
	print "Test Case #3"
	
	# Login as a NON-ROOT user
	obtainInternalToken("grinderUSR1416591626@apixio.net", "apixio.123")
	if (addACLOperation("CanCode100", "Can Code Things100") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")		
	if (getSetDeletePermissions("U_e77e3280-948b-4b16-b69c-010493a7f886", "CanCode100", "Scripps", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")	
		raw_input("Press Enter to continue...")	
	if (getSetDeletePermissions("U_ffb9d112-f6a3-4f2e-a9df-509313571c3e", "CanCode100", "Scripps", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")		
	if (getSetDeletePermissions("U_ffb9d112-f6a3-4f2e-a9df-509313571c3e", "CanCode100", "Scripps", "GET") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")		

	if (getSetDeletePermissions("U_ffb9d112-f6a3-4f2e-a9df-509313571c3e", "CanCode100", "CHMC", "GET") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (getSetDeletePermissions("U_ffba21dd-5661-4539-b8c0-b9ced8a0fbb1", "CanCode100", "Scripps", "GET") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (getSetDeletePermissions("U_ffba21dd-5661-4539-b8c0-b9ced8a0fbb1", "CanCode100", "Scripps", "GET") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (getSetDeletePermissions("U_ffba21dd-5661-4539-b8c0-b9ced8a0fbb1", "CanCode100", "Scripps", "DELETE") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (addAndDeleteGrants("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanCode100", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (addAndDeleteGrants("G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45", "CanCode100", "DELETE") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (addAndDeleteGrants("U_ffb9d112-f6a3-4f2e-a9df-509313571c3e", "CanCode100", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	if (addAndDeleteGrants("U_ffb9d112-f6a3-4f2e-a9df-509313571c3e", "CanCode100", "DELETE") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	


#========================================================================================================

# TEST CASE 4:
#	grantAddPermission(alex, eric, CanCode, CodeBustersGroup, Scripps) should return true; Alex is granting Eric the ability to addPerm on CanCode
#	addPermission(eric, brooke, CanCode, Scripps) should return true
#	addPermission(eric, brooke, CanCode, CHMC) should return false (constraint failure)
#	grantAddPermission(eric, garth, CanCode, CodeBustersGroup, CHMC) should return false; Eric still has no rights to delegate permissions
#
# ROOT:
# Alex / Igor - "U_e77e3280-948b-4b16-b69c-010493a7f886" / "U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"
# USERS:
# Garth -  grinderUSR1416591631@apixio.net - "U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c"
# Eric -   grinderUSR1416591626@apixio.net - "U_f8d8d099-8512-44df-83af-216f0140e758"
# Brooke - grinderUSR1416591636@apixio.net - "U_ee7a0cf3-8111-4277-b5ff-d3793159697e"
# Kim -    grinderUSR1416591640@apixio.net - "U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6"
# GROUPS:
# grinderGRP1416591623 - "G_766e9de6-a9a4-40b0-a82d-8414be97953f"
# CodeBusters          - "G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"
def testCase4():
	print "Test Case #4"
	# Login as ROOT and give permissions to Eric and CodeBusters 
	obtainInternalToken("ishekhtman@apixio.com", "apixio.123")
	
	if (addAndDeleteGrants("U_f8d8d099-8512-44df-83af-216f0140e758", "CanCode101", "PUT") == ok):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
	
	if (addAndDeleteGrants("G_766e9de6-a9a4-40b0-a82d-8414be97953f", "CanCode101", "PUT") == ok):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")
	
	# LogIn as Eric	
	obtainInternalToken("grinderUSR1416591626@apixio.net", "apixio.123")			
	if (getSetDeletePermissions("U_ee7a0cf3-8111-4277-b5ff-d3793159697e", "CanCode101", "Scripps", "PUT") == ok):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")	
		raw_input("Press Enter to continue...")
	
	if (getSetDeletePermissions("U_ee7a0cf3-8111-4277-b5ff-d3793159697e", "CanCode101", "CHMC", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")		
	
	if (addAndDeleteGrants("U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c", "CanCode101", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	

#========================================================================================================

# TEST CASE 5:
#
#	removeAddPermission(alex, eric, CanCode) should return true; after this Eric should not be able to addPermission
#	addPermission(eric, kim, CanCode, CHMC) should return false (no permissions now)
#
# ROOT:
# Alex / Igor - "U_e77e3280-948b-4b16-b69c-010493a7f886" / "U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"
# USERS:
# Garth -  grinderUSR1416591631@apixio.net - "U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c"
# Eric -   grinderUSR1416591626@apixio.net - "U_f8d8d099-8512-44df-83af-216f0140e758"
# Brooke - grinderUSR1416591636@apixio.net - "U_ee7a0cf3-8111-4277-b5ff-d3793159697e"
# Kim -    grinderUSR1416591640@apixio.net - "U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6"
# GROUPS:
# grinderGRP1416591623 - "G_766e9de6-a9a4-40b0-a82d-8414be97953f"
# CodeBusters          - "G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"
#
def testCase5():
	print "Test Case #5"
	# Login as ROOT and give permissions to Eric and CodeBusters 
	obtainInternalToken("ishekhtman@apixio.com", "apixio.123")
	
	if (getSetDeletePermissions("U_f8d8d099-8512-44df-83af-216f0140e758", "CanCode101", "Scripps", "DELETE") == ok):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")	
		
	# Login as Eric - non Root user 
	obtainInternalToken("grinderUSR1416591626@apixio.net", "apixio.123")
	if (getSetDeletePermissions("U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6", "CanCode101", "CHMC", "PUT") == forbidden):
		print (">>>>>>>>>>>>> PASSED QA <<<<<<<<<<<<<<")
	else:
		print (">>>>>>>>>>>>> FAILED QA <<<<<<<<<<<<<<")
		raw_input("Press Enter to continue...")			
	
	
	
	
	

#========================================================================================================

testCase2()
testCase3()
testCase4()
testCase5()

quit()

#logInToHCC()
#writeReportDetails("log into hcc")
	
#ListUserGroupOrg()

#writeReportFooter()

#archiveReport()

#emailReport()	
	
print ("==== End of Meta ACLs Regression Test =====")
print ("===========================================")
#=========================================================================================