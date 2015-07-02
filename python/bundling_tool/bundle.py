#=========================================================================================
#====================================== bundle.py ========================================
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
	print ("* ACL URL                = %s"%UA_URL)
	print ("* HCC URL                = %s"%HCC_URL)
	print ("* ACL Admin User Name    = %s"%ACLUSERNAME)
	print ("* Project ID             = %s"%PROJECTID)
	print ("* Batch ID               = %s"%BATCHID)

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
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - project ID
	# Arg3 - batch ID
	
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS, PROJECTID, BATCHID, BUNDL_URL
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
		UA_URL="https://acladmin.apixio.com"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="root@api.apixio.com"
		ACLPASSWORD="thePassword"
		BUNDL_URL="http://cmp.apixio.com:8087"
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
		BUNDL_URL="http://cmp-stg.apixio.com:8087"
	
	if (len(sys.argv) > 2):
		PROJECTID=str(sys.argv[2])
	else:
		print "Missing project ID, aborting now ..."
		print "Proper use instructions:"
		print "python2.7 bundle.py <environment> <projectID (required)> <batchID (optional)>"
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
	
def writeReportHeader ():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	
	print ("Begin writing report header ...\n")
	# REPORT = MIMEMultipart()
	REPORT = ""
	REPORT = REPORT + "<h1>User Accounts Regression Test Report</h1>"
	REPORT = REPORT + "Run date & time: <b>%s</b><br>\n" % (CUR_TIME)
	REPORT = REPORT + "Report type: <b>%s</b><br>\n" % (REPORT_TYPE)
	REPORT = REPORT + "UA Root user name: <b>%s</b><br>\n" % (ACLUSERNAME)
	REPORT = REPORT + "UA app url: <b>%s</b><br>\n" % (UA_URL)	
	REPORT = REPORT + "Enviromnent: <b><font color='red'>%s%s</font></b><br>" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + "<table align='left' width='800' cellpadding='1' cellspacing='0'>"
	REPORT = REPORT + "<tr><td>"	
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
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/useraccountsregression/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/useraccountsregression/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		print ("creating report backup folder if do not exist already ...")
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		print ("Backup Folder: %s" % BACKUPREPORTFOLDER)
		print ("Report Folder: %s" % REPORTFOLDER)	
		print ("completed creating report backup folders ...")	
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="User Accounts Regression "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/useraccountsregression/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="user_accounts_regression_reports_"+ENVIRONMENT.lower()+".txt"
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
		os.chdir("/mnt/automation/python/regression_test")
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
	message['Subject'] = 'User Accounts %s Regression Test Report - %s\n\n' % (ENVIRONMENT, START_TIME)
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
def logTestCaseStatus(exp_statuscode, statuscode, tc, step, function, p1, p2, p3, p4, p5, p6, p7, p8):
	global REPORT
	print ("* TEST CASE NUMBER       = %s" % tc)
	print ("* TEST STEP NUMBER       = %s" % step)
	
	REPORT = REPORT + "<tr><td colspan='4'><table border='1' width='100%%' cellspacing='0' cellpadding='0'><tr><td><table width='100%%'>"
	REPORT = REPORT + "<tr><td colspan='4' bgcolor='#D0D0D0'><font size='4'> %d.%d - <b><i>%s</i></b></font></td></tr>" % (tc, step, function)
	report_local = ""
	for i in range (1,8):
		exec('if p'+str(i)+ ' > "": report_local  = report_local  + "<tr><td colspan=4>"+p'+str(i)+'+"</td></tr>"')
	REPORT = REPORT + report_local
		
	if statuscode in exp_statuscode:
		print ("* TEST STATUS            = PASSED QA")
		print ("----------------------------------------------------------------------------")
		REPORT = REPORT + "<tr><td bgcolor='green' ><font color='#FFFFFF'>End test case: %s step: %s</td><td bgcolor='green'><font color='#FFFFFF'>%s</td> \
			<td bgcolor='green'><font color='#FFFFFF'>%s</td><td bgcolor='green'><font color='#FFFFFF'>PASSED QA</td></tr>"% (tc, step, exp_statuscode, statuscode)
		#REPORT = REPORT + "<tr><td colspan='4'><hr></td></tr>"
	else:
		print ("* TEST STATUS            = FAILED QA")
		print ("----------------------------------------------------------------------------")
		REPORT = REPORT + "<tr><td bgcolor='red' ><font color='#FFFFFF'>End test case: %s step: %s</td><td bgcolor='red'><font color='#FFFFFF'>%s</td> \
			<td bgcolor='red'><font color='#FFFFFF'>%s</td><td bgcolor='red'><font color='#FFFFFF'>FAILED QA</td></tr>"% (tc, step, exp_statuscode, statuscode)
		#REPORT = REPORT + "<tr><td colspan='4'><hr></td></tr>"
		if int(PAUSE_FOR_FAILURES) == 1:
			raw_input("Press Enter to continue...")	
	REPORT = REPORT + "</table></td></tr></table>"		
	#print ("\n")				
			
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
	
	
	TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
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

	# skip this step for tc or step of zero, which is indication of a cleanup process	
	if (step > 0):
		logTestCaseStatus(exp_statuscode, statuscode, tc, step, "obtainInternalToken", un, pw, external_token, TOKEN, "", "", "", "")

