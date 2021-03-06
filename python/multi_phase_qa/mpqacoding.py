####################################################################################################
#
# PROGRAM: mpqacoding.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    09/15/2015 Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: 
# SPECIFICS: 
#
# PURPOSE:
#          This program should be executed via Python 2.7 and is meant for testing HCC Multi-Phase QA functionality:
#          * Login
#          * View   Docs + Opportunities - 0
#          * Accept Docs + Opportunities - 1
#          * Reject Docs + Opportunities - 2
#          * Skip   Docs + Opportunities - 3
#          * Logout
#
# SETUP:
#		   * Clean profile
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.7 environment is available
#          * From QA2 server (50.204.82.254) /mnt/automation/python/multi_phase_qa folder enter "python2.7 mpqacoding.py"
#		   * note: opprouteroptimization.csv configuration file must coexist in same folder as opprouteroptimization.py
#
# USAGE:
#          * Set the global variables (CSV_CONFIG_FILE_PATH and CSV_CONFIG_FILE_NAME), see below
#          * Configure global parameters in opprouteroptimization.csv located in the same folder
#          * Results will be printed on Console screen as well as mailed via QA report
#		   *
#		   * python2.7 mpqacoding staging ishekhtman@apixio.com ishekhtman@apixio.com
#		   *
#
# SPECIFIC TEST CASE PROVIDED BY HA:
#		- Contained in annotation-plan.json file
#       - for the annotation automation, let's use org 372
#       - the annotation plan was created for that org
#       - project is CP_e2435ecb-3fb3-4e37-bdb5-7fdd2c6b3789
# 		qa-mp-coder@apixio.net
# 		qa-mp-cqa1@apixio.net
# 		qa-mp-cqa2@apixio.net
# 		qa-mp-cqa3@apixio.net
# 		org: 372
# 		project: CP_e2435ecb-3fb3-4e37-bdb5-7fdd2c6b3789
#		apixio.123
#		code flow:
#			load the annotation plan
#			login to hcc
#			get next item
#				with get-next-item data, lookup to find out what annotation sequence to apply?
#				repeat get-next-item
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

# GLOBAL VARIABLES #######################################################################

CODE_OPPS_MAX=10000
LOGOUT=1
MAX_NUM_RETRIES=2


# Email reports to eng@apixio.com and archive report html file:
# 0 - False
# 1 - True
DEBUG_MODE=bool(0)
# HTML report version to archive
REPORT = ""
# HTML report version to email
REPORT_EMAIL = ""
REPORT_TYPE = "ES Multi Phase QA Test"
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


HCC = {str(key): 0 for key in range(0, 200)}
#LABEL_SET_VERSION = {str(key): 0 for key in range(2000, 2040)}
#SWEEP = {'Final': 0, 'Initial': 0}
MODEL_PAYMENT_YEAR = {str(key): 0 for key in range(2000, 2040)}
LABEL_SET_VERSION = {'V12': 0, 'V22': 0}
SWEEP = {'midYear': 0, 'finalReconciliation': 0, 'initial': 0}


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
    
  if REVISION <> VERSION:
  	print ("============================================================================================================")
  	print ("Version of the mpqacoding.csv file (%s) does not match version of the mpqacoding.py script (%s)" % (REVISION, VERSION))
  	print ("============================================================================================================")
  	sys.exit(1)
  else:
  	print ("==============================================================================")
  	print ("mpqacoding.csv VERSION:        %s" % REVISION)
  	print ("mpqacoding.py VERSION:         %s" % VERSION)
  	print ("==============================================================================")
  return result
##########################################################################################

ok 				= 200
created 		= 201
accepted 		= 202
nocontent 		= 204
movedperm 		= 301
redirect 		= 302
unauthorized 	= 401
forbidden 		= 403
notfound 		= 404
intserveror 	= 500
servunavail 	= 503

FAILED = SUCCEEDED = RETRIED = 0
VOO = VAO = VRO = VSO = 0

###########################################################################################################################################
# MAIN FUNCTIONS ##########################################################################################################################
###########################################################################################################################################

#============================================================================================================
#=================================== LOAD ANNOTATIONS PLAN ==================================================
#============================================================================================================

