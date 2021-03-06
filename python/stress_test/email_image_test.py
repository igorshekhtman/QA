####################################################################################################
#
# PROGRAM: opprouteroptimization.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    2015.01.22 Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: 2014.12.11
# SPECIFICS: Added IncrementTestResultsTotals()function to print out retried, failed and succeeded totals
#
# PURPOSE:
#          This program should be executed via Python 2.7 and is meant for testing HCC functionality:
#          * Login
#          * View   Docs + Opportunities
#          * Accept Docs + Opportunities
#          * Reject Docs + Opportunities
#          * Skip   Docs + Opportunities
#          * Logout
#
# SETUP:
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.7 environment is available
#          * From QA2 server (54.176.225.214) /mnt/automation/hcc folder enter "python2.7 opprouteroptimization.py"
#		   * note: opprouteroptimization.csv configuration file must coexist in same folder as opprouteroptimization.py
#
# USAGE:
#          * Set the global variables (CSV_CONFIG_FILE_PATH and CSV_CONFIG_FILE_NAME), see below
#          * Configure global parameters in opprouteroptimization.csv located in the same folder
#          * Results will be printed on Console screen as well as mailed via QA report
#		   *
#		   * python2.7 opprouteroptimization.py staging ishekhtman@apixio.com ishekhtman@apixio.com
#		   *
#
# SPECIFIC TEST CASE PROVIDED BY RICHARD:
#		- Choose an HCC, such as 15-2013-Final-2014. The HCC should not be overly rare. 
#		- Choose an acceptance probability for that HCC, such as 20%. All other HCCs get probability zero. 
#		- Reset the database to pristine state using reset script. 
#		- Start routing. 
#		- Tally number of serves of the targeted HCC in time buckets of perhaps 100 annotations. 
#		- Throw random number and apply accept or reject according to the probabilities mentioned above for each opportunity. 
#		- Observe that the curve slowly rises until saturating.
#
####################################################################################################
#
# REVISION: 1.0.1
#
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
#
# DATE: 12-Dec-2014
#
# SPECIFICS: Introduced opprouteroptimization.csv file, which now contains all GLOBAL variables and their
#            initial values.  Test script read GLOBAL variable values in as a first step. There
#            are two GLOBAL variables that need to be updated prior to script execution:
#            CSV_CONFIG_FILE_PATH = "/mnt/automation/hcc/"
#            CSV_CONFIG_FILE_NAME = "opprouteroptimization.csv"
#            As suggested, they specify location and name of the hccstress.csv file
#
####################################################################################################
#
# REVISION: 1.0.2
#
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
#
# DATE: 22-Jan-2015
#
# SPECIFICS: Introduced RANDOM_OPPS_ACTION=1 or 0 to allow random coder response to either View
#            Accept Reject or Skip an Opportunity.  It is defined in opprouteroptimization.csv file.  Possible
#            values are 0 for specific and 1 for random
#
####################################################################################################

# LIBRARIES ########################################################################################

import requests
from collections import OrderedDict
import time
import datetime
import csv
import operator
import re
import sys, os
import shutil
import json
from time import gmtime, strftime, localtime
import calendar
import mmap
from sortedcontainers import SortedDict
from pylab import *
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# GLOBAL VARIABLES #######################################################################

CSV_CONFIG_FILE_PATH = "/mnt/automation/python/stress_test/"
CSV_CONFIG_FILE_NAME = "opprouteroptimization.csv"
VERSION = "1.0.3"
# Email reports to eng@apixio.com and archive report html file:
# 0 - False
# 1 - True
DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "Opp Router Optimization Test"
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

PASSED_TBL="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED_TBL="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR_TBL="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp; %s</b></font></td></tr></table>"

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
			"logout":"16" \
			}
FAILED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
SUCCEEDED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
RETRIED_TOT = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
for i in range (0, 17):
	FAILED_TOT[i] = 0
	SUCCEEDED_TOT[i] = 0
	RETRIED_TOT[i] = 0
	
