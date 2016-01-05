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
def obtainExternalToken(un, pw, ua_url):

  url = ua_url+'/auths'
  DATA =    { 'email': un, 'password': pw}
  HEADERS = {}

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

def loginHCC(usr, pwd, hcchost, uahost, caller, max_opps):

  url = hcchost+'/account/login/'
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
  url = hcchost+"/"
  print "* Url 2".ljust(25)+" = " + url
  response = requests.get(url)
  print "* Status Code".ljust(25)+" = "+str(response.status_code)
  print LSS
  if response.status_code != 200:
    quit()
#-----------------------------------------------------------------------------------------------------------------------
  jsessionid = response.cookies["JSESSIONID"]
  url = uahost+"/"
  DATA = {'username': usr, 'password': pwd, 'hash':'', 'caller':caller, 'log_ref':'1441056621484', 'origin':'loging' }
  HEADERS = { 'Cookie': 'JSESSIONID='+jsessionid }

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
  #print "* Cookies".ljust(25)+" = "+ str(cookies)
  print "* Log in user".ljust(25)+" = "+str(response.status_code)
  print LSS
  print "* Environment".ljust(25)+" = "+(env)
  print "* Max # of Opps".ljust(25)+" = "+ str(max_opps)
  print "* Max # of Retries".ljust(25)+" = "+ str(max_ret)
  print "* Max # of Doc Pages".ljust(25)+" = "+ str(max_doc_pages)
  print "* Coding Delay Time".ljust(25)+" = "+ str(coding_delay_time)+" second(s)"
  print "* Action Weights".ljust(25)+" = " + " ".join(["%s:%s%%" % (key, ('%('+key+')s') % action_weights) for key in sorted(action_weights)])
  print "* Accept Date of Service".ljust(25)+" = "+str(dos)
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
    trackCount("Do NOT Accept or Reject", totals)
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
    while retries < max_ret:
      response = requests.post(aurl, cookies=cookies, data=json.dumps(DATA), headers=HEADERS)
      print ("* "+ACTIONS[action].upper()+" FINDING").ljust(25)+" = "+ str(response.status_code)
      if response.status_code == 200:
        retries = max_ret
      else:
        retries += 1
        trackCount(ACTIONS[action]+"(retries)", totals)
      trackCount(ACTIONS[action]+"("+str(response.status_code)+")", totals)

  return (totals)

#============================================== RANDOM CODING ACTION ===================================================

def weightedRandomCodingAction(action_weights):

  weight = { "0": 0, "1": 0, "2": 0, "3": 0 }
  weight['0'] = int(action_weights['view'])
  weight['1'] = int(action_weights['accept'])
  weight['2'] = int(action_weights['reject'])
  weight['3'] = int(action_weights['skip'])
  action = random.choice([k for k in weight for dummy in range(weight[k])])
  return (int(action))

#============================================== START CODING ===========================================================

