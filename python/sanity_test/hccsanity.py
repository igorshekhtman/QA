####################################################################################################
#
# PROGRAM: grinder.py
# AUTHOR:  Alex Beyk abeyk@apixio.com
# DATE:    2014.10.16 Initial Version
# DATE:    2014.10.27 Updated Org ID to Patient Org ID
# DATE:    2014.11.21 Updated patient_org_id and document_load_time
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: 2014.10.20
# SPECIFICS: Added IncrementTestResultsTotals()function to print out retried, failed and succeeded totals
#
# PURPOSE:
#          This program should be executed via "The Grinder" and is meant for testing HCC functionality:
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
#          * Assumes a Grinder environment is available
#          * For further details, see http://grinder.sourceforge.net
#
# USAGE:
#          * Ensure Grinder is configured to execute grinder.py (this program)
#          * Set the global variables, see below
#          * Run grinder.py (this program)
#          * Results will be printed on both the Grinder Agent and in Grinder Console log files
#
####################################################################################################
#
# REVISION: 1.0.1
#
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
#
# DATE: 23-Oct-2014
#
# SPECIFICS: Introduced HCCConfig.csv file, which now contains all GLOBAL variables and their
#            initial values.  Test script read GLOBAL variable values in as a first step. There
#            are two GLOBAL variables that need to be updated prior to script execution:
#            CSV_CONFIG_FILE_PATH = "/Users/ishekhtman/Documents/grinder/grinder-3.11/examples/"
#            CSV_CONFIG_FILE_NAME = "HCCConfig.csv"
#            As suggested, they specify location and name of the HCCConfig.csv file
#
####################################################################################################
#
# REVISION: 1.0.2
#
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
#
# DATE: 25-Nov-2014
#
# SPECIFICS: Introduced RANDOM_OPPS_ACTION=1 or 0 to allow random coder response to either View
#            Accept Reject or Skip an Opportunity.  It is defined in HCCConfig.csv file.  Possible
#            values are 0 for specific and 1 for random
#
####################################################################################################
#
# REVISION: 1.0.3
#
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
#
# DATE: 01-Dec-2014
#
# SPECIFICS: Introduced VIEW_HISTORY_PAGINATION, VIEW_HISTORY_SEARCH, VIEW_HISTORY_FILTER,
#            VIEW_HISTORY_PAGES_MAX, QA_REPORT_PAGINATION, QA_REPORT_SEARCH, QA_REPORT_FILTER,
#            QA_REPORT_PAGES_MAX global variables, allowing configuring and testing pagination,
#            search and filtering of both View History and QA Reports. All global variables are
#            initialized within HCCConfig.csv configuration file.
#            Introduced VOO_W, VAO_W, VRO_W and VSO_W global variables related to setting specific
#            weights to random function algorithm, used in selecting specific coder action. These
#            are pre-defined in HCCConfig.csv configuration file.
#
####################################################################################################

# LIBRARIES ########################################################################################

#import urllib2
import requests
import SimpleHTTPServer
import SocketServer
import simplejson
import time
import datetime
import csv
import operator
import random
import re
import sys, os
import json

# GLOBAL VARIABLES #######################################################################

CSV_CONFIG_FILE_PATH = "/mnt/automation/hcc/"
CSV_CONFIG_FILE_NAME = "config.csv"
VERSION = "1.0.3"

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
  	print ("Version of the HCCConfig.csv file (%s) does not match version of the grinder.hcc.tests.py script (%s)" % (REVISION, VERSION))
  	print ("============================================================================================================")
  	sys.exit(1)
  else:
  	print ("==============================================================================")
  	print ("HCCConfig.csv VERSION:               %s" % REVISION)
  	print ("grinder.hcc.test.py VERSION:         %s" % VERSION)
  	print ("==============================================================================")
  return result
##########################################################################################

ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
forbidden = 403
notfound = 404
intserveror = 500
servunavail = 503

FAILED = SUCCEEDED = RETRIED = 0
VOO = VAO = VRO = VSO = 0

# MAIN FUNCTIONS ####################################################################################################
 
