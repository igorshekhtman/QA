#=========================================================================================
#============================= esuaregressiontest.py =====================================
#=========================================================================================
#
# PROGRAM:         esuaregressiontest.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    30-Nov-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for testing New User Accounts functionality:
#
# NOTES / COMMENTS:
#
#
#
# COVERED TEST CASES:
#
#
# SETUP:
#          * Assumes User Accounts are available
#		   * Assumes that Python2.7 is available 
#
# USAGE:
#          * Set the global variables, see below (Global Test Environment Selection)
#          * Run: python2.7 esuaregressiontest.py dev eng@apixio.com ops@apixio.com
#          * Results can be accessed through Apixio Reports portal: https://reports.apixio.com/html/user_accounts_regression_reports_staging.html
#
# MISC: 
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
requests.packages.urllib3.disable_warnings()
#=========================================================================================
#================= Global Variable Initialization Section ================================
#=========================================================================================
REPORT = ""
REPORT_TYPE = "User Accounts Regression Test"
SENDER = "donotreply@apixio.com"
CUR_TIME = strftime("%m/%d/%Y %H:%M:%S", gmtime())
START_TIME = strftime("%m/%d/%Y %H:%M:%S", gmtime())
TIME_START = time.time()
END_TIME = strftime("%m/%d/%Y %H:%M:%S", gmtime())
DURATION_TIME = strftime("%m/%d/%Y %H:%M:%S", gmtime())
DAY = strftime("%d", gmtime())
MONTH = strftime("%m", gmtime())
MONTH_FMN = strftime("%B", gmtime())
YEAR = strftime("%Y", gmtime())
CURDAY = strftime("%d", gmtime())
CURMONTH = strftime("%m", gmtime())
CURYEAR = strftime("%Y", gmtime())

PASSED_STAT="<table width='100%%'><tr><td bgcolor='#00A303' align='center'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED_STAT="<table width='100%%'><tr><td bgcolor='#DF1000' align='center'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<br><table width='100%%'><tr><td bgcolor='#4E4E4E' align='left'><font size='3' color='white'><b>&nbsp;&nbsp; %s</b></font></td></tr></table>"
	
ok      			= 200
created 			= 201
accepted 			= 202
nocontent 			= 204
movedperm 			= 301
redirect 			= 302
requestdenied  		= 400
unauthorized 		= 401
forbidden 			= 403
notfound 			= 404
unprocessablentity	= 422
intserveror 		= 500
servunavail 		= 503

STATUS_CODES = {	200: "OK", 201: "CREATED", 202: "ACCEPTED", 204: "NO CONTENT", 301: "MOVED PERM", \
				302: "REDIRECT", 400: "REQUEST DENIED", 401: "UNAUTHORIZED", 403: "FORBIDDEN", \
				404: "NOT FOUND", 500: "INT SERVER ERROR", 503: "SERVER UNAVAILABLE" } 

ALEX_EMAIL			=	"ishekhtman@apixio.com"
IGOR_EMAIL			=	"ishekhtman@apixio.com"
IGOR_UUID			=	"U_6d6a994f-7fe3-45cd-8d0e-76d92ba81066"
GARTH_EMAIL			=	"grinderUSR1416591631@apixio.net"
GARTH_UUID			=	"U_7ba7f9e3-8cf5-48e6-b1b1-5d577ef4a72c"
ERIC_EMAIL			=	"grinderUSR1416591626@apixio.net"
ERIC_UUID			=	"U_f8d8d099-8512-44df-83af-216f0140e758"
BROOKE_EMAIL		=	"grinderUSR1416591636@apixio.net"
BROOKE_UUID			=	"U_ee7a0cf3-8111-4277-b5ff-d3793159697e"
KIM_EMAIL			=	"grinderUSR1416591640@apixio.net"
KIM_UUID			=	"U_5ee129d3-2ea3-4ab9-b166-8ddf818cfce6"
CODEBUSTERS_UUID	=	"G_db9ffdb6-b9a0-4b8c-b963-2be05a9ecf45"
SCRIPPS_UUID		=	"X_7040367c-d8fd-411c-b87a-4382bbda4027"
CHMC_UUID			=	"X_1879b8a5-2e6e-4595-9846-eb10048bf5d8"
ACL_OPERATION		=	"CanTest"

MAX_NUM_RETRIES		=5
TEST_FLOW_CONTROL	=1
# 1=pause 0=no pause
WAIT_FOR_USER_INPUT_BETWEEN_TEST_CASES=0
PAUSE_FOR_FAILURES	=0
#=========================================================================================
def printGlobalParamaterSettings():
	print ("============================================================================")
	print ("* Environment            = %s" % ENVIRONMENT)
	print ("* UA URL                 = %s" % UA_URL)
	print ("* Receivers              = %s, %s" % (RECEIVERS,RECEIVERS2))
	return ()
