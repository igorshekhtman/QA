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
#		   1.) Clean profile
#		   2.) Install catch-all rule
#		   3.) Turn ON energy routing (use Python utility: 
#				python2.7 energyroutingstatus.py engineering none
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.7 environment is available
#          * From QA2 server (54.176.225.214) /mnt/automation/hcc folder enter "python2.7 opprouteroptimization.py"
#		   * note: opprouteroptimization.csv configuration file must coexist in same folder as opprouteroptimization.py
#
# USAGE:
#          * Set the global variables (CSV_CONFIG_FILE_PATH and CSV_CONFIG_FILE_NAME), see below
#          * Configure global parameters in opprouteroptimization.csv located in the same folder
#          * Results will be printed on Console screen as well as mailed via QA report
#		   ***************************************************************************************************************
#		   * python2.7 esopprouteroptimization.py staging ishekhtman@apixio.com ishekhtman@apixio.com
#		   ***************************************************************************************************************
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
import time
import csv
import operator
import os
import shutil
import json
from time import gmtime, strftime
import mmap
from pylab import *
from matplotlib.pyplot import *
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import collections
requests.packages.urllib3.disable_warnings()

# GLOBAL VARIABLES #######################################################################

START_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
TIME_START=time.time()
MONTH_FMN=strftime("%B", gmtime())
CURDAY=strftime("%d", gmtime())
CURMONTH=strftime("%m", gmtime())

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

FAILED_TOT = []
SUCCEEDED_TOT = []
RETRIED_TOT = []

for i in range (0, 17):
	FAILED_TOT.append(0)
	SUCCEEDED_TOT.append(0)
	RETRIED_TOT.append(0)

	
TOTAL_OPPS_ACCEPTED = 0
TOTAL_OPPS_REJECTED = 0
TOTAL_OPPS_SKIPPED = 0
TOTAL_OPPS_SERVED = 0
TOTAL_DOCS_REJECTED = 0
TOTAL_DOCS_ACCEPTED = 0


HCC = {str(key): 0 for key in range(0, 200)}
MODEL_PAYMENT_YEAR = {str(key): 0 for key in range(2000, 2040)}
LABEL_SET_VERSION = {'V12': 0, 'V22': 0}
SWEEP = {'midYear': 0, 'finalReconciliation': 0, 'initial': 0}
#=======================================================================================================================
def readConfigurationFile(filename):
  result={ }
  csvfile = open(filename, 'rb')
  reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
  for row in reader:
    if (str(row[0])[0:1] <> '#') and (str(row[0])[0:1] <> ' '):
      result[row[0]] = row[1]
  globals().update(result)
  return result
#=======================================================================================================================
def loginHCC(options):

  url = options['env_hosts']['hcchost']+'account/login/'
  print LS
  print "* Url 1".ljust(25)+" = " + url
  response = requests.get(url)
  print "* Status Code".ljust(25)+" = "+str(response.status_code) + " " + stat_codes[response.status_code]
  print LSS
  if response.status_code != r_stat_codes['ok']:
    print "* Connection to host".just(25)+" =  FAILED"
    print LS
    quit()
#-----------------------------------------------------------------------------------------------------------------------
  url = options['env_hosts']['hcchost']+""
  print "* Url 2".ljust(25)+" = " + url
  response = requests.get(url)
  print "* Status Code".ljust(25)+" = "+str(response.status_code) + " " + stat_codes[response.status_code]
  print LSS
  if response.status_code != r_stat_codes['ok']:
    quit()
#-----------------------------------------------------------------------------------------------------------------------
  jsessionid = response.cookies["JSESSIONID"]
  url = options['env_hosts']['ssohost']+"/"
  DATA = {'username': options['usr'], 'password': options['pwd'], 'hash':'', 'caller':options['env_hosts']['caller'], 'log_ref':'1441056621484', 'origin':'loging' }
  HEADERS = {'Cookie': 'JSESSIONID='+jsessionid}

  print "* Url 3".ljust(25)+ " = " + url
  response = requests.post(url, data=DATA, headers=HEADERS)
  print "* Status Code".ljust(25)+" = "+ str(response.status_code) + " " + stat_codes[response.status_code]
  print LSS
  if response.status_code != r_stat_codes['ok']:
    quit()

  token = response.cookies["csrftoken"]
  sessid = response.cookies["sessionid"]
  apxtoken = obtainExternalToken(options)
  cookies = dict(csrftoken=''+token+'', sessionid=''+sessid+'', ApxToken=''+apxtoken+'', jsessionid=''+jsessionid)

  print "* Url 5".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ options['usr']
  print "* Password".ljust(25)+" = "+ options['pwd']
  print "* Cookies".ljust(25)+" = "+ "\n".ljust(29).join(["%s:%s" % (key, ('%('+key+')s') % cookies) for key in sorted(cookies)])
  print "* Log in user".ljust(25)+" = "+str(response.status_code) + " " + stat_codes[response.status_code]
  print LSS
  print "* Environment".ljust(25)+" = "+(options['env'])
  print "* Max # of Opps".ljust(25)+" = "+ str(options['max_opps'])
  print "* Max # of Retries".ljust(25)+" = "+ str(options['max_ret'])
  print "* Coding Delay Time".ljust(25)+" = "+ str(options['coding_delay_time'])+" second(s)"
  print "* Accept Date of Service".ljust(25)+" = "+str(options['dos'])
  print "* Report Recepients".ljust(25)+" = "+str(options['report_recepients'])
  if response.status_code != r_stat_codes['ok']:
    quit()
  print LS
  return(cookies)
  	