def startCoding(usr, pw, url, cookies, max_opps, deltime, action_weights, dos):

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

  HEADERS = {'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"]}
  DATA = {}
  totals={}

  for coding_opp_current in range(max_opps):
    printSeparator("NEXT OPPORTUNITY")
    time.sleep(deltime)
    print "* Url".ljust(25)+" = "+ url

    retries=0
    while retries < max_ret:
        response = requests.get(nwiurl, data=DATA, headers=HEADERS)
        print "* Get coding opp".ljust(25)+" = "+str(response.status_code)
        if response.status_code == 200:
            opportunity = response.json()
            retries = max_ret
        else:
            retries += 1
            trackCount(str(nwiurl.split("/")[4])+"(retries)", totals)
        trackCount(str(nwiurl.split("/")[4])+"("+str(response.status_code)+")", totals)
    if response.status_code != 200:
                return (totals)

    hcc = opportunity.get("code").get("hcc")
    label_set_version = opportunity.get("code").get("labelSetVersion")
    sweep = opportunity.get("code").get("sweep")
    model_payment_year = opportunity.get("code").get("modelPaymentYear")

    print SL
    print "* HCC CODE".ljust(25)+" = "+str(hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year)
    print SL

    patient_details = response.text

    if opportunity == None:
      print("* ERROR".ljust(25)+" = Login Failed or No More Opportunities For This Coder")
      trackCount("No more opps", totals)
      return (totals)

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
      dturl = url+"api/document-text/"
      print "* URL".ljust(25)+" = "+ dturl

      retries=0
      while retries < max_ret:
        response = requests.get(dturl + document_uuid, data=DATA, headers=HEADERS)
        print "* GET SCRBLE DOC".ljust(25)+" = "+ str(response.status_code)
        if response.status_code == 200:
            retries = max_ret
        else:
            retries += 1
            trackCount(str(dturl.split("/")[4])+"(retries)", totals)
        trackCount(str(dturl.split("/")[4])+"("+str(response.status_code)+")", totals)
      if response.status_code != 200:
        return (totals)

      # looping through each and every available page in a document
      if mime_type == "application/pdf":
        printSeparator("GET DOCUMENT PAGES")
        totalPages = finding.get("total_pages")
        print "* TOTAL # OF PAGES(DOC)".ljust(25)+" = "+ str((int(totalPages)-1))
        print "* TOTAL # OF PAGES(LIMIT)".ljust(25)+" = "+ str(max_doc_pages)

        for i in range (1, int(totalPages)):
          if i <= max_doc_pages:
            dpurl = url+"document_page/"
            retries=0
            while retries < max_ret:
                response = requests.get(dpurl + document_uuid + "/" + str(i), cookies=cookies, data=DATA, headers=HEADERS)
                print ("* DOC PAGE "+str(i)+" OF "+str((int(min(int(totalPages)-1,max_doc_pages))))).ljust(25)+" = "+str(response.status_code)
                if response.status_code == 200:
                    retries = max_ret
                else:
                    retries += 1
                    trackCount(str(dpurl.split("/")[3])+"(retries)", totals)
                trackCount(str(dpurl.split("/")[3])+"("+str(response.status_code)+")", totals)
            if response.status_code != 200:
                return (totals)

      action = weightedRandomCodingAction(action_weights)
      print "* ANNOTATION ACTION".ljust(25)+" = " + ACTIONS[action]
      printSeparator("ANNOTATE: " + ACTIONS[action])
      totals = act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, max_docs, action, totals, dos)

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
    return(colors['GREEN'])