def loadAnnotationPlan():
  global APLANS_FN, APLANS
  global OPPS_PLAN_TOT, OPPS_SERVED_TOT, FINDINGS_ANNO_TOT
 
  # 0 - coder
  # 1 - QA1
  # 2 - QA2
  # 3 - QA3
  
  
  print "Loading annotations plan ..."
  
  OPPS_PLAN_TOT = [0, 0, 0, 0]
  OPPS_SERVED_TOT = [0, 0, 0, 0]
  
  
  #"0" - coder [view, accept, reject, skip]
  #"1" - QA1 [view, accept, reject, skip]
  #"2" - QA2 [view, accept, reject, skip]
  #"3" - QA3 [view, accept, reject, skip]
  
  FINDINGS_ANNO_TOT = {"0":[0,0,0,0], "1":[0,0,0,0], "2":[0,0,0,0], "3":[0,0,0,0]}
  
  
  # --------------- load input data from a json file --------
  APLANS_FN = "org-372-annotation-plan.json"
  f = open(APLANS_FN, 'r')
  APLANS = json.load(f)
  # ---------------------------------------------------------
  for aplan in APLANS:
    steps = len(APLANS[0].get("steps"))
    for i in range (0, steps):
      OPPS_PLAN_TOT[i] += 1        

  print ("==============================================================================")	
  print ("* CODERS LIST                           = %s" % coders)			
  print ("* MAXIMUM NUMBER OF RETRIES             = %s" % MAX_NUM_RETRIES)
  print ("* MAXIMUM NUMBER OF OPPS TO CODE        = %s" % CODE_OPPS_MAX)
  print ("* INPUT JSON FILE NAME                  = %s" % APLANS_FN)
  print ("* CODER OPPS PER PLAN                   = %d" % OPPS_PLAN_TOT[0])
  print ("* QA1 OPPS PER PLAN                     = %d" % OPPS_PLAN_TOT[1])
  print ("* QA2 OPPS PER PLAN                     = %d" % OPPS_PLAN_TOT[2])
  print ("* QA3 OPPS PER PLAN                     = %d" % OPPS_PLAN_TOT[3])
  print ("==============================================================================")
  print "Annotations plan loaded ..."	
  user_response = raw_input("Enter 'P' to Proceed or 'Q' to Quit: ")
  if user_response.upper() == "Q":
    print "exiting ..."
    quit()
  else:
    print "proceeding ..."	
  return OPPS_PLAN_TOT

#============================================================================================================
#=================================== LOG INTO HCC ===========================================================
#============================================================================================================
 
def logInToHCC(coder, pw): 
  global TOKEN, SESSID, DATA, HEADERS, COOKIES, TOKEN, APXTOKEN, JSESSIONID
  
  
  print ("Logging into HCC ...")
  print ("==============================================================================")
	
  url = URL+'/account/login/'
  referer = URL+'/account/login/'
  
  response = requests.get(url)
  print "* CONNECT TO HOST    = "+str(response.status_code)
  if response.status_code == 500:
  	print "* Connection to host = FAILED QA"
  	logInToHCC()
#-----------------------------------------------------------------------------------------  	
  url = "https://hcceng.apixio.com/"
  response = requests.get(url)
  print "* LOGIN PAGE         = "+str(response.status_code)
#-----------------------------------------------------------------------------------------  	
  TOKEN = response.cookies["JSESSIONID"]
  SESSID = response.cookies["JSESSIONID"]
  COOKIES = dict(csrftoken=''+TOKEN+'')
  JSESSIONID = response.cookies["JSESSIONID"]
  
  origin = "https://accounts-stg.apixio.com"
  referer = "https://accounts-stg.apixio.com/?caller=hcc_eng"
  host = "accounts-stg.apixio.com"
  url = "https://accounts-stg.apixio.com/"
  
  DATA = {'username': coder, 'password': pw, 'hash':'', 'caller':'hcc_eng', 'log_ref':'1441056621484', 'origin':'loging' }
  
  
  HEADERS = { \
  			'Accept': '*/*', \
  			'Accept-Encoding': 'gzip, deflate', \
  			'Accept-Language': 'en-US,en;q=0.8', \
  			'Connection': 'keep-alive', \
  			'Content-Length': '1105', \
			'Cookie': 'JSESSIONID='+TOKEN, \
			'Host': host, \
			'Origin': origin, \
			'Referer': referer \
			}	
  					
  response = requests.post(url, data=DATA, headers=HEADERS)  
  TOKEN = response.cookies["csrftoken"]
  SESSID = response.cookies["sessionid"]
  APXTOKEN = str(apxapi.APXSession(coder,pw).external_token())
  COOKIES = dict(csrftoken=''+TOKEN+'', sessionid=''+SESSID+'', ApxToken=APXTOKEN)
  
  print("* URL                = %s" % url)
  print("* CODER NUMBER       = %d of %d" % ((coders.index(coder)+1), len(coders)))
  print("* CODER              = %s" % coder)
  print("* PASSWORD           = %s" % pw)
  print("* CSRFTOKEN          = %s" % TOKEN)
  print("* APXTOKEN           = %s" % APXTOKEN)
  print("* SESSID             = %s" % SESSID)
  print("* JSESSIONID         = %s" % JSESSIONID)
  
  print "* LOG IN CODER       = "+str(response.status_code)
  #quit()
  if response.status_code == 500:
  	print "* Log in user = FAILED QA"
  	logInToHCC()
  
  print ("==============================================================================")
  	
  return 0	
  	
