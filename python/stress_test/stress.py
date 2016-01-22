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
# SPECIFICS: Added HTML version of the Test Results Summary Report
#
# PURPOSE:
#          This program should be executed via Python 2.6 and is meant for testing HCC functionality:
#          * Login
#          * Retrieve new Opportunity
#          * Retrieve new Finding for an Opportunity
#          * Retrieve all available Document pages for a Finding
#          * View   Docs + Opportunities
#          * Accept Docs + Opportunities
#          * Reject Docs + Opportunities
#          * Skip   Docs + Opportunities
#          * Logout
#
# SETUP:
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.7 environment is available
#          * From QA server (qa.apixio.com) /mnt/automation/python/stress_test folder enter "python2.7 stress.py grinder0@apixio.net 3000"
#
# USAGE:   * Test Results will be printed on Console screen as well as mailed via QA report
#
########################################################################################################################
#================================================ IMPORTS ==============================================================
import requests
import time
import sys, os
import json
from time import gmtime, strftime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import collections
requests.packages.urllib3.disable_warnings()
#=======================================================================================================================
def defineGlobals():
    global LS, LSS, SL, ACTIONS
    LS  = "="*80
    LSS = "-"*80
    SL  = "*"*80
    ACTIONS = {0: "View Only", 1: "Accept", 2: "Reject", 3: "Skip"}
    return()
#=======================================================================================================================

def pauseBreak():
  user_response = raw_input(">>> Press [Enter] to Proceed or [Q] to Quit: ")
  if user_response.upper() == "Q":
    print "exiting ..."
    quit()
  return ()
#=======================================================================================================================
def obtainExternalToken(options):

  url = options['env_hosts']['uahost']+options['env_hosts']['uaport']+'/auths'
  DATA =    { 'email': options['usr'], 'password': options['pwd']}
  HEADERS = {}

  print "* Url 4".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ options['usr']
  print "* Password".ljust(25)+" = "+ options['pwd']

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
def loginHCC(options):

  url = options['env_hosts']['hcchost']+'account/login/'
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
  url = options['env_hosts']['hcchost']+""
  print "* Url 2".ljust(25)+" = " + url
  response = requests.get(url)
  print "* Status Code".ljust(25)+" = "+str(response.status_code)
  print LSS
  if response.status_code != 200:
    quit()
#-----------------------------------------------------------------------------------------------------------------------
  jsessionid = response.cookies["JSESSIONID"]
  url = options['env_hosts']['ssohost']+"/"
  DATA = {'username': options['usr'], 'password': options['pwd'], 'hash':'', 'caller':options['env_hosts']['caller'], 'log_ref':'1441056621484', 'origin':'loging' }
  HEADERS = {'Cookie': 'JSESSIONID='+jsessionid}

  print "* Url 3".ljust(25)+ " = " + url
  response = requests.post(url, data=DATA, headers=HEADERS)
  print "* Status Code".ljust(25)+" = "+ str(response.status_code)
  print LSS
  if response.status_code != 200:
    quit()
  token = response.cookies["csrftoken"]
  sessid = response.cookies["sessionid"]
  apxtoken = obtainExternalToken(options)
  cookies = dict(csrftoken=''+token+'', sessionid=''+sessid+'', ApxToken=''+apxtoken+'', jsessionid=''+jsessionid)

  print "* Url 5".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ options['usr']
  print "* Password".ljust(25)+" = "+ options['pwd']
  print "* Cookies".ljust(25)+" = "+ "\n".ljust(29).join(["%s:%s" % (key, ('%('+key+')s') % cookies) for key in sorted(cookies)])
  print "* Log in user".ljust(25)+" = "+str(response.status_code)
  print LSS
  print "* Environment".ljust(25)+" = "+(options['env'])
  print "* Max # of Opps".ljust(25)+" = "+ str(options['max_opps'])
  print "* Max # of Docs".ljust(25)+" = "+ str(options['max_docs'])
  print "* Max # of Doc Pages".ljust(25)+" = "+ str(options['max_doc_pages'])
  print "* Max # of Retries".ljust(25)+" = "+ str(options['max_ret'])
  print "* Coding Delay Time".ljust(25)+" = "+ str(options['coding_delay_time'])+" second(s)"
  print "* Action Weights".ljust(25)+" = " + " ".join(["%s:%s%%" % (key, ('%('+key+')s') % options['action_weights']) for key in sorted(options['action_weights'])])
  print "* Accept Date of Service".ljust(25)+" = "+str(options['dos'])
  print "* Report Recepients".ljust(25)+" = "+str(options['report_recepients'])
  if response.status_code != 200:
    quit()
  print LS
  return(cookies)
