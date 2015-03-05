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
SUBHDR="<br><table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp; %s</b></font></td></tr></table>"

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
	REPORT = REPORT + "ACL Root user name: <b>%s</b><br>\n" % (ACLUSERNAME)
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
			print ("Report entry found, skipping append ...\n")
		else:
			print ("Report entry not found, appending new entry ...\n")
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
	print ("Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2))	

#=========================================================================================
def logTestCaseStatus(exp_statuscode, statuscode, step, function, p1, p2, p3, p4, p5, p6, p7, p8):
	global REPORT
	print ("* TEST STEP NUMBER       = %s" % step)
	
	REPORT = REPORT + "<tr><td colspan='4' bgcolor='#D0D0D0'><font size='4'> %d - <b><i>%s</i></b></font></td></tr>" % (step, function)
	report_local = ""
	for i in range (1,8):
		exec('if p'+str(i)+ ' > "": report_local  = report_local  + "<tr><td>"+p'+str(i)+'+"</td></tr>"')
	REPORT = REPORT + report_local
		
	if statuscode in exp_statuscode:
		print ("* TEST STATUS            = PASSED QA")
		print ("----------------------------------------------------------------------------")
		REPORT = REPORT + "<tr><td bgcolor='green'><font color='#FFFFFF'>End step: %s</td><td bgcolor='green'><font color='#FFFFFF'>%s</td> \
			<td bgcolor='green'><font color='#FFFFFF'>%s</td><td bgcolor='green'><font color='#FFFFFF'>PASSED QA</td></tr>"% (step, exp_statuscode, statuscode)
		#REPORT = REPORT + "<tr><td colspan='4'><hr></td></tr>"
	else:
		print ("* TEST STATUS            = FAILED QA")
		print ("----------------------------------------------------------------------------")
		REPORT = REPORT + "<tr><td bgcolor='red'><font color='#FFFFFF'>End step: %s</td><td bgcolor='red'><font color='#FFFFFF'>%s</td> \
			<td bgcolor='red'><font color='#FFFFFF'>%s</td><td bgcolor='red'><font color='#FFFFFF'>FAILED QA</td></tr>"% (step, exp_statuscode, statuscode)
		#REPORT = REPORT + "<tr><td colspan='4'><hr></td></tr>"
		if int(PAUSE_FOR_FAILURES) == 1:
			raw_input("Press Enter to continue...")	
	#print ("\n")				
			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def obtainExternalToken(un, pw, exp_statuscode, step):

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
		print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
		print ("* RECEIVED STATUS CODE   = %s" % statuscode)
		print ("****************************************************************************")
			
	return (external_token)

#=========================================================================================
def obtainInternalToken(un, pw, exp_statuscode, step):
	global TOKEN
	
	print ("----------------------------------------------------------------------------")
	print (">>> ACL - OBTAIN EXTERNAL AND EXCHANGE FOR INTERNAL TOKEN <<<")
	print ("----------------------------------------------------------------------------")
	
	
	TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
	external_token = obtainExternalToken(un, pw, exp_statuscode, step)
	url = TOKEN_URL
  	referer = TOKEN_URL  				
  	DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + external_token} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + external_token}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
  	userjson = response.json()
  	if userjson is not None:
  		TOKEN = userjson.get("token")
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
	logTestCaseStatus(exp_statuscode, statuscode, step, "obtainInternalToken", un, pw, external_token, TOKEN, "", "", "", "")

#=========================================================================================				
def addACLOperation(name, description, exp_statuscode, step):

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

	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* OPERATION NAME         = %s" % name)
	print ("* OPERATION DESCRIPTION  = %s" % description)
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	logTestCaseStatus(exp_statuscode, statuscode, step, "addACLOperation", TOKEN, name, description, "", "", "", "", "")
	return (statuscode)	
#=========================================================================================
def getListOfUserGroups(param, grp_name, exp_statuscode, step):
	
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
  	
	if response == ok:   	
  		userjson = response.json()
  		group_list = response.json()
  		for i in range (0, len(group_list)):
			print (json.dumps(group_list[i]))
  	else:
  		group_list = "Not Available"	
  	#if userjson is not None:
  	#	group_list = userjson.get("grp_name")
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* TYPE                   = %s" % param)
	print ("* NAME                   = %s" % grp_name)
	print ("* GROUP LIST             = %s" % group_list)
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	logTestCaseStatus(exp_statuscode, statuscode, step, "getListOfUserGroups", TOKEN, param, grp_name, "", "", "", "", "")

	#print group_list[1]
	#print group_list[2]
	#print group_list[3]
	
	#grp_list = json.dumps(group_list[0])
	#print grp_list
	
	return json.dumps(group_list)
	
