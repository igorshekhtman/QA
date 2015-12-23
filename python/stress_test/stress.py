__author__ = 'ishekhtman'

########################################################################################################################
#
# PROGRAM: stress.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    Dec. 21, 2015 - Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: Dec. 21, 2015
# SPECIFICS: Added IncrementTestResultsTotals()function to print out retried, failed and succeeded totals
#
# PURPOSE:
#          This program should be executed via Python 2.6 and is meant for testing HCC functionality:
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
#          * Assumes a Python 2.6 environment is available
#          * From QA server (ec2-54-219-117-239) /mnt/automation/hcc folder enter "python2.6 hccstress.py"
#		   * note: hccstress.csv configuration file must coexist in same folder as hccstress.py
#
# USAGE:
#          * Set the global variables (CSV_CONFIG_FILE_PATH and CSV_CONFIG_FILE_NAME), see below
#          * Configure global parameters in hccstress.csv located in the same folder
#          * Results will be printed on Console screen as well as mailed via QA report
#
########################################################################################################################
#================================================ IMPORTS ==============================================================
import requests
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
#from pylab import *
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
#import numpy as np
requests.packages.urllib3.disable_warnings()

#=======================================================================================================================
def defineGlobals():
    global USR, PWD, LS, LSS, SL, ACTIONS, DOS

    USR = "ishekhtman@apixio.com"
    PWD = "apixio.321"
    LS  = "="*80
    LSS = "-"*80
    SL  = "*"*80
    ACTIONS = {0: "View Only", 1: "Accept", 2: "Reject", 3: "Skip"}
    DOS = "04/04/2014"

    return()
#=======================================================================================================================

def pauseBreak():
	user_response = raw_input(">>> Press [Enter] to Proceed or [Q] to Quit: ")
	if user_response.upper() == "Q":
		print "exiting ..."
		quit()
	return ()
#=======================================================================================================================
def obtainExternalToken(un, pw, ua_url):

  url = ua_url+'/auths'
  referer = ua_url

  DATA =    {'Referer': referer, 'email': un, 'password': pw}
  HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}


  print "* Url 4".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ un
  print "* Password".ljust(25)+" = "+ pw


  response = requests.post(url, data=DATA, headers=HEADERS)
  statuscode = response.status_code
  if statuscode != 200:
    print "* Ext. token status code".ljust(25)+" = "+ str(statuscode)
    quit()
  external_token = response.json().get("token")
  print "* External token".ljust(25)+" = "+ response.json().get("token")
  print "* Ext. token status code".ljust(25)+" = "+ str(statuscode)
  print LSS
  return (external_token)
#================================================ LOGIN TO HCC =========================================================

def loginHCC(usr, pwd, url, sso_url, caller):
  global APXTOKEN

  URL = "https://hccdev.apixio.com"
  SSO_URL="https://accounts-dev.apixio.com"
  CALLER="hcc_dev"

  url = URL+'/account/login/'
  referer = URL+'/account/login/'
  print LS
  print "* Url 1".ljust(25)+" = " + url
  response = requests.get(url)
  print "* Status Code".ljust(25)+" = "+str(response.status_code)
  print LSS
  if response.status_code == 500:
    print "* Connection to host".just(25)+" =  FAILED"
    print LS
    quit()
#-----------------------------------------------------------------------------------------------------------------------
  url = URL+"/"
  print "* Url 2".ljust(25)+" = " + url
  response = requests.get(url)
  print "* Status Code".ljust(25)+" = "+str(response.status_code)
  print LSS
  if response.status_code != 200:
    quit()