#================================== ACT ON DOC (VIEW, ACCEPT, REJECT, SKIP) ============================================
def act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, max_docs, action, totals, dos):

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
  print "* HCC CODE".ljust(25)+" = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
  print "* FINDING ID".ljust(25)+" = "+ finding_id
  print "* ANNO URL".ljust(25)+" = "+aurl


  if (action == 0) or (action not in [1,2,3]): # Do NOT Accept or Reject Doc
    print "* CODER ACTION".ljust(25)+" = Do NOT Accept or Reject"
    trackCount("NOT Accept-Reject-Skip(200)", totals, 0)
  else:
    if action == 1: #=============================== ACCEPT DOC ==============
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
			"dateOfService": dos, \
			"comment": "Grinder Flag for Review" \
			}}}
    elif action == 2: #================================== REJECT DOC ===========
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
    elif action == 3: #=========================== SKIP OPP ====================
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

    retries=0
    while retries < options['max_ret']:
      st = time.time()
      response = requests.post(aurl, cookies=cookies, data=json.dumps(DATA), headers=HEADERS)
      dt = time.time() - st
      print ("* "+ACTIONS[action].upper()+" FINDING").ljust(25)+" = "+ str(response.status_code)
      if response.status_code == 200:
        retries = options['max_ret']
      else:
        retries += 1
        trackCount(ACTIONS[action]+"(retries)", totals, dt)
        trackCount(ACTIONS[action]+" "+json.dumps(DATA), totals, dt)
      trackCount(ACTIONS[action]+"("+str(response.status_code)+")", totals, dt)

  return (totals)
#============================================== RANDOM CODING ACTION ===================================================
def weightedRandomCodingAction(action_weights):
  weights = {0: action_weights['view'], \
             1: action_weights['accept'], \
             2: action_weights['reject'], \
             3: action_weights['skip']}
  action = random.choice([w for w in weights for dummy in range(weights[w])])
  return (action)