#=========================================================================================	
def getUserRole(userID, exp_statuscode, step):
	
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
  	
  	if response == ok:
  		userjson = response.json()
  		user_name = response.json()
  		status_role = json.dumps(user_name)
  	else:
  		status_role = "Not Available"	
  	#if userjson is not None:
  	#	group_member = userjson.get()
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* STATUS / ROLE          = %s" % status_role)
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	logTestCaseStatus(exp_statuscode, statuscode, step, "getUserRole", TOKEN, json.dumps(user_name), "", "", "", "", "", "")
	
	return status_role
#=========================================================================================
def getListOfGroupMembers(groupID, exp_statuscode, step):
	
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
  	
  	if response == ok:
  		userjson = response.json()
  		group_member_list = response.json()
  		for i in range (0, len(group_member_list)):
			print (json.dumps(group_member_list[i]))
	else:
		group_member_list = "Not Available"			
  		
  	#if userjson is not None:
  	#	group_member = userjson.get()
	statuscode = response.status_code	
	print ("* USERNAME               = %s" % ACLUSERNAME)
	print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* GROUP MEMBER LIST      = %s" % group_member_list)
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	logTestCaseStatus(exp_statuscode, statuscode, step, "getListOfGroupMembers", TOKEN, group_member_list, "", "", "", "", "", "")	
	
	return json.dumps(group_member_list)
#=========================================================================================

def getSetDeletePermissions(subject_uuid, op_name, customer, method, exp_statuscode, step):

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
		perm_status = "successfully %s" % method
	else:
		perm_status = "failed %s" % method
	#print ("* USERNAME               = %s" % ACLUSERNAME)
	#print ("* PASSWORD               = %s" % ACLPASSWORD)
	print ("* URL                    = %s" % url)
	print ("* INTERNAL TOKEN         = %s" % TOKEN)
	print ("* USER / GROUP UUID      = %s" % subject_uuid)
	print ("* OPERATION NAME         = %s" % op_name)
	print ("* CUSTOMER               = %s" % customer)
	print ("* METHOD                 = %s" % method)
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	logTestCaseStatus(exp_statuscode, statuscode, step, "getSetDeletePermissions", TOKEN, subject_uuid, op_name, customer, method, "", "", "")

	return (statuscode)
#=========================================================================================

def addAndDeleteGrants(subject_uuid, op_name, method, type_sub, type_value_sub, type_ob, type_value_ob, exp_statuscode, step):

	print ("\n----------------------------------------------------------------------------")
	print (">>> ACL - SUBJECT GRANTS - "+method+" <<<")
	print ("----------------------------------------------------------------------------")
	grant_status = ""
	SUBJECT = {"type": "All"}
  	OBJECT = {"type": "All"}	
	url = ACL_URL+'/grants/'+subject_uuid+'/'+op_name
  	referer = ACL_URL
  	apixio_token="Apixio "+str(TOKEN)
  	if type_sub == "All":
  		SUBJECT = {"type": "All"}
  	elif type_sub == "UserGroup":
  		SUBJECT = {"type": "UserGroup", "groupID": type_value_sub}
  	elif type_sub == "Set":
  		SUBJECT = {"type": "Set", "members": type_value_sub}	
  	if type_ob == "All":	
  		OBJECT = {"type": "All"}
  	elif type_ob == "UserGroup":
  		OBJECT = {"type": "UserGroup", "groupID": type_value_ob}
  	elif type_ob == "Set":
  		OBJECT = {"type": "Set", "members": type_value_ob}	
  	DATA = {"subject": SUBJECT, "object": OBJECT}
  	HEADERS = {"Content-Type": "application/json", "Authorization": apixio_token}
	# this is a requirement to convert single quotes to double quotes in order for dropwizard to work
  	DATA = json.dumps(DATA)
  	SUBJECT = json.dumps(SUBJECT)
  	OBJECT = json.dumps(OBJECT)  
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
	print ("* TYPE SUBJECT           = %s" % type_sub)
	print ("* TYPE SUBJECT VALUE     = %s" % type_value_sub)
	print ("* TYPE OBJECT            = %s" % type_ob)
	print ("* TYPE OBJECT VALUE	     = %s" % type_value_ob)
	print ("* EXPECTED STATUS CODE   = %s" % exp_statuscode)
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	logTestCaseStatus(exp_statuscode, statuscode, step, "addAndDeleteGrants", TOKEN, subject_uuid, op_name, method, type_sub, type_value_sub, type_ob, type_value_ob)

	return (statuscode)

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