#=======================================================================================================================
def act_on_doc(opportunity, finding, finding_id, doc_no_current, doc_no_max, options, cookies, action):
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
    	'Referer': options['env_hosts']['hcchost']+'/', \
        'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"], \
    	'X_REQUESTED_WITH': 'XMLHttpRequest', \
        'X-CSRFToken': cookies["csrftoken"] \
    	}

  if action == "0": # Do NOT Accept or Reject Doc
    print "* HCC CODE".ljust(25)+ " = " + str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
    print "* CODER ACTION".ljust(25)+ " = " + "Do NOT Accept or Reject Doc"
    IncrementTestResultsTotals("coding view only", 200)
  elif action == "1": #=============================== ACCEPT DOC ==============
    TOTAL_DOCS_ACCEPTED += 1
    #finding_id = scorable.get("id")
    print "* FINDING ID".ljust(25)+ " = " + str(finding_id)
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
			#"dateOfService": finding.get("doc_date"), \
			"dateOfService": options['dos'], \
			"comment": "Grinder Flag for Review" \
			}}}
    response = requests.post(options['env_hosts']['hcchost']+ "api/annotate/", cookies=cookies, data=json.dumps(DATA), headers=HEADERS)
    print "* ANNOTATE FINDING".ljust(25)+ " = " + str(response.status_code)
    IncrementTestResultsTotals("coding view and accept", response.status_code)
    if response.status_code == r_stat_codes['ok']:
      print "* HCC CODE".ljust(25)+ " = " + str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print "* CODER ACTION".ljust(25)+ " = " + "Accept Doc"
      print "* HCC RESPONSE".ljust(25)+ " = " + str(response.status_code) + " " + stat_codes[response.status_code]
    else:
      print "* CODER ACTION".ljust(25)+ "Accept Doc"
      print "* HCC RESPONSE".ljust(25)+ "WARNING : Bad HCC Server Response " + str(response.status_code) + " " + stat_codes[response.status_code]
      act_on_doc(opportunity, finding, finding_id, doc_no_current, doc_no_max)
  elif action == "2": #================================== REJECT DOC ===========
    TOTAL_DOCS_REJECTED += 1
    #finding_id = scorable.get("id")
    print "* FINDING ID".ljust(25)+ " = " + str(finding_id)
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
    response = requests.post(options['env_hosts']['hcchost']+ "api/annotate/", cookies=cookies, data=json.dumps(DATA), headers=HEADERS)	
    IncrementTestResultsTotals("coding view and reject", response.status_code)
    if response.status_code == r_stat_codes['ok']:
      print "* HCC CODE".ljust(25)+ " = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print "* CODER ACTION".ljust(25)+ " = "+ "Reject Doc"
      print "* HCC RESPONSE".ljust(25)+ " = "+ str(response.status_code) + " " + stat_codes[response.status_code]
    else:
      print "* CODER ACTION".ljust(25) + "Reject Doc"
      print "* HCC RESPONSE".ljust(25) + "WARNING : Bad HCC Server Response " + str(response.status_code) + " " + stat_codes[response.status_code]
      act_on_doc(opportunity, finding, finding_id, doc_no_current, doc_no_max)
  elif action == "3": #=========================== SKIP OPP ====================
    TOTAL_OPPS_SKIPPED += 1
    #finding_id = scorable.get("id")
    print "* FINDING ID".ljust(25)+ " = " + str(finding_id)
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
    response = requests.post(options['env_hosts']['hcchost']+ "api/annotate/", cookies=cookies, data=json.dumps(DATA), headers=HEADERS)		
    IncrementTestResultsTotals("coding view and skip", response.status_code)
    if response.status_code ==  r_stat_codes['ok']:
      print "* HCC CODE".ljust(25)+ " = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print "* CODER ACTION".ljust(25)+ " = " + "Skip Opp"
      print "* HCC RESPONSE".ljust(25)+ " = " + str(response.status_code) + " " + str(response.status_code) + " " + stat_codes[response.status_code]
    else:
      print "* CODER ACTION".ljust(25) + " = " + "Skip Opp"
      print "* HCC RESPONSE".ljust(25) + " = " + "WARNING : Bad HCC Server Response " + str(response.status_code) + " " + stat_codes[response.status_code]
      act_on_doc(opportunity, finding, finding_id, doc_no_current, doc_no_max)
  else:
    print "* CODER ACTION".ljust(25) + " = " + "Unknown"
  return 0

