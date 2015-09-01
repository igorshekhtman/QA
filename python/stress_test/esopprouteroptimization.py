####################################################################################################
#
# PROGRAM: esopprouteroptimization.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    2015.08.05 Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: 2015.08.05
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
import numpy as np
import apxapi
requests.packages.urllib3.disable_warnings()
#from scipy import spline

# GLOBAL VARIABLES #######################################################################

CSV_CONFIG_FILE_PATH = "/mnt/automation/python/stress_test/"
CSV_CONFIG_FILE_NAME = "esopprouteroptimization.csv"
VERSION = "1.0.1"
# Email reports to eng@apixio.com and archive report html file:
# 0 - False
# 1 - True
DEBUG_MODE=bool(0)
# HTML report version to archive
REPORT = ""
# HTML report version to email
REPORT_EMAIL = ""
REPORT_TYPE = "ES Energy Routing Test"
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


HCC = {str(key): 0 for key in range(0, 200)}
#LABEL_SET_VERSION = {str(key): 0 for key in range(2000, 2040)}
#SWEEP = {'Final': 0, 'Initial': 0}
MODEL_PAYMENT_YEAR = {str(key): 0 for key in range(2000, 2040)}
LABEL_SET_VERSION = {'V12': 0, 'V22': 0}
SWEEP = {'midYear': 0, 'finalReconciliation': 0, 'initial': 0}

# This list of codes will overwrite random choice function to accept an opportunity
#HCC_CODES_TO_ACCEPT = {'15', '27', '100'}
#HCC_CODES_TO_ACCEPT = {'27'}
#HCC_CODES_TO_ACCEPT = {'131'}
HCC_CODES_TO_ACCEPT = {'130'}

#TARGET_HCC = '27'
#TARGET_HCC = '177'
#TARGET_HCC = '32'
#TARGET_HCC = '131'
#TARGET_HCC = '29'
#TARGET_HCC = '150'
TARGET_HCC = '130'
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
  global MAX_NUM_RETRIES, START, STOP, STEP
  global COUNT_OF_SERVED, PERCENT_OF_SERVED, PERCENT_OF_TARGET_HCC_SERVED

  result={ }
  csvfile = open(filename, 'rb')
  reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
  for row in reader:
    if (str(row[0])[0:1] <> '#') and (str(row[0])[0:1] <> ' '):
      result[row[0]] = row[1]
  globals().update(result)
  
  MAX_NUM_RETRIES = int(result["MAX_NUM_RETRIES"])
  
  START = (int(CODE_OPPS_MAX)/10)
  STOP = int(CODE_OPPS_MAX)
  STEP = (int(CODE_OPPS_MAX)/10)
  
  COUNT_OF_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
  PERCENT_OF_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
  PERCENT_OF_TARGET_HCC_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
  
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

###########################################################################################################################################
# MAIN FUNCTIONS ##########################################################################################################################
###########################################################################################################################################
 
def logInToHCC(): 
  global TOKEN, SESSID, DATA, HEADERS, COOKIES, TOKEN, APXTOKEN, JSESSIONID
  response = requests.get(URL+'/')
  print "* Connect to host    = "+str(response.status_code)
  if response.status_code == 500:
  	print "* Connection to host = FAILED QA"
  	quit()
#-----------------------------------------------------------------------------------------  	
  # Original - url = referer = URL+'/account/login/?next=/'
  url = URL+'/account/login/'
  referer = URL+'/account/login/'
  
  response = requests.get(url)
  IncrementTestResultsTotals("login", response.status_code)
  print "* Login page         = "+str(response.status_code)
  if response.status_code == 500:
  	print "* Connection to host = FAILED QA"
  	logInToHCC()