writeReportHeader()


printGlobalParamaterSettings()
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
def testCase1():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #1")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("\n----------------------------------------------------------------------------")
	print ("Test Case #1")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")
	
# TEST CASE 1: 	
#	with just initial setup, no User should be able to perform any Operation	
	acl_operation = ACL_OPERATION+str(time.time())
	# Login as Eric (NON-ROOT user)
	obtainInternalToken(ERIC_EMAIL, "apixio.123", {ok, created}, 1)
	addACLOperation(acl_operation, "Can Code Things",  {forbidden}, 2)
	getListOfUserGroups("type=System:Role", "ROOT Users", {forbidden}, 3)
	getUserRole(GARTH_UUID, {forbidden}, 4)
	getListOfGroupMembers(CODEBUSTERS_UUID, {forbidden}, 5)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "Scripps", "PUT", {forbidden}, 6)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "Scripps", "GET", {forbidden}, 7)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "Scripps", "DELETE", {forbidden}, 8)


#========================================================================================================

def testCase2():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #2")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("\n----------------------------------------------------------------------------")
	print ("Test Case #2")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")	
# TEST CASE 2:
#	addPermission(alex, garth, CanCode, Scripps) should return true; Alex(ROOT) can give Garth (in CodeBusters) any permission
#	hasPermission(garth, CanCode, Scripps) should return true
#	hasPermission(garth, CanCode, CHMC) should return false
#	hasPermission(eric, CanCode, Scripps) should return false

	# Login as a ROOT user
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 1)
	acl_operation = ACL_OPERATION+str(time.time())
	addACLOperation(acl_operation, "Can Code Things",  {ok}, 2)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "Scripps", "PUT", {ok}, 3)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "Scripps", "GET", {ok}, 4)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "CHMC", "GET", {forbidden}, 5)	
	getSetDeletePermissions(ERIC_UUID, acl_operation, "Scripps", "GET", {forbidden}, 6)
	addAndDeleteGrants(GARTH_UUID, acl_operation, "PUT", "All", "", "All", "", {forbidden}, 7)
	addAndDeleteGrants(GARTH_UUID, acl_operation, "DELETE", "All", "", "All", "", {forbidden}, 8)	
	
	REPORT = REPORT+"</table>"	

#========================================================================================================

# TEST CASE 3:
#	addPermission(eric, garth, CanCode, <any>) should return false; Eric can't directly give someone permissions
#	grantAddPermission(eric, garth, CanCode, <any>, <any>) should return false; Eric can't delegate permissions either
#
# ALEX_EMAIL="ishekhtman@apixio.com"
# IGOR_EMAIL="ishekhtman@apixio.com"
# ERIC_EMAIL="grinderUSR1416591626@apixio.net"
# BROOKE_EMAIL="grinderUSR1416591636@apixio.net"
# GARTH_EMAIL="grinderUSR1416591631@apixio.net"
# KIM_EMAIL="grinderUSR1416591640@apixio.net"
#
# IGOR_UUID="U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"
# GARTH_UUID="U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c"
# ERIC_UUID="U_f8d8d099-8512-44df-83af-216f0140e758"
# BROOKE_UUID="U_ee7a0cf3-8111-4277-b5ff-d3793159697e"
# KIM_UUID="U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6"
#
# CODEBUSTERS_UUID="G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"
# SCRIPPS_UUID="X_7040367c-d8fd-411c-b87a-4382bbda4027"
# CHMC_UUID="X_1879b8a5-2e6e-4595-9846-eb10048bf5d8"