#=========================================================================================
# * POST:/uorgs/cproperties => POST:/customer/property # creates a new custom property definition
# * GET:/uorgs/cproperties => GET:/customer/properties # gets list of property definitions
# * DELETE:/uorgs/cproperties/{name} => no equivalent # removes given property definition

# * PUT:/uorgs/{id}/properties/{name} => POST:/customer/{id}/{name} # set property value on entity

# * DELETE:/uorgs/{id}/properties/{name} => DELETE:/customer/{id}/property?name={name} # remove prop value
# * GET:/uorgs/{id}/properties => no equivalent # get all props on given entity
# * GET:/uorgs/properties => no equivalent # get all props on all entities
# * GET:/uorgs/properties/{name} => GET:/customer/property/{name} get single prop value on all entities
#=========================================================================================

#		Type: "uorgs" / "users"
def viewCustomPropertyDefinition(type, exp_statuscode, tc, step):
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - VIEW CUSTOM PROPERTY DEFINITION %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	if type == "customer":
		URL = UA_URL+'/'+type+'/properties'
	else:	
		URL = UA_URL+'/'+type+'/cproperties'
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else: 
		print "Failure occured, exiting now ..."
		#quit()	

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "viewCustomPropertyDefinition", APIXIO_TOKEN, type, prop_list, "", "", "", "", "")
	return(response)
	
#=========================================================================================
#		Type: "uorgs" / "users"
def createCustomPropertyDefinition(type, pname, ptype, exp_statuscode, tc, step):
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - CREATE NEW CUSTOM PROPERTY DEFINITION %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	#pname = "uatest9"
	#ptype = "STRING"
	if type == "customer":
		URL = UA_URL+'/'+type+'/property?name='+pname+'&type='+ptype
	else:	
		URL = UA_URL+'/'+type+'/cproperties'
	DATA = {"name": pname, "type": ptype}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}

	response = requests.post(URL, data=json.dumps(DATA), headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if (statuscode == 200):
		print ("New custom propery definition was successfully created ...")
		print ("Name: %s  Type: %s" % (pname, ptype))
	elif (statuscode == 400):
		print ("This custom property name already exists.  Skipping ...")
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()
	else:
		print "Failure occured, exiting now ..."
		#quit()		
	
	
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "createCustomPropertyDefinition", APIXIO_TOKEN, type, pname, ptype, "", "", "", "")
	return(response)

#=========================================================================================
	
#		Type: "uorgs" / "users"
def deleteCustomPropertyDefinition(type, pname, exp_statuscode, tc, step):
	
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - DELETE CUSTOM PROPERTY DEFINITION %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/cproperties/'+pname+''
	print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}

	response = requests.delete(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:
		print "Failure occured, exiting now ..."
		#quit()		
	
	
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "deleteCustomPropertyDefinition", APIXIO_TOKEN, type, pname, "", "", "", "", "")
	return(response)	

#=========================================================================================
# * PUT:/uorgs/{id}/properties/{name} => POST:/customer/{id}/{name} # set property value on entity

def setPropertyValueOnEntity(type, entityID, pname, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - SET PROPERTY VALUE ON ENTITY %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	value="80"
	if type == "customer":
		URL = UA_URL+'/'+type+'/'+entityID+'/property/'+pname
	else:
		URL = UA_URL+'/'+type+'/'+entityID+'/properties/'+pname	
	print URL
	DATA = json.dumps({"value": value})
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	if type == "customer":
		response = requests.post(URL, data=DATA, headers=HEADERS)
	else:
		response = requests.put(URL, data=DATA, headers=HEADERS)	
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:
		print "Failure occured, exiting now ..."
		#quit()	

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "setPropertyValueOnEntity", APIXIO_TOKEN, type, entityID, pname, value, "", "", "")
	return()