TOTAL_OPPS_ACCEPTED = 0
TOTAL_OPPS_REJECTED = 0
TOTAL_OPPS_SKIPPED = 0
TOTAL_OPPS_SERVED = 0
TOTAL_DOCS_REJECTED = 0
TOTAL_DOCS_ACCEPTED = 0

MODEL_YEAR = {str(key): 0 for key in range(2000, 2040)}
PAYMENT_YEAR = {str(key): 0 for key in range(2000, 2040)}
HCC = {str(key): 0 for key in range(0, 200)}
MODEL_RUN = {'Final': 0, 'Initial': 0}

# Buckets of 100 annotations
#COUNT_OF_SERVED = {str(key): 0 for key in range(100, 1100, 100)}
#PERCENT_OF_SERVED = {str(key): 0 for key in range(100, 1100, 100)}

START = 10
STOP = 110
STEP = 10

COUNT_OF_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
PERCENT_OF_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
PERCENT_OF_SP_HCC_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
#PERCENT_OF_SP_HCC_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}

# This list of codes will overwrite random choice function to accept an opportunity
#HCC_CODES_TO_ACCEPT = {'15', '27', '100'}
#HCC_CODES_TO_ACCEPT = {'27'}
HCC_CODES_TO_ACCEPT = {'131'}
HCC_CODE_TO_ACCEPT = '27'
#HCC_CODE_TO_ACCEPT = '32'
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
  	print ("Version of the hccstress.csv file (%s) does not match version of the hccstress.py script (%s)" % (REVISION, VERSION))
  	print ("============================================================================================================")
  	sys.exit(1)
  else:
  	print ("==============================================================================")
  	print ("hccstress.csv VERSION:        %s" % REVISION)
  	print ("hccstress.py VERSION:         %s" % VERSION)
  	print ("==============================================================================")
  return result
##########################################################################################

ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
unauthorized = 401
forbidden = 403
notfound = 404
intserveror = 500
servunavail = 503

FAILED = SUCCEEDED = RETRIED = 0
VOO = VAO = VRO = VSO = 0

#######################################################################################################################
# MAIN FUNCTIONS ######################################################################################################
#######################################################################################################################
 
def logInToHCC(): 
  global TOKEN, SESSID, DATA, HEADERS
  response = requests.get(URL+'/')
  print "* Connect to host    = "+str(response.status_code)
  if response.status_code == 500:
  	print "* Connection to host = FAILED QA"
  	quit()
  url = referer = URL+'/account/login/?next=/'
  response = requests.get(url)
  IncrementTestResultsTotals("login", response.status_code)
  print "* Login page         = "+str(response.status_code)
  if response.status_code == 500:
  	print "* Connection to host = FAILED QA"
  	logInToHCC()
  TOKEN = response.cookies["csrftoken"]
  SESSID = response.cookies["sessionid"]
  DATA =    {'csrfmiddlewaretoken': TOKEN, 'username': USERNAME, 'password': PASSWORD } 
  HEADERS = {'Connection': 'keep-alive', 'Content-Length': '115', \
			'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
			'Referer': referer}			
  response = requests.post(url, data=DATA, headers=HEADERS) 
  IncrementTestResultsTotals("login", response.status_code)
  print "* Log in user        = "+str(response.status_code)
  if response.status_code == 500:
  	print "* Log in user = FAILED QA"
  	logInToHCC()
  
