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
#			* Log into Meta ACL
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
# NOTES / COMMENTS:
#			* Based on the 5 specific test cases I outlined in an email last week and that were copied to the JIRA QA ticket, I think it makes 
#				sense to provide the following new RESTful APIs to be added to user-account service:
#
#			* GET /perms/{subject}/{operation}/{object}
#
#			  This API would perform a "has permission" test on the Subject/Operation/Object and return either 200 (has permission) or 403 (doesn't have permission)
#
#* PUT /perms/{subject}/{operation}/{object}
#
#  This API would attempt to add the given permission.  If the user linked with the token presented in the Authorization: HTTP header has the ability to add that permission, the 200 status code will be returned, otherwise a 403 will be returned.  There is no HTTP body.
#
#* DELETE /perms/{subject}/{operation}/{object}
#
#  This API will undo the effects of the PUT call, if the authenticated user has permission.
#
#* PUT /grants/{subject}/{operation}
#
#  This APi will attempt to grant the given subject the rights to add permission on the given operation.  The constraints on the subject and object of that "add permission" operation will be given by a string-ized JSON object that is the HTTP body.
#
#* DELETE /grants/{subject}/{operation}
#
#  This API will attempt to undo the effect of the PUT form of this URL.  No HTTP body is required.
#
#* GET /groups
#
#  This API will return a list of all UserGroups.  An optional query parameter of "type=role" will restrict the returned groups to those that are role-based UserGroups.  Only ROOT can request this list of groups.
#
#* GET /groups/{group}/members
#
#  This API will return the members of the given UserGroup.
#
#I believe those 7 APIs will support testing of the core of the MetaACLs functionality.  What that list doesn't support are query functions to answer questions such as, Who has Rights on this Object, etc.
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
def obtainExternalToken():

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
	
	DATA =    {'Referer': referer, 'email': ACLUSERNAME, 'password': ACLPASSWORD} 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
	
	response = requests.post(url, data=DATA, headers=HEADERS) 

	statuscode = response.status_code

	userjson = response.json()
	if userjson is not None:
		external_token = userjson.get("token") 
		print ("* ACL USERNAME           = %s" % ACLUSERNAME)
		print ("* ACL PASSWORD           = %s" % ACLPASSWORD)
		print ("* URL                    = %s" % url)
		print ("* EXTERNAL TOKEN         = %s" % external_token)
		print ("* STATUS CODE            = %s" % statuscode)
		print ("****************************************************************************")
			
	return (external_token)

#=========================================================================================
def obtainInternalToken():
	global TOKEN
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - OBTAIN EXTERNAL AND EXCHANGE FOR INTERNAL TOKEN <<<")
	print ("----------------------------------------------------------------------------")
	
	
	TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
	external_token = obtainExternalToken()
	url = TOKEN_URL
  	referer = TOKEN_URL  				
  	DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + external_token} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + external_token}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
  	userjson = response.json()
  	if userjson is not None:
  		TOKEN = userjson.get("token")
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
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

#writeReportHeader()

PrintGlobalParamaterSettings()

obtainInternalToken()

addACLOperation("CanAnnotate3", "Can Annotate Things3")



quit()















#writeReportDetails("log into acl")

# Org related testing
#ACLCreateNewCodingOrg()
#writeReportDetails("create new coding organization")

# Group related testing
#ACLCreateNewGroup()
#ACLDeleteExistingGroup(GRP_UUID)
#ACLCreateNewGroup()
#writeReportDetails("create and delete new group")
		

#ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
#ACLDelGroupPermission(permission, GRP_UUID, ORG_UUID)
#ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
#writeReportDetails("add and delete group permissions")	
			
# User related testing			
#ACLCreateNewUser(0)
#HCCUSERSLIST.append(i)
#HCCUSERSLIST[i] = HCCUSERNAME
#ACLActivateNewUser()
#ACLDectivateUser(USR_UUID)
#ACLActivateNewUser()
#ACLSetPassword()
#ACLAssignCodingOrg()
#ACLAddMemberToGroup()
#ACLDelMemberFromGroup(GRP_UUID, USR_UUID)
#ACLAddMemberToGroup()
#logInToHCC()	
#writeReportDetails("user/password/group/org creation/deletion/assignment")

#logInToHCC()
#writeReportDetails("log into hcc")
	
#ListUserGroupOrg()

#writeReportFooter()

#archiveReport()

#emailReport()	
	
print ("==== End of Meta ACLs Regression Test =====")
print ("===========================================")
#=========================================================================================