#=======================================================================================================================
  
def startCoding(options, cookies):
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION, TOTAL_OPPS_SERVED, CODING_OPP_CURRENT
  global VOO, VAO, VRO, VSO
  global PERCENT_OF_SERVED, HCC, COUNT_OF_SERVED
  #global model_year, payment_year, hcc, model_run

  print LSS
  print "* HCC Url".ljust(25)+" = " + options['env_hosts']['hcchost']
  print "* Coder name".ljust(25)+ " = " + options['usr']
  print "* Coder pwd".ljust(25)+ " = " + options['pwd']
  print "* Max Opp(s)".ljust(25)+ " = " + str(options['max_opps'])
  print LSS
  #====================================================
  # main loop controlling number of OPPS to process
  #====================================================
  buckets = -1
  nwiurl = options['env_hosts']['hcchost']+"api/next-work-item/"
  print "* HCC Url".ljust(25)+" = "+ nwiurl
  print "* csrftoken".ljust(25)+" = "+ cookies['csrftoken']
  print "* ApxToken".ljust(25)+" = "+ cookies['ApxToken']
  print "* sessionid".ljust(25)+" = "+ cookies['sessionid']
  
  
  HEADERS = {'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"]}			
  DATA = {}
  
  
  
  for coding_opp_current in range(1, (int(options['max_opps'])+1)):
    time.sleep(int(options['coding_delay_time']))
    testCode = 10 + (1 * coding_opp_current)
    response = requests.get(nwiurl, data=DATA, headers=HEADERS)
    print "* Url".ljust(25)+" = "+ nwiurl
    print "* Get Coding Opp".ljust(25)+" = "+ str(response.status_code) + " " + stat_codes[response.status_code]
    
    IncrementTestResultsTotals("coding opportunity check", response.status_code)
    
    
    if response.status_code != r_stat_codes['ok']:
      print LS
      print "* Failed Get Coding Opp".ljust(25)+" = "+str(response.status_code)
      print LS
      quit()
    else:	
      opportunity = response.json()
    ######################################################################################

    hcc = opportunity.get("code").get("hcc")
    tallyDetails("hcc", hcc)
    label_set_version = opportunity.get("code").get("labelSetVersion")
    tallyDetails("label_set_version", label_set_version)
    sweep = opportunity.get("code").get("sweep")
    tallyDetails("sweep", sweep)
    model_payment_year = opportunity.get("code").get("modelPaymentYear")
    tallyDetails("model_payment_year", model_payment_year)

    print "\n"+SL
    print "* HCC CODE".ljust(25)+" = "+hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year
    print SL+"\n"

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
    #print LS
    print "PATIENT OPP %d OF %d" % (coding_opp_current, int(options['max_opps']))
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
      
      print "PATIENT DOC %d OF %d"    % (doc_no_current, doc_no_max)
      print "* STATUS".ljust(25)+ " = " + str(status)
      print "* PATIENT ORG".ljust(25)+ " = " + str(patient_org_id)
      print "* PATIENT ID".ljust(25)+ " = " + str(patient_id)
      print "* FINDING ID".ljust(25)+ " = " + str(finding_id)
      print "* AVAILABLE CODES".ljust(25)+ " = " + str(numpossiblecodes)
      print "* PROJECT ID".ljust(25)+ " = " + str(project)
      print "* DOC UUID".ljust(25)+ " = " + str(document_uuid)
      print "* DOC TITLE".ljust(25)+ " = " + str(document_title)
      print "* DOC DATE".ljust(25)+ " = " + str(date_of_service)
      print "* DOC TYPE".ljust(25)+ " = " + str(mime_type)
      response = requests.get(options['env_hosts']['hcchost'] + "/api/document-text/" + document_uuid, data=DATA, headers=HEADERS)
      print "* GET SCRBLE DOC".ljust(25)+ " = " + str(response.status_code) + " " + stat_codes[response.status_code]
      IncrementTestResultsTotals("coding scorable document check", response.status_code)
      test_counter += 1
      action = WeightedRandomCodingAction(hcc, options)
      act_on_doc(opportunity, finding, finding_id, doc_no_current, doc_no_max, options, cookies, action)

  return 0
#=======================================================================================================================
def logout(options):
  print LS
  testCode = 99
  response = requests.get(options['env_hosts']['hcchost'] + "/account/logout")
  print "* LOGOUT".ljust(25) + " = " +str(response.status_code) + " " + stat_codes[response.status_code]
  IncrementTestResultsTotals("logout", response.status_code)
  if response.status_code != r_stat_codes['ok']:
    print "* CODER ACTION".ljust(25)+ " = " + "Logout"
    print "* HCC RESPONSE".ljust(25)+ " = " + "WARNING : Bad HCC Server Response " + str(response.status_code) + " " + stat_codes[response.status_code]
  return 0
#=======================================================================================================================
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
#=======================================================================================================================
def WeightedRandomCodingAction(hcc_code, options):
	global VOO, VAO, VRO, VSO
	weight = { "0": 0, "1": 0, "2": 0, "3": 0 }
	weight['0'] = int(options['action_weights']['all']['vo'])
	weight['1'] = int(options['action_weights']['all']['va'])
	weight['2'] = int(options['action_weights']['all']['vr'])
	weight['3'] = int(options['action_weights']['all']['vs'])
	action = random.choice([k for k in weight for dummy in range(weight[k])])
	
	weight2 = { "0": 0, "1": 0, "2": 0, "3": 0 }
	weight2['0'] = int(options['action_weights']['target']['vo'])
	weight2['1'] = int(options['action_weights']['target']['va'])
	weight2['2'] = int(options['action_weights']['target']['vr'])
	weight2['3'] = int(options['action_weights']['target']['vs'])
	action2 = random.choice([l for l in weight2 for dummy2 in range(weight2[l])])
	
	#if hcc_code in HCC_CODES_TO_ACCEPT:
	if hcc_code == options['target_hcc']:
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
#=======================================================================================================================
def printResultsSummary():
  print LS
  print "Test execution results summary:"
  print LS
  print "* VIEWED ONLY OPPS".ljust(25)+" = "+ str(VOO)
  print "* ACCEPTED OPPS".ljust(25)+" = "+ str(VAO)
  print "* REJECTED OPPS".ljust(25)+" = "+str(VRO)
  print "* SKIPPED OPPS".ljust(25)+" = "+str(VSO)
  print "* TOTAL OPPS PROCESSED".ljust(25)+" = "+str(VOO+VAO+VRO+VSO)
  print LS
  print "* RETRIED".ljust(25)+" = "+str(RETRIED)
  print "* FAILED".ljust(25)+" = "+str(FAILED)
  print "* SUCCEEDED".ljust(25)+" = "+str(SUCCEEDED)
  print "* TOTAL".ljust(25)+" = "+str(RETRIED+FAILED+SUCCEEDED)
  print LS
  print LS
  print LS
  return()
#=======================================================================================================================
def obtainExternalToken(options):
  url = options['env_hosts']['uahost']+options['env_hosts']['uaport']+'/auths'
  data =    { 'email': options['usr'], 'password': options['pwd']}
  headers = {}
  print "* Url 4".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ options['usr']
  print "* Password".ljust(25)+" = "+ options['pwd']
  response = requests.post(url, data=data, headers=headers)
  statuscode = response.status_code
  if statuscode != r_stat_codes['ok']:
    print "* Ext. token status code".ljust(25)+" = "+ str(statuscode) + " " + stat_codes[response.status_code]
    quit()
  external_token = response.json().get("token")
  print "* External token".ljust(25)+" = "+ response.json().get("token")
  print "* Ext. token status code".ljust(25)+" = "+ str(statuscode) + " " + stat_codes[response.status_code]
  print LSS
  return (external_token)
#=======================================================================================================================
def obtainInternalToken(options, cookies):
  url = options['env_hosts']['tokenhost']
  data =    {}
  headers = {'Authorization': 'Apixio ' + cookies['ApxToken']}
  response = requests.post(url, data=data, headers=headers)
  if response.status_code != r_stat_codes['created']:
      "* Failure".ljust(25)+" = Obtain Internal Token"
      "* Status Code".ljust(25)+" = "+str(response.status_code)
      quit()
  else:
    return ('Apixio '+str(response.json().get("token")))
#=======================================================================================================================
def setEnergyRoutingOn(options, cookies):
  apixio_token = obtainInternalToken(options, cookies)
  url = options['env_hosts']['rtrhost'] + "/true"
  data = {}
  headers = {"Content-Type": "application/json", "Authorization": apixio_token}
  response = requests.put(url, data=json.dumps(data), headers=headers)
  if response.status_code != r_stat_codes['ok']:
    print "* Failure".ljust(25)+" = Enable Energy Routing"
    print "* Status Code".ljust(25)+" = "+str(response.status_code) + " " + stat_codes[response.status_code]
    quit()
  else:
    return (response.json().get("energyRouting"))
#=======================================================================================================================
def confirmSettings(options, cookies):
  print LS
  #print "* Version".ljust(25)+ " = "+ str(VERSION)
  print "* Environment".ljust(25)+" = "+ str(options['env'])
  print "* HCC Host".ljust(25)+" = "+ str(options['env_hosts']['hcchost'])
  print "* Report Receivers".ljust(25)+ " = "+ str(options['report_recepients'])
  print "* HCC User".ljust(25)+ " = "+ str(options['usr'])
  print "* HCC Password".ljust(25)+" = "+ str(options['pwd'])
  print "* Csrftoken".ljust(25)+" = "+ str(cookies['csrftoken'])
  print "* Apxtoken".ljust(25)+" = "+ str(cookies['ApxToken'])
  print "* Sessid".ljust(25)+" = "+str(cookies['sessionid'])
  print "* Jsessionid".ljust(25)+ " = " +str(cookies['jsessionid'])
  print "* Coding Delay".ljust(25)+ " = "+ str(options['coding_delay_time'])+" sec"
  print "* Retries".ljust(25)+" = "+ str(options['max_ret'])
  print "* Max Opps".ljust(25)+" = "+str(options['max_opps'])
  if options['max_opps']%10 !=0:
    print "* Error".ljust(25)+" = Maximum number of opps "+str(options['max_opps'])+" must be divisible by 10"
    quit()
  print "* Energy Routing Status".ljust(25)+ " = "+ str(setEnergyRoutingOn(options, cookies))
  print "* TARGETED HCC".ljust(25)+ " = HCC-"+str(options['target_hcc'])
  print "* OVERALL ACCEPTS".ljust(25)+ " = "+ str(options['action_weights']['all']['va'])+"%"
  print "* OVERALL REJECT".ljust(25)+" = "+ str(options['action_weights']['all']['vr'])+"%"
  print ("* TARG HCC-"+str(options['target_hcc'])+" ACCEPT").ljust(25)+" = "+ str(options['action_weights']['target']['va'])+"%"
  print ("* TARG HCC-"+str(options['target_hcc'])+" REJECT").ljust(25)+" = "+ str(options['action_weights']['target']['vr'])+"%"
  print LS
  user_response = raw_input("Enter 'P' to Proceed or 'Q' to Quit: ")
  if user_response.upper() == "Q":
    print "exiting ..."
    quit()
  else:
    print "proceeding ..."
  return()
#=======================================================================================================================
def writeReportHeader(options):
  global REPORT
  REPORT = """ """
  REPORT += """<h1>Apixio %s Report</h1>""" % (options['rep_type'])
  REPORT += """Run date & time (run): <b>%s</b><br>""" % (strftime("%m/%d/%Y %H:%M:%S", gmtime()))
  REPORT += """Report type: <b>%s</b><br>""" % (options['rep_type'])
  REPORT += """HCC user name: <b>%s</b><br>""" % (options['usr'])
  REPORT += """HCC app url: <b>%s</b><br>""" % (options['env_hosts']['hcchost'])
  REPORT += """Maximum # of Opps: <b>%s</b><br>""" % (options['max_opps'])
  REPORT += """Maximum # of Retries: <b>%s</b><br>""" % (options['max_ret'])
  REPORT += """Coding delay: <b>%s sec</b><br>""" % (options['coding_delay_time'])
  REPORT += """Enviromnent: <b><font color='red'>%s</font></b><br><br>""" % (options['env'])
  REPORT += """<table align="left" width="800" cellpadding="1" cellspacing="1"><tr><td>"""
  return()
#=======================================================================================================================
def writeReportDetails(module):	
  global REPORT
  global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
  REPORT += SUBHDR_TBL % module.upper()
  REPORT += "<table spacing='1' padding='1'><tr><td>Succeeded:</td><td>"+str(SUCCEEDED_TOT[int(MODULES[module])])+"</td></tr>"
  REPORT += "<tr><td>Retried:</td><td>"+str(RETRIED_TOT[int(MODULES[module])])+"</td></tr>"
  REPORT += "<tr><td>Failed:</td><td>"+str(FAILED_TOT[int(MODULES[module])])+"</td></tr></table>"
  if (FAILED_TOT[int(MODULES[module])] > 0) or (RETRIED_TOT[int(MODULES[module])] > 0):
    REPORT += str(FAILED_TBL)
  else:
    REPORT += str(PASSED_TBL)
  return()
#=======================================================================================================================
def drawGraph(srcedict, options):
  global CURDAY, START, STOP
  key = sorted(srcedict.keys())
  temp = []
  for i in key:
    value = srcedict[i]
    temp.append(value)
  x = sorted(srcedict.keys())
  y = temp
  plot(x, y, color='green', linewidth=3, linestyle='solid', marker='o', markerfacecolor='blue', markersize=6)
  xlabel('# of serves per time bucket')
  ylabel('% of targeted HCC-'+str(options['target_hcc'])+' served')
  title('HCC Opportunity Router Optimization Test')
  grid(True)
  savefig(str(CURDAY))
  #show()
  return()
###########################################################################################################################################
def getKey(key):
  try:
    return int(key)
  except ValueError:
    return key
###########################################################################################################################################
def convertJsonToTable(srcedict, sortby):
  global REPORT
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
          if (item[1] == most_served) or (item[0] == options['target_hcc']):
            b_color = '#FFFF00'
          else:
            b_color = '#FFFFFF'
        REPORT += "<tr><td bgcolor='"+b_color+"'> HCC-"+str(item[0])+"</td><td bgcolor='"+b_color+"'><b>"+str(item[1])+"</b></td></tr>"
        ctr += 1
  else:
    sorteditems = sorted(srcedict.items(), key=operator.itemgetter(0), reverse=False)
    for item in sorteditems:
      if item[1] > 0:
        REPORT +="<tr><td>"+str(item[0])+"</td><td><b>"+str(item[1])+"</b></td></tr>"
  REPORT += "</table>"
  return()
#=======================================================================================================================
def extractTargetedHccData(targhcc, srcedict):
  extrdict = {}
  for k, v in sorted(srcedict.iteritems()):
    if targhcc in v.keys():
      extrdict.update({k: v[targhcc]})
    else:
      extrdict.update({k: 0})
  return (extrdict)
#=======================================================================================================================
def writeReportFooter(options):
  global REPORT, SORTED_PERCENT_OF_TARGET_HCC_SERVED, REPORT_EMAIL

  REPORT += "<table align='left' width='800' cellpadding='1' cellspacing='1'>"
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
  REPORT += "<tr><td colspan='2' align='center'><font size='4'><b>TARGETED HCC-%s</b></font></td></tr>" % (options['target_hcc'])
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>Opps served:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % (TOTAL_OPPS_SERVED)
  REPORT += "<tr><td nowrap>Opps skipped:</td><td><b>%s</b></td></tr>" % (TOTAL_OPPS_SKIPPED)
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>Docs accepted:</td><td bgcolor='#D8D8D8'><b>%s</b></td></tr>" % (TOTAL_DOCS_ACCEPTED)
  REPORT += "<tr><td nowrap>Docs rejected:</td><td><b>%s</b></td></tr>" % (TOTAL_DOCS_REJECTED)
		
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>Accepting Opps rate:</td><td bgcolor='#D8D8D8'><b>%s %%</b></td></tr>" % (options['action_weights']['all']['va'])
  REPORT += "<tr><td nowrap>Rejecting Opps rate:</td><td><b>%s %%</b></td></tr>" % (options['action_weights']['all']['vr'])
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>Accepting HCC-%s Opps rate:</td><td bgcolor='#D8D8D8'><b>%s %%</b></td></tr>" % (options['target_hcc'], options['action_weights']['target']['va'])
  REPORT += "<tr><td nowrap>Rejecting HCC-%s Opps rate:</td><td><b>%s %%</b></td></tr>" % (options['target_hcc'], options['action_weights']['target']['vr'])
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
		
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>Model payment year:</td><td bgcolor='#D8D8D8'>"
  convertJsonToTable(MODEL_PAYMENT_YEAR, "key")
  REPORT += "</td></tr>"
  REPORT += "<tr><td nowrap>Sweep:</td><td>"
  convertJsonToTable(SWEEP, "key")
  REPORT += "</td></tr>"
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>Label set version:</td><td bgcolor='#D8D8D8'>"
  convertJsonToTable(LABEL_SET_VERSION, "key")
  REPORT += "</td></tr>"
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
  REPORT += "<tr><td nowrap>HCCs total:</td><td>"
  convertJsonToTable(HCC, "value")
  REPORT += "</td></tr>"
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>HCCs per bucket:</td><td bgcolor='#D8D8D8'>"
  convertJsonToTable(COUNT_OF_SERVED, "key")
  REPORT += "</td></tr>"
  REPORT += "<tr><td nowrap>HCCs % per bucket:</td><td>"
  convertJsonToTable(PERCENT_OF_SERVED, "key")
  REPORT += "</td></tr>"
  REPORT += "<tr><td bgcolor='#D8D8D8' nowrap>HCC-%s %% per bucket:</td><td bgcolor='#D8D8D8'>" % (options['target_hcc'])
  convertJsonToTable(extractTargetedHccData(options['target_hcc'], PERCENT_OF_SERVED), "key")
  REPORT += "</td></tr>"
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
	
  drawGraph(extractTargetedHccData(options['target_hcc'], PERCENT_OF_SERVED), options)
		
  REPORT_EMAIL = "" + REPORT
  REPORT += "<tr><td colspan='2'><img src='"+str(CURDAY)+".png' width='800' height='600'></td></tr>"
  REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><img src='cid:picture@example.com' width='800' height='600'></td></tr>"
  REPORT += "<tr><td colspan='2'><hr></td></tr>"
  REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><hr></td></tr>"
  END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
  REPORT += "<tr><td colspan='2'><br>Start of %s - <b>%s</b></td></tr>" % (options['rep_type'], START_TIME)
  REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><br>Start of %s - <b>%s</b></td></tr>" % (options['rep_type'], START_TIME)
  REPORT += "<tr><td colspan='2'>End of %s - <b>%s</b></td></tr>" % (options['rep_type'], END_TIME)
  REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'>End of %s - <b>%s</b></td></tr>" % (options['rep_type'], END_TIME)
  TIME_END = time.time()
  TIME_TAKEN = TIME_END - TIME_START
  hours, REST = divmod(TIME_TAKEN,3600)
  minutes, seconds = divmod(REST, 60)
  REPORT += "<tr><td colspan='2'>Test Duration: <b>%s hrs %s min %s sec</b><br></td></tr>" % (int(hours), int(minutes), int(seconds))
  REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'>Test Duration: <b>%s hrs %s min %s sec</b><br></td></tr>" % (int(hours), int(minutes), int(seconds))
  REPORT += "<tr><td colspan='2'><br><i>-- Apixio QA Team</i></td></tr>"
  REPORT_EMAIL = REPORT_EMAIL+"<tr><td colspan='2'><br><i>-- Apixio QA Team</i></td></tr>"
  REPORT += "</table>"
  REPORT_EMAIL = REPORT_EMAIL+"</table>"
  REPORT += "</td></tr></table>"
  REPORT_EMAIL = REPORT_EMAIL+"</td></tr></table>"
  return()
#=======================================================================================================================

def archiveReport():
	global DEBUG_MODE, ENVIRONMENT, CURMONTH, CURDAY, IMAGEFILENAME
	if not DEBUG_MODE:
		print ("Archiving report ...\n")
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/opprtropt/"+strftime("%Y", gmtime())+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/opprtropt/"+strftime("%Y", gmtime())+"/"+str(CURMONTH)
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
		REPORTXTSTRING="OppRtrOpt "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+strftime("%Y", gmtime())+"\t"+"reports/"+ENVIRONMENT+"/opprtropt/"+strftime("%Y", gmtime())+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
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

#=======================================================================================================================
def emailReport(options):
  imagefname=str(CURDAY)+".png"
  message = MIMEMultipart('related')
  message.attach(MIMEText((REPORT_EMAIL), 'html'))
  with open(imagefname, 'rb') as image_file:
    image = MIMEImage(image_file.read())
  image.add_header('Content-ID', '<picture@example.com>')
  image.add_header('Content-Disposition', 'inline', filename=imagefname)
  message.attach(image)

  message['From'] = 'Apixio QA <QA@apixio.com>'
  message['To'] = 'To: Eng <eng@apixio.com>,Ops <ops@apixio.com>'
  message['Subject'] = 'ES %s Energy Routing Test Report - %s\n\n' % (options['env'], START_TIME)
  msg_full = message.as_string()
		
  s=smtplib.SMTP()
  s.connect("smtp.gmail.com",587)
  s.starttls()
  s.login("donotreply@apixio.com", "apx.mail47")
  s.sendmail("donotreply@apixio.com", [options['report_recepients']], msg_full)
  s.quit()
  # Delete graph image file from stress_test folder
  os.remove(imagefname)
  print "Report completed, successfully sent email to %s ..." % (options['report_recepients'])
  return()
#=======================================================================================================================
def pages_payload(details):
  report_json = details.json()
  if report_json is not None:
    pages = report_json.get("pages")
    payload = len(details.text)
  else:
    pages = 0
    payload = 0
  return (pages, payload)
#=======================================================================================================================
def IncrementTestResultsTotals(module, code):
  global FAILED, SUCCEEDED, RETRIED
  global FAILED_TOT, SUCCEEDED_TOT, RETRIED_TOT
  if (code == r_stat_codes['ok']) or (code == r_stat_codes['nocontent']):
    SUCCEEDED = SUCCEEDED+1
    SUCCEEDED_TOT[int(MODULES[module])] = SUCCEEDED_TOT[int(MODULES[module])] + 1
  else:
    FAILED = FAILED+1
    FAILED_TOT[int(MODULES[module])] = FAILED_TOT[int(MODULES[module])] + 1
    RETRIED = RETRIED+1
    RETRIED_TOT[int(MODULES[module])] = RETRIED_TOT[int(MODULES[module])] + 1
    if RETRIED > int(MAX_NUM_RETRIES):
      print "Number of retries %s reached pre-set limit of %s.  Exiting now ..." % (RETRIED, MAX_NUM_RETRIES)
      quit()
    if (code == r_stat_codes['unauthorized']):
      print "%s response code received from server.  Re-obtaining Autorization." % code
      loginHCC()
    if ((code == r_stat_codes['servunavail']) or (code == r_stat_codes['nocontent'])) and (module == "coding opportunity check"):
      print "%s response code received from server.  Re-obtaining Next Opportunity." % code
      startCoding()
  return()
#=======================================================================================================================
def getEnvHosts(env):
  if env.lower()[0] == 's':
    hcchost = 'https://hcc-stg.apixio.com/'
    ssohost = 'https://accounts-stg.apixio.com'
    uahost = 'https://useraccount-stg.apixio.com'
    uaport = ':7076'
    caller = 'hcc_stg'
    rtrhost = 'https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode'
    tokenhost= 'https://tokenizer-stg.apixio.com:7075/tokens'
  elif env.lower()[0] == 'd':
    hcchost = 'https://hccdev.apixio.com/'
    ssohost = 'https://accounts-dev.apixio.com'
    uahost = 'https://useraccount-dev.apixio.com'
    uaport = ':7076'
    caller = 'hcc_dev'
    rtrhost = 'https://hcc-opprouter-dev.apixio.com:8443/ctrl/router/energy/energyMode'
    tokenhost= 'https://tokenizer-dev.apixio.com:7075/tokens'
  elif env.lower()[0] == 'e':
    hcchost = 'https://hcceng.apixio.com/'
    ssohost = 'https://accounts-stg.apixio.com'
    uahost = 'https://useraccount-eng.apixio.com'
    uaport = ':7076'
    caller = 'hcc_eng'
    rtrhost = 'https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode'
    tokenhost= 'https://tokenizer-stg.apixio.com:7075/tokens'
  return {'hcchost':hcchost,'ssohost':ssohost,'uahost':uahost,'uaport':uaport,'caller':caller, 'rtrhost':rtrhost, 'tokenhost': tokenhost}
#=======================================================================================================================
def defineGlobals(options):
  global LS, LSS, SL, ACTIONS
  global MAX_NUM_RETRIES, COUNT_OF_SERVED, PERCENT_OF_SERVED, PERCENT_OF_TARGET_HCC_SERVED
  global START, STOP, STEP
  global stat_codes, r_stat_codes
  global FAILED, SUCCEEDED, RETRIED
  global VOO, VAO, VRO, VSO

  stat_codes = {200:'ok', 201:'created', 202:'accepted', 204:'nocontent', \
                301:'movedperm', 302:'redirect', \
                401:'unauthorized', 404:'notfound', \
                500:'intservererror', 503:'survunavail'}
  r_stat_codes = {v: k for k, v in stat_codes.items()}

  FAILED = SUCCEEDED = RETRIED = 0
  VOO = VAO = VRO = VSO = 0

  LS  = "="*80
  LSS = "-"*80
  SL  = "*"*80
  ACTIONS = {0: "View Only", 1: "Accept", 2: "Reject", 3: "Skip"}
  MAX_NUM_RETRIES = int(options['max_ret'])
  START = (int(options['max_opps'])/10)
  STOP = int(options['max_opps'])
  STEP = (int(options['max_opps'])/10)

  if options['max_opps'] % 10 != 0:
      print "* Error".ljust(25)+" = Maximum number of opps "+str(options['max_opps'])+" must be divisible by 10"
      quit()
  COUNT_OF_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
  PERCENT_OF_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
  PERCENT_OF_TARGET_HCC_SERVED = {str(key): 0 for key in range(START, STOP, STEP)}
  return()
###########################################################################################################################################
# MAIN FUNCTION CALLER ####################################################################################################################
###########################################################################################################################################
def Main():
  global options
  os.system('clear')
  start_time=time.time()
  
  options=collections.OrderedDict()
  options['rep_type'] = 'Energy Routing Test'
  options['env'] = sys.argv[1] if len(sys.argv) > 1 else "Development"
  options['usr'] = sys.argv[2] if len(sys.argv) > 2 else "energyrouting@apixio.net"
  options['pwd'] = 'apixio.123'
  options['env_hosts'] = getEnvHosts(options['env'])
  options['max_opps'] = int(sys.argv[3]) if len(sys.argv) > 3 else 10
  options['max_ret'] = int(sys.argv[4]) if len(sys.argv) > 4 else 2
  options['coding_delay_time'] = int(sys.argv[5]) if len(sys.argv) > 5 else 0
  options['target_hcc'] = [str(sys.argv[6])] if len(sys.argv) > 6 else "108"
  options['dos'] = str(sys.argv[7]) if len(sys.argv) > 7 else "04/04/2014"
  options['report_recepients'] = [str(sys.argv[8])] if len(sys.argv) > 8 else ["ishekhtman@apixio.com"]
  options['action_weights'] = {'all':{'vo':0, 'va':10, 'vr':90, 'vs':0}, 'target':{'vo':0, 'va':95, 'vr':5, 'vs':0}}

  defineGlobals(options)
  #readConfigurationFile(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME)
  writeReportHeader(options)
  cookies = loginHCC(options)
  writeReportDetails("login")
  confirmSettings(options, cookies)
  startCoding(options, cookies)
  writeReportDetails("coding opportunity check")
  writeReportDetails("coding scorable document check")
  writeReportDetails("coding view only")
  writeReportDetails("coding view and accept")
  writeReportDetails("coding view and reject")
  writeReportDetails("coding view and skip")
  logout(options)
  writeReportDetails("logout")
  printResultsSummary()
  writeReportFooter(options)
  #archiveReport()
  emailReport(options)

if __name__ == "__main__":
  Main()
#=======================================================================================================================