def act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max):
  global CODE_OPPS_ACTION
  global TOTAL_OPPS_ACCEPTED, TOTAL_OPPS_REJECTED, TOTAL_OPPS_SKIPPED, TOTAL_OPPS_SERVED
  global TOTAL_DOCS_ACCEPTED, TOTAL_DOCS_REJECTED
  if CODE_OPPS_ACTION == "0": # Do NOT Accept or Reject Doc
    print "* HCC CODE         = %s" % str(opportunity.get("hcc"))+"-"+str(opportunity.get("model_year"))+"-"+str(opportunity.get("model_run"))+"-"+str(opportunity.get("payment_year"))
    print("* CODER ACTION     = Do NOT Accept or Reject Doc")
    IncrementTestResultsTotals("coding view only", 200)
  elif CODE_OPPS_ACTION == "1": # Accept Doc
    TOTAL_DOCS_ACCEPTED += 1
    finding_id = scorable.get("id")
    print "* FINDING ID       = %s" % finding_id
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "accept", \
    		"comment": "Comment by the OppRtrOptTest", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"flag_for_review": "true", \
    		"icd9[code_system_name]": opportunity.get("suggested_codes")[0].get("code_system_name"), \
    		"icd9[code]": opportunity.get("suggested_codes")[0].get("code"), \
    		"icd9[display_name]": opportunity.get("suggested_codes")[0].get("display_name")+" OppRtrOptTest", \
    		"icd9[code_system]": opportunity.get("suggested_codes")[0].get("code_system"), \
    		"icd9[code_system_version]": opportunity.get("suggested_codes")[0].get("code_system_version"), \
    		"provider[name]": "The OppRtrOptTest M.D.", \
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
    		"predicted_code[code_system_name]": "The OppRtrOptTest", \
    		"predicted_code[code]": "The OppRtrOptTest", \
    		"predicted_code[display_name]": "The OppRtrOptTest", \
    		"predicted_code[code_system]": "The OppRtrOptTest", \
    		"predicted_code[code_system_version]": "The OppRtrOptTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    response = requests.post(URL+ "/api/annotate/" + str(finding_id) + "/", data=DATA, headers=HEADERS)
    print "* ANNOTATE FINDING = %s" % response.status_code
    IncrementTestResultsTotals("coding view and accept", response.status_code)
    if response.status_code == 200:
      print "* HCC CODE         = %s" % str(opportunity.get("hcc"))+"-"+str(opportunity.get("model_year"))+"-"+str(opportunity.get("model_run"))+"-"+str(opportunity.get("payment_year"))
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max)
  elif CODE_OPPS_ACTION == "2": # Reject Doc
    TOTAL_DOCS_REJECTED += 1
    finding_id = scorable.get("id")
    #annotation = create_request(Test(testname, "Annotate Finding"))
    #response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    print "* FINDING ID       = %s" % finding_id
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "reject", \
    		"reject_reason": "Additional documentation needed to Accept the document for this HCC", \
    		"comment": "Comment by The OppRtrOptTest", \
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
    		"predicted_code[code_system_name]": "The OppRtrOptTest", \
    		"predicted_code[code]": "The OppRtrOptTest", \
    		"predicted_code[display_name]": "The OppRtrOptTest", \
    		"predicted_code[code_system]": "The OppRtrOptTest", \
    		"predicted_code[code_system_version]": "The OppRtrOptTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    response = requests.post(URL+ "/api/annotate/" + str(finding_id) + "/", data=DATA, headers=HEADERS)		
    IncrementTestResultsTotals("coding view and reject", response.status_code)
    if response.status_code == 200:
      print "* HCC CODE         = %s" % str(opportunity.get("hcc"))+"-"+str(opportunity.get("model_year"))+"-"+str(opportunity.get("model_run"))+"-"+str(opportunity.get("payment_year"))
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max)
  elif CODE_OPPS_ACTION == "3": # Skip Opp
    TOTAL_OPPS_SKIPPED += 1
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
    		"hcc[description]": opportunity.get("hcc_description") + " (OppRtrOptTest)", \
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
    		"predicted_code[code_system_name]": "The OppRtrOptTest", \
    		"predicted_code[code]": "The OppRtrOptTest", \
    		"predicted_code[display_name]": "The OppRtrOptTest", \
    		"predicted_code[code_system]": "The OppRtrOptTest", \
    		"predicted_code[code_system_version]": "The OppRtrOptTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    response = requests.post(URL+ "/api/annotate/" + str(finding_id) + "/", data=DATA, headers=HEADERS)		
    IncrementTestResultsTotals("coding view and skip", response.status_code)
    if response.status_code == 200:
      print "* HCC CODE         = %s" % str(opportunity.get("hcc"))+"-"+str(opportunity.get("model_year"))+"-"+str(opportunity.get("model_run"))+"-"+str(opportunity.get("payment_year"))
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max)
  else:
    print("* CODER ACTION     = Unknown\n")
  return 0

  