#-----------------------------------------------------------------------------------------------------------------------
  jsessionid = response.cookies["JSESSIONID"]

  origin = SSO_URL
  referer = SSO_URL+"/?caller="+CALLER
  host = SSO_URL[8:]
  url = SSO_URL+"/"

  DATA = {'username': usr, 'password': pwd, 'hash':'', 'caller':CALLER, 'log_ref':'1441056621484', 'origin':'loging' }
  HEADERS = { \
  			'Accept': '*/*', \
  			'Accept-Encoding': 'gzip, deflate', \
  			'Accept-Language': 'en-US,en;q=0.8', \
  			'Connection': 'keep-alive', \
  			'Content-Length': '1105', \
			'Cookie': 'JSESSIONID='+jsessionid, \
			'Host': host, \
			'Origin': origin, \
			'Referer': referer \
			}
  print "* Url 3".ljust(25)+ " = " + url
  response = requests.post(url, data=DATA, headers=HEADERS)
  print "* Status Code".ljust(25)+" = "+ str(response.status_code)
  print LSS
  if response.status_code != 200:
  	quit()

  token = response.cookies["csrftoken"]
  sessid = response.cookies["sessionid"]
  apxtoken = obtainExternalToken(usr, pwd, "https://useraccount-dev.apixio.com:7076")
  cookies = dict(csrftoken=''+token+'', sessionid=''+sessid+'', ApxToken=''+apxtoken+'', jsessionid=''+jsessionid)


  print "* Url 5".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ usr
  print "* Password".ljust(25)+" = "+ pwd
  print "* Csrftoken".ljust(25)+" = "+ token
  print "* ApxToken".ljust(25)+" = "+ apxtoken
  print "* Sessid".ljust(25)+" = "+ sessid
  print "* Jsessionid".ljust(25)+" = "+ jsessionid
  print "* Cookies".ljust(25)+" = "+ str(cookies)
  print "* Log in user".ljust(25)+" = "+str(response.status_code)
  if response.status_code != 200:
  	quit()
  print LS
  return(cookies)

#================================== ACT ON DOC (VIEW, ACCEPT, REJECT, SKIP) ============================================

def act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, max_docs, action):

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
    	'Referer': url+'/', \
        'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"], \
    	'X_REQUESTED_WITH': 'XMLHttpRequest', \
        'X-CSRFToken': cookies["csrftoken"] \
    	}

  aurl = url+ "api/annotate/"
  if action == 0: # Do NOT Accept or Reject Doc
    print "* HCC CODE".ljust(25)+" = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
    print "* CODER ACTION".ljust(25)+" = Do NOT Accept or Reject Doc"
  elif action == 1: #=============================== ACCEPT DOC ==============
    #finding_id = scorable.get("id")
    print "* FINDING ID".ljust(25)+" = "+ finding_id
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
			"dateOfService": DOS, \
			"comment": "Grinder Flag for Review" \
			}}}
    print "* ANNO URL".ljust(25)+" = "+aurl
    response = requests.post(aurl, cookies=cookies, data=json.dumps(DATA), headers=HEADERS)
    print "* ANNOTATE FINDING".ljust(25)+" = "+ str(response.status_code)
    if response.status_code == 200:
      print "* HCC CODE".ljust(25)+" = "+str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print "* CODER ACTION".ljust(25)+" =  Accept Doc"
      print "* HCC RESPONSE".ljust(25)+" = 200 OK"
    else:
      print "* CODER ACTION".ljust(25)+" Reject Doc"
      print "* HCC RESPONSE".ljust(25)+" WARNING : Bad HCC Server Response: "+ str(response)
      act_on_doc(url, cookies,opportunity, finding, finding_id, doc_no, max_docs, action)
  elif action == 2: #================================== REJECT DOC ===========
    #finding_id = scorable.get("id")
    print "* FINDING ID".ljust(25)+" = "+ finding_id
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
    print "* ANNO URL".ljust(25)+" = "+ aurl
    response = requests.post(aurl, cookies=cookies, data=json.dumps(DATA), headers=HEADERS)
    if response.status_code == 200:
      print "* HCC CODE".ljust(25)+" = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print "* CODER ACTION".ljust(25)+" = Reject Doc"
      print "* HCC RESPONSE".ljust(25)+" = 200 OK"
    else:
      print "* CODER ACTION".ljust(25)+" Reject Doc"
      print "* HCC RESPONSE".ljust(25)+" WARNING : Bad HCC Server Response: "+ str(response)
      act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, max_docs, action)
  elif action == 3: #=========================== SKIP OPP ====================
    #finding_id = scorable.get("id")
    print "* FINDING ID".ljust(25)+" = "+ finding_id
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
    print "* ANNO URL".ljust(25)+" = "+aurl
    response = requests.post(aurl, cookies=cookies, data=json.dumps(DATA), headers=HEADERS)
    if response.status_code == 200:
      print "* HCC CODE".ljust(25)+" = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
      print "* CODER ACTION".ljust(25)+" = Skip Opp"
      print "* HCC RESPONSE".ljust(25)+" = 200 OK"
    else:
      print("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
      act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, max_docs, action)
  else:
    print "* CODER ACTION".ljust(25)+" = ? Unknown ?\n"
  return 0

#============================================== RANDOM CODING ACTION ===================================================

def weightedRandomCodingAction(view, accept, reject, skip):

	weight = { "0": 0, "1": 0, "2": 0, "3": 0 }
	weight['0'] = int(view)
	weight['1'] = int(accept)
	weight['2'] = int(reject)
	weight['3'] = int(skip)
	action = random.choice([k for k in weight for dummy in range(weight[k])])
	return (int(action))