#=========================================================================================

def removePropertyValueFromEntity(type, entityID, pname, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - REMOVE PROPERTY VALUE ON ENTITY %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	value=""
	URL = UA_URL+'/'+type+'/'+entityID+'/properties/'+pname
	print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.delete(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:
		print "Failure occured, exiting now ..."
		#quit()	

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "removePropertyValueFromEntity", APIXIO_TOKEN, type, entityID, pname, "", "", "", "")
	return()
	
#=========================================================================================	
	
def getAllPropertiesOnGivenEntity(type, entityID, exp_statuscode, tc, step):

	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - VIEW ALL PROPERTIES ON GIVEN ENTITY %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/'+entityID+'/properties'
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else: 
		print "Failure occured, exiting now ..."
		#quit()	

	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "getAllPropertiesOnGivenEntity", APIXIO_TOKEN, type, entityID, prop_list, "", "", "", "")

	return()
	
#=========================================================================================	

def getAllPropertiesOnAllEntities(type, exp_statuscode, tc, step):

	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - VIEW ALL PROPERTIES FOR ALL ENTITIES %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/properties'
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else: 
		print "Failure occured, exiting now ..."
		#quit()	

	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "getAllPropertiesOnAllEntities", APIXIO_TOKEN, type, prop_list, "", "", "", "", "")
	return()
	
#=========================================================================================	
	
def getSinglePropertyValueOnAllEntities(type, pname, exp_statuscode, tc, step):


	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - VIEW SINGLE PROPERTY ON ALL ENTITIES %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/properties/'+pname
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else: 
		print "Failure occured, exiting now ..."
		#quit()	

	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "getSinglePropertyValueOnAllEntities", APIXIO_TOKEN, type, pname, "", "", "", "", "")
	return()	
	
	
#=========================================================================================	
	
def getCustomerRelatedData(type, option, exp_statuscode, tc, step):


	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - VIEW CUSTOMER RELATED ALL PROJECTS AND PROPERTIES %s <<<" % option.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/'+option
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else: 
		print "Failure occured, exiting now ..."
		#quit()	

	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "getCustomerRelatedData", APIXIO_TOKEN, type, option, "", "", "", "", "")
	return()	
	
#=========================================================================================	
# POST:/customer/{id}/{name} # set property value on entity
# POST:/customer/{customerID}/property/{name}	
def setCurtomerPropertyValue(type, customerID, pname, exp_statuscode, tc, step):

	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - SET CUSTOMER PROPERTY VALUE %s <<<" % pname.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/'+customerID+'/property?name='+pname
	#print URL
	#DATA = {}
	DATA = json.dumps({"value":"paa"})
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.post(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()	

	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "setCurtomerPropertyValue", APIXIO_TOKEN, type, customerID, pname, "", "", "", "")

	return()		

#=========================================================================================
# * DELETE:/uorgs/{id}/properties/{name} => DELETE:/customer/{id}/property?name={name} remove prop value
def removeCurtomerPropertyValue(type, customerID, pname, exp_statuscode, tc, step):

	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - REMOVE CUSTOMER PROPERTY VALUE %s <<<" % pname.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/'+customerID+'/property?name='+pname
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.delete(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()	

	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "removeCurtomerPropertyValue", APIXIO_TOKEN, type, customerID, pname, "", "", "", "")

	return()	

#=========================================================================================
# * GET:/uorgs/properties/{name} => GET:/customer/property/{name} get single prop value on all entities

def getSinglePropValueOnAllCustomers(type, pname, exp_statuscode, tc, step):

	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - GET PROPERTY VALUE ON ALL CUSTOMERS %s <<<" % pname.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/property/'+pname
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else:		
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()


	#GET:/uorgs/properties
	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "getSinglePropValueOnAllCustomers", APIXIO_TOKEN, type, pname, prop_list, "", "", "", "")

	return()	

#=========================================================================================

def getObject(type, typeName, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - GET %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	prop_list={}
	URL = UA_URL+'/'+type+'/'+typeName
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else:		
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "get"+type+"Object", APIXIO_TOKEN, type, typeName, prop_list, "", "", "", "")

	return()
#=========================================================================================