def startCoding():
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION, TOTAL_OPPS_SERVED
  global VOO, VAO, VRO, VSO
  global PERCENT_OF_SERVED, HCC, COUNT_OF_SERVED
  #global model_year, payment_year, hcc, model_run
  print("-------------------------------------------------------------------------------")
  print("-------------------------------------------------------------------------------")
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* MAX PATIENT OPP(S) = %s" % (URL, USERNAME, PASSWORD, CODE_OPPS_MAX))
  print("-------------------------------------------------------------------------------")
  print("-------------------------------------------------------------------------------")
  #coding_opp_current = 1
  #====================================================
  # main loop controlling number of OPPS to process
  #====================================================
  for coding_opp_current in range(1, (int(CODE_OPPS_MAX)+1)):
    testCode = 10 + (1 * coding_opp_current)
    response = requests.get(URL + "/api/coding-opportunity/", data=DATA, headers=HEADERS)
    print "* GET CODNG OPP    = %s" % response.status_code
    opportunity = response.json()
    ######################################################################################         
    model_year = opportunity.get("model_year")
    tallyDetails("model_year", opportunity.get("model_year"))
    payment_year = opportunity.get("payment_year")
    tallyDetails("payment_year", opportunity.get("payment_year"))
    hcc = opportunity.get("hcc")
    tallyDetails("hcc", opportunity.get("hcc"))
    model_run = opportunity.get("model_run")
    tallyDetails("model_run", opportunity.get("model_run"))
    print "* HCC CODE         = %s" % hcc+"-"+model_year+"-"+model_run+"-"+payment_year
    ######################################################################################
    patient_details = response.text
    IncrementTestResultsTotals("coding opportunity check", response.status_code)
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
    TOTAL_OPPS_SERVED = coding_opp_current   
    
    if str(TOTAL_OPPS_SERVED) in PERCENT_OF_SERVED:
    	COUNT_OF_SERVED[str(TOTAL_OPPS_SERVED)]=(dict((key, value) for key, value in HCC.items() if (value > 0)))   	
    	TEMP_HCC = (dict((key, value) for key, value in HCC.items() if (value > 0)))
    	for hcc in TEMP_HCC:
    		TEMP_HCC[hcc] = round(float(TEMP_HCC[hcc])/float(TOTAL_OPPS_SERVED),2)
    		if hcc == HCC_CODE_TO_ACCEPT:
    			PERCENT_OF_SP_HCC_SERVED[str(TOTAL_OPPS_SERVED)]=(round(float(TEMP_HCC[hcc])/float(TOTAL_OPPS_SERVED),2))*STEP
    	PERCENT_OF_SERVED[str(TOTAL_OPPS_SERVED)]=TEMP_HCC
    	
    	#quit()    
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
      IncrementTestResultsTotals("coding scorable document check", response.status_code)
      test_counter += 1
      if RANDOM_OPPS_ACTION == "1":
      	CODE_OPPS_ACTION = WeightedRandomCodingAction(hcc)
      act_on_doc(opportunity, scorable, testCode + test_counter, doc_no_current, doc_no_max)
      #quit()
  return 0


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

#######################################################################################################################
# HELPER FUNCTIONS ####################################################################################################
#######################################################################################################################

def tallyDetails(item, value):
	global MODEL_YEAR, PAYMENT_YEAR, HCC, MODEL_RUN
	if item == "model_year":
		MODEL_YEAR[value] += 1
	elif item == "payment_year":	
		PAYMENT_YEAR[value] += 1
	elif item == "hcc":	
		HCC[value] += 1
	elif item == "model_run":	
		MODEL_RUN[value] += 1
	return 0


