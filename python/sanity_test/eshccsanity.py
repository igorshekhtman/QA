####################################################################################################
#
# PROGRAM: eshccsanity.py (Elastic Search version of the HCC Sanity Test)
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    2015.08.13 Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: 2015.08.13
# SPECIFICS: Added IncrementTestResultsTotals()function to print out retried, failed and succeeded totals
#
# PURPOSE:
#          This program should be executed via Python 2.7 and is meant for testing HCC functionality:
#          * Login
#          * View   Docs + Opportunities
#          * Accept Docs + Opportunities
#          * Reject Docs + Opportunities
#          * Skip   Docs + Opportunities
#          * View History Report
#          * Paginate History Report
#          * Search History Report
#          * Filter History Report
#          * View QA Report
#          * Paginate History Report
#          * Search QA Report
#          * Dual Filter History Report
#          * Logout
#
# SETUP:
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.7 environment is available
#          * From QA server (ec2-54-219-117-239) /mnt/automation/hcc folder enter "python2.6 hccsanity.py"
#		   * note: hccsanity.csv configuration file must coexist in same folder as hccsanity.py
#
# USAGE:
#          * Set the global variables (CSV_CONFIG_FILE_PATH and CSV_CONFIG_FILE_NAME), see below
#          * Configure global parameters in hccsanity.csv located in the same folder
#          * Results will be printed on Console screen as well as mailed via QA report
#
####################################################################################################
#
# LIBRARIES ########################################################################################

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

# GLOBAL VARIABLES #######################################################################

CSV_CONFIG_FILE_PATH = "/mnt/automation/python/sanity_test/"
CSV_CONFIG_FILE_NAME = "eshccsanity.csv"
VERSION = "1.0.3"
# Email reports to eng@apixio.com and archive report html file:
# 0 - False
# 1 - True
DEBUG_MODE=bool(0)
REPORT = ""
REPORT_EMAIL = ""
REPORT_TYPE = "ES HCC Sanity Test"
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
			"coding opportunity check":"1", \
			"coding scorable document check":"2", \
			"coding view only":"3", \
			"coding view and accept":"4", \
			"coding view and reject":"5", \
			"coding view and skip":"6", \
			"history report opportunity check":"7", \
			"history report pagination":"8", \
			"history report searching":"9", \
			"history report filtering":"10", \
			"qa report coder list check":"11", \
			"qa report opportunity check":"12", \
			"qa report pagination":"13", \
			"qa report searching":"14", \
			"qa report filtering":"15", \
			"logout":"16", \
			"document page retrieval":"17" \
			}
FAILED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
SUCCEEDED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
RETRIED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
for i in range (0, 18):
	FAILED_TOT[i] = 0
	SUCCEEDED_TOT[i] = 0
	RETRIED_TOT[i] = 0


##########################################################################################
################### Global variable declaration, initialization ##########################
##########################################################################################
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
  
def readConfigurationFile(filename):
  global MAX_NUM_RETRIES

  result={ }
  csvfile = open(filename, 'rb')
  reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
  for row in reader:
    if (str(row[0])[0:1] <> '#') and (str(row[0])[0:1] <> ' '):
      result[row[0]] = row[1]
  globals().update(result)
  MAX_NUM_RETRIES = int(result["MAX_NUM_RETRIES"])
  if REVISION <> VERSION:
  	print ("============================================================================================================")
  	print ("Version of the hccsanity.csv file (%s) does not match version of the hccsanity.py script (%s)" % (REVISION, VERSION))
  	print ("============================================================================================================")
  	sys.exit(1)
  else:
  	print ("==============================================================================")
  	print ("hccsanity.csv VERSION:        %s" % REVISION)
  	print ("hccsanity.py VERSION:         %s" % VERSION)
  	print ("==============================================================================")
  return result
##########################################################################################

ok           = 200
created      = 201
accepted     = 202
nocontent    = 204
movedperm    = 301
redirect     = 302
unauthorized = 401
forbidden    = 403
notfound     = 404
intserveror  = 500
servunavail  = 503

FAILED = SUCCEEDED = RETRIED = 0
VOO = VAO = VRO = VSO = 0

# MAIN FUNCTIONS ####################################################################################################
 
def logInToHCC(): 
  global TOKEN, SESSID, DATA, HEADERS, COOKIES
  response = requests.get(URL+'/')
  print "* Host Url           = "+str(URL+'/')
  print "* Connect to host    = "+str(response.status_code)
  url = referer = URL+'/account/login/?next=/'
  response = requests.get(url)
  IncrementTestResultsTotals("login", response.status_code)
  print "* Host Url           = "+str(url)
  print "* Login page         = "+str(response.status_code)
  
  
  #print response.cookies
  
  TOKEN = response.cookies["csrftoken"]
  SESSID = response.cookies["sessionid"]
  COOKIES = dict(csrftoken=''+TOKEN+'')
  DATA =    {'csrfmiddlewaretoken': TOKEN, 'username': USERNAME, 'password': PASSWORD } 
  HEADERS = {'Connection': 'keep-alive', 'Content-Length': '115', \
			'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
			'Referer': referer}	
 		 
  response = requests.post(url, data=DATA, headers=HEADERS) 
  IncrementTestResultsTotals("login", response.status_code)
  print ("* Host Url           = %s" % (url))
  print ("* Log in user        = %s" % (response.status_code))
  print ("* Token              = %s" % TOKEN)
  print ("* Session ID         = %s" % SESSID)
  print ("* Cookies            = %s" % COOKIES)
  #quit()