#-----------------------------------------------------------------------------------------  	
  
  
  #TOKEN = response.cookies["csrftoken"]
  #SESSID = response.cookies["sessionid"]
  #COOKIES = dict(csrftoken=''+TOKEN+'')
  
  TOKEN = response.cookies["JSESSIONID"]
  SESSID = response.cookies["JSESSIONID"]
  COOKIES = dict(csrftoken=''+TOKEN+'')
  JSESSIONID = response.cookies["JSESSIONID"]
  
  
  #url = URL+'/account/login/'
  #referer = URL+'/account/login/'
  #host = DOMAIN
  #origin = URL

  origin = "https://accounts-stg.apixio.com"
  referer = "https://accounts-stg.apixio.com/?caller=hcc_eng"
  host = "accounts-stg.apixio.com"
  url = "https://accounts-stg.apixio.com/"
  
  #DATA =    {'csrfmiddlewaretoken': TOKEN, 'username': USERNAME, 'password': PASSWORD } 
  
  DATA = {'username': USERNAME, 'password': PASSWORD, 'hash':'', 'caller':'hcc_eng', 'log_ref':'1441056621484', 'origin':'loging' }
  
  
  HEADERS = { \
  			'Accept': '*/*', \
  			'Accept-Encoding': 'gzip, deflate', \
  			'Accept-Language': 'en-US,en;q=0.8', \
  			'Connection': 'keep-alive', \
  			'Content-Length': '1105', \
			#'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
			'Cookie': 'JSESSIONID='+TOKEN, \
			'Host': host, \
			'Origin': origin, \
			'Referer': referer \
			}	
  					
  response = requests.post(url, data=DATA, headers=HEADERS) 
  
  TOKEN = response.cookies["csrftoken"]
  SESSID = response.cookies["sessionid"]
  APXTOKEN = str(apxapi.APXSession(USERNAME,PASSWORD).external_token())
  COOKIES = json.dumps(dict(csrftoken=''+TOKEN+'', sessionid=''+SESSID+'', ApxToken=APXTOKEN))
  
  print("* URL                = %s" % url)
  print("* USER               = %s" % USERNAME)
  print("* PASSWORD           = %s" % PASSWORD)
  print("* CSRFTOKEN          = %s" % TOKEN)
  print("* APXTOKEN           = %s" % APXTOKEN)
  print("* SESSID             = %s" % SESSID)
  print("* JSESSIONID         = %s" % JSESSIONID)
  
  IncrementTestResultsTotals("login", response.status_code)
  print "* Log in user        = "+str(response.status_code)
  #quit()
  if response.status_code == 500:
  	print "* Log in user = FAILED QA"
  	logInToHCC()
  	
###########################################################################################################################################  	
  
def act_on_doc(opportunity, finding, finding_id, testname, doc_no_current, doc_no_max):
  global CODE_OPPS_ACTION
  global TOTAL_OPPS_ACCEPTED, TOTAL_OPPS_REJECTED, TOTAL_OPPS_SKIPPED, TOTAL_OPPS_SERVED
  global TOTAL_DOCS_ACCEPTED, TOTAL_DOCS_REJECTED
  
  hcc = opportunity.get("code").get("hcc")
  label_set_version = opportunity.get("code").get("labelSetVersion")
  sweep = opportunity.get("code").get("sweep")
  model_payment_year = opportunity.get("code").get("modelPaymentYear")
  
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
  
  
  if CODE_OPPS_ACTION == "0": # Do NOT Accept or Reject Doc
    print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
    print("* CODER ACTION     = Do NOT Accept or Reject Doc")
    IncrementTestResultsTotals("coding view only", 200)
  elif CODE_OPPS_ACTION == "1": #=============================== ACCEPT DOC ==============
    TOTAL_DOCS_ACCEPTED += 1
    #finding_id = scorable.get("id")
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
    print "* ANNOTATE FINDING = %s" % response.status_code
    IncrementTestResultsTotals("coding view and accept", response.status_code)
    if response.status_code == 200:
      print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max)
  elif CODE_OPPS_ACTION == "2": #================================== REJECT DOC ===========
    TOTAL_DOCS_REJECTED += 1
    #finding_id = scorable.get("id")
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
    IncrementTestResultsTotals("coding view and reject", response.status_code)
    if response.status_code == 200:
      print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max)
  elif CODE_OPPS_ACTION == "3": #=========================== SKIP OPP ====================
    TOTAL_OPPS_SKIPPED += 1
    #finding_id = scorable.get("id")
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
    IncrementTestResultsTotals("coding view and skip", response.status_code)
    if response.status_code == 200:
      print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = 200 OK")
    else:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max)
  else:
    print("* CODER ACTION     = Unknown\n")
  return 0