#=======================================================================================================================
def printResults(dos, rep_type, env, action_weights, coding_delay_time, max_opps, max_ret, max_doc_pages, hcchost, start_time, totals, emailout, recepients):

  hours, minuts, seconds = checkDuration(start_time)
  r = ""
  r += "<h2>Apixio HCC Stress Test Report</h2>"
  r += "Run date & time (run): <b>%s</b><br>" % (strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time)))
  r += "Test Started: <b>"+strftime("%m/%d/%Y %H:%M:%S<br>", gmtime(start_time))+"</b>"
  r += "Test Ended: <b>"+strftime("%m/%d/%Y %H:%M:%S<br>", gmtime())+"</b>"
  r += "Test Duration: <b>"+"%s hours, %s minutes, %s seconds<br>"% (int(round(hours)), int(round(minuts)), int(round(seconds)))+"</b><br>"
  r += "Report type: <b>%s</b><br>" % (rep_type)
  r += "HCC user name: <b>%s</b><br>" % (usr)
  r += "HCC app url: <b>%s</b><br>" % (hcchost)
  r += "Enviromnent: <b><font color='red'>%s</font></b><br><br>" % (env)
  r += "Max. # of Opps: <b>%s</b><br>"%(max_opps)
  r += "Max. # of Retries: <b>%s</b><br>"%(max_ret)
  r += "Max. # of Doc Pages: <b>%s</b><br>"%(max_doc_pages)
  r += "Coding Delay Time: <b>%s sec</b><br>"%(coding_delay_time)
  r += "Accepts Date of Service: <b>%s</b><br>"%(dos)
  r += "Action Weights: <b>%s</b><br><br>"%(", ".join(["%s:%s%%" % (key[0].upper()+key[1:], ('%('+key+')s') % action_weights) for key in sorted(action_weights)]))
  r += "<table align='left' width='800' cellpadding='1' cellspacing='1'>"

  printSeparator("HCC STRESS TEST RESULTS SUMMARY")
  r +=  "<tr><td bgcolor='"+getBgColor('(heading)')+"' colspan='2'>HCC STRESS TEST RESULTS SUMMARY</td><tr>"
  print "* Test Started".ljust(25)+" = "+strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time))
  print "* Test Ended".ljust(25)+" = "+strftime("%m/%d/%Y %H:%M:%S", gmtime())
  print "* Test Duration".ljust(25)+" = "+"%s hours, %s minutes, %s seconds"% (int(round(hours)), int(round(minuts)), int(round(seconds)))
  for total in sorted(totals, key=lambda x:x[0].upper()):
    print ("* "+ total[0].upper()+total[1:]).ljust(25)+" = " + str(totals[total])
    r +=  ("<tr><td width='200' bgcolor='"+getBgColor(total)+"'> "+ total[0].upper())+total[1:]+"</td><td bgcolor='"+getBgColor(total)+"'> " + str(totals[total])+"</td></tr>"
  printSeparator("HCC STRESS TEST COMPLETE")
  r +=  "<tr><td bgcolor='"+getBgColor('(heading)')+"' colspan='2'>HCC STRESS TEST COMPLETE</td><tr></table>"

  if emailout:
    message = MIMEMultipart('related')
    message.attach(MIMEText((r), 'html'))
    message['From'] = 'Apixio QA <qa@apixio.com>'
    message['To'] = 'To: Eng <'+recepients[0]+'>,Ops <'+recepients[1]+'>'
    message['Subject'] = 'HCC %s Stress Test Report - %s' % (env, strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time)))
    msg_full = message.as_string()

    s=smtplib.SMTP()
    s.connect("smtp.gmail.com",587)
    s.starttls()
    s.login("donotreply@apixio.com", "apx.mail47")
    s.sendmail("qa@apixio.com", recepients, msg_full)
    s.quit()
  return()
#=======================================================================================================================
def trackCount(item, totals):
  if item not in totals:
    totals[item]=1
  else:
    totals[item] += 1
  return(totals)
#=======================================================================================================================
def checkDuration(start_time):
  end_time = time.time()
  duration = end_time - start_time
  hours, rest = divmod(duration,3600)
  minutes, seconds = divmod(rest, 60)
  return(hours, minutes, seconds)
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
os.system('clear')
start_time=time.time()

rep_type="Stress Test"
env="Development"
pwd="apixio.123"
hcchost="https://hccdev.apixio.com/"
uahost="https://accounts-dev.apixio.com"
caller="hcc_dev"
max_ret=2
max_doc_pages=2
max_opps = 2
coding_delay_time = 0
#recepients=["eng@apixio.com", "ops@apixio.com"]
recepients=["ishekhtman@apixio.com", "ishekhtman@apixio.com"]
usr="mmgenergyes@apixio.net"
action_weights = {'view':0, 'accept':34, 'reject':33, 'skip':33}
dos="04/04/2014"

if len(sys.argv) >= 2:
  usr=str(sys.argv[1])
if len(sys.argv) == 3:
  max_opps = int(sys.argv[2])


defineGlobals()
cookies = loginHCC(usr, pwd, hcchost, uahost, caller, max_opps)
pauseBreak()
totals = startCoding(usr, pwd, hcchost, cookies, max_opps, coding_delay_time, action_weights, dos)
printResults(dos, rep_type, env, action_weights, coding_delay_time, max_opps, max_ret, max_doc_pages, hcchost, start_time, totals, True, recepients)
#=======================================================================================================================