def logInToHCC(): 
  global TOKEN, SESSID, DATA, HEADERS
  response = requests.get(URL+'/')
  print "* Connect to host    = "+str(response.status_code)
  url = referer = URL+'/account/login/?next=/'
  response = requests.get(url)
  print "* Login page         = "+str(response.status_code)
  TOKEN = response.cookies["csrftoken"]
  SESSID = response.cookies["sessionid"]
  DATA =    {'csrfmiddlewaretoken': TOKEN, 'username': USERNAME, 'password': PASSWORD } 
  HEADERS = {'Connection': 'keep-alive', 'Content-Length': '115', \
			'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
			'Referer': referer}			
  response = requests.post(url, data=DATA, headers=HEADERS) 
  print "* Log in user        = "+str(response.status_code)
  
  
def startCoding():
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION
  global VOO, VAO, VRO, VSO
  print("-------------------------------------------------------------------------------")
  if RANDOM_OPPS_ACTION == "1":
    CODE_OPPS_ACTION = str(random.randint(0,3))
    action = "Random Accept/Reject/Skip Doc"    
  elif CODE_OPPS_ACTION == "0": # Do NOT Accept or Reject Doc
    action = "Do NOT Accept or Reject Doc"
  elif CODE_OPPS_ACTION == "1": # Accept Doc
    action = "Accept Docs"
  elif CODE_OPPS_ACTION == "2": # Reject Doc
    action = "Reject Docs"
  elif CODE_OPPS_ACTION == "3": # Skip Opp
    action = "Skip Opp"
  else:
    action = "Unknown"
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* CODER ACTION       = %s\n* MAX PATIENT OPP(S) = %s" % (URL, USERNAME, PASSWORD, action, CODE_OPPS_MAX))
  print("-------------------------------------------------------------------------------")
  coding_opp_current = 1
  for coding_opp_current in range(1, (int(CODE_OPPS_MAX)+1)):
    testCode = 10 + (1 * coding_opp_current)
    response = requests.get(URL + "/api/coding-opportunity/", data=DATA, headers=HEADERS)
    print "* GET CODNG OPP    = %s" % response.status_code
    opportunity = response.json()
    patient_details = response.text
    IncrementTestResultsTotals(response.status_code)
    if opportunity == None:
      print("ERROR : Login Failed or No More Opportunities For This Coder")
      return 1
    patient_uuid = ""
    patient_uuid = opportunity.get("patient_uuid")
    #print "patient uuid: %s" % patient_uuid
    scorables = opportunity.get("scorables")
    #print "scorables: %s" % scorables
    print("-------------------------------------------------------------------------------")
    print("PATIENT OPP %d OF %d" % (coding_opp_current, int(CODE_OPPS_MAX)))
    test_counter = 0
    doc_no_current = 0
    doc_no_max = len(scorables)
    for scorable in scorables:
      patient_org_id  = ""
      finding_id      = ""
      document_uuid   = ""
      document_title  = ""
      date_of_service = ""
      doc_no_current = doc_no_current + 1
      patient_org_id = scorable.get("patient_org_id")
      finding_id = scorable.get("id")
      document_uuid = scorable.get("document_uuid")
      document_title = scorable.get("document_title")
      date_of_service = scorable.get("date_of_service")
      print("PATIENT DOC %d OF %d\n* PATIENT ORG ID   = %s\n* PATIENT UUID     = %s\n* FINDING ID       = %s\n* DOC UUID         = %s\n* DOC TITLE        = %s\n* DOC DATE         = %s" % (doc_no_current, doc_no_max, patient_org_id, patient_uuid, finding_id, document_uuid, document_title, date_of_service))
      if patient_uuid    == "":
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
      response = requests.get(URL + "/api/document/" + document_uuid, data=DATA, headers=HEADERS)
      print "* GET SCRBLE DOC   = %s" % response.status_code
      
      
      IncrementTestResultsTotals(response.status_code)
      test_counter += 1
      if RANDOM_OPPS_ACTION == "1":
      	CODE_OPPS_ACTION = WeightedRandomCodingAction()
      act_on_doc(opportunity, scorable, testCode + test_counter, doc_no_current, doc_no_max)
  return 0