###########################################################################################################################################
  
def startCoding():
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION, TOTAL_OPPS_SERVED, CODING_OPP_CURRENT
  global VOO, VAO, VRO, VSO
  global PERCENT_OF_SERVED, HCC, COUNT_OF_SERVED
  #global model_year, payment_year, hcc, model_run
  #print("-------------------------------------------------------------------------------")
  print("-------------------------------------------------------------------------------")
  print("* URL                = %s\n* CODER USERNAME     = %s\n* CODER PASSWORD     = %s\n* MAX PATIENT OPP(S) = %s" % (URL, USERNAME, PASSWORD, CODE_OPPS_MAX))
  print("-------------------------------------------------------------------------------")
  #print("-------------------------------------------------------------------------------")
  #coding_opp_current = 1
  #====================================================
  # main loop controlling number of OPPS to process
  #====================================================
  buckets = -1
  
  #Host: hcceng.apixio.com
  #Connection: keep-alive
  #Accept: application/json, text/plain, */*
  #X-REQUESTED-WITH: XMLHttpRequest
  #User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36
  #Referer: https://hcceng.apixio.com/
  #Accept-Encoding: gzip, deflate, sdch
  #Accept-Language: en-US,en;q=0.8
  #Cookie: SS_MID=93555fab-4853-4a24-ab6f-eedb8cac1c0diar9bgxa; ss_cid=396c3902-defc-4e80-aba1-dd22809d28cf; ApxToken=TA_3d87c4ea-7299-492f-b175-019a61f51ee4; csrftoken=iPt7GVUjjLjTRxe4V6Yg7qQrdoc9B6ml; sessionid=nel0hbg9qx663qbdfk04o2x2lrxqugdm
  
  
  print("* URL                = %s/api/next-work-item/" % URL)
  print("* csrftoken          = %s" % TOKEN)
  print("* ApxToken           = %s" % APXTOKEN)
  print("* sessionid          = %s" % SESSID) 
  
  
  HEADERS = { \
  			'Accept': 'application/json, text/plain, */*', \
  			'Accept-Encoding': 'gzip, deflate, sdch', \
  			'Accept-Language': 'en-US,en;q=0.8', \
  			'Connection': 'keep-alive', \
			'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+'; ApxToken='+APXTOKEN+' ', \
			'Host': 'hcceng.apixio.com', \
			'Referer': 'https://hcceng.apixio.com/' \
			}	
			
  DATA = {}
  
  
  
  for coding_opp_current in range(1, (int(CODE_OPPS_MAX)+1)):
    testCode = 10 + (1 * coding_opp_current)
    response = requests.get(URL + "/api/next-work-item/", data=DATA, headers=HEADERS)
    print ("* URL                = %s/api/next-work-item/" % URL)
    print ("* GET CODNG OPP      = %s" % response.status_code)
    
    print response.cookies.list_domains()
    print response.cookies.list_paths()
    print response.cookies.get_dict()
    print response.status_code
    print response.headers
    print response.text
    print response.json()
    quit()
    
    
    opportunity = response.json()
    ######################################################################################
    
    #hcc, label, sweep, payment year
        
    #print json.dumps(opportunity)         
    
    #model_year = opportunity.get("code").get("modelPaymentYear")
    #tallyDetails("model_year", opportunity.get("model_year"))
    #payment_year = opportunity.get("payment_year")
    #tallyDetails("payment_year", opportunity.get("payment_year"))
    #hcc = opportunity.get("hcc")
    #tallyDetails("hcc", opportunity.get("hcc"))
    #model_run = opportunity.get("model_run")
    #tallyDetails("model_run", opportunity.get("model_run"))
    
    hcc = opportunity.get("code").get("hcc")
    tallyDetails("hcc", hcc)
    label_set_version = opportunity.get("code").get("labelSetVersion")
    tallyDetails("label_set_version", label_set_version)
    sweep = opportunity.get("code").get("sweep")
    tallyDetails("sweep", sweep)
    model_payment_year = opportunity.get("code").get("modelPaymentYear")
    tallyDetails("model_payment_year", model_payment_year)

    
    print "\n"
    print "********************************************************************************************"
    print "********************************************************************************************"
    print "********************************************************************************************"
    print "\n"
    print "* HCC CODE         = %s" % hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year
    print "\n"
    print "********************************************************************************************"
    print "********************************************************************************************"
    print "********************************************************************************************"
    print "\n"
    ######################################################################################
    patient_details = response.text
    IncrementTestResultsTotals("coding opportunity check", response.status_code)
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
    print("PATIENT OPP %d OF %d" % (coding_opp_current, int(CODE_OPPS_MAX)))
    TOTAL_OPPS_SERVED = coding_opp_current   
    
    if str(TOTAL_OPPS_SERVED) in PERCENT_OF_SERVED:
    	buckets += 1
    	COUNT_OF_SERVED[str(TOTAL_OPPS_SERVED)]=(dict((key, value) for key, value in HCC.items() if (value > 0)))   	
    	TEMP_HCC = (dict((key, value) for key, value in HCC.items() if (value > 0)))
    	for hcc in TEMP_HCC:
    		TEMP_HCC[hcc] = round(float(TEMP_HCC[hcc])/float(TOTAL_OPPS_SERVED),2)
    	PERCENT_OF_SERVED[str(TOTAL_OPPS_SERVED)]=TEMP_HCC
    	

    test_counter = 0
    doc_no_current = 0
    doc_no_max = 1
    for i in range (0,1):
      finding = findings[i]
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
    	#  PATIENT_ORG_NAME = getOrgName(patient_org_id)
      
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
      response = requests.get(URL + "/api/document-text/" + document_uuid, data=DATA, headers=HEADERS)
      print "* GET SCRBLE DOC   = %s" % response.status_code      
      IncrementTestResultsTotals("coding scorable document check", response.status_code)
      test_counter += 1
      if RANDOM_OPPS_ACTION == "1":
      	CODE_OPPS_ACTION = WeightedRandomCodingAction(hcc)
      act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max)

  return 0