#============================================== START CODING ===========================================================

def startCoding(usr, pw, url, cookies, max_opps, deltime):

  print "* Url".ljust(25)+" = "+url
  print "* Username".ljust(25)+" = "+usr
  print "* Password".ljust(25)+" = "+pw
  print "* Max. # of opps".ljust(25)+" = "+str(max_opps)
  print "* Delay time".ljust(25)+" = "+str(deltime)
  print LSS
  nwiurl = url+"api/next-work-item/"
  print "* Url".ljust(25)+" = "+nwiurl
  print "* Csrftoken".ljust(25)+" = "+cookies["csrftoken"]
  print "* Apxtoken".ljust(25)+" = "+cookies["ApxToken"]
  print "* Sessionid".ljust(25)+" = "+cookies["sessionid"]
  print "* Jsessionid".ljust(25)+" = "+cookies["jsessionid"]
  #pauseBreak()

  HEADERS = {'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"]}
  DATA = {}

  for coding_opp_current in range(max_opps+1):
    print LS
    print ">"*31+" NEXT OPPORTUNITY "+"<"*31
    print LS
    time.sleep(deltime)
    print "* Url".ljust(25)+" = "+ url
    response = requests.get(nwiurl, data=DATA, headers=HEADERS)
    print "* Get coding opp".ljust(25)+" = "+str(response.status_code)

    if response.status_code != 200:
    	print "* Failed retrieve next-work-item".ljust(25)+" = "+str(response.status_code)
        quit()
    else:
    	opportunity = response.json()

    hcc = opportunity.get("code").get("hcc")
    label_set_version = opportunity.get("code").get("labelSetVersion")
    sweep = opportunity.get("code").get("sweep")
    model_payment_year = opportunity.get("code").get("modelPaymentYear")


    print SL
    print "* HCC CODE".ljust(25)+" = "+str(hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year)
    print SL

    patient_details = response.text
    #print patient_details

    if opportunity == None:
      print("* ERROR".ljust(25)+" = Login Failed or No More Opportunities For This Coder")
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

    print "PATIENT OPP %d OF %d" % (coding_opp_current, max_opps)

    doc_no = 0
    for finding in findings:
      finding_id = finding_ids[doc_no]
      doc_no += 1
      patient_org_id = finding.get("patient_org_id")
      document_uuid = finding.get("sourceId")
      document_title = finding.get("document_title")
      date_of_service = finding.get("doc_date")
      mime_type = finding.get("mimeType")
      if mime_type == None:
    	  mime_type = "text/plain"
      max_docs = len(findings)
      print "PATIENT DOC %d OF %d"    % (doc_no, max_docs)
      print "* STATUS".ljust(25)+" = "+status
      print "* PATIENT ORG".ljust(25)+" = "+patient_org_id
      print "* PATIENT ID".ljust(25)+" = "+patient_id
      print "* FINDING ID".ljust(25)+" = "+finding_id
      print "* AVAILABLE CODES".ljust(25)+" = "+str(numpossiblecodes)
      print "* PROJECT ID".ljust(25)+" = "+project
      print "* DOC UUID".ljust(25)+" = "+document_uuid
      print "* DOC TITLE".ljust(25)+" = "+document_title
      print "* DOC DATE OF SERVICE".ljust(25)+" = "+date_of_service
      print "* DOC TYPE".ljust(25)+" = "+mime_type

      dturl = url+"api/document-text/"


      print "* URL".ljust(25)+" = "+ dturl

      response = requests.get(dturl + document_uuid, data=DATA, headers=HEADERS)

      print "* GET SCRBLE DOC".ljust(25)+" = "+ str(response.status_code)

      action = weightedRandomCodingAction(0, 34, 33, 33)
      print "* ANNOTATION ACTION".ljust(25)+" = "+ACTIONS[action]
      print LSS
      act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, max_docs, action)

  return 0
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
os.system('clear')
defineGlobals()
cookies = loginHCC("protest01@apixio.net", "apixio.123", "http://hccdev.apixio.com/", "https://accounts-dev.apixio.com", "hcc_dev")
pauseBreak()
startCoding("protest01@apixio.net", "apixio.123", "https://hccdev.apixio.com/", cookies, 5, 1)
print LS
print ">"*27+" HCC STRESS TEST COMPLETE "+"<"*27
print LS
#=======================================================================================================================