#============================================== START CODING ===========================================================
def startCoding(options, cookies):

  print "* Url".ljust(25)+" = "+options['env_hosts']['hcchost']
  print "* Username".ljust(25)+" = "+options['usr']
  print "* Password".ljust(25)+" = "+options['pwd']
  print "* Max. # of opps".ljust(25)+" = "+str(options['max_opps'])
  print "* Delay time".ljust(25)+" = "+str(options['coding_delay_time'])
  print LSS
  nwiurl = options['env_hosts']['hcchost']+"api/next-work-item/"
  print "* Url".ljust(25)+" = "+nwiurl
  print "* csrftoken".ljust(25)+" = "+cookies["csrftoken"]
  print "* apxtoken".ljust(25)+" = "+cookies["ApxToken"]
  print "* sessionid".ljust(25)+" = "+cookies["sessionid"]
  print "* jsessionid".ljust(25)+" = "+cookies["jsessionid"]

  HEADERS = {'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"]}
  DATA = {}
  totals={}

  for coding_opp_current in range(1,int(options['max_opps'])+1):
    printSeparator("NEXT OPPORTUNITY")
    time.sleep(options['coding_delay_time'])
    print "* Url".ljust(25)+" = "+ options['env_hosts']['hcchost']

    retries=0
    while retries < options['max_ret']:
        st = time.time()
        response = requests.get(nwiurl, data=DATA, headers=HEADERS)
        dt = time.time() - st
        print "* Get coding opp".ljust(25)+" = "+str(response.status_code)
        if response.status_code == 200:
            opportunity = response.json()
            retries = options['max_ret']
        else:
            retries += 1
            trackCount(str(nwiurl.split("/")[4])+"(retries)", totals, dt)
        trackCount(str(nwiurl.split("/")[4])+"("+str(response.status_code)+")", totals, dt)
    if response.status_code != 200:
                return (totals)

    hcc = opportunity.get("code").get("hcc")
    label_set_version = opportunity.get("code").get("labelSetVersion")
    sweep = opportunity.get("code").get("sweep")
    model_payment_year = opportunity.get("code").get("modelPaymentYear")

    print SL
    print "* PATIENT OPP".ljust(25)+" = "+"%d OF %d" % (coding_opp_current, int(options['max_opps']))
    print "* HCC CODE".ljust(25)+" = "+str(hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year)
    print "* PATIENT NAME".ljust(25)+" = "+str(opportunity.get("patient").get("first_name")+" "+opportunity.get("patient").get("middle_name")+opportunity.get("patient").get("last_name"))
    print "* PATIENT DOB".ljust(25)+" = "+str(opportunity.get("patient").get("dob"))
    print "* PATIENT GENDER".ljust(25)+" = "+str(opportunity.get("patient").get("gender"))
    print "* PATIENT ORG ID".ljust(25)+" = "+str(opportunity.get("patient").get("org_id"))
    print "* PATIENT ID".ljust(25)+" = "+str(opportunity.get("patientId"))
    print "* USER".ljust(25)+" = "+str(opportunity.get("user"))
    print "* ORGANIZATION".ljust(25)+" = "+str(opportunity.get("organization"))
    print "* TRANSACTION ID".ljust(25)+" = "+str(opportunity.get("transactionId"))
    print SL
    status = opportunity.get("status")
    possiblecodes = opportunity.get("possibleCodes")
    numpossiblecodes = len(possiblecodes)
    findings = opportunity.get("findings")
    patient_id = opportunity.get("patientId")
    project = opportunity.get("project")
    finding_ids = opportunity.get("finding_ids")

    doc_no = 0
    for finding in findings:
      if doc_no < options['max_docs']:
        finding_id = finding_ids[doc_no]
        doc_no += 1
        patient_org_id = finding.get("patient_org_id")
        document_uuid = finding.get("sourceId")
        document_title = finding.get("document_title")
        date_of_service = finding.get("doc_date")
        mime_type = finding.get("mimeType")
        if mime_type == None:
          mime_type = "text/plain"
        max_docs = min(len(findings),options['max_docs'])
        printSeparator("GET NEXT FINDING")
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
        dturl = options['env_hosts']['hcchost']+"api/document-text/"
        print "* URL".ljust(25)+" = "+ dturl

        retries=0
        while retries < options['max_ret']:
          st = time.time()
          response = requests.get(dturl + document_uuid, data=DATA, headers=HEADERS)
          dt = time.time() - st
          print "* GET SCRBLE DOC".ljust(25)+" = "+ str(response.status_code)
          if response.status_code == 200:
            retries = options['max_ret']
          else:
            retries += 1
            trackCount(str(dturl.split("/")[4])+"(retries)", totals, dt)
            trackCount(str(dturl.split("/")[4])+" "+str(json.dumps(finding)), totals, dt)
          trackCount(str(dturl.split("/")[4])+"("+str(response.status_code)+")", totals, dt)
        if response.status_code != 200:
          return (totals)

      # looping through each and every available page in a document
        if mime_type == "application/pdf":
          printSeparator("GET DOCUMENT PAGES")
          totalPages = finding.get("total_pages")
          print "* TOTAL # OF PAGES(DOC)".ljust(25)+" = "+ str((int(totalPages)-1))
          print "* TOTAL # OF PAGES(LIMIT)".ljust(25)+" = "+ str(options['max_doc_pages'])

          for i in range (1, int(totalPages)):
            if i <= options['max_doc_pages']:
              dpurl = options['env_hosts']['hcchost']+"document_page/"
              retries=0
              while retries < options['max_ret']:
                st = time.time()
                response = requests.get(dpurl + document_uuid + "/" + str(i), cookies=cookies, data=DATA, headers=HEADERS)
                dt = time.time() - st
                print ("* DOC PAGE "+str(i)+" OF "+str((int(min(int(totalPages)-1,options['max_doc_pages']))))).ljust(25)+" = "+str(response.status_code)
                if response.status_code == 200:
                    retries = options['max_ret']
                else:
                    retries += 1
                    trackCount(str(dpurl.split("/")[3])+"(retries)", totals, dt)
                    trackCount(str(dpurl.split("/")[3])+" "+str(json.dumps(finding))+" PAGE#: "+str(i), totals, dt)
                trackCount(str(dpurl.split("/")[3])+"("+str(response.status_code)+")", totals, dt)
              if response.status_code != 200:
                return (totals)

        action = weightedRandomCodingAction(options['action_weights'])
        print "* ANNOTATION ACTION".ljust(25)+" = " + ACTIONS[action]
        printSeparator("ANNOTATE: " + ACTIONS[action])
        totals = act_on_doc(options['env_hosts']['hcchost'], cookies, opportunity, finding, finding_id, doc_no, max_docs, action, totals, options['dos'])

  return(totals)
#=======================================================================================================================
def printSeparator(msg):
  ladj=1
  radj=1
  print LS
  if len(msg)%2!=0:
    radj=2
  print ">"*((80-len(msg)-ladj)/2)+" "+msg+" "+"<"*((80-len(msg)-radj)/2)
  print LS
  return()
#=======================================================================================================================
def getBgColor(total):
  colors = {"RED":"#FF0000", "YELLOW":"#FFFF00", "GREEN":"#00FF00", "WHITE":"#FFFFFF", "GREY":"#DCDCDC"}
  if "(" in total and ")" in total:
    if total.split("(")[1].split(")")[0] == "200":
      return(colors['GREEN'])
    elif total.split("(")[1].split(")")[0] == "retries":
      return(colors['YELLOW'])
    elif total.split("(")[1].split(")")[0] == "heading":
      return (colors['GREY'])
    else:
      return(colors['RED'])
  else:
    return(colors['YELLOW'])
#=======================================================================================================================
def printResults(options, start_time, totals):

  hours, minuts, seconds = checkDuration(start_time)
  r = ""
  r += "<h2>Apixio HCC Stress Test Report</h2>"
  r += "Run date & time (run): <b>%s</b><br>" % (strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time)))
  r += "Test Started: <b>"+strftime("%m/%d/%Y %H:%M:%S<br>", gmtime(start_time))+"</b>"
  r += "Test Ended: <b>"+strftime("%m/%d/%Y %H:%M:%S<br>", gmtime())+"</b>"
  r += "Test Duration: <b>"+"%s hours, %s minutes, %s seconds<br>"% (int(round(hours)), int(round(minuts)), int(round(seconds)))+"</b><br>"
  r += "Report type: <b>%s</b><br>" % (options['rep_type'])
  r += "HCC user name: <b>%s</b><br>" % (options['usr'])
  r += "HCC app url: <b>%s</b><br>" % (options['env_hosts']['hcchost'])
  r += "Enviromnent: <b><font color='red'>%s</font></b><br><br>" % (options['env'])
  r += "Max. # of Opps: <b>%s</b><br>"%(options['max_opps'])
  r += "Max. # of Docs: <b>%s</b><br>"%(options['max_docs'])
  r += "Max. # of Doc Pages: <b>%s</b><br>"%(options['max_doc_pages'])
  r += "Max. # of Retries: <b>%s</b><br>"%(options['max_ret'])
  r += "Coding Delay Time: <b>%s sec</b><br>"%(options['coding_delay_time'])
  r += "Accepts Date of Service: <b>%s</b><br>"%(options['dos'])
  r += "Action Weights: <b>%s</b><br><br>"%(", ".join(["%s:%s%%" % (key[0].upper()+key[1:], ('%('+key+')s') % options['action_weights']) for key in sorted(options['action_weights'])]))
  r += "<table align='left' width='800' cellpadding='1' cellspacing='1'>"

  printSeparator("HCC STRESS TEST RESULTS SUMMARY")
  r +=  "<tr><td bgcolor='"+getBgColor('(heading)')+"'>HCC STRESS TEST RESULTS SUMMARY</td><td bgcolor='"+getBgColor('(heading)')+"'>TOT#</td><td bgcolor='"+getBgColor('(heading)')+"'>AVE</td><td bgcolor='"+getBgColor('(heading)')+"'>MIN</td><td bgcolor='"+getBgColor('(heading)')+"'>MAX</td><tr>"
  print "* Test Started".ljust(25)+" = "+strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time))
  print "* Test Ended".ljust(25)+" = "+strftime("%m/%d/%Y %H:%M:%S", gmtime())
  print "* Test Duration".ljust(25)+" = "+"%s hours, %s minutes, %s seconds"% (int(round(hours)), int(round(minuts)), int(round(seconds)))
  for total in sorted(totals, key=lambda x:x[0].upper()):
    print ("* "+ total[0].upper()+total[1:]).ljust(25)+" = " + str(totals[total][0]) + ' ' + convTimeString(totals[total][1]/totals[total][0]) + ' ' + convTimeString(totals[total][2]) + ' ' + convTimeString(totals[total][3])
    r +=  ("<tr><td width='650' bgcolor='"+getBgColor(total)+"'> "+ total[0].upper())+total[1:]+"</td><td bgcolor='"+getBgColor(total)+"'> " + str(totals[total][0])+"</td><td bgcolor='"+getBgColor(total)+"'> " + convTimeString(totals[total][1]/totals[total][0])+"</td><td bgcolor='"+getBgColor(total)+"'> " + convTimeString(totals[total][2])+"</td><td bgcolor='"+getBgColor(total)+"'> " + convTimeString(totals[total][3])+"</td></tr>"
  printSeparator("HCC STRESS TEST COMPLETE")
  r +=  "<tr><td bgcolor='"+getBgColor('(heading)')+"' colspan='5'>HCC STRESS TEST COMPLETE</td><tr></table>"


  message = MIMEMultipart('related')
  message.attach(MIMEText((r), 'html'))
  message['From'] = 'Apixio QA <qa@apixio.com>'
  #message['To'] = 'To: Eng <'+options['report_recepients'][0]+'>,Ops <'+options['report_recepients'][1]+'>'
  message['To'] = 'To: Eng <'+options['report_recepients'][0]+'>'
  message['Subject'] = 'HCC %s Stress Test Report - %s' % (options['env'], strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time)))
  msg_full = message.as_string()

  s=smtplib.SMTP()
  s.connect("smtp.gmail.com",587)
  s.starttls()
  s.login("donotreply@apixio.com", "apx.mail47")
  s.sendmail("qa@apixio.com", options['report_recepients'], msg_full)
  s.quit()
  return()
