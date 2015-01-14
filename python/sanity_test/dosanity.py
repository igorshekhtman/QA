#=========================================================================================
#========================== dosanity.py ==================================================
#=========================================================================================
#
# PROGRAM:         dosanity.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    13-Jan-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for testing DataOrchestrator functionality:
#			* Log into DataOrchestrator API
#			* Obtain and save token
#			* Test Patient, Util and Document endpoints
#
#
# SETUP:
#          * Assumes DataOrchestrator environment is available
#          * Assume  Python2.7 is available
#
# USAGE:
#          * Execute via following command dosanitytest.py staging eng@apixio.com ops@apixio.com
#		   * Ensure that dosanity.csv file is located in the same folder as dosanity.py script
#
#=========================================================================================
# Global Paramaters descriptions and possible values:
# These are defined in CSV_CONFIG_FILE_NAME = "dosanity.csv", 
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
from time import gmtime, strftime, localtime
import calendar	
#=========================================================================================
#===================== Initialization of the DOConfig file ===============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/sanity_test/"
CSV_CONFIG_FILE_NAME = "dosanity.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "DataOrchestrator Sanity Test"
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

MODULES = {	"obtain internal token":"0", \
			"patient demographics":"1", \
			"patient externalIds":"2", \
			"patient apo":"3", \
			"util healthcheck":"4", \
			"util version":"5", \
			"document text":"6", \
			"document metadata":"7", \
			"document file":"8", \
			"document textContent":"9", \
			"document simpleContent":"10", \
			"document rawContent":"11", \
			"document extractedContent":"12", \
			"document apo":"13" \
			}
FAILED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
SUCCEEDED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
RETRIED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
for i in range (0, 14):
	FAILED_TOT[i] = 0
	SUCCEEDED_TOT[i] = 0
	RETRIED_TOT[i] = 0

#=========================================================================================
#================== Global variable declaration, initialization ==========================
#=========================================================================================
#
# Author: Igor Shekhtman ishekhtman@apixio.com
#
# Creation Date: 13-Jan-2015
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
unauthorized = 401
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
	print ("* Username               = %s"%USERNAME)
	print ("* Password               = %s"%PASSWORD)
	print ("* Patient UUID           = %s"%PAT_UUID)
	print ("* Document UUID          = %s"%DOC_UUID)
	print ("* Authorization URL      = %s"%AUTH_URL)
	print ("* Token URL              = %s"%TOKEN_URL)
	print ("* Document URL           = %s"%DOCUMENT_URL)
	print ("* Patient URL            = %s"%PATIENT_URL)
	print ("* Event URL              = %s"%EVENT_URL)
	print ("* Util URL               = %s"%UTIL_URL)