def WeightedRandomCodingAction(hcc_code):
	#===============================
	# Action:
	# 0 - View Only Opportunity 
	# 1 - Accept Document
	# 2 - Reject Document
	# 3 - Reject Opportunity
	#===============================
	global VOO_W, VAO_W, VRO_W, VSO_W
	global VOO_W2, VAO_W2, VRO_W2, VSO_W2
	global VOO, VAO, VRO, VSO
	weight = { "0": 0, "1": 0, "2": 0, "3": 0 }
	weight['0'] = int(VOO_W)
	weight['1'] = int(VAO_W)
	weight['2'] = int(VRO_W)
	weight['3'] = int(VSO_W)
	action = random.choice([k for k in weight for dummy in range(weight[k])])
	
	weight2 = { "0": 0, "1": 0, "2": 0, "3": 0 }
	weight2['0'] = int(VOO_W2)
	weight2['1'] = int(VAO_W2)
	weight2['2'] = int(VRO_W2)
	weight2['3'] = int(VSO_W2)
	action2 = random.choice([l for l in weight2 for dummy2 in range(weight2[l])])
	
	#if hcc_code in HCC_CODES_TO_ACCEPT:
	if hcc_code == HCC_CODE_TO_ACCEPT:
		if action2 == "0":
			VOO += 1
		elif action2 == "1":
			VAO += 1
		elif action2 == "2":
			VRO += 1
		elif action2 == "3":
			VSO += 1
		return (action2)	
	else:	
		if action == "0":
			VOO += 1
		elif action == "1":
			VAO += 1
		elif action == "2":
			VRO += 1
		elif action == "3":
			VSO += 1
		return (action)
	
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
	
def checkEnvironmentandReceivers():
	# Environment for OppRtrOptTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	# Environment for OppRtrOptTest is passed as a paramater. Staging is a default value
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

def writeReportHeader ():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Begin writing report header ...\n")
	# REPORT = MIMEMultipart()
	REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	REPORT = REPORT + HTML_RECEIVERS
	REPORT = REPORT + """MIME-Version: 1.0\n"""
	REPORT = REPORT + """Content-type: text/html\n"""
	REPORT = REPORT + """Subject: OppRouter %s Optimization Test Report - %s\n\n""" % (ENVIRONMENT, START_TIME)

	REPORT = REPORT + """<h1>Apixio Opp Router Optimization Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """HCC user name: <b>%s</b><br>\n""" % (USERNAME)
	REPORT = REPORT + """HCC app url: <b>%s</b><br>\n""" % (URL)
	REPORT = REPORT + """Maximum # of Opps to serve: <b>%s</b><br>\n""" % (CODE_OPPS_MAX)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s%s</font></b><br><br>\n""" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + """<table align="left" width="800" cellpadding="1" cellspacing="1"><tr><td>"""
	print ("End writing report header ...\n")
	
def writeReportDetails(module):	
	global REPORT
	global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
	
	REPORT = REPORT + SUBHDR_TBL % module.upper()
	#obtainFailedJobs("summary_coordinator_jobfinish"+POSTFIX)
	REPORT = REPORT + "<table spacing='1' padding='1'><tr><td>Succeeded:</td><td>"+str(SUCCEEDED_TOT[int(MODULES[module])])+"</td></tr>"
	REPORT = REPORT + "<tr><td>Retried:</td><td>"+str(RETRIED_TOT[int(MODULES[module])])+"</td></tr>"
	REPORT = REPORT + "<tr><td>Failed:</td><td>"+str(FAILED_TOT[int(MODULES[module])])+"</td></tr></table>"
	if (FAILED_TOT[int(MODULES[module])] > 0) or (RETRIED_TOT[int(MODULES[module])] > 0):
		REPORT = REPORT+str(FAILED_TBL)
	else:
		REPORT = REPORT+str(PASSED_TBL)
	print ("Completed writeReportDetails ... \n")
		
	