#=======================================================================================================================
def trackCount(item, totals, resp_time):
  #total_number, tot_time, min_time, max_time
  if item not in totals:
    totals[item]=[1,resp_time,resp_time,resp_time]
  else:
    totals[item][0] += 1
    totals[item][1] += resp_time
    if resp_time > totals[item][3]:
      totals[item][3] = resp_time
    if resp_time < totals[item][2]:
      totals[item][2] = resp_time
  return(totals)
#=======================================================================================================================
def convTimeString(ftime):
  hours, rest = divmod(ftime,3600)
  minutes, seconds = divmod(rest, 60)
  stime = str(round(seconds,2)) +'s'
  return(stime)
#=======================================================================================================================
def checkDuration(start_time):
  end_time = time.time()
  duration = end_time - start_time
  hours, rest = divmod(duration,3600)
  minutes, seconds = divmod(rest, 60)
  return(hours, minutes, seconds)
#=======================================================================================================================
def getEnvHosts(env):
  if env.lower()[0] == 's':
    hcchost = 'https://hcc-stg.apixio.com/'
    ssohost = 'https://accounts-stg.apixio.com'
    uahost = 'https://useraccount-stg.apixio.com'
    uaport = ':7076'
    caller = 'hcc_stg'
  elif env.lower()[0] == 'd':
    hcchost = 'https://hccdev.apixio.com/'
    ssohost = 'https://accounts-dev.apixio.com'
    uahost = 'https://useraccount-dev.apixio.com'
    uaport = ':7076'
    caller = 'hcc_dev'
  elif env.lower()[0] == 'e':
    hcchost = 'https://hcceng.apixio.com/'
    ssohost = 'https://accounts-stg.apixio.com'
    uahost = 'https://useraccount-eng.apixio.com'
    uaport = ':7076'
    caller = 'hcc_eng'
  return {'hcchost':hcchost,'ssohost':ssohost,'uahost':uahost,'uaport':uaport,'caller':caller}