###########################################################################################################################################

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

###########################################################################################################################################
# HELPER FUNCTIONS ########################################################################################################################
###########################################################################################################################################

def tallyDetails(item, value):
	global MODEL_YEAR, PAYMENT_YEAR, HCC, MODEL_RUN
	global MODEL_PAYMENT_YEAR, SWEEP, LABEL_SET_VERSION
	
	if item == "model_year":
		MODEL_YEAR[value] += 1
	elif item == "payment_year":	
		PAYMENT_YEAR[value] += 1
	elif item == "hcc":	
		HCC[value] += 1
	elif item == "model_run":	
		MODEL_RUN[value] += 1
	elif item == "model_payment_year":
		MODEL_PAYMENT_YEAR[value] += 1
	elif item == "sweep":
		SWEEP[value] += 1
	elif item == "label_set_version":
		LABEL_SET_VERSION[value] += 1			
	return 0

###########################################################################################################################################

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
	if hcc_code == TARGET_HCC:
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

###########################################################################################################################################		
	
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

###########################################################################################################################################
	
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

###########################################################################################################################################

def writeReportHeader ():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Begin writing report header ...\n")
	# REPORT = MIMEMultipart()
	#REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	#REPORT = REPORT + HTML_RECEIVERS
	#REPORT = REPORT + """MIME-Version: 1.0\n"""
	#REPORT = REPORT + """Content-type: text/html\n"""
	#REPORT = REPORT + """Subject: OppRouter %s Optimization Test Report - %s\n\n""" % (ENVIRONMENT, START_TIME)
	REPORT = """ """
	REPORT = REPORT + """<h1>Apixio ES Energy Routing Test Report</h1>\n"""
	REPORT = REPORT + """Run date & time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	#REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """HCC user name: <b>%s</b><br>\n""" % (USERNAME)
	REPORT = REPORT + """HCC app url: <b>%s</b><br>\n""" % (URL)
	REPORT = REPORT + """Maximum # of Opps to serve: <b>%s</b><br>\n""" % (CODE_OPPS_MAX)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s%s</font></b><br><br>\n""" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + """<table align="left" width="800" cellpadding="1" cellspacing="1"><tr><td>"""
	print ("End writing report header ...\n")