#----------------------------------------------------------------------------------------------------------------------  
  
def startCoding():
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION, CODING_OPP_CURRENT
  global VOO, VAO, VRO, VSO, PATIENT_ORG_NAME
  global FAILED, SUCCEEDED, RETRIED, MODULES, MAX_NUM_RETRIES
  global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT


  url = URL+"/api/next-work-item/"
  referer = URL+"/"
  host = URL[8:]
   
  DATA = {}
	
  HEADERS = { \
  		'Accept': 'application/json, text/plain, */*', \
		'Accept-Encoding': 'gzip, deflate, sdch', \
		'Accept-Language': 'en-US,en;q=0.8', \
		'Connection': 'keep-alive', \
		'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
		'Host': host, \
		'Referer': referer \
		}	

  testCode = 10 + (1 * CODING_OPP_CURRENT)

  response = requests.get(url, cookies=COOKIES, data=DATA, headers=HEADERS)
  if response.status_code == unauthorized:
    if RETRIED < MAX_NUM_RETRIES:
      FAILED += 1
      RETRIED += 1
      logInToHCC()
      chooseCodingAction()
      startCoding()
    else:
      print ("Number of retries %s exceeded limit of %s, exiting now ..." % (RETRIED, MAX_NUM_RETRIES)) 
      quit()

  IncrementTestResultsTotals("coding opportunity check", response.status_code)
  print "* GET CODNG OPP    = %s" % response.status_code
  opportunity = response.json()
  patient_details = response.text
    
  if opportunity == None:
    print("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  status = opportunity.get("status")
  possiblecodes = opportunity.get("possibleCodes") 
  numpossiblecodes = len(possiblecodes) 
  code = opportunity.get("code") 
  patient = opportunity.get("patient") 
  findings = opportunity.get("findings")
  patient_id = opportunity.get("patientId")
  project = opportunity.get("project")
  finding_ids = opportunity.get("finding_ids")
  user = opportunity.get("user")
  organization = opportunity.get("organization")
  transaction_id = opportunity.get("transactionId")
  print("-------------------------------------------------------------------------------")
  print("PATIENT OPP %d OF %d" % (CODING_OPP_CURRENT, int(CODE_OPPS_MAX)))
  test_counter = 0
  doc_no_current = 0
  doc_no_max = len(findings)
  
  for finding in findings:
    finding_id = finding_ids[doc_no_current]
    doc_no_current = doc_no_current + 1
    patient_org_id = finding.get("patient_org_id")  
    document_uuid = finding.get("sourceId")
    document_title = finding.get("document_title")
    date_of_service = finding.get("doc_date")
    mime_type = finding.get("mimeType")
    if mime_type == None:
    	mime_type = "text/plain"
    #if CODING_OPP_CURRENT == 1:
    #	PATIENT_ORG_NAME = getOrgName(patient_org_id)
      
    print("PATIENT DOC %d OF %d"    % (doc_no_current, doc_no_max))
    print("* STATUS           = %s" % (status))
    print("* PATIENT ORG      = %s" % (patient_org_id))
    print("* PATIENT ID       = %s" % (patient_id))
    print("* FINDING ID       = %s" % (finding_id))
    print("* AVAILABLE CODES  = %s" % (numpossiblecodes))
    print("* PROJECT ID       = %s" % (project))
    print("* DOC UUID         = %s" % (document_uuid))
    print("* DOC TITLE        = %s" % (document_title))
    print("* DOC DATE         = %s" % (date_of_service))
    print("* DOC TYPE         = %s" % (mime_type))
    if patient_id    == "":
      print("WARNING : PATIENT UUID is Empty")
    if patient_org_id  == "":
      print("WARNING : ORG ID is Empty")
    if finding_id      == "":
      print("WARNING : FINDING ID is Empty")
    if document_uuid   == "":
      print("WARNING : DOC UUID is Empty")
    if document_title  == "":
      print("WARNING : DOC TITLE is Empty")
    if date_of_service == "":
      print("WARNING : DOC DATE is Empty")
    test_counter = test_counter + 1
      
    response = requests.get(URL + "/api/document-text/" + document_uuid, cookies=COOKIES, data=DATA, headers=HEADERS)
    IncrementTestResultsTotals("coding scorable document check", response.status_code)
    print "* GET SCORABLE DOC = %s" % response.status_code     
    
    totalPages = getDocPageTotal(finding)
    print "* TOTAL # OF PAGES = %s" % totalPages
 
    # looping through each and every available page in a document
    #if mime_type == "application/pdf":
    #  for i in range (0,int(totalPages)):
    #    response = requests.get(URL + "/document_page/" + document_uuid + "/" + str(i), cookies=COOKIES, data=DATA, headers=HEADERS)
    #    if response.status_code != ok:
   # 	  print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
   # 	  print ("!!!! Failure occured trying to retrieve document page with status code = %s !!!!!" % response.status_code)
   # 	  print ("!!!! Test is being terminated !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
   # 	  print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
   # 	  #quit()
   #     #IncrementTestResultsTotals("document page retrieval", response.status_code)
   #     print "* DOCUMENT PAGE %d  = %s" % (i+1, response.status_code)

    test_counter += 1

    if RANDOM_OPPS_ACTION == "1":
   	  CODE_OPPS_ACTION = WeightedRandomCodingAction()
    act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max)
  return 0