def createGraph():
	global CURDAY, START, STOP

	#x = arange(START, STOP, STEP)
	#y = sin(2*pi*x)
	#PERCENT_OF_SP_HCC_SERVED = {'10':0.0, '20':0.0, '30':0.1, '40':0.2, '50':0.3, '50':0.4, '60':0.5, '70':0.5, '80':0.6, '90':0.8, '100':0.9}
	
	#SORTED_PERCENT_OF_SP_HCC_SERVED = OrderedDict(sorted(PERCENT_OF_SP_HCC_SERVED.items(), key=lambda t: t[0]))
	#print SORTED_PERCENT_OF_SP_HCC_SERVED
	
	x = SORTED_PERCENT_OF_SP_HCC_SERVED.keys()
	y = SORTED_PERCENT_OF_SP_HCC_SERVED.values()
	
	plot(x, y, color='blue', linestyle='solid', marker='o', markerfacecolor='green', markersize=3)

	xlabel('# of serves per time bucket')
	ylabel('% of specific HCC-'+str(HCC_CODE_TO_ACCEPT)+' served')
	title('HCC Opportunity Router Optimization Test')
	grid(True)
	savefig(str(CURDAY))
	show()


def writeReportFooter():
	global REPORT, SORTED_PERCENT_OF_SP_HCC_SERVED
	print ("Write report footer ...\n")
	REPORT = REPORT+"<table align='left' width='800' cellpadding='1' cellspacing='1'>"
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Opps served:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % \
		(TOTAL_OPPS_SERVED)
	REPORT = REPORT+"<tr><td nowrap>Opps skipped:</td><td><b>%s</b></td></tr>" % \
		(TOTAL_OPPS_SKIPPED)
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Docs accepted:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % \
		(TOTAL_DOCS_ACCEPTED)
	REPORT = REPORT+"<tr><td nowrap>Docs rejected:</td><td><b>%s</b></td></tr>" % \
		(TOTAL_DOCS_REJECTED)
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"	
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Model year:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % \
		(dict((key, value) for key, value in MODEL_YEAR.items() if (value > 0)))
	REPORT = REPORT+"<tr><td nowrap>Model run:</td><td><b>%s</b></td></tr>" % \
		(dict((key, value) for key, value in MODEL_RUN.items() if (value > 0)))		
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Payment year:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % \
		(dict((key, value) for key, value in PAYMENT_YEAR.items() if (value > 0)))
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"	
	###############################################################################################################
	# Sort all dictionaries here
	SORTED_HCC = OrderedDict(sorted(HCC.items(), key=lambda t: t[0]))
	SORTED_COUNT_OF_SERVED = OrderedDict(sorted(COUNT_OF_SERVED.items(), key=lambda t: t[0]))
	SORTED_PERCENT_OF_SERVED = OrderedDict(sorted(PERCENT_OF_SERVED.items(), key=lambda t: t[0]))
	#SORTED_PERCENT_OF_SP_HCC_SERVED = OrderedDict(sorted(PERCENT_OF_SP_HCC_SERVED.items(), key=lambda t: t[0]))
	SORTED_PERCENT_OF_SP_HCC_SERVED = SortedDict(PERCENT_OF_SP_HCC_SERVED)
	#print SORTED_PERCENT_OF_SP_HCC_SERVED.items()
	#quit()
	###############################################################################################################
	REPORT = REPORT+"<tr><td nowrap>HCC total:</td><td><b>%s</b></td></tr>" % \
		(dict((key, value) for key, value in SORTED_HCC.items() if (value > 0)))
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>HCC per bucket:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % \
		(dict((key, value) for key, value in SORTED_COUNT_OF_SERVED.items() if (value > 0)))	
	REPORT = REPORT+"<tr><td nowrap>HCC (all) %% per bucket:</td><td><b>%s</b></td></tr>" % \
		(dict((key, value) for key, value in SORTED_PERCENT_OF_SERVED.items()))	
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>HCC (%s) %% per bucket:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % \
		(HCC_CODE_TO_ACCEPT, dict((key, value) for key, value in SORTED_PERCENT_OF_SP_HCC_SERVED.items()))			
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
	
	#print PERCENT_OF_SERVED.items()[0]
	#print PERCENT_OF_SERVED.keys()[0]
	#print PERCENT_OF_SERVED.values()[0]
	#print (PERCENT_OF_SERVED['10'])['27']
	
	createGraph()
	
	REPORT = REPORT+"<tr><td colspan='2'><img src='"+str(CURDAY)+".png' alt='HCC Opportunity Router Optimization Test' height='600' width='800'></td></tr>"
	
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
	
	
	END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	REPORT = REPORT+"<tr><td colspan='2'><br>Start of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, START_TIME)
	REPORT = REPORT+"<tr><td colspan='2'>End of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, END_TIME)
	TIME_END = time.time()
	TIME_TAKEN = TIME_END - TIME_START
	hours, REST = divmod(TIME_TAKEN,3600)
	minutes, seconds = divmod(REST, 60)
	REPORT = REPORT+"<tr><td colspan='2'>Test Duration: <b>%s hours, %s minutes, %s seconds</b><br></td></tr>" % (hours, minutes, seconds)
	REPORT = REPORT+"<tr><td colspan='2'><br><i>-- Apixio QA Team</i></td></tr>"
	REPORT = REPORT+"</table>"
	REPORT = REPORT+"</td></tr></table>"
	print ("Finished writing report ...\n")