def testCase3():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #3")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("Test Case #3")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")	
	
	# Login as a NON-ROOT user
	obtainInternalToken(ERIC_EMAIL, "apixio.123", {ok, created}, 1)
	acl_operation = ACL_OPERATION+str(time.time())
	addACLOperation(acl_operation, "Can Code Things",  {forbidden}, 2)
	getSetDeletePermissions(GARTH_UUID, acl_operation, "Scripps", "PUT", {forbidden}, 3)
	getSetDeletePermissions(IGOR_UUID, acl_operation, "Scripps", "PUT", {forbidden}, 4)
	getSetDeletePermissions(BROOKE_UUID, acl_operation, "Scripps", "PUT", {forbidden}, 5)
	addAndDeleteGrants(GARTH_UUID, acl_operation, "PUT", "All", "", "All", "", {forbidden}, 6)
	addAndDeleteGrants(GARTH_UUID, acl_operation, "DELETE", "All", "", "All", "", {forbidden}, 7)
	REPORT = REPORT+"</table>"		

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
# Garth -  GARTH_EMAIL - GARTH_UUID
# Eric -   grinderUSR1416591626@apixio.net - ERIC_UUID
# Brooke - grinderUSR1416591636@apixio.net - BROOKE_UUID
# Kim -    grinderUSR1416591640@apixio.net - KIM_UUID
# GROUPS:
# grinderGRP1416591623 - "G_766e9de6-a9a4-40b0-a82d-8414be97953f"
# CodeBusters          - CODEBUSTER_UUID

# me: I need to modify OBJECT
# Scott:  yes
# me:  to "Scripps" instead of "All"
# Scott:  it needs to say {"type":"Set", "members",["X_forscripps"]} I believe
# me:  ok, let me try that
# Scott:  (change X_forscripts to be what is passed in on line 1103)

def testCase4():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #4")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("Test Case #4")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")	
		
	# Login as ROOT and give permissions to Eric and CodeBusters 
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 1)	
	acl_operation = ACL_OPERATION+str(time.time())
	addACLOperation(acl_operation, "Can Code Things",  {ok}, 2)
	addAndDeleteGrants(ERIC_UUID, acl_operation, "PUT", "All", "", "Set", [SCRIPPS_UUID], {ok}, 3)
	addAndDeleteGrants(CODEBUSTERS_UUID, acl_operation, "PUT", "All", "", "Set", [SCRIPPS_UUID], {ok}, 4)

	# LogIn as Eric	
	obtainInternalToken(ERIC_EMAIL, "apixio.123", {ok, created}, 5)
	getSetDeletePermissions(BROOKE_UUID, acl_operation, SCRIPPS_UUID, "PUT", {ok}, 6)
	getSetDeletePermissions(BROOKE_UUID, acl_operation, CHMC_UUID, "PUT", {forbidden}, 7)
	addAndDeleteGrants(GARTH_UUID, acl_operation, "PUT", "Set", [CHMC_UUID], "Set", [CHMC_UUID], {forbidden}, 8)
	REPORT = REPORT+"</table>"		

#========================================================================================================
# TEST CASE 5:
#	removeAddPermission(alex, eric, CanCode) should return true; after this Eric should not be able to addPermission
#	addPermission(eric, kim, CanCode, CHMC) should return false (no permissions now)

def testCase5():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #5")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("Test Case #5")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")		
	# Login as ROOT and give permissions to Eric and CodeBusters 
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 1)
	acl_operation = ACL_OPERATION+str(time.time())
	addACLOperation(acl_operation, "Can Code Things",  {ok}, 2)
	getSetDeletePermissions(ERIC_UUID, acl_operation, "Scripps", "DELETE", {ok}, 3)
	
	# Login as Eric - non Root user 
	obtainInternalToken(ERIC_EMAIL, "apixio.123", {ok, created}, 4)
	getSetDeletePermissions(KIM_UUID, acl_operation, "CHMC", "PUT", {forbidden}, 5)
	REPORT = REPORT+"</table>"		
#========================================================================================================
# TEST CASE 6:
#	1. addGrants(Igor, Kim, CanCode103, CHMC) should return true; after this Kim should not be able to addPermission
#	2. addPermission(Kim, Eric, CanCode103, CHMC) should return true
#	3. deletePermission(Kim, Eric, CanCode103, CHMC) should return true
#	4. viewPermission(Kim, Eric, CanCode103, CHMC) should return true
#	5. addPermission(Kim, Eric, CanCode103, CHMC) should return true
#   6. DeleteGrants(Igor, Kim, CanCode103, CHMC) should return true; after this Kim should not be able to addPermission
#	7. viewPermission(Kim, Eric, CanCode103, CHMC) should return false (since grants have been removed)
#	8. addPermission(Kim, Eric, CanCode103, CHMC) should return false (since grants have been removed)
#	9. deletePermission(Kim, Eric, CanCode103, CHMC) should return false (since grants have been removed)