#=========================================================================================
def IncrementTestResultsTotals(module, code):
	global FAILED, SUCCEEDED, RETRIED
	global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
	if (code == ok) or (code == nocontent) or (code == created):
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
	global PAT_UUID, DOC_UUID, AUTH_URL, TOKEN_URL, DOCUMENT_URL, PATIENT_URL, EVENT_URL
	global UTIL_URL, DO_URL, PREFIX
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		USERNAME="apxdemop01@apixio.net"
		PASSWORD="Hadoop.4522"
		ENVIRONMENT = "production"
		PAT_UUID = "aa5c0726-5e67-451a-a863-cb82b4f01399"
		DOC_UUID = "ccf9248d-0421-47dd-87cf-fbb4e02a2f94"
		AUTH_URL = "https://useraccount-prd.apixio.com:7076/auths"
		TOKEN_URL = "https://tokenizer-prd.apixio.com:7075/tokens"
		DOCUMENT_URL = "https://dataorchestrator-prd.apixio.com:7085/document"
		PATIENT_URL = "https://dataorchestrator-prd.apixio.com:7085/patient"
		EVENT_URL = "https://dataorchestrator-prd.apixio.com:7085/events"
		UTIL_URL = "https://dataorchestrator-prd.apixio.com:7085/util"
		DO_URL = "https://dataorchestrator-prd.apixio.com:7085"
		PREFIX = "P_"
	else:
		USERNAME="apxdemot01@apixio.net"
		PASSWORD="Hadoop.4522"
		ENVIRONMENT = "staging"
		PAT_UUID = "29ccd6d1-da94-4921-8a0f-e33989d4d2b9"
		DOC_UUID = "b327252e-81a1-4a85-b712-a10d70a204fe"
		AUTH_URL = "https://useraccount-stg.apixio.com:7076/auths"
		TOKEN_URL = "https://tokenizer-stg.apixio.com:7075/tokens"
		DOCUMENT_URL = "https://dataorchestrator-stg.apixio.com:7085/document"
		PATIENT_URL = "https://dataorchestrator-stg.apixio.com:7085/patient"
		EVENT_URL = "https://dataorchestrator-stg.apixio.com:7085/events"
		UTIL_URL = "https://dataorchestrator-stg.apixio.com:7085/util"
		DO_URL = "https://dataorchestrator-stg.apixio.com:7085"
		PREFIX = "S_"
	
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
	REPORT = REPORT + """Subject: DataOrchestrator %s Sanity Test Report - %s\n\n""" % (ENVIRONMENT, START_TIME)

	REPORT = REPORT + """<h1>Apixio DataOrchestrator Sanity Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """DataOrch user name: <b>%s</b><br>\n""" % (USERNAME)
	REPORT = REPORT + """DataOrch app url: <b>%s</b><br>\n""" % (DO_URL)
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
	print ("* REPORT DETAILS         = LOGGED")

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
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/dosanity/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/dosanity/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="DO Sanity "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/dosanity/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="do_sanity_reports_"+ENVIRONMENT.lower()+".txt"
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
#===================== Main Test Functions ===============================================
#=========================================================================================

def obtainAuthorizationGetToken():
	global I_TOKEN, E_TOKEN
	print ("\n----------------------------------------------------------------------------")
	print (">>> DataOrchestrator - OBTAIN AUTHORIZATION EXCHANGE TOKENS<<<")
	print ("----------------------------------------------------------------------------")
	print ("* AUTH URL               = %s" % AUTH_URL)
	print ("* TOKEN URL              = %s" % TOKEN_URL)

	
	for i in range(1, 6):
		var_name=PREFIX+"USERNAME_"+str(i)
		value=globals()[var_name]
		print ("* USERNAME               = %s" % value)
		print ("* PASSWORD               = %s" % PASSWORD)
		url = AUTH_URL
  		referer = AUTH_URL  				
  		DATA =    {'Referer': referer, 'email': value, 'password': PASSWORD} 
  		HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
  		response = requests.post(url, data=DATA, headers=HEADERS) 
  		userjson = response.json()
  		if userjson is not None:
  			E_TOKEN = userjson.get("token")
		print ("* EXTERNAL TOKEN         = %s" % E_TOKEN)
		statuscode = response.status_code
		print ("* STATUS CODE            = %s" % statuscode)
		IncrementTestResultsTotals("obtain internal token", statuscode)
  		url = TOKEN_URL
  		referer = TOKEN_URL  				
  		DATA =    {'Referer': referer, 'Authorization': 'Apixio ' + E_TOKEN} 
  		HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer, 'Authorization': 'Apixio ' + E_TOKEN}
  		response = requests.post(url, data=DATA, headers=HEADERS) 
  		userjson = response.json()
  		if userjson is not None:
  			I_TOKEN = userjson.get("token")
		print ("* USERNAME               = %s" % value)
		print ("* PASSWORD               = %s" % PASSWORD)
		print ("* EXTERNAL TOKEN         = %s" % E_TOKEN)
		print ("* INTERNAL TOKEN         = %s" % I_TOKEN)
		statuscode = response.status_code
		print ("* STATUS CODE            = %s" % statuscode)
		IncrementTestResultsTotals("obtain internal token", statuscode)
		#quit()
	
#=========================================================================================	

def getPatient(endpoint):
	print ("\n----------------------------------------------------------------------------")
	print (">>> DataOrchestrator - PATIENT %s ENDPOINT <<<" % str(endpoint).upper())
	print ("----------------------------------------------------------------------------")
	print ("* PATIENT URL 1          = %s" % PATIENT_URL)
	for i in range(1, 6):
		var_name=PREFIX+"PAT_UUID_"+str(i)
		value=globals()[var_name]	
  		url = PATIENT_URL+'/'+value+'/'+str(endpoint)
  		referer = PATIENT_URL+'/'+value+'/'+str(endpoint)	
  		print ("* PATIENT URL 2          = %s" % url)			
  		DATA =    {'Authorization': 'Apixio ' + I_TOKEN} 
  		HEADERS = {'Authorization': 'Apixio ' + I_TOKEN}
  		response = requests.get(url, data=DATA, headers=HEADERS) 
		print ("* USERNAME               = %s" % USERNAME)
		print ("* PASSWORD               = %s" % PASSWORD)
		print ("* EXTERNAL TOKEN         = %s" % E_TOKEN)
		print ("* INTERNAL TOKEN         = %s" % I_TOKEN)
		print ("* PATIENT UUID           = %s" % PAT_UUID)
		statuscode = response.status_code
		print ("* STATUS CODE            = %s" % statuscode)
		IncrementTestResultsTotals("patient "+str(endpoint), statuscode)
		#quit()

#=========================================================================================

def getUtil(endpoint):
	print ("\n----------------------------------------------------------------------------")
	print (">>> DataOrchestrator - UTIL %s ENDPOINT <<<" % str(endpoint).upper())
	print ("----------------------------------------------------------------------------")
	print ("* UTIL URL 1             = %s" % UTIL_URL)
	statuscode = 500
	# repeat until successful login is reached
	#while statuscode != 200:
  	url = UTIL_URL+'/'+str(endpoint)
  	referer = UTIL_URL+'/'+str(endpoint) 	
  	print ("* UTIL URL 2             = %s" % url)			
  	DATA =    {'Authorization': 'Apixio ' + I_TOKEN} 
  	HEADERS = {'Authorization': 'Apixio ' + I_TOKEN}
  	response = requests.get(url, data=DATA, headers=HEADERS) 
	print ("* USERNAME               = %s" % USERNAME)
	print ("* PASSWORD               = %s" % PASSWORD)
	print ("* EXTERNAL TOKEN         = %s" % E_TOKEN)
	print ("* INTERNAL TOKEN         = %s" % I_TOKEN)
	#print ("* PATIENT UUID           = %s" % PAT_UUID)
	statuscode = response.status_code
	print ("* STATUS CODE            = %s" % statuscode)
	IncrementTestResultsTotals("util "+str(endpoint), statuscode)
	#quit()

#=========================================================================================	
	
def getDocument(endpoint):
	print ("\n----------------------------------------------------------------------------")
	print (">>> DataOrchestrator - DOCUMENT %s ENDPOINT <<<" % str(endpoint).upper())
	print ("----------------------------------------------------------------------------")
	print ("* DOCUMENT URL 1         = %s" % DOCUMENT_URL)
	for i in range(1, 6):
		var_name=PREFIX+"DOC_UUID_"+str(i)
		value=globals()[var_name]	
		statuscode = 500
		# repeat until successful login is reached
		#while statuscode != 200:
  		url = DOCUMENT_URL+'/'+value+'/'+str(endpoint)
  		referer = DOCUMENT_URL+'/'+value+'/'+str(endpoint) 	
  		print ("* DOCUMENT URL 2         = %s" % url)			
  		DATA =    {'Authorization': 'Apixio ' + I_TOKEN} 
  		HEADERS = {'Authorization': 'Apixio ' + I_TOKEN}
  		response = requests.get(url, data=DATA, headers=HEADERS) 
		print ("* USERNAME               = %s" % USERNAME)
		print ("* PASSWORD               = %s" % PASSWORD)
		print ("* EXTERNAL TOKEN         = %s" % E_TOKEN)
		print ("* INTERNAL TOKEN         = %s" % I_TOKEN)
		print ("* DOCUMENT UUID          = %s" % value)
		statuscode = response.status_code
		print ("* STATUS CODE            = %s" % statuscode)
		IncrementTestResultsTotals("document "+str(endpoint), statuscode)
		#quit()	

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
os.system('clear')

print ("\n\nStarting Data Orchestrator Sanity Test...\n")

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

checkEnvironmentandReceivers()

writeReportHeader()

PrintGlobalParamaterSettings()

obtainAuthorizationGetToken()
writeReportDetails("obtain internal token")

# Patient related DataOrchestrator API endpint testing
getPatient("demographics")
writeReportDetails("patient demographics")
getPatient("externalIds")
writeReportDetails("patient externalIds")
getPatient("apo")
writeReportDetails("patient apo")

# Util related DataOrchestrator API endpoint testing
getUtil("healthcheck")
writeReportDetails("util healthcheck")
getUtil("version")
writeReportDetails("util version")

# Document related DataOrchestrator API endpoint testing
getDocument("text")
writeReportDetails("document text")
getDocument("metadata")
writeReportDetails("document metadata")
getDocument("file")
writeReportDetails("document file")
getDocument("textContent")
writeReportDetails("document textContent")
getDocument("simpleContent")
writeReportDetails("document simpleContent")
getDocument("rawContent")
writeReportDetails("document rawContent")
getDocument("extractedContent")
writeReportDetails("document extractedContent")
getDocument("apo")
writeReportDetails("document apo")

writeReportFooter()

archiveReport()

emailReport()	
	
print ("====================== End of DataOrchestrator Sanity Test ======================")
print ("=================================================================================")
#=========================================================================================