###########################################################################################################################################
	
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
		
###########################################################################################################################################
	
def drawGraph(srcedict):
	global CURDAY, START, STOP
	
	key = sorted(srcedict.keys())
	temp = []
	for i in key:
		value = srcedict[i]
		temp.append(value)
	
	x = sorted(srcedict.keys())	
	y = temp
	z = sorted(srcedict.items())
		
	plot(x, y, color='green', linewidth=3, linestyle='solid', marker='o', markerfacecolor='blue', markersize=6)
	xlabel('# of serves per time bucket')
	ylabel('% of targeted HCC-'+str(TARGET_HCC)+' served')
	title('HCC Opportunity Router Optimization Test')
	grid(True)
	savefig(str(CURDAY))
	show()

###########################################################################################################################################

def getKey(key):
    try:
        return int(key)
    except ValueError:
        return key

###########################################################################################################################################

def convertJsonToTable(srcedict, sortby):
	global REPORT
	#print srcedict
	REPORT = REPORT+"<table width='500' cellspacing='0' cellpadding='2' border='1'>"
	#key = sorted(srcedict.keys())
	#sorted(mydict, key=lambda key: mydict[key])
	#key = sorted(srcedict, key=lambda key: srcedict[key])
	#sortedict = sorted(srcedict.items(), key=lambda t: getKey(t[0]))
	#sortedict = sorted(srcedict.items(), key=lambda t: int(t[0]))
	#sortedkeys = sorted(srcedict.keys())
	#=====sort by values=======================================
	#import operator
	#x = {1: 2, 3: 4, 4:3, 2:1, 0:0}
	#sorted_x = sorted(x.items(), key=operator.itemgetter(1))
	#=====sort by keys=========================================
	#import operator
	#x = {1: 2, 3: 4, 4:3, 2:1, 0:0}
	#sorted_x = sorted(x.items(), key=operator.itemgetter(0))
	#==========================================================
	if sortby == "value":
		sorteditems = sorted(srcedict.items(), key=operator.itemgetter(1), reverse=True)
		ctr = 0
		for item in sorteditems:
			if item[1] > 0:
				if ctr == 0:
					b_color = '#FFFF00'
					most_served = item[1]
				else:
					if item[1] == most_served:
						b_color = '#FFFF00'
					else:
						b_color = '#FFFFFF'
				REPORT = REPORT+"<tr><td bgcolor='"+b_color+"'> HCC-"+str(item[0])+"</td><td bgcolor='"+b_color+"'><b>"+str(item[1])+"</b></td></tr>"
				ctr += 1
	else:
		sorteditems = sorted(srcedict.items(), key=operator.itemgetter(0), reverse=False)	
		for item in sorteditems:
			if item[1] > 0:
				REPORT = REPORT+"<tr><td>"+str(item[0])+"</td><td><b>"+str(item[1])+"</b></td></tr>"
			
	REPORT = REPORT+"</table>"

###########################################################################################################################################

def extractTargetedHccData(targhcc, srcedict):
	#print targhcc
	#print srcedict
	#key = sorted(srcedict.keys())
	extrdict = {}
	for k, v in sorted(srcedict.iteritems()):
		#print k, v
		if targhcc in v.keys():
			extrdict.update({k: v[targhcc]})
		else:
			extrdict.update({k: 0})	
			
	#print extrdict
	#quit()
	return (extrdict)	