def testCase6():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #6")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("Test Case #6")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")		
	
	# Login as ROOT (Igor)
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 1)
	acl_operation = ACL_OPERATION+str(time.time())
	addACLOperation(acl_operation, "Can Code Things",  {ok}, 2)
	addAndDeleteGrants(KIM_UUID, acl_operation, "PUT", "All", "", "Set", [CHMC_UUID], {ok}, 3)
	
	# Login as Kim - non Root user 
	obtainInternalToken(KIM_EMAIL, "apixio.123", {ok, created}, 4)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "PUT", {ok}, 5)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "DELETE", {ok}, 6)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "GET", {forbidden}, 7)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "PUT", {ok}, 8)
	
	# Login as ROOT (Igor)
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 9)	
	addAndDeleteGrants(KIM_UUID, acl_operation, "DELETE", "All", "", "Set", [CHMC_UUID], {ok}, 10)
	
	# Login as Kim - non Root user 
	obtainInternalToken(KIM_EMAIL, "apixio.123", {ok, created}, 11)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "GET", {ok}, 11)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "PUT", {forbidden}, 12)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "DELETE", {forbidden}, 13)
	REPORT = REPORT+"</table>"		
									
#========================================================================================================
# TEST CASE 7:

def testCase7():
	global REPORT
	REPORT = REPORT+(SUBHDR % "Test Case #7")
	REPORT = REPORT+"<table border='0' width='100%'>"
	print ("Test Case #7")
	if int(WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES) == 1:	
		raw_input("Press Enter to continue...")		
	
	# Login as Igor (Root)
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 1)	
	acl_operation = ACL_OPERATION+str(time.time())
	addACLOperation(acl_operation, "Can Code Things",  {ok}, 2)
	addAndDeleteGrants(BROOKE_UUID, acl_operation, "PUT", "All", "", "Set", [SCRIPPS_UUID, CHMC_UUID], {ok}, 3)
		
	# Log in as Brooke (Non-root)
	obtainInternalToken(BROOKE_EMAIL, "apixio.123", {ok, created}, 4)	
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "PUT", {ok}, 5)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "PUT", {ok}, 6)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "GET", {ok}, 7)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "DELETE", {ok}, 8)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "DELETE", {ok}, 9)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "GET", {forbidden}, 10)
	
	# Log in as Igor (Root)
	obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 11)	
	addAndDeleteGrants(BROOKE_UUID, acl_operation, "DELETE", "All", "", "Set", [SCRIPPS_UUID, CHMC_UUID], {ok}, 12)
		
	# Log in as Brooke (Non-root)
	obtainInternalToken(BROOKE_EMAIL, "apixio.123", {ok, created}, 13)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "PUT", {forbidden}, 14)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "PUT", {forbidden}, 15)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "GET", {forbidden}, 16)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "DELETE", {forbidden}, 17)
	getSetDeletePermissions(ERIC_UUID, acl_operation, CHMC_UUID, "DELETE", {forbidden}, 18)
	getSetDeletePermissions(ERIC_UUID, acl_operation, SCRIPPS_UUID, "GET", {forbidden}, 19)
	REPORT = REPORT+"</table>"		
									
#========================================================================================================
#ALEX_EMAIL="ishekhtman@apixio.com"
#IGOR_EMAIL="ishekhtman@apixio.com"
#IGOR_UUID="U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"
#GARTH_EMAIL="grinderUSR1416591631@apixio.net"
#GARTH_UUID="U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c"
#ERIC_EMAIL="grinderUSR1416591626@apixio.net"
#ERIC_UUID="U_f8d8d099-8512-44df-83af-216f0140e758"
#BROOKE_EMAIL="grinderUSR1416591636@apixio.net"
#BROOKE_UUID="U_ee7a0cf3-8111-4277-b5ff-d3793159697e"
#KIM_EMAIL="grinderUSR1416591640@apixio.net"
#KIM_UUID="U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6"
#CODEBUSTERS_UUID="G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"
#SCRIPPS_UUID="X_7040367c-d8fd-411c-b87a-4382bbda4027"
#CHMC_UUID="X_1879b8a5-2e6e-4595-9846-eb10048bf5d8"

#ACL_OPERATION="CanCode"
#ACL_CAN_CODE_CTR=240


testCase1()
testCase2()
testCase3()
testCase4()
testCase5()
testCase6()
testCase7()
#testCase8()
#testCase9()
#testCase10()

#logInToHCC()
#writeReportDetails("log into hcc")
	
#ListUserGroupOrg()

writeReportFooter()

archiveReport()

emailReport()	

print ("\n============================================================================")	
print ("===================== End of Meta ACLs Regression Test =====================")
print ("============================================================================")
#=========================================================================================