#---------------------------------------------------------------------------------------------------------------------- 

def historyReport():
  global VIEW_HISTORY_PAGES_MAX
  print("-------------------------------------------------------------------------------")
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* CODER ACTION       = View History Report" % (URL, USERNAME, PASSWORD))
  view_history_count = 1
  testCode = 10 + (1 * view_history_count)
  
  #response = requests.get(URL + "/api/coding-opportunity/", data=DATA, headers=HEADERS)
  response = requests.get(URL + "/api/next-work-item/", data=DATA, headers=HEADERS)
  print "* GET CODNG OPP      = %s" % response.status_code
  opportunity = response.json()
  patient_details = response.text
  IncrementTestResultsTotals("history report opportunity check", response.status_code)
  
  if opportunity == None:
    print("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  for view_history_count in range(1, (int(VIEW_HISTORY_MAX)+1)):
    print("-------------------------------------------------------------------------------")
    print("Report %d OF %d" % (view_history_count, int(VIEW_HISTORY_MAX)))  
    
    #https://hccstage2.apixio.com/api/report/qa_report?end=2015-06-11T06:59:59.999Z&page=1&result=all&start=2015-06-03T07:00:00.000Z&terms=&user=sanitytest001@apixio.net
    
    
    
    now = datetime.datetime.now()    

    report_range = """/api/report/qa_report?end=%d-%d-%dT06:59:59.999Z&page=1&result=all&start=2015-06-03T07%%3A00%%3A00.000Z&terms=&user=%s""" % (now.year, now.month, now.day, USERNAME.lower())
    
    
    #response = create_request(Test(testCode, "View History Report")).GET(URL + report_range)
    response = requests.get(URL + report_range, data=DATA, headers=HEADERS)    
    IncrementTestResultsTotals("history report pagination", response.status_code)
    if response.status_code == 200:
      print("* CODER ACTION     = View History Report\n* PAGE NUMBER      = [1]\n* HCC RESPONSE     = 200 OK")
      print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
      pages, payload = pages_payload(response)
    else:
      print("* CODER ACTION     = View History Report\n* PAGE NUMBER      = [1]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)

    if VIEW_HISTORY_PAGINATION == "1":
    	if VIEW_HISTORY_PAGES_MAX == "0":
    		VIEW_HISTORY_PAGES_MAX = pages
    	for page in range (2, int(VIEW_HISTORY_PAGES_MAX)+1):
    		testCode += 1
    		report_range = """/api/report/qa_report?page=%s&result=all&start=start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (page, now.year, now.month, now.day, USERNAME.lower())
    		#response = create_request(Test(testCode, "View History Report Pagination")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals("history report pagination", response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = History Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = 200 OK" % page)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else:
      			print("* CODER ACTION     = History Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (page, response))
    		  	    	
    if VIEW_HISTORY_SEARCH == "1":
    	terms = ['2012', '2013', '2014', 'Robert', 'George', 'John', 'Diabetes', 'Diarrhea', 'DM']
    	for term in terms:
    		testCode += 1
    		report_range = """/api/report/qa_report?page=1&result=all&start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s&terms=%s""" % (now.year, now.month, now.day, USERNAME.lower(), term)
    		#response = create_request(Test(testCode, "View History Report Searching")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals("history report searching", response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = History Report Searching\n* SEARCH TERM      = [%s]\n* HCC RESPONSE     = 200 OK" % term)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else: 
      			print("* CODER ACTION     = History Report Searching\n* SEARCH TERM      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (term, response)) 		
    	
    if VIEW_HISTORY_FILTER == "1":
    	results = ['reject', 'accept', 'all']
    	for result in results:
    		testCode += 1
    		report_range = """/api/report/qa_report?page=1&result=%s&start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (result, now.year, now.month, now.day, USERNAME.lower())
    		#response = create_request(Test(testCode, "View History Report Filtering")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals("history report filtering", response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = History Report Filtering\n* FILTER BY        = [%s]\n* HCC RESPONSE     = 200 OK" % result)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else: 
      			print("* CODER ACTION     = History Report Filtering\n* FILTER BY        = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (result, response))
      		
  return 0

#---------------------------------------------------------------------------------------------------------------------- 

def qaReport():
  global QA_REPORT_PAGES_MAX
  global DATA, HEADERS, TOKEN, SESSID
  print("-------------------------------------------------------------------------------")
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* CODER ACTION       = QA Report" % (URL, USERNAME, PASSWORD))

  qa_report_count = 1
  testCode = 10 + (1 * qa_report_count)
  
  #response = requests.get(URL + "/api/coding-opportunity/", data=DATA, headers=HEADERS)
  response = requests.get(URL + "/api/next-work-item/", data=DATA, headers=HEADERS)
  print "* GET CODNG OPP      = %s" % response.status_code
  opportunity = response.json()
  patient_details = response.text
  IncrementTestResultsTotals("qa report opportunity check", response.status_code)
    
  if opportunity == None:
    print("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  patient_details = response.text
  print("-------------------------------------------------------------------------------")
  if response.status_code == 200:
    print("* CODER ACTION     = Get coding opportunity")
    print("* HCC RESPONSE     = 200 OK")
    print("* MODEL YEAR       = %s" % opportunity.get("model_year"))
    print("* HCC DESCR        = %s" % opportunity.get("hcc_description"))
    print("* PAYMENT YEAR     = %s" % opportunity.get("payment_year"))
    print("* PAYMENT ID       = %s" % opportunity.get("patient_id"))
    print("* HCC              = %s" % opportunity.get("hcc"))
    print("* GET ID           = %s" % opportunity.get("get_id"))
    print("* LABEL VERSION    = %s" % opportunity.get("label_set_version"))
    print("* PATIENT UUID     = %s" % opportunity.get("patient_uuid"))
    print("* MODEL RUN        = %s" % opportunity.get("model_run"))
  else: 
    print("* CODER ACTION     = Get coding opportunity\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]\n[%s]" % (response.status_code, opportunity.get("message")))
  
  testCode = testCode + 1
  response = requests.get(URL + "/api/report/orgCoders/", data=DATA, headers=HEADERS)
  print "* GET CODERS LIST  = %s" % response.status_code
  coders = response.json()
  patient_details = response.text
  IncrementTestResultsTotals("qa report coder list check", response.status_code)
  
  
  print("-------------------------------------------------------------------------------")
  IncrementTestResultsTotals("qa report pagination", response.status_code)
  if response.status_code == 200:
    print("* CODER ACTION     = Get orgCoders list")
    print("* HCC RESPONSE     = 200 OK")
    i = 0
    for coder in coders:
      i = i + 1
      print ("* CODER-%d          = %s" % (i, coder))      
  else: 
    print("* CODER ACTION     = Get orgCoders list\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]\n[%s]" % (response.status_code, coders.get("message")))
  #quit()    
    
    
  for qa_report_count in range(1, (int(QA_REPORT_MAX)+1)):
    print("-------------------------------------------------------------------------------")
    print("Report %d OF %d" % (qa_report_count, int(QA_REPORT_MAX)))
    now = datetime.datetime.now()
    report_range = "/api/report/qa_report?page=1&result=all&start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z" % (now.year, now.month, now.day)
    #response = create_request(Test(testCode, "QA Report")).GET(URL + report_range)
    response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    IncrementTestResultsTotals("qa report pagination", response.status_code)
    if response.status_code == 200:
      print("* CODER ACTION     = QA Report\n* PAGE NUMBER      = [1]\n* HCC RESPONSE     = 200 OK")
      print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
      pages, payload = pages_payload(response) 
    else:
      print("* CODER ACTION     = QA Report\n* PAGE NUMBER      = [1]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
    
    if QA_REPORT_PAGINATION == "1":
    	if QA_REPORT_PAGES_MAX == "0":
    		QA_REPORT_PAGES_MAX = pages
    	for page in range (2, int(QA_REPORT_PAGES_MAX)+1):
    		testCode += 1
    		report_range = "/api/report/qa_report?page=%s&result=all&start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z" % (page, now.year, now.month, now.day)
    		#response = create_request(Test(testCode, "QA Report")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals("qa report pagination", response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = QA Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = 200 OK" % page)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else:
      			print("* CODER ACTION     = QA Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (page, response))     		    	
    	
    if QA_REPORT_SEARCH == "1":
    	terms = ['2012', '2013', '2014', 'Robert', 'George', 'John', 'Diabetes', 'Diarrhea', 'DM']
    	for term in terms:
    		testCode += 1
    		report_range = """/api/report/qa_report?page=1&result=all&start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&terms=%s""" % (now.year, now.month, now.day, term)
    		#response = create_request(Test(testCode, "QA Report Searching")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals("qa report searching", response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = QA Report Searching\n* SEARCH TERM      = [%s]\n* HCC RESPONSE     = 200 OK" % term)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else: 
      			print("* CODER ACTION     = QA Report Searching\n* SEARCH TERM      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (term, response))
      		 	
    if QA_REPORT_FILTER == "1":
    	results = ['reject', 'accept', 'all']
    	for coder in coders:
    		for result in results:
    			testCode += 1
    			report_range = """/api/report/qa_report?page=1&result=%s&start=2015-06-03T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (result, now.year, now.month, now.day, coder.lower())
    			#response = create_request(Test(testCode, "QA Report Filtering")).GET(URL + report_range)
    			response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    			print("-------------------------------------------------------------------------------")
    			IncrementTestResultsTotals("qa report filtering", response.status_code)
    			if response.status_code == 200:
      				print("* CODER ACTION     = QA Report Filtering\n* FILTER BY        = [%s]\n* FILTER BY        = [%s]\n* HCC RESPONSE     = 200 OK" % (result, coder))
      				print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    			else: 
      				print("* CODER ACTION     = QA Report Filtering\n* FILTER BY        = [%s]\n* FILTER BY        = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (result, coder, response))
      			    	
  return 0

#---------------------------------------------------------------------------------------------------------------------- 

def logout():
  print("-------------------------------------------------------------------------------")
  testCode = 99
  response = requests.get(URL + "/account/logout")    
  print "* LOGOUT           = "+str(response.status_code)  
  IncrementTestResultsTotals("logout", response.status_code)
  if response.status_code == 200:
    print("* CODER ACTION     = Logout\n* HCC RESPONSE     = 200 OK")
  else:
    print("* CODER ACTION     = Logout\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  return 0

# HELPER FUNCTIONS ####################################################################################################

def getDocPageTotal(scorable):
    elements = json.dumps(scorable.get("elements"))
    elementstr = elements[1:len(elements)-1]  
    strindex = elementstr.find("event.totalPages")
    i = 20
    totalPagesStr = ""
    while elementstr[strindex+i] != ",":
    	totalPagesStr = totalPagesStr+elementstr[strindex+i]
    	i += 1
    totalPages = int(totalPagesStr[:len(totalPagesStr)-1])
    return (totalPages)    	

#=========================================================================================

def getOrgName(id):
    # TODO: hit a customer endpoint on the user account service for the customer org name
    # If orgName is not retrievable for any reason, return orgID
    
    obtainInternalToken(AUTH_EMAIL, AUTH_PASSW, {ok, created}, 0, 0)
    
    idString = str(id)
    blankUUID = 'O_00000000-0000-0000-0000-000000000000'
    url = AUTHHOST+"/customer/"+blankUUID[0:-(len(idString))]+idString
    
    referer = AUTHHOST
    #Content-Type header in your request, or it's incorrect. In your case it must be application/xml
    HEADERS = { 'Content-Type': 'application/json', \
                'Referer': referer, \
                'Authorization': 'Apixio ' + ORG_TOKEN}
    response = requests.get(url, data={}, headers=HEADERS)
    statuscode = response.status_code
    if statuscode == ok:
    	customerOrg = response.json()
    	customerOrgName = customerOrg['name']
    else:
    	customerOrgName = id   
    return (customerOrgName)	

#=========================================================================================

def WeightedRandomCodingAction():
	global VOO_W, VAO_W, VRO_W, VSO_W
	global VOO, VAO, VRO, VSO
	weight = { "0": 0, "1": 0, "2": 0, "3": 0 }
	weight['0'] = int(VOO_W)
	weight['1'] = int(VAO_W)
	weight['2'] = int(VRO_W)
	weight['3'] = int(VSO_W)
	action = random.choice([k for k in weight for dummy in range(weight[k])])
	if action == "0":
		VOO += 1
	elif action == "1":
		VAO += 1
	elif action == "2":
		VRO += 1
	elif action == "3":
		VSO += 1 
	return (action)

#---------------------------------------------------------------------------------------------------------------------- 
	
def printResultsSummary():
	log("=============================================================================")
	log("Test execution results summary:")
	log("=============================================================================")
	log("* VIEWED ONLY OPPS:       %s" % VOO)
	log("* VIEWED + ACCEPTED OPPS: %s" % VAO)
	log("* VIEWED + REJECTED OPPS: %s" % VRO)
	log("* VIEWED + SKIPPED OPPS:  %s" % VSO)
	log("* TOTAL OPPS PROCESSED:   %s" % (VOO+VAO+VRO+VSO))
	log("=============================================================================")
	log("* RETRIED:   %s" % RETRIED)
	log("* FAILED:    %s" % FAILED)
	log("* SUCCEEDED: %s" % SUCCEEDED)
	log("* TOTAL:     %s" % (RETRIED+FAILED+SUCCEEDED))
	log("=============================================================================")
	log("=============================================================================")
	log("=============================================================================")	

#=========================================================================================
	
def checkEnvironmentandReceivers():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	# Arg3 - report recepient #2
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global DOMAIN, URL
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		ENVIRONMENT = "production"
		DOMAIN="hcc.apixio.com"
		URL="https://hcc.apixio.com"
		USERNAME="grinderusr1414166341@apixio.net"
		PASSWORD="apixio.123"
		#USERNAME="apxdemot0500@apixio.net"
		#PASSWORD="apixio.123"
	else:
		ENVIRONMENT = "staging"
		DOMAIN="hcceng.apixio.com"
		URL="https://hcceng.apixio.com"
		USERNAME="mmgenergyes@apixio.net"
		PASSWORD="apixio.123"
	
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
	REPORT = """ """
	REPORT = REPORT + """<h1>Apixio ES HCC Sanity Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """HCC user name: <b>%s</b><br>\n""" % (USERNAME)
	REPORT = REPORT + """HCC app url: <b>%s</b><br>\n""" % (URL)
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
	#print ("Completed writeReportDetails ... \n")
		
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
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/hccsanity/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/hccsanity/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="HCC Sanity "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/hccsanity/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="hcc_sanity_reports_"+ENVIRONMENT.lower()+".txt"
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
		os.chdir("/mnt/automation/python/sanity_test")
		print ("Finished archiving report ... \n")

#=========================================================================================

def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2, REPORT_EMAIL
	
	print ("Emailing report ...\n")
	REPORT_EMAIL = REPORT
	IMAGEFILENAME=str(CURDAY)+".png" 
	message = MIMEMultipart('related')
	message.attach(MIMEText((REPORT_EMAIL), 'html'))
	#with open(IMAGEFILENAME, 'rb') as image_file:
	#	image = MIMEImage(image_file.read())
	#image.add_header('Content-ID', '<picture@example.com>')
	#image.add_header('Content-Disposition', 'inline', filename=IMAGEFILENAME)
	#message.attach(image)

	message['From'] = 'Apixio QA <QA@apixio.com>'
	message['To'] = 'To: Eng <eng@apixio.com>,Ops <ops@apixio.com>'
	message['Subject'] = 'ES HCC %s Sanity Test Report - %s\n\n' % (ENVIRONMENT, START_TIME)
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

def pages_payload(details):
	report_json = details.json()
    	if report_json is not None:
    		pages = report_json.get("pages")
    		payload = len(details.text)
    	else:
    		pages = 0
    		payload = 0
	return (pages, payload)

#=========================================================================================

def create_request(test, headers=None):
  request = HTTPRequest()
  if headers:
    request.headers = headers
  test.record(request)
  return (request)

#=========================================================================================

def get_csrf_token(thread_context):
  cookies = CookieModule.listAllCookies(thread_context)
  csrftoken = ""
  for cookie in cookies:
    if cookie.getName() == "csrftoken":
      csrftoken = cookie.getValue()
  return (csrftoken)

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
    
def log(text):
	global REPORT
	#REPORT = REPORT + text + "<br>"
	print(text)
	return 0    

#=========================================================================================

def act_on_doc(opportunity, finding, finding_id, testname, doc_no_current, doc_no_max):
  global CODE_OPPS_ACTION
  global TOKEN, SESSID, COOKIES

  HEADERS = { \
  		'Accept': 'application/json, text/plain, */*', \
  		'Accept-Encoding': 'gzip, deflate', \
    	'Accept-Language': 'en-US,en;q=0.8', \
  		'Connection': 'keep-alive', \
    	'Content-Type': 'application/json', \
    	'Referer': URL+'/', \
    	'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
    	'X_REQUESTED_WITH': 'XMLHttpRequest', \
    	'X-CSRFToken': TOKEN \
    	}	
    	
 	 	   	    	  
  if CODE_OPPS_ACTION == "0": #=== DO NOT ACCEPT OR REJECT, JUST VIEW ====================
    print("* CODER ACTION     = Do NOT Accept or Reject Doc")
    IncrementTestResultsTotals("coding view only", 200)
  elif CODE_OPPS_ACTION == "1": #=============================== ACCEPT DOC ==============
    #finding_id = finding.get("id")
    print("* CODER ACTION     = Accept Doc")
    print "* FINDING ID       = %s" % finding_id

			
    DATA = { \
			"opportunity": \
			{ \
			"status":opportunity.get("status"), \
			"possibleCodes": opportunity.get("possibleCodes"), \
			"code": \
			{ \
			"labelSetVersion": opportunity.get("code").get("labelSetVersion"), \
			"displayName": opportunity.get("code").get("displayName"), \
			"description": opportunity.get("code").get("description"), \
			"modelPaymentYear": opportunity.get("code").get("modelPaymentYear"), \
			"sweep": opportunity.get("code").get("sweep"), \
			"hcc": opportunity.get("code").get("labelSetVersion") \
			}, \
			"patient": \
			{ \
			"first_name": opportunity.get("patient").get("first_name"), \
			"last_name": opportunity.get("patient").get("last_name"), \
			"middle_name": opportunity.get("patient").get("middle_name"), \
			"dob": opportunity.get("patient").get("dob"), \
			"gender": opportunity.get("patient").get("gender"), \
			"org_id": opportunity.get("patient").get("org_id") \
			}, \
			"findings": \
			[ \
			{ \
			"document_title": finding.get("document_title"), \
			"elements": finding.get("elements"), \
			"sourceType": finding.get("sourceType"), \
			"sourceId": finding.get("sourceId"), \
			"patient_org_id": finding.get("patient_org_id"), \
			"doc_date": finding.get("doc_date"), \
			"pages": finding.get("pages"), \
			"list_position":0, \
			"lifecycle_id":"4af87d4c-9aad-4a55-d238-31bff01390a9", \
			"text":{} \
			} \
			], \
			"patientId": opportunity.get("patientId"), \
			"project": opportunity.get("project"), \
			"finding_ids":opportunity.get("finding_ids"), \
			"user": opportunity.get("user"), \
			"organization": opportunity.get("organization"), \
			"transactionId": opportunity.get("transactionId") \
			}, \
			"annotations": \
			{ \
			finding.get("sourceId"): \
			{ \
			"changed":True, \
			"flaggedForReview":True, \
			"result":"accept", \
			"encounterType": \
			{ \
			"id":"02", \
			"name":"Hospital Inpatient Setting: Other Diagnosis" \
			}, \
			"icd": \
			{ \
			"codeSystemVersion": opportunity.get("possibleCodes")[0].get("codeSystemVersion"), \
			"codeSystemName": opportunity.get("possibleCodes")[0].get("codeSystemName"), \
			"code": opportunity.get("possibleCodes")[0].get("code"), \
			"displayName": opportunity.get("possibleCodes")[0].get("displayName"), \
			"codeSystem":opportunity.get("possibleCodes")[0].get("codeSystem") \
			}, \
			"provider": "Dr. Grinder", \
			"dateOfService": finding.get("doc_date"), \
			"comment": "Grinder Flag for Review" \
			}}}
			
			
    response = requests.post(URL+ "/api/annotate/", cookies=COOKIES, data=json.dumps(DATA), headers=HEADERS)
    if response.status_code == ok:
    	print "* ANNOTATE FINDING = %s" % response.status_code
    else:
    	print("\n")
    	print("-------------------------------------------------------------------------------")
    	print("* ANNOTATE FINDING = %s >>>>>>>>> !!! FAILURE OCCURED !!! <<<<<<<<<<" % response.status_code)
    	print("-------------------------------------------------------------------------------")
    	print("\n")
    	#quit()
    	
    IncrementTestResultsTotals("coding view and accept", response.status_code)
    if response.status_code == ok:
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = %s" % response.status_code)
    else:
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max)
      
  elif CODE_OPPS_ACTION == "2": #================================== REJECT DOC ===========
    #finding_id = finding.get("id")
    print("* CODER ACTION     = Reject Doc")
    print "* FINDING ID       = %s" % finding_id

			
    DATA = { \
			"opportunity": \
			{ \
			"status":opportunity.get("status"), \
			"possibleCodes": opportunity.get("possibleCodes"), \
			"code": \
			{ \
			"labelSetVersion": opportunity.get("code").get("labelSetVersion"), \
			"displayName": opportunity.get("code").get("displayName"), \
			"description": opportunity.get("code").get("description"), \
			"modelPaymentYear": opportunity.get("code").get("modelPaymentYear"), \
			"sweep": opportunity.get("code").get("sweep"), \
			"hcc": opportunity.get("code").get("labelSetVersion") \
			}, \
			"patient": \
			{ \
			"first_name": opportunity.get("patient").get("first_name"), \
			"last_name": opportunity.get("patient").get("last_name"), \
			"middle_name": opportunity.get("patient").get("middle_name"), \
			"dob": opportunity.get("patient").get("dob"), \
			"gender": opportunity.get("patient").get("gender"), \
			"org_id": opportunity.get("patient").get("org_id") \
			}, \
			"findings": \
			[ \
			{ \
			"document_title": finding.get("document_title"), \
			"elements": finding.get("elements"), \
			"sourceType": finding.get("sourceType"), \
			"sourceId": finding.get("sourceId"), \
			"patient_org_id": finding.get("patient_org_id"), \
			"doc_date": finding.get("doc_date"), \
			"pages": finding.get("pages"), \
			"list_position":0, \
			"lifecycle_id":"4af87d4c-9aad-4a55-d238-31bff01390a9", \
			"text":{} \
			} \
			], \
			"patientId": opportunity.get("patientId"), \
			"project": opportunity.get("project"), \
			"finding_ids":opportunity.get("finding_ids"), \
			"user": opportunity.get("user"), \
			"organization": opportunity.get("organization"), \
			"transactionId": opportunity.get("transactionId") \
			}, \
			"annotations": \
			{ \
			finding.get("sourceId"): \
			{ \
			"changed": True, \
			"flaggedForReview": True, \
			"result": "reject", \
			"rejectReason": "This document does not mention this HCC for the patient", \
			"comment": "Grinder Flag for Review Comment" \
			}}}						
			

    response = requests.post(URL+ "/api/annotate/", cookies=COOKIES, data=json.dumps(DATA), headers=HEADERS)
    
    if response.status_code == ok:
    	print "* ANNOTATE FINDING = %s" % response.status_code
    else:
    	print("\n")
    	print("-------------------------------------------------------------------------------")
    	print("* ANNOTATE FINDING = %s >>>>>>>>> !!! FAILURE OCCURED !!! <<<<<<<<<<" % response.status_code)
    	print("-------------------------------------------------------------------------------")
    	print("\n")
    	#quit()
    
    
    IncrementTestResultsTotals("coding view and reject", response.status_code)
    if response.status_code == ok:
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = %s" % response.status_code)
    else:
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max)
  elif CODE_OPPS_ACTION == "3": #=========================== SKIP OPP ====================
    #finding_id = finding.get("id")
    print("* CODER ACTION     = Skip Doc")
    print "* FINDING ID       = %s" % finding_id
    
    DATA = { \
			"opportunity": \
			{ \
			"status":opportunity.get("status"), \
			"possibleCodes": opportunity.get("possibleCodes"), \
			"code": \
			{ \
			"labelSetVersion": opportunity.get("code").get("labelSetVersion"), \
			"displayName": opportunity.get("code").get("displayName"), \
			"description": opportunity.get("code").get("description"), \
			"modelPaymentYear": opportunity.get("code").get("modelPaymentYear"), \
			"sweep": opportunity.get("code").get("sweep"), \
			"hcc": opportunity.get("code").get("labelSetVersion") \
			}, \
			"patient":{ \
			"first_name": opportunity.get("patient").get("first_name"), \
			"last_name": opportunity.get("patient").get("last_name"), \
			"middle_name": opportunity.get("patient").get("middle_name"), \
			"dob": opportunity.get("patient").get("dob"), \
			"gender": opportunity.get("patient").get("gender"), \
			"org_id": opportunity.get("patient").get("org_id") \
			}, \
			"findings": \
			[ \
			{ \
			"document_title": finding.get("document_title"), \
			"elements": finding.get("elements"), \
			"sourceType": finding.get("sourceType"), \
			"sourceId": finding.get("sourceId"), \
			"patient_org_id": finding.get("patient_org_id"), \
			"doc_date": finding.get("doc_date"), \
			"pages": finding.get("pages"), \
			"list_position":0, \
			"lifecycle_id":"4af87d4c-9aad-4a55-d238-31bff01390a9", \
			"text":{} \
			} \
			], \
			"patientId": opportunity.get("patientId"), \
			"project": opportunity.get("project"), \
			"finding_ids":opportunity.get("finding_ids"), \
			"user": opportunity.get("user"), \
			"organization": opportunity.get("organization"), \
			"transactionId": opportunity.get("transactionId") \
			}, \
			"annotations": \
			{ \
			finding.get("sourceId"): \
			{ \
			"changed":True, \
			"flaggedForReview":False, \
			"result":"skipped" \
			}}}			
   

    response = requests.post(URL+ "/api/annotate/", cookies=COOKIES, data=json.dumps(DATA), headers=HEADERS)		
    if response.status_code == ok:
    	print "* ANNOTATE FINDING = %s" % response.status_code
    else:
    	print("\n")
    	print("-------------------------------------------------------------------------------")
    	print("* ANNOTATE FINDING = %s >>>>>>>>> !!! FAILURE OCCURED !!! <<<<<<<<<<" % response.status_code)
    	print("-------------------------------------------------------------------------------")
    	print("\n")
    	#quit()
    IncrementTestResultsTotals("coding view and skip", response.status_code)
    if response.status_code == ok:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = %s" % response.status_code)
    else:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max)
  else:
    print("* CODER ACTION     = Unknown\n")
  return 0


# MAIN FUNCTION CALLER ####################################################################################################

os.system('clear')

readConfigurationFile(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME)

checkEnvironmentandReceivers()

writeReportHeader()	

logInToHCC()

writeReportDetails("login")

for CODING_OPP_CURRENT in range(1, (int(CODE_OPPS_MAX)+1)):
	startCoding()

writeReportDetails("coding opportunity check")
writeReportDetails("coding scorable document check")
writeReportDetails("document page retrieval")
writeReportDetails("coding view only")
writeReportDetails("coding view and accept")
writeReportDetails("coding view and reject")
writeReportDetails("coding view and skip")

if int(VIEW_HISTORY) != 0:
	historyReport()
	writeReportDetails("history report opportunity check")
	writeReportDetails("history report pagination")
	writeReportDetails("history report searching")
	writeReportDetails("history report filtering")

if int(QA_REPORT) != 0:
	qaReport()
	writeReportDetails("qa report coder list check")
	writeReportDetails("qa report opportunity check")
	writeReportDetails("qa report pagination")
	writeReportDetails("qa report searching")
	writeReportDetails("qa report filtering")

logout()

writeReportDetails("logout")

printResultsSummary()

writeReportFooter()

archiveReport()

emailReport()