#============================================================================================================
#====================================== ACT ON DOC (FINDING) ================================================
#============================================================================================================
def debug_act_on_doc(opportunity, finding, finding_id, testname, doc_no_current, doc_no_max, action, coder):
  
  hcc = opportunity.get("code").get("hcc")
  label_set_version = opportunity.get("code").get("labelSetVersion")
  sweep = opportunity.get("code").get("sweep")
  model_payment_year = opportunity.get("code").get("modelPaymentYear")
  patient_id = opportunity.get("patientId")
  finding_ids = opportunity.get("finding_ids")
  organization = opportunity.get("organization")
  transaction_id = opportunity.get("transactionId")
  patient_org_id = finding.get("patient_org_id")  
  document_uuid = finding.get("sourceId")  
  retrieved_id = "SequenceKey(OrgName(%s);PatientId(%s);HccDescriptor(%s,%s,%s,%s))"%(patient_org_id,patient_id,hcc,label_set_version,sweep,model_payment_year)
  
  print("****************************************************")
  if action == 0:
    print("* Action                    = VIEW ONLY - DO NOTHING")
  elif action == 1:
    print("* Action                    = ACCEPT")
  elif action == 2:
    print("* Action                    = REJECT")
  elif action == 3:
    print("* Action                    = SKIP")
  print("*")
  print("* Patient id                = %s" % opportunity.get("patientId"))
  print("* Org id                    = %s" % opportunity.get("patient").get("org_id"))
  print("* Document id               = %s" % finding.get("sourceId"))
  print("* HCC                       = %s" % retrieved_id)
  print("* Total number of docs      = %s" % doc_no_max)
  print("****************************************************")
  #user_response = raw_input("Enter 'P' to Proceed or 'Q' to Quit: ")
  #if user_response.upper() == "Q":
  #  print "exiting ..."
  #  quit()

  if action > 0:
    print action
    quit()


  return 0
	