#=======================================================================================================================
def commandLineParamatersDescription(options):
  print "Please enter command line paramaters.  If none entered, default values will be used."
  i = 0
  for option in options:
      if ((option != 'pwd') and (option != 'rep_type')):
        print '['+str(i)+']'+option,
        i += 1
  print
  return 0
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
def Main():
  global options
  os.system('clear')
  start_time=time.time()

  # ARGV list description:
  # [0] - stress.py
  # [1] - usr
  # [2] - env
  # [3] - Opps limit
  # [4] - Docs limit
  # [5] - Pages limit
  # [6] - Retries limit
  # [7] - Coding Delay (sec)
  # [8] - %accept
  # [9] - %reject
  # [10] - %skip
  # [11] - Accept DOS
  # [12] - Report Recepients

  # assigning default values if command line paramater(s) were not passed
  options=collections.OrderedDict()
  options['rep_type'] = 'Stress Test'
  options['usr'] = sys.argv[1] if len(sys.argv) > 1 else "mmgenergyes@apixio.net"
  options['env'] = sys.argv[2] if len(sys.argv) > 2 else "Development"
  options['pwd'] = 'apixio.123'
  options['env_hosts'] = getEnvHosts(options['env'])
  options['max_opps'] = int(sys.argv[3]) if len(sys.argv) > 3 else 2
  options['max_docs'] = int(sys.argv[4]) if len(sys.argv) > 4 else 2
  options['max_doc_pages'] = int(sys.argv[5]) if len(sys.argv) > 5 else 2
  options['max_ret'] = int(sys.argv[6]) if len(sys.argv) > 6 else 2
  options['coding_delay_time'] = int(sys.argv[7]) if len(sys.argv) > 7 else 0
  accept = int(sys.argv[8]) if len(sys.argv) > 8 else 45
  reject = int(sys.argv[9]) if len(sys.argv) > 9 else 45
  skip = int(sys.argv[10]) if len(sys.argv) > 10 else 10
  options['action_weights'] = {'view':0,'accept':accept,'reject':reject,'skip':skip}
  options['dos'] = str(sys.argv[11]) if len(sys.argv) > 11 else "04/04/2014"
  options['report_recepients'] = [str(sys.argv[12])] if len(sys.argv) > 12 else ["ishekhtman@apixio.com"]


  defineGlobals()
  cookies = loginHCC(options)
  commandLineParamatersDescription(options)
  pauseBreak()
  totals = startCoding(options, cookies)
  printResults(options, start_time, totals)

if __name__ == "__main__":
  Main()
#=======================================================================================================================