#=========================================================================================
def checkEnvironmentandReceivers():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global HCC_DOMAIN, HCC_URL, HCC_PASSWORD, PROTOCOL, ACLUSERNAME, ACLPASSWORD
	global ACL_DOMAIN, HCC_USERNAME_PREFIX, HCC_USERNAME_POSTFIX
	global TOKEN_URL, UA_URL, SSO_URL, CALLER, ADMIN_PW, ADMIN_USR, UA_PORT
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT[:1].upper() == "P"): ###### PRODUCTION #########
		ENVIRONMENT = "production"
		ACL_DOMAIN="acladmin.apixio.com"
		UA_URL="https://acladmin.apixio.com"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="root@api.apixio.com"
		ACLPASSWORD="thePassword"
		ADMIN_USR="ishekhtman@apixio.com"
		ADMIN_PW="apixio.321"
	elif (ENVIRONMENT[:1].upper() == "E"): ######### ENGINEERING ##############
		ENVIRONMENT = "engineering"
		PROTOCOL="https://"
		HCC_USERNAME_PREFIX="sanityUSR"
		HCC_USERNAME_POSTFIX="@apixio.net"
		ADMIN_PW="apixio.321"
		TOKEN_URL="https://tokenizer-eng.apixio.com:7075/tokens"
		UA_URL="https://useraccount-eng.apixio.com:7076"
		SSO_URL="https://accounts-eng.apixio.com"
		CALLER="hcc_eng"
		ADMIN_USR="ishekhtman@apixio.com"
		ADMIN_PW="apixio.321"
	elif (ENVIRONMENT[:1].upper() == "D"):   ######## DEVELOPMENT ###########
		ENVIRONMENT = "development"
		PROTOCOL="https://"
		HCC_USERNAME_PREFIX="sanityUSR"
		HCC_USERNAME_POSTFIX="@apixio.net"
		TOKEN_URL="https://tokenizer-dev.apixio.com:7075/tokens"
		UA_URL="https://useraccount-dev.apixio.com"
		UA_PORT="7076"
		SSO_URL="https://accounts-dev.apixio.com"
		CALLER="hcc_dev"
		ADMIN_USR="ishekhtman@apixio.com"
		ADMIN_PW="apixio.321"
	elif (ENVIRONMENT[:1].upper() == "S"):   ######### STAGING ##############	
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://acladmin-stg.apixio.com"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ADMIN_USR="ishekhtman@apixio.com"
		ADMIN_PW="apixio.321"
	else: ######### STAGING ##############
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://acladmin-stg.apixio.com"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ADMIN_USR="ishekhtman@apixio.com"
		ADMIN_PW="apixio.321"
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS2=str(sys.argv[3])
		HTML_RECEIVERS="""To: Eng <%s>,Ops <%s>\n""" % (str(sys.argv[2]), str(sys.argv[3]))
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS2="ishekhtman@apixio.com"
		HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""
				
	return ()		
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
	return ()
	
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
	return ()

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
	return ()

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
	return ()	

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
	return()

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
	return ()				
			
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def obtainExternalToken(un, pw):

	external_token = ""
	url = UA_URL+':'+UA_PORT+'/auths'
	referer = UA_URL+':'+UA_PORT  	
	
	DATA =    {'Referer': referer, 'email': un, 'password': pw} 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
	
	response = requests.post(url, data=DATA, headers=HEADERS)
	 
	if (response.status_code != ok):
		print ("* Failed to obtain external token: %s. Exiting now ..." % response.status_code)
		quit()
	else:	
		userjson = response.json()
		if userjson is not None:
			external_token = userjson.get("token") 
			print ("* USERNAME               = %s" % un)
			print ("* PASSWORD               = %s" % pw)
			print ("* URL                    = %s" % url)
			print ("* EXT TOKEN              = %s" % external_token)
			print ("* STATUS CODE            = %s" % response.status_code)
			
	return (external_token)