#============================================================================================================  
def act_on_doc(opportunity, finding, finding_id, testname, doc_no_current, doc_no_max, action, coder):
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
    	#'Cookie': 'csrftoken='+TOKEN+'; sessionid='+SESSID+' ', \
    	'Cookie': 'csrftoken='+TOKEN+'; sessionid='+JSESSIONID+'; ApxToken='+APXTOKEN+' ', \
    	'X_REQUESTED_WITH': 'XMLHttpRequest', \
    	'X-CSRFToken': TOKEN \
    	}	

  for i in range(0,1,1):
    if (action == 0): # Do NOT Accept or Reject Doc
      print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print("* CODER ACTION     = No action taken - View Only")
      print("* CODER / QA       = %s" % (coder))
          
    elif (action == 1): #=============================== ACCEPT DOC ==============
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
			"hcc": opportunity.get("code").get("hcc") \
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
      if response.status_code == 200:
        print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
        print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = 200 OK")
        print("* CODER / QA       = %s" % (coder))
      else:
        print("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)

      
    elif (action == 2): #================================== REJECT DOC ===========
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
			"hcc": opportunity.get("code").get("hcc") \
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
      if response.status_code == 200:
        print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
        print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = 200 OK")
        print("* CODER / QA       = %s" % (coder))
      else:
        print("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)

      
    elif (action == 3): #=========================== SKIP OPP ====================
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
			"hcc": opportunity.get("code").get("hcc") \
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
      if response.status_code == 200:
        print "* HCC CODE         = %s" % str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
        print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = 200 OK")
        print("* CODER / QA       = %s" % (coder))
      else:
        print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)

    else:
      print("* CODER ACTION     = Unknown\n")
    print("\n")
   
  return 0

#============================================================================================================
#========================================== GET CODER TYPE ==================================================
#============================================================================================================    

def getCoderType(coder):
  if ("coder" in coder) or ("mmgenergyes@apixio.net" in coder):
    ctype = "coder"
  elif "qa1" in coder:
    ctype = "qa1"
  elif "qa2" in coder:
    ctype = "qa2"
  elif "qa3" in coder:
    ctype = "qa3"
  else:
    ctype = coder          
  return (ctype)
#============================================================================================================
#========================================== GET ACTION ======================================================
#============================================================================================================  

def getActions(opportunity, finding, coder):
  global OPPS_PLAN_TOT, OPPS_SERVED_TOT, FINDINGS_ANNO_TOT 
      # Available return actions:
      # 0 - nothing or view only
      # 1 - accept
      # 2 - reject
      # 3 - skip
  
  aplans = APLANS
    					
  coder_steps = {"coder": 0, "qa1": 1, "qa2": 2, "qa3": 3}  					  									
  actions_dict =   {"view" : 0, "accept" : 1, "reject" : 2, "skip" : 3}					
  							  
  # Information from pulled opportunity and finding  
  hcc = opportunity.get("code").get("hcc")
  label_set_version = opportunity.get("code").get("labelSetVersion")
  sweep = opportunity.get("code").get("sweep")
  model_payment_year = opportunity.get("code").get("modelPaymentYear")
  patient_id = opportunity.get("patientId")
  finding_ids = opportunity.get("finding_ids")
  organization = opportunity.get("organization")
  transaction_id = opportunity.get("transactionId")
  patient_org_id = finding.get("patient_org_id")  
  document_uuid = finding.get("sourceId")
  
  #SequenceKey(OrgName(415);PatientId(b5ca1144-3bf8-4ecd-9a59-c497702890f6);HccDescriptor(157,V12,finalReconciliation,2015))



  retrieved_id = "SequenceKey(OrgName(%s);PatientId(%s);HccDescriptor(%s,%s,%s,%s))"%(patient_org_id,patient_id,hcc,label_set_version,sweep,model_payment_year)


  #retrieved_id = "SequenceKey(OrgName(372);PatientId(3c2470f3-daf2-436c-ae29-ae98cb5caf17);HccDescriptor(79,V12,initial,2014))"
  #retrieved_id = "SequenceKey(OrgName(372);PatientId(3c2470f3-daf2-436c-ae29-ae98cb5caf17);HccDescriptor(79,V12,initial,2014))"
  #print retrieved_id
  #document_uuid = "899c478f-5cc0-405a-a512-30d0287992d0"
  #document_uuid = "e2311453-0417-48be-a4bc-0b6cbbc68fc9"
  
  
  ctype = getCoderType(coder)
  
  
  # Match ID and State then build a set of actions
  action = 0
  action_index = coder_steps.get(ctype)
  step_index = coder_steps.get(ctype)
  
  i = 0
  for aplan in aplans:
    if (aplan.get("id") == retrieved_id):
      #i += 1
      #print json.dumps(aplan)
      #print i
      j = -1
      for step in aplan.get("steps"):
        j += 1
        if (step.get("findingId") == document_uuid) and (step_index == j):
          action = actions_dict.get(step.get("action"))
          string_action = step.get("action")
          #print json.dumps(step)
          #print step.get("action")
          #print j
          #print action
     
       
  if action == 0:
    print ("* ACTION SELECTED  = None")
    return 0
  
  #print ("* ACTIONS LIST     = %s" % actions)
  #action = actions[coder_steps.get(getCoderType(coder))]
      
  # 0 - coder
  # 1 - QA1
  # 2 - QA2
  # 3 - QA3
  
  OPPS_SERVED_TOT[coder_steps.get(ctype)] += 1
  
  #"0" - coder [view, accept, reject, skip]
  #"1" - QA1 [view, accept, reject, skip]
  #"2" - QA2 [view, accept, reject, skip]
  #"3" - QA3 [view, accept, reject, skip]
  
  FINDINGS_ANNO_TOT.get(str(coder_steps.get(ctype)))[action] += 1
  
  print ("* ACTION SELECTED  = %s" % string_action) 
  #quit()
  return (action)

#============================================================================================================
#========================================== START CODING ====================================================
#============================================================================================================  	
  
def startCoding(coder):
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION, TOTAL_OPPS_SERVED, CODING_OPP_CURRENT
  global VOO, VAO, VRO, VSO
  global PERCENT_OF_SERVED, HCC, COUNT_OF_SERVED, OPPS_SERVED_TOT

  coder_steps = {"coder": 0, "qa1": 1, "qa2": 2, "qa3": 3} 

  print("-------------------------------------------------------------------------------")
  print("* URL                = %s" % URL)
  print("* CODER USERNAME     = %s" % coder)
  print("* CODER PASSWORD     = %s" % pw)
  print("* MAX PATIENT OPP(S) = %s" % CODE_OPPS_MAX)
  print("* MAX RETRIES        = %s" % MAX_NUM_RETRIES)
  print("* INPUT JSON FILE    = %s" % APLANS_FN)
  print("-------------------------------------------------------------------------------")

  buckets = -1
    
  print("* URL                = %s/api/next-work-item/" % URL)
  print("* csrftoken          = %s" % TOKEN)
  print("* ApxToken           = %s" % APXTOKEN)
  print("* JSESSIONID         = %s" % JSESSIONID) 
  
  HEADERS = { \
  			'Accept': 'application/json, text/plain, */*', \
  			'Accept-Encoding': 'gzip, deflate, sdch', \
  			'Accept-Language': 'en-US,en;q=0.8', \
  			'Connection': 'keep-alive', \
			'Cookie': 'csrftoken='+TOKEN+'; sessionid='+JSESSIONID+'; ApxToken='+APXTOKEN+' ', \
			'Host': 'hcceng.apixio.com', \
			'Referer': 'https://hcceng.apixio.com/' \
			}	
			
  DATA = {}
  
  for coding_opp_current in range(1, (int(CODE_OPPS_MAX)+1)):
    testCode = 10 + (1 * coding_opp_current)
    response = requests.get(URL + "/api/next-work-item/", data=DATA, headers=HEADERS)
    print ("* URL                = %s/api/next-work-item/" % URL)
    print ("* GET CODNG OPP      = %s" % response.status_code)
    
    
    
    if response.status_code != ok:
    	print "=================================================="
    	print "Failure occurred !!!"
    	
    	print response.cookies.list_domains()
    	print response.cookies.list_paths()
    	print response.cookies.get_dict()
    	print response.cookies
    	print response.status_code
    	print response.headers
    	print response.text
    	print json.dumps(response.json())
    	print "=================================================="
    	print("WARNING: No More Opportunities For This Coder")
    	return 0
    else:	
    	opportunity = response.json()
    	OPPS_SERVED_TOT[coder_steps.get(getCoderType(coder))] += 1
  
    hcc = opportunity.get("code").get("hcc")
    label_set_version = opportunity.get("code").get("labelSetVersion")
    sweep = opportunity.get("code").get("sweep")
    model_payment_year = opportunity.get("code").get("modelPaymentYear")
    
    print "\n"
    print "********************************************************************************************"
    print "* HCC CODE         = %s" % hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year
    print "* patient id       = %s" % opportunity.get("patientId")
    finding_ids = opportunity.get("finding_ids")
    print "* document id      = %s" % finding_ids[0]
    print "********************************************************************************************"
    print "\n"

    patient_details = response.text
    if opportunity == None:
      print("WARNING: No More Opportunities For This Coder")
      return 0
            
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
    

    test_counter = 0
    doc_no_current = 0
    #doc_no_max = 1
    doc_no_max = len(findings)
    for finding in findings:
      finding_id = finding_ids[doc_no_current]
      doc_no_current += 1
      patient_org_id = finding.get("patient_org_id")  
      document_uuid = finding.get("sourceId")
      document_title = finding.get("document_title")
      date_of_service = finding.get("doc_date")
      mime_type = finding.get("mimeType")
      if mime_type == None:
    	  mime_type = "text/plain"
      
      print("PATIENT DOC %d OF %d"    % (doc_no_current, doc_no_max))
      print("* STATUS           = %s" % (status))
      print("* CODER / QA       = %s" % (coder))
      print("* PATIENT ORG      = %s" % (patient_org_id))
      print("* PATIENT ID       = %s" % (patient_id))
      print("* FINDING ID       = %s" % (finding_id))
      print("* AVAILABLE CODES  = %s" % (numpossiblecodes))
      print("* PROJECT ID       = %s" % (project))
      print("* DOC UUID         = %s" % (document_uuid))
      print("* DOC TITLE        = %s" % (document_title))
      print("* DOC DATE         = %s" % (date_of_service))
      print("* DOC TYPE         = %s" % (mime_type))
      
      
      test_counter = test_counter + 1
      response = requests.get(URL + "/api/document-text/" + document_uuid, data=DATA, headers=HEADERS)
      print "* GET SCRBLE DOC   = %s" % response.status_code
      print "* DOCUMENT TITLE   = %s" % finding.get("document_title")      
      test_counter += 1
    
      #act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max, getActions(opportunity, finding, coder), coder)
      debug_act_on_doc(opportunity, finding, finding_id, testCode + test_counter, doc_no_current, doc_no_max, getActions(opportunity, finding, coder), coder)
  return 0

#============================================================================================================
#========================================== LOGOUT FUNCTION =================================================
#============================================================================================================  	

def logout():
  print("-------------------------------------------------------------------------------")
  testCode = 99
  response = requests.get(URL + "/account/logout")    
  #print "* LOGOUT           = "+str(response.status_code)  
  if response.status_code == 200:
    print("* CODER ACTION     = Logout\n* HCC RESPONSE     = 200 OK")
  else:
    print("* CODER ACTION     = Logout\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  return 0

##################################################################################################################
# HELPER FUNCTIONS ###############################################################################################
##################################################################################################################

	
def printResultsSummary():
	print("=============================================================================")
	print("Test execution results summary:")
	print("=============================================================================")
	print("* MAXIMUM NUMBER OF OPPS TO CODE        = %s" % CODE_OPPS_MAX)
	print("* INPUT JSON FILE NAME                  = %s" % APLANS_FN)
	print("* CODER OPPS PER PLAN                   = %d" % OPPS_PLAN_TOT[0])
	print("* QA1 OPPS PER PLAN                     = %d" % OPPS_PLAN_TOT[1])
	print("* QA2 OPPS PER PLAN                     = %d" % OPPS_PLAN_TOT[2])
	print("* QA3 OPPS PER PLAN                     = %d" % OPPS_PLAN_TOT[3])
	print("* CODER OPPS SERVED BY HCC              = %d" % OPPS_SERVED_TOT[0])
	print("* QA1 OPPS SERVED BY HCC                = %d" % OPPS_SERVED_TOT[1])
	print("* QA2 OPPS SERVED BY HCC                = %d" % OPPS_SERVED_TOT[2])
	print("* QA3 OPPS SERVED BY HCC                = %d" % OPPS_SERVED_TOT[3])
	print("* CODER FINDINGS V/A/R/S TOTALS         = %s" % FINDINGS_ANNO_TOT.get("0"))
	print("* QA1 FINDINGS V/A/R/S TOTALS           = %s" % FINDINGS_ANNO_TOT.get("1"))
	print("* QA2 FINDINGS V/A/R/S TOTALS           = %s" % FINDINGS_ANNO_TOT.get("2"))
	print("* QA3 FINDINGS V/A/R/S TOTALS           = %s" % FINDINGS_ANNO_TOT.get("3")) 
	print("=============================================================================")
	print("=============================================================================")
	print("=============================================================================")	

###########################################################################################################################################
	
def checkEnvironmentandReceivers():
	# Environment for OppRtrOptTest is passed as a paramater. Staging is a default value
	# default value for environment is engineering
	# Arg1 - environment
	# Arg2 - report recipient
	
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global ENERGY_RTR_URL, DOMAIN, URL, USERNAME, PASSWORD, TOKEN_URL, UA_URL
	
	# Environment for OppRtrOptTest is passed as a paramater. Staging is a default value
	
	print ("\nSetting environment ...")
	if len(sys.argv) < 2:
		ENVIRONMENT="engineering"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		#USERNAME="apxdemot0138"
		#PASSWORD="Hadoop.4522"
		ENVIRONMENT = "production"
		ENERGY_RTR_URL = "https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode"
		TOKEN_URL="https://tokenizer-stg.apixio.com:7075/tokens"
		UA_URL="https://useraccount-stg.apixio.com:7076"
	elif (ENVIRONMENT.upper() == "ENGINEERING"):
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "engineering"
		DOMAIN="hcceng.apixio.com"
		URL="https://hcceng.apixio.com"
		#USERNAME="mmgenergyes@apixio.net"
		#PASSWORD="apixio.123"
		ENERGY_RTR_URL = "https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode"
		TOKEN_URL="https://tokenizer-stg.apixio.com:7075/tokens"
		UA_URL="https://useraccount-stg.apixio.com:7076"
	else:
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
		ENERGY_RTR_URL = "https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode"
		TOKEN_URL="https://tokenizer-stg.apixio.com:7075/tokens"
		UA_URL="https://useraccount-stg.apixio.com:7076"
			
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS2=str(sys.argv[3])
		HTML_RECEIVERS="""To: Eng <%s>,Ops <%s>\n""" % (str(sys.argv[2]), str(sys.argv[3]))
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS2="abeyk@apixio.com"
		HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""
				
	
	print ("==============================================================================")				
	print ("* ENVIRONMENT                           = %s" % ENVIRONMENT)
	print ("* HCC HOST                              = %s" % URL)
	print ("* HCC DOMAIN                            = %s" % DOMAIN)
	print ("* REPORT RECEIVERS                      = %s, %s" % (RECEIVERS, RECEIVERS2))
	print ("==============================================================================")
	print ("Completed setting enviroment ...\n")	

###########################################################################################################################################

def confirmSettings():
	print ("==============================================================================")				
	print ("* VERSION                               = %s" % VERSION)
	print ("* ENVIRONMENT                           = %s" % ENVIRONMENT)
	print ("* HCC HOST                              = %s" % URL)
	print ("* HCC DOMAIN                            = %s" % DOMAIN)
	print ("* REPORT RECEIVERS                      = %s, %s" % (RECEIVERS, RECEIVERS2))
	print ("* CODER                                 = %s" % coder)
	print ("* PASSWORD                              = %s" % pw)
	print ("* CSRFTOKEN                             = %s" % TOKEN)
	print ("* APXTOKEN                              = %s" % APXTOKEN)
	print ("* SESSID                                = %s" % SESSID)
	print ("* JSESSIONID                            = %s" % JSESSIONID)
	print ("* MAXIMUM NUMBER OF RETRIES             = %s" % MAX_NUM_RETRIES)
	print ("* MAXIMUM NUMBER OF OPPS TO CODE        = %s" % CODE_OPPS_MAX)
	print ("==============================================================================")
	user_response = raw_input("Enter 'P' to Proceed or 'Q' to Quit: ")
	if user_response.upper() == "Q":
		print "exiting ..."
		quit()
	else:
		print "proceeding ..."	
	return()

###########################################################################################################################################

def writeReportHeader ():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Begin writing report header ...\n")
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
	if sortby == "value":
		sorteditems = sorted(srcedict.items(), key=operator.itemgetter(1), reverse=True)
		ctr = 0
		for item in sorteditems:
			if item[1] > 0:
				if ctr == 0:
					b_color = '#FFFF00'
					most_served = item[1]
				else:
					if (item[1] == most_served) or (item[0] == TARGET_HCC):
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
    
def log(text):
	global REPORT
	#REPORT = REPORT + text + "<br>"
	print(text)
	return 0    

###########################################################################################################################################
# MAIN FUNCTION CALLER ####################################################################################################################
###########################################################################################################################################

os.system('clear')

#coders = ["qa-mp-coder@apixio.net", "qa-mp-qa1@apixio.net", "qa-mp-qa2@apixio.net", "qa-mp-qa3@apixio.net"]
#coders = ["mmgenergyes@apixio.net"]
coders = ["qa-mp-coder@apixio.net"]
#coders = ["qa-mp-qa1@apixio.net"]
#coders = ["qa-mp-qa2@apixio.net"]
#coders = ["qa-mp-qa3@apixio.net"]
pw = "apixio.123"

loadAnnotationPlan()
checkEnvironmentandReceivers()

#writeReportHeader()	
for coder in coders:
	logInToHCC(coder, pw)
	startCoding(coder)
	logout()


printResultsSummary()
#writeReportFooter()
#archiveReport()
#emailReport()