def historyReport():
  global VIEW_HISTORY_PAGES_MAX
  print("-------------------------------------------------------------------------------")
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* CODER ACTION       = View History Report" % (URL, USERNAME, PASSWORD))
  #thread_context = HTTPPluginControl.getThreadHTTPClientContext()
  #control = HTTPPluginControl.getConnectionDefaults()
  #control.setFollowRedirects(1)
  #result = create_request(Test(1, "Connect to host")).GET(URL + "/")
  #result = create_request(Test(2, "Get login page")).GET(URL + "/account/login/?next=/")
  #login = create_request(Test(3, "Log in user"),[NVPair("Referer", URL + "/account/login/?next=/"),])
  #response = login.POST(URL + "/account/login/?next=/", (NVPair("csrfmiddlewaretoken", get_csrf_token(thread_context)), NVPair("username", USERNAME), NVPair("password", PASSWORD),))
  #IncrementTestResultsTotals(response.status_code)
  view_history_count = 1
  testCode = 10 + (1 * view_history_count)
  
  #response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
  #opportunity = JSONValue.parse(response.getText())
  #patient_details = response.getText()
  
  response = requests.get(URL + "/api/coding-opportunity/", data=DATA, headers=HEADERS)
  print "* GET CODNG OPP      = %s" % response.status_code
  opportunity = response.json()
  patient_details = response.text
  IncrementTestResultsTotals(response.status_code)
  
  if opportunity == None:
    print("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  for view_history_count in range(1, (int(VIEW_HISTORY_MAX)+1)):
    print("-------------------------------------------------------------------------------")
    print("Report %d OF %d" % (view_history_count, int(VIEW_HISTORY_MAX)))  
    now = datetime.datetime.now()    
    report_range = """/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (now.year, now.month, now.day, USERNAME.lower())
    
    #response = create_request(Test(testCode, "View History Report")).GET(URL + report_range)
    response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    
    
    IncrementTestResultsTotals(response.status_code)
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
    		report_range = """/api/report/qa_report?page=%s&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (page, now.year, now.month, now.day, USERNAME.lower())
    		#response = create_request(Test(testCode, "View History Report Pagination")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals(response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = History Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = 200 OK" % page)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else:
      			print("* CODER ACTION     = History Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (page, response))
    		  	    	
    if VIEW_HISTORY_SEARCH == "1":
    	terms = ['2012', '2013', '2014', 'Robert', 'George', 'John', 'Diabetes', 'Diarrhea', 'DM']
    	for term in terms:
    		testCode += 1
    		report_range = """/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s&terms=%s""" % (now.year, now.month, now.day, USERNAME.lower(), term)
    		#response = create_request(Test(testCode, "View History Report Searching")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals(response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = History Report Searching\n* SEARCH TERM      = [%s]\n* HCC RESPONSE     = 200 OK" % term)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else: 
      			print("* CODER ACTION     = History Report Searching\n* SEARCH TERM      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (term, response)) 		
    	
    if VIEW_HISTORY_FILTER == "1":
    	results = ['reject', 'accept', 'all']
    	for result in results:
    		testCode += 1
    		report_range = """/api/report/qa_report?page=1&result=%s&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (result, now.year, now.month, now.day, USERNAME.lower())
    		#response = create_request(Test(testCode, "View History Report Filtering")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals(response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = History Report Filtering\n* FILTER BY        = [%s]\n* HCC RESPONSE     = 200 OK" % result)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else: 
      			print("* CODER ACTION     = History Report Filtering\n* FILTER BY        = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (result, response))
      		
  return 0

def qaReport():
  global QA_REPORT_PAGES_MAX
  global DATA, HEADERS, TOKEN, SESSID
  print("-------------------------------------------------------------------------------")
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* CODER ACTION       = QA Report" % (URL, USERNAME, PASSWORD))
  #thread_context = HTTPPluginControl.getThreadHTTPClientContext()
  #control = HTTPPluginControl.getConnectionDefaults()
  #control.setFollowRedirects(1)
  #result = create_request(Test(1, "Connect to host")).GET(URL + "/")
  #result = create_request(Test(2, "Get login page")).GET(URL + "/account/login/?next=/")
  #login = create_request(Test(3, "Log in user"),[NVPair("Referer", URL + "/account/login/?next=/"),])
  #response = login.POST(URL + "/account/login/?next=/", (NVPair("csrfmiddlewaretoken", get_csrf_token(thread_context)), NVPair("username", USERNAME), NVPair("password", PASSWORD),))
  #IncrementTestResultsTotals(response.status_code)

  qa_report_count = 1
  testCode = 10 + (1 * qa_report_count)
  
  #response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
  #opportunity = JSONValue.parse(response.getText())
  
  response = requests.get(URL + "/api/coding-opportunity/", data=DATA, headers=HEADERS)
  print "* GET CODNG OPP      = %s" % response.status_code
  opportunity = response.json()
  patient_details = response.text
  IncrementTestResultsTotals(response.status_code)
    
  if opportunity == None:
    print("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  patient_details = response.text
  print("-------------------------------------------------------------------------------")
  IncrementTestResultsTotals(response.status_code)
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
  IncrementTestResultsTotals(response.status_code)
  
  
  #print coders
  #print patient_details
  print("-------------------------------------------------------------------------------")
  IncrementTestResultsTotals(response.status_code)
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
    report_range = "/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z" % (now.year, now.month, now.day)
    #response = create_request(Test(testCode, "QA Report")).GET(URL + report_range)
    response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    IncrementTestResultsTotals(response.status_code)
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
    		report_range = "/api/report/qa_report?page=%s&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z" % (page, now.year, now.month, now.day)
    		#response = create_request(Test(testCode, "QA Report")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals(response.status_code)
    		if response.status_code == 200:
      			print("* CODER ACTION     = QA Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = 200 OK" % page)
      			print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    		else:
      			print("* CODER ACTION     = QA Report Pagination\n* PAGE NUMBER      = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (page, response))     		    	
    	
    if QA_REPORT_SEARCH == "1":
    	terms = ['2012', '2013', '2014', 'Robert', 'George', 'John', 'Diabetes', 'Diarrhea', 'DM']
    	for term in terms:
    		testCode += 1
    		report_range = """/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&terms=%s""" % (now.year, now.month, now.day, term)
    		#response = create_request(Test(testCode, "QA Report Searching")).GET(URL + report_range)
    		response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    		print("-------------------------------------------------------------------------------")
    		IncrementTestResultsTotals(response.status_code)
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
    			report_range = """/api/report/qa_report?page=1&result=%s&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT07%%3A59%%3A59.999Z&user=%s""" % (result, now.year, now.month, now.day, coder.lower())
    			#response = create_request(Test(testCode, "QA Report Filtering")).GET(URL + report_range)
    			response = requests.get(URL + report_range, data=DATA, headers=HEADERS)
    			print("-------------------------------------------------------------------------------")
    			IncrementTestResultsTotals(response.status_code)
    			if response.status_code == 200:
      				print("* CODER ACTION     = QA Report Filtering\n* FILTER BY        = [%s]\n* FILTER BY        = [%s]\n* HCC RESPONSE     = 200 OK" % (result, coder))
      				print("* PAGES, PAYLOAD   = %d, %d KBytes" % pages_payload(response))
    			else: 
      				print("* CODER ACTION     = QA Report Filtering\n* FILTER BY        = [%s]\n* FILTER BY        = [%s]\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % (result, coder, response))
      			    	
  return 0

def logout():
  print("-------------------------------------------------------------------------------")
  testCode = 99
  response = requests.get(URL + "/account/logout")    
  print "* LOGOUT           = "+str(response.status_code)  
  IncrementTestResultsTotals(response.status_code)
  if response.status_code == 200:
    print("* CODER ACTION     = Logout\n* HCC RESPONSE     = 200 OK")
  else:
    print("* CODER ACTION     = Logout\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  return 0

# HELPER FUNCTIONS ####################################################################################################

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

def pages_payload(details):
	report_json = details.json()
    	if report_json is not None:
    		pages = report_json.get("pages")
    		payload = len(details.text)
    	else:
    		pages = 0
    		payload = 0
	return (pages, payload)

def create_request(test, headers=None):
  request = HTTPRequest()
  if headers:
    request.headers = headers
  test.record(request)
  return (request)

def get_csrf_token(thread_context):
  cookies = CookieModule.listAllCookies(thread_context)
  csrftoken = ""
  for cookie in cookies:
    if cookie.getName() == "csrftoken":
      csrftoken = cookie.getValue()
  return (csrftoken)

def IncrementTestResultsTotals(code):
  global FAILED, SUCCEEDED, RETRIED
  if (code == ok) or (code == nocontent):
    SUCCEEDED = SUCCEEDED+1
  #elif code == intserveror:
  #  RETRIED = RETRIED+1
  else:
    FAILED = FAILED+1

def act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max):
  global CODE_OPPS_ACTION
  if CODE_OPPS_ACTION == "0": # Do NOT Accept or Reject Doc
    print("* CODER ACTION     = Do NOT Accept or Reject Doc")
  elif CODE_OPPS_ACTION == "1": # Accept Doc
    finding_id = scorable.get("id")
    print "* FINDING ID       = %s" % finding_id
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "accept", \
    		"comment": "Comment by the SanityTest", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"flag_for_review": "true", \
    		"icd9[code_system_name]": opportunity.get("suggested_codes")[0].get("code_system_name"), \
    		"icd9[code]": opportunity.get("suggested_codes")[0].get("code"), \
    		"icd9[display_name]": opportunity.get("suggested_codes")[0].get("display_name")+" SanityTest", \
    		"icd9[code_system]": opportunity.get("suggested_codes")[0].get("code_system"), \
    		"icd9[code_system_version]": opportunity.get("suggested_codes")[0].get("code_system_version"), \
    		"provider[name]": "The SanityTest M.D.", \
    		"provider[id]": "1992754832", \
    		"provider[type]": "Hospital Outpatient Setting", \
    		"payment_year": str(opportunity.get("payment_year")), \
    		"orig_date_of_service": scorable.get("date_of_service"), \
    		"page": "2015", \
    		"opportunity_hash": opportunity.get("hash"), \
    		"rule_hash": opportunity.get("rule_hash"), \
    		"get_id": str(opportunity.get("get_id")), \
    		"patient_uuid": opportunity.get("patient_uuid"), \
    		"patient_org_id": str(scorable.get("patient_org_id")), \
    		"hcc[code]": str(opportunity.get("hcc")), \
    		"hcc[model_run]": opportunity.get("model_run"), \
    		"hcc[model_year]": str(opportunity.get("model_year")), \
    		"hcc[description]": opportunity.get("hcc_description")+" grinder", \
    		"hcc[label_set_version]": opportunity.get("label_set_version"), \
    		"hcc[mapping_version]": str(opportunity.get("model_year")) + " " + opportunity.get("model_run"), \
    		"hcc[code_system]": str(opportunity.get("model_year")) + "PYFinal", \
    		"finding_id": str(finding_id), \
    		"document_uuid": scorable.get("document_uuid"), \
    		"list_position": str(doc_no_current), \
    		"list_length": str(doc_no_max), \
    		"document_date": scorable.get("date_of_service"), \
    		"predicted_code[code_system_name]": "The SanityTest", \
    		"predicted_code[code]": "The SanityTest", \
    		"predicted_code[display_name]": "The SanityTest", \
    		"predicted_code[code_system]": "The SanityTest", \
    		"predicted_code[code_system_version]": "The SanityTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    response = requests.post(URL+ "/api/annotate/" + str(finding_id) + "/", data=DATA, headers=HEADERS)
    
    print "* ANNOTATE FINDING = %s" % response.status_code
    IncrementTestResultsTotals(response.status_code)
    if response.status_code == 200:
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  elif CODE_OPPS_ACTION == "2": # Reject Doc
    finding_id = scorable.get("id")
    #annotation = create_request(Test(testname, "Annotate Finding"))
    #response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    print "* FINDING ID       = %s" % finding_id
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "reject", \
    		"reject_reason": "Additional documentation needed to Accept the document for this HCC", \
    		"comment": "Comment by The SanityTest", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"flag_for_review": "true", \
    		"payment_year": str(opportunity.get("payment_year")), \
    		"orig_date_of_service": scorable.get("date_of_service"), \
    		"opportunity_hash": opportunity.get("hash"), \
    		"rule_hash": opportunity.get("rule_hash"), \
    		"get_id": str(opportunity.get("get_id")), \
    		"patient_uuid": opportunity.get("patient_uuid"), \
    		"patient_org_id": str(scorable.get("patient_org_id")), \
    		"hcc[code]": str(opportunity.get("hcc")), \
    		"hcc[model_run]": opportunity.get("model_run"), \
    		"hcc[model_year]": str(opportunity.get("model_year")), \
    		"hcc[description]": opportunity.get("hcc_description"), \
    		"hcc[label_set_version]": opportunity.get("label_set_version"), \
    		"hcc[mapping_version]": str(opportunity.get("model_year")) + " " + opportunity.get("model_run"), \
    		"hcc[code_system]": str(opportunity.get("model_year")) + "PYFinal", \
    		"finding_id": str(finding_id), \
    		"document_uuid":  scorable.get("document_uuid"), \
    		"list_position": str(doc_no_current), \
    		"list_length": str(doc_no_max), \
    		"document_date": scorable.get("date_of_service"), \
    		"snippets": str(scorable.get("snippets")), \
    		"predicted_code[code_system_name]": "The SanityTest", \
    		"predicted_code[code]": "The SanityTest", \
    		"predicted_code[display_name]": "The SanityTest", \
    		"predicted_code[code_system]": "The SanityTest", \
    		"predicted_code[code_system_version]": "The SanityTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    response = requests.post(URL+ "/api/annotate/" + str(finding_id) + "/", data=DATA, headers=HEADERS)		
    IncrementTestResultsTotals(response.status_code)
    if response.status_code == 200:
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  elif CODE_OPPS_ACTION == "3": # Skip Opp
    finding_id = scorable.get("id")
    #annotation = create_request(Test(testname, "Annotate Finding"))
    #response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    print "* FINDING ID       = %s" % finding_id
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "skipped", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"payment_year": str(opportunity.get("payment_year")), \
    		"orig_date_of_service": scorable.get("date_of_service"), \
    		"opportunity_hash": opportunity.get("hash"), \
    		"rule_hash": opportunity.get("rule_hash"), \
    		"get_id": str(opportunity.get("get_id")), \
    		"patient_uuid": opportunity.get("patient_uuid"), \
    		"hcc[code]": str(opportunity.get("hcc")), \
    		"hcc[model_run]": opportunity.get("model_run"), \
    		"hcc[model_year]": str(opportunity.get("model_year")), \
    		"hcc[description]": opportunity.get("hcc_description") + " (SanityTest)", \
    		"hcc[label_set_version]": opportunity.get("label_set_version"), \
    		"hcc[mapping_version]": str(opportunity.get("model_year")) + " " + opportunity.get("model_run"), \
    		"hcc[code_system]": str(opportunity.get("model_year")) + "PYFinal", \
    		"finding_id": str(finding_id), \
    		"document_uuid": scorable.get("document_uuid"), \
    		"patient_org_id": str(scorable.get("patient_org_id")), \
    		"list_position": str(doc_no_current), \
    		"list_length": str(doc_no_max), \
    		"document_date": scorable.get("date_of_service"), \
    		"snippets": str(scorable.get("snippets")), \
    		"predicted_code[code_system_name]": "The SanityTest", \
    		"predicted_code[code]": "The SanityTest", \
    		"predicted_code[display_name]": "The SanityTest", \
    		"predicted_code[code_system]": "The SanityTest", \
    		"predicted_code[code_system_version]": "The SanityTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    response = requests.post(URL+ "/api/annotate/" + str(finding_id) + "/", data=DATA, headers=HEADERS)		
    IncrementTestResultsTotals(response.status_code)
    if response.status_code == 200:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  else:
    print("* CODER ACTION     = Unknown\n")
  return 0

# MAIN FUNCTION CALLER ####################################################################################################

os.system('clear')

readConfigurationFile(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME)

logInToHCC()

startCoding()

historyReport()

qaReport()

logout()


#print("========================== START HCC SANITY TEST ============================")
#if CODE_OPPS    == "1":
#	startCoding()
#if VIEW_HISTORY == "1":
#	historyReport()
#if QA_REPORT    == "1":
#	qaReport()
#if LOGOUT       == "1":
#	logout()
print("=============================================================================")
print("Test execution results summary:")
print("=============================================================================")
print("* VIEWED ONLY OPPS:       %s" % VOO)
print("* VIEWED + ACCEPTED OPPS: %s" % VAO)
print("* VIEWED + REJECTED OPPS: %s" % VRO)
print("* VIEWED + SKIPPED OPPS:  %s" % VSO)
print("* TOTAL OPPS PROCESSED:   %s" % (VOO+VAO+VRO+VSO))
print("-----------------------------------------------------------------------------")
print("* RETRIED:   %s" % RETRIED)
print("* FAILED:    %s" % FAILED)
print("* SUCCEEDED: %s" % SUCCEEDED)
print("* TOTAL:     %s" % (RETRIED+FAILED+SUCCEEDED))
print("=============================================================================")
print("============================== END SANITY TEST ==============================")
print("=============================================================================")
print("\n")