###########################################################################################################################################
def writeReportFooter():
	global REPORT, SORTED_PERCENT_OF_TARGET_HCC_SERVED, REPORT_EMAIL
	

	print ("Write report footer ...\n")
	REPORT = REPORT+"<table align='left' width='800' cellpadding='1' cellspacing='1'>"
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
	REPORT = REPORT+"<tr><td colspan='2' align='center'><font size='4'><b>TARGETED HCC-%s</b></font></td></tr>" % \
		(TARGET_HCC)
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
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Accepting Opps rate:</td><td bgcolor='#D8D8D8'><b>%s %%</b></td></tr>" % \
		(VAO_W)	
	REPORT = REPORT+"<tr><td nowrap>Rejecting Opps rate:</td><td><b>%s %%</b></td></tr>" % \
		(VRO_W)	
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"		
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Accepting HCC-%s Opps rate:</td><td bgcolor='#D8D8D8'><b>%s %%</b></td></tr>" % \
		(TARGET_HCC, VAO_W2)	
	REPORT = REPORT+"<tr><td nowrap>Rejecting HCC-%s Opps rate:</td><td><b>%s %%</b></td></tr>" % \
		(TARGET_HCC, VRO_W2)					
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
		
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Model payment year:</td><td bgcolor='#D8D8D8'>"
	convertJsonToTable(MODEL_PAYMENT_YEAR, "key")
	REPORT = REPORT+"</td></tr>"
	REPORT = REPORT+"<tr><td nowrap>Sweep:</td><td>"
	convertJsonToTable(SWEEP, "key")
	REPORT = REPORT+"</td></tr>"
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>Label set version:</td><td bgcolor='#D8D8D8'>"
	convertJsonToTable(LABEL_SET_VERSION, "key")
	REPORT = REPORT+"</td></tr>"
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"	
	###############################################################################################################
	# Sort all dictionaries here
	#SORTED_HCC = OrderedDict(sorted(HCC.items(), key=lambda t: t[0]))
	#SORTED_COUNT_OF_SERVED = OrderedDict(sorted(COUNT_OF_SERVED.items(), key=lambda t: t[0]))
	#SORTED_PERCENT_OF_SERVED = OrderedDict(sorted(PERCENT_OF_SERVED.items(), key=lambda t: t[0]))
	#SORTED_PERCENT_OF_TARGET_HCC_SERVED = OrderedDict(sorted(PERCENT_OF_TARGET_HCC_SERVED.items(), key=lambda t: t[0]))
	#SORTED_PERCENT_OF_TARGET_HCC_SERVED = SortedDict(PERCENT_OF_TARGET_HCC_SERVED)
	#print SORTED_PERCENT_OF_TARGET_HCC_SERVED.items()
	#quit()
	###############################################################################################################
	#REPORT = REPORT+"<tr><td nowrap>HCCs total:</td><td><b>%s</b></td></tr>" % \
	REPORT = REPORT+"<tr><td nowrap>HCCs total:</td><td>"
	convertJsonToTable(HCC, "value")
	REPORT = REPORT+"</td></tr>"				
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>HCCs per bucket:</td><td bgcolor='#D8D8D8'>"
	convertJsonToTable(COUNT_OF_SERVED, "key")
	REPORT = REPORT+"</td></tr>"	
	REPORT = REPORT+"<tr><td nowrap>HCCs % per bucket:</td><td>"
	convertJsonToTable(PERCENT_OF_SERVED, "key")
	REPORT = REPORT+"</td></tr>"	
	REPORT = REPORT+"<tr><td bgcolor='#D8D8D8' nowrap>HCC-%s %% per bucket:</td><td bgcolor='#D8D8D8'>" % (TARGET_HCC)
	convertJsonToTable(extractTargetedHccData(TARGET_HCC, PERCENT_OF_SERVED), "key")
	REPORT = REPORT+"</td></tr>"
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
	
	drawGraph(extractTargetedHccData(TARGET_HCC, PERCENT_OF_SERVED))
		
	REPORT_EMAIL = REPORT_EMAIL + REPORT	
	REPORT = REPORT+"<tr><td colspan='2'><img src='"+str(CURDAY)+".png' width='800' height='600'></td></tr>"
	REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><img src='cid:picture@example.com' width='800' height='600'></td></tr>"	
	REPORT = REPORT+"<tr><td colspan='2'><hr></td></tr>"
	REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><hr></td></tr>"
	END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	REPORT = REPORT+"<tr><td colspan='2'><br>Start of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, START_TIME)
	REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><br>Start of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, START_TIME)
	REPORT = REPORT+"<tr><td colspan='2'>End of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, END_TIME)
	REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'>End of %s - <b>%s</b></td></tr>" % (REPORT_TYPE, END_TIME)
	TIME_END = time.time()
	TIME_TAKEN = TIME_END - TIME_START
	hours, REST = divmod(TIME_TAKEN,3600)
	minutes, seconds = divmod(REST, 60)
	REPORT = REPORT+"<tr><td colspan='2'>Test Duration: <b>%s hours, %s minutes, %s seconds</b><br></td></tr>" % (hours, minutes, seconds)
	REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'>Test Duration: <b>%s hours, %s minutes, %s seconds</b><br></td></tr>" % (hours, minutes, seconds)
	REPORT = REPORT+"<tr><td colspan='2'><br><i>-- Apixio QA Team</i></td></tr>"
	REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><br><i>-- Apixio QA Team</i></td></tr>"
	REPORT = REPORT+"</table>"
	REPORT_EMAIL = REPORT_EMAIL+"</table>"
	REPORT = REPORT+"</td></tr></table>"
	REPORT_EMAIL = REPORT_EMAIL+"</td></tr></table>"
	print ("Finished writing report ...\n")