#=========================================================================================
def obtainInternalToken(un, pw):
	
	external_token = obtainExternalToken(un, pw)
	url = TOKEN_URL
  	referer = TOKEN_URL  				
  	DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + external_token} 
  	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + external_token}
  	
  	response = requests.post(url, data=DATA, headers=HEADERS) 
  	if (response.status_code != created):
		print ("* Failed to create internal token: %s. Exiting now ..." % response.status_code)
		quit()
	else:
  		userjson = response.json()
  		if userjson is not None:
  			token = userjson.get("token")
  			apixio_token = 'Apixio '+str(token)
			print ("* USERNAME               = %s" % un)
			print ("* PASSWORD               = %s" % pw)
			print ("* TOKENIZER URL          = %s" % url)
			print ("* EXT TOKEN              = %s" % external_token)
			print ("* INT TOKEN              = %s" % token)
			print ("* APIXIO TOKEN           = %s" % apixio_token)
			print ("* STATUS CODE            = %s" % response.status_code)
			print ("============================================================================")
  		else:
			token = "Not Available"	
	
	return(apixio_token)		
#========================================================================================================
def accessGrants(fn, subject, operation):
	url = UA_URL+':'+UA_PORT+'/grants/'+subject+"/"+operation
	if fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)
	elif fn == "delete":
		response = requests.delete(url, data=DATA, headers=HEADERS)
	print url	
	print response.status_code
	return()
#========================================================================================================
def accessPassPolicies(fn, policyName):
	url = UA_URL+':'+UA_PORT+'/passpolicies/'+policyName
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)	
	print url	
	print response.status_code
	return()
#========================================================================================================
def accessPatientDataSets(fn, name, entityID, pdsID):
	url = UA_URL+':'+UA_PORT+'/patientdatasets'
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)	
	elif fn == "delete":
		response = requests.delete(url, data=DATA, headers=HEADERS)	
	print url	
	print response.status_code
	return(response.json())
#========================================================================================================
def accessPerms(fn, subject, operation, object):
	url = UA_URL+':'+UA_PORT+'/perms/'+subject+'/'+operation+'/'+object
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)	
	elif fn == "delete":
		response = requests.delete(url, data=DATA, headers=HEADERS)	
	print url	
	print response.status_code
	return()
#========================================================================================================
def accessProjects(fn, bag, name, userid, entityID, projID, role):
	url = UA_URL+':'+UA_PORT+'/projects/'+bag
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)	
	elif fn == "delete":
		response = requests.delete(url, data=DATA, headers=HEADERS)	
	print url	
	print response.status_code
	return()
#========================================================================================================
def accessRoleSets(fn, nameID, role):
	url = UA_URL+':'+UA_PORT+'/rolesets/'+nameID+'/'+role
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)		
	print url	
	print response.status_code
	return()
#========================================================================================================
def accessTexts(fn, blobID):
	url = UA_URL+':'+UA_PORT+'/texts/'+blobID
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)		
	print url	
	print response.status_code
	return()
#========================================================================================================
def accessUorgs(fn, name, entityID, orgID, userID, pdsID, roleName):
	url = UA_URL+':'+UA_PORT+'/uorgs'
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)	
	elif fn == "delete":
		response = requests.delete(url, data=DATA, headers=HEADERS)	
	print url	
	print response.status_code
	return(response.json())
#========================================================================================================
def accessUsers(fn, name, userID, entityID, detail):
	url = UA_URL+':'+UA_PORT+'/users'
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	elif fn == "put":
		response = requests.put(url, data=DATA, headers=HEADERS)	
	elif fn == "delete":
		response = requests.delete(url, data=DATA, headers=HEADERS)	
	print url	
	print response.status_code
	return(response.json())
#========================================================================================================
def accessVerifications(fn, id):
	url = UA_URL+':'+UA_PORT+'/verifications/'+id
	if fn == "get":
		response = requests.get(url, data=DATA, headers=HEADERS)
	elif fn == "post":
		response = requests.post(url, data=DATA, headers=HEADERS)
	print url	
	print response.status_code
	return()
#========================================================================================================
def testCase1():
	return()		
	
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

checkEnvironmentandReceivers()

#writeReportHeader()

printGlobalParamaterSettings()

APIXIO_TOKEN = obtainInternalToken(IGOR_EMAIL, ADMIN_PW) 
DATA = {}
HEADERS = {'Content-Type':'application/json', 'Authorization':APIXIO_TOKEN}

dataSets = accessPatientDataSets("get", None, None, None)
uOrgs = accessUorgs("get", None, None, None, None, None, None)
users = accessUsers("get", None, None, None, None)
#print users
#print uOrgs





#for i in range (1,2):
	#cleanUp()
#	exec('testCase' + str(i) + '()')

#writeReportFooter()
#archiveReport()
#emailReport()	

print ("\n============================================================================")	
print ("================== End of User Accounts Regression Test ====================")
print ("============================================================================")
#=========================================================================================