def archiveReport():
	global DEBUG_MODE, ENVIRONMENT, CURMONTH, CURDAY, IMAGEFILENAME
	if not DEBUG_MODE:
		print ("Archiving report ...\n")
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/opprtropt/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/opprtropt/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		IMAGEFILENAME=str(CURDAY)+".png" 
		REPORTXTSTRING="OppRtrOpt "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/opprtropt/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="opprtropt_reports_"+ENVIRONMENT.lower()+".txt"
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
		os.chdir("/mnt/automation/python/stress_test")
		# Copy graph image files to reports and backup folders
		shutil.copy(IMAGEFILENAME, REPORTFOLDER)
		shutil.copy(IMAGEFILENAME, BACKUPREPORTFOLDER)
		# Delete graph image file from test folder
		# os.remove(IMAGEFILENAME)
		print ("Finished archiving report ... \n")


def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2
	#============================================================================
	# Embedding image in html email - waiting for future implementation
	# http://stackoverflow.com/questions/6706891/embedding-image-in-html-email
	# waiting ...
	#============================================================================
	#print ("Emailing report ...\n")
	#s=smtplib.SMTP()
	#s.connect("smtp.gmail.com",587)
	#s.starttls()
	#s.login("donotreply@apixio.com", "apx.mail47")	        
	#s.sendmail(SENDER, RECEIVERS, REPORT)	
	#s.sendmail(SENDER, RECEIVERS2, REPORT)
	#s.quit()
	#print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)

	print ("Emailing report ...\n")
	message = MIMEMultipart('related')

	msg_content = '''<html><body><p><table><tr> \
  		<td>Hello,</td></tr> \
  		<tr><td><img src="cid:picture@example.com" width="800" height="600"></td></tr> \
  		<tr><td>world</td> \
		</tr></table></p></body></html>'''
	message.attach(MIMEText((msg_content), 'html'))

	with open('30.png', 'rb') as image_file:
		image = MIMEImage(image_file.read())
	image.add_header('Content-ID', '<picture@example.com>')
	image.add_header('Content-Disposition', 'inline', filename='30.png')
	message.attach(image)


	message['From'] = 'ishekhtman@apixio.com'
	message['To'] = 'ishekhtman@apixio.com'
	message['Subject'] = 'Python Test E-mail'
	msg_full = message.as_string()

	server = smtplib.SMTP()
	server.connect("smtp.gmail.com",587)
	server.starttls()
	server.login("donotreply@apixio.com", "apx.mail47")
	server.sendmail('ishekhtman@apixio.com',['ishekhtman@apixio.com'],msg_full)
	server.quit()
	print "Report completed, successfully sent email..."



# MAIN FUNCTION CALLER ####################################################################################################


os.system('clear')


emailReport()