###########################################################################################################################################

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

###########################################################################################################################################

def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2
	
	print ("Emailing report ...\n")
	IMAGEFILENAME=str(CURDAY)+".png" 
	message = MIMEMultipart('related')
	message.attach(MIMEText((REPORT_EMAIL), 'html'))
	with open(IMAGEFILENAME, 'rb') as image_file:
		image = MIMEImage(image_file.read())
	image.add_header('Content-ID', '<picture@example.com>')
	image.add_header('Content-Disposition', 'inline', filename=IMAGEFILENAME)
	message.attach(image)

	message['From'] = 'Apixio QA <QA@apixio.com>'
	message['To'] = 'To: Eng <eng@apixio.com>,Ops <ops@apixio.com>'
	message['Subject'] = 'ES %s Energy Routing Test Report - %s\n\n' % (ENVIRONMENT, START_TIME)
	msg_full = message.as_string()
		
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, [RECEIVERS, RECEIVERS2], msg_full)	
	s.quit()
	# Delete graph image file from stress_test folder
	os.remove(IMAGEFILENAME)
	print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)

###########################################################################################################################################

def pages_payload(details):
	report_json = details.json()
    	if report_json is not None:
    		pages = report_json.get("pages")
    		payload = len(details.text)
    	else:
    		pages = 0
    		payload = 0
	return (pages, payload)

###########################################################################################################################################

def create_request(test, headers=None):
  request = HTTPRequest()
  if headers:
    request.headers = headers
  test.record(request)
  return (request)

###########################################################################################################################################

def get_csrf_token(thread_context):
  cookies = CookieModule.listAllCookies(thread_context)
  csrftoken = ""
  for cookie in cookies:
    if cookie.getName() == "csrftoken":
      csrftoken = cookie.getValue()
  return (csrftoken)

###########################################################################################################################################

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
		RETRIED = RETRIED+1
		RETRIED_TOT[int(MODULES[module])] = RETRIED_TOT[int(MODULES[module])] + 1
		if RETRIED > int(MAX_NUM_RETRIES):
			print "Number of retries %s reached pre-set limit of %s.  Exiting now ..." % (RETRIED, MAX_NUM_RETRIES)
			quit()
		if (code == unauthorized):
			print "%s response code received from server.  Re-obtaining Autorization." % code
			logInToHCC()
			#print "%s response code received from server.  Test is being terminated" % code
			#quit()
			#logInToHCC()
			#startCoding()

###########################################################################################################################################
    
def log(text):
	global REPORT
	#REPORT = REPORT + text + "<br>"
	print(text)
	return 0    

###########################################################################################################################################
# MAIN FUNCTION CALLER ####################################################################################################################
###########################################################################################################################################

os.system('clear')

readConfigurationFile(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME)

checkEnvironmentandReceivers()

print "Maximum number of retries is set to = %s" % MAX_NUM_RETRIES

writeReportHeader()	

logInToHCC()

writeReportDetails("login")

startCoding()

writeReportDetails("coding opportunity check")
writeReportDetails("coding scorable document check")
writeReportDetails("coding view only")
writeReportDetails("coding view and accept")
writeReportDetails("coding view and reject")
writeReportDetails("coding view and skip")

logout()

writeReportDetails("logout")

printResultsSummary()

writeReportFooter()

archiveReport()

emailReport()
