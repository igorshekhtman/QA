#=========================================================================================
#=========================== resanity.py =================================================
#=========================================================================================
#
# PROGRAM:         resanity.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    15-Jan-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Grinder for testing ACL functionality:
#			* Log into Rules Editor
#			* Obtain and save token
#
#
#
# SETUP:
#          * Assumes Python2.7 is available
#
# USAGE:
#          * python2.7 resanity.py production ops@apixio.com eng@apixio.com
#
#=========================================================================================
# Global Paramaters descriptions and possible values:
# These are defined in CSV_CONFIG_FILE_NAME = "resanity.csv", 
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
#===================== Initialization of the ACLConfig file ==============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/sanity_test/"
CSV_CONFIG_FILE_NAME = "resanity.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "Rules Editor Sanity Test"
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

MODULES = {	"log into rules editor":"0", \
			"access customers tab":"1", \
			"access users tab":"2", \
			"update opportunity router":"3", \
			"update cache":"4", \
			"access rules state":"5", \
			"access customers filter":"6", \
			"pause and resume routing":"7" \
			}
FAILED_TOT = [0,1,2,3,4,5,6,7]
SUCCEEDED_TOT = [0,1,2,3,4,5,6,7]
RETRIED_TOT = [0,1,2,3,4,5,6,7]
for i in range (0, 8):
	FAILED_TOT[i] = 0
	SUCCEEDED_TOT[i] = 0
	RETRIED_TOT[i] = 0
	
SUBTASKS = { "route", "strategy", "user", "filter", "annotator" }

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
	print ("* Rules Editor URL       = %s"%URL)
	print ("* Rules Editor Customer  = %s"%CUSTOMER)
	print ("* Rules Editor User      = %s"%USER)            
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
	global URL, USERNAME, PASSWORD, CUSTOMER, USER
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		USERNAME="apxdemot0138"
		PASSWORD="Hadoop.4522"
		ENVIRONMENT = "production"
		URL = "http://ruleseditor.apixio.com:80"
		CUSTOMER = "MMG (10000232)"
		USER = "apxdemot0500@apixio.net"

	else:
		USERNAME="grinderUSR1416591626@apixio.net"
		PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
		URL = "http://ruleseditor-stg.apixio.com:8041"
		CUSTOMER = "O_00000000-0000-0000-0000-000000000370"
		USER = "sanityusr1421099389@apixio.net"
		
	
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
	REPORT = REPORT + """Subject: Rules Editor %s Sanity Test Report - %s\n\n""" % (ENVIRONMENT, START_TIME)

	REPORT = REPORT + """<h1>Apixio Rules Editor Sanity Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """Customer: <b>%s</b><br>\n""" % (CUSTOMER)
	REPORT = REPORT + """User: <b>%s</b><br>\n""" % (USER)
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
	print ("\nCompleted writeReportDetails ... \n")

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
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/resanity/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/resanity/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="RulesEditor Sanity "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/resanity/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="re_sanity_reports_"+ENVIRONMENT.lower()+".txt"
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
def logInToRulesEditor():
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - LOGIN <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL
	referer = URL 				
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.get(url, data=DATA, headers=HEADERS) 
	#print response.cookies
	#print response.json()
	#print response.text
	#print response.encoding
	#print response.raw
	#print response
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("log into rules editor", statuscode)	
	#quit()
#=========================================================================================
def customersTab():
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - CUSTOMER TAB <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/customer/"
	referer = URL+"/access/customer/"	
	print ("* CUSTOMER TAB URL       = %s" % url)			
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("access customers tab", statuscode)	
	#quit()
#=========================================================================================
def usersTab():
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - USERS TAB <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/annotators/"
	referer = URL+"/access/annotators/"	
	print ("* USERS TAB URL          = %s" % url)			
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("access users tab", statuscode)	
	#quit()
#=========================================================================================
def updateOpportunityRouter():
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - UPDATE ROUTER <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/rules/update"
	referer = URL+"/access/rules/update"	
	print ("* UPDATE ROUTER URL      = %s" % url)			
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.post(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("update opportunity router", statuscode)	
	#quit()

#=========================================================================================
def updateCache():
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - UPDATE CACHE <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/cache/refresh/force"
	referer = URL+"/access/cache/refresh/force"	
	print ("* UPDATE CACHE URL       = %s" % url)			
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.post(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("update cache", statuscode)	


#=========================================================================================
def accessRulesState():
	#Request URL:http://ruleseditor-stg.apixio.com:8041/access/rules/state
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - ACCESS RULES STATE <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/rules/state"
	referer = URL+"/access/rules/state"	
	print ("* UPDATE CACHE URL       = %s" % url)			
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("access rules state", statuscode)

#=========================================================================================
def accessCustomer(subtask):
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - ACCESS CUSTOMER: %s <<<"%subtask.upper())
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/customer/"+CUSTOMER+"/"+subtask
	referer = URL+"/access/customer/"+CUSTOMER+"/"+subtask
	print ("* ACCESS CUSTOMER URL    = %s" % url)		
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', 'Host': URL}
	response = requests.get(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("access customers filter", statuscode)
	
#=========================================================================================	
def routingPR(subtask):	
	print ("\n----------------------------------------------------------------------------")
	print (">>> RULES EDITOR - PAUSE AND RESUME ROUTING <<<")
	print ("----------------------------------------------------------------------------")
	print ("* RULES EDITOR URL       = %s" % URL)
	#statuscode = 500
	# repeat until successful login is reached
	url = URL+"/access/customer/"+CUSTOMER+"/state/"+subtask
	referer = "http://ruleseditor-stg.apixio.com:8041/"
	print ("* ROUTING URL            = %s" % url)		
	DATA =    {'Referer': referer} 
	HEADERS = {'Connection': 'keep-alive', \
				'Content-Length':'0', \
				'Host':'ruleseditor-stg.apixio.com:8041', \
				'Origin':'http://ruleseditor-stg.apixio.com:8041', \
				'Referer':'http://ruleseditor-stg.apixio.com:8041/' }	
				
	response = requests.post(url, data=DATA, headers=HEADERS) 
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("pause and resume routing", statuscode)
	

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
os.system('clear')

print ("\n\nStarting ACL-Admin New User Creation...\n")

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

writeReportHeader()

PrintGlobalParamaterSettings()

logInToRulesEditor()
writeReportDetails("log into rules editor")

customersTab()
writeReportDetails("access customers tab")

usersTab()
writeReportDetails("access users tab")

updateOpportunityRouter()
writeReportDetails("update opportunity router")

updateCache()
writeReportDetails("update cache")

accessRulesState()
writeReportDetails("access rules state")

for subtask in SUBTASKS:
	accessCustomer(subtask)
writeReportDetails("access customers filter")

routingPR("pause")
routingPR("resume")
writeReportDetails("pause and resume routing")

writeReportFooter()

archiveReport()

emailReport()	
	
print ("==== End of Rules Editor Sanity Test =====")
print ("==========================================")
#=========================================================================================