def postObject(type, atoname, atodescription, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - CRERATE NEW %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/'
	#print URL
	DATA = {"name": atoname,"description": atodescription}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.post(URL, data=json.dumps(DATA), headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:		
		print "Failure occured, exiting now ..."
		print json.dumps(response.json())
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "post"+type+"Object", APIXIO_TOKEN, type, atoname, atodescription, "", "", "", "")

	return()
#=========================================================================================

def deleteObject(type, atoname, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - DELETE %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = UA_URL+'/'+type+'/'+atoname
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.delete(URL, data=json.dumps(DATA), headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode != ok:		
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "delete"+type+"Object", APIXIO_TOKEN, type, atoname, "", "", "", "", "")

	return()

#=========================================================================================	
	
def getSysPassRolUsr(type, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - GET SYS %s <<<" % type.upper())
	print ("----------------------------------------------------------------------------")
	response = ""
	prop_list={}
	URL = UA_URL+'/sys/'+type
	#print URL
	DATA = {}
	HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
	response = requests.get(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print statuscode
	if statuscode == ok:
		prop_list = json.dumps(response.json())
		print json.dumps(response.json())
	else:		
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "getSysPassRolUsr", APIXIO_TOKEN, type, "", "", "", "", "", "")

	return()	
	
#=========================================================================================

def authenticateUser(etoken, type, email, password, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - AUTHENTICATE USER %s <<<" % email.upper())
	print ("----------------------------------------------------------------------------")
	prop_list = {}
	response = ""
	itoken = ""
	TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
	if type == "external":
		URL = UA_URL+'/auths'
		DATA = {'email': email, 'password': password}
		HEADERS = {"Content-Type": "application/json"}
	else:
		URL = "https://tokenizer-stg.apixio.com:7075/tokens"
		DATA = {'Referer': TOKEN_URL, 'Authorization': 'Apixio ' + etoken}	
		HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': TOKEN_URL, 'Authorization': 'Apixio ' + etoken}	
	
	response = requests.post(URL, data=json.dumps(DATA), headers=HEADERS)
	statuscode = response.status_code
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	if statuscode == created or statuscode == ok:
		prop_list = json.dumps(response.json())
		#print json.dumps(response.json())
		userjson = response.json()
		if type == "external":
			etoken = userjson.get("token")
		else:
			itoken = userjson.get("token")	
		print ("* EXTERNAL TOKEN VALUE   = %s" % etoken)
		print ("* INTERNAL TOKEN VALUE   = %s" % itoken)	
	elif statuscode == unauthorized:
		print ("* EXTERNAL TOKEN VALUE   = %s" % etoken)
		print ("* INTERNAL TOKEN VALUE   = %s" % itoken)	
	else:		
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		#quit()

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "authenticateUser", etoken, itoken, email, prop_list, "", "", "", "")	

	return(etoken)
	
#=========================================================================================	
	
def deleteExternalToken(etoken, email, password, exp_statuscode, tc, step):
	print ("\n----------------------------------------------------------------------------")
	print (">>> UA - DELETE USER TOKEN %s <<<" % email.upper())
	print ("----------------------------------------------------------------------------")
	response = ""

	URL = UA_URL+'/auths/?id='+etoken
	DATA = {}
	HEADERS = {"Content-Type": "application/json"}
	
	response = requests.delete(URL, data=DATA, headers=HEADERS)
	statuscode = response.status_code
	print ("* RECEIVED STATUS CODE   = %s" % statuscode)
	if statuscode != ok:
		print "Failure occured, exiting now ..."
		print "URL = %s" % URL
		print "DATA = %s" % DATA
		print "HEADERS = %s" % HEADERS
		quit()

	logTestCaseStatus(exp_statuscode, statuscode, tc, step, "deleteExternalToken", etoken, email, "", "", "", "", "", "")	

	return(etoken)	
#=========================================================================================


def cleanUp():
	acl_operation = ACL_OPERATION
	# log-in as a Root-User
	# obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 0, 0)
	return()
	
#=========================================================================================

def bundleDataSet():
	print ("\n----------------------------------------------------------------------------")
	print (">>> BUNDLE DATA SET FOR %s PROJECT <<<" % PROJECTID)
	print ("----------------------------------------------------------------------------")
	response = ""
	URL = BUNDL_URL+"/cmp/v1/project/"+PROJECTID+"/bundle"
	if BATCHID > "":
		URL = BUNDL_URL+"/cmp/v1/project/"+PROJECTID+"/bundle?batch_id="+BATCHID
	
	print ("\n")
	print ("* URL                    = %s"%URL)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* Admin User Name        = %s"%ACLUSERNAME)
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

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

printGlobalParamaterSettings()

obtainInternalToken(IGOR_EMAIL, "apixio.123", {ok, created}, 0, 0)

bundleDataSet()
	

print ("\n============================================================================")	
print ("============================= End of Bundler =================================")
print ("============================================================================")
#=========================================================================================
