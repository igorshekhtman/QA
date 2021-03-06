####################################################################################################
#
# PROGRAM: energyrouting.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    2015.08.05 Initial Version
#
# REVISION: Complete revision, re-design and re-write of the original test script
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    2016.01.29 Initial Version
#
#
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
#          * Results will be printed on Console screen as well as mailed via QA report
#		   ***************************************************************************************************************
#		   * python2.7 energyrouting.py
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
from copy import deepcopy
import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import *
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import collections
requests.packages.urllib3.disable_warnings()
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
#================================== ACT ON DOC (VIEW, ACCEPT, REJECT, SKIP) ============================================
def act_on_doc(url, cookies, opportunity, finding, finding_id, doc_no, action, totals, dos):

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
  print LSS
  print "* HCC CODE".ljust(25)+" = "+ str(hcc)+"-"+str(label_set_version)+"-"+str(sweep)+"-"+str(model_payment_year)
  print LSS
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
      print ("* "+ACTIONS[action].upper()+" FINDING").ljust(25)+" = "+ str(response.status_code)+" "+stat_codes[response.status_code]
      if response.status_code == r_stat_codes['ok']:
        retries = options['max_ret']
      else:
        retries += 1
        trackCount(ACTIONS[action]+"(retries)", totals, dt)
        trackCount(ACTIONS[action]+" "+json.dumps(DATA), totals, dt)
      trackCount(ACTIONS[action]+"("+str(response.status_code)+")", totals, dt)

  return (totals)
#=======================================================================================================================
def oppsServedTotals(options, coding_opp_current, opp, served_totals, buckets):
  bucket = getBucket(coding_opp_current, buckets)
  print "BUCKET NUMBER "+str(bucket)+" OF "+str(options['buckets'])
  if bucket not in served_totals:
    served_totals[bucket]={str(opp):1}
  else:
    if str(opp) not in served_totals[bucket]:
      served_totals[bucket][str(opp)]=1
    else:
      served_totals[bucket][str(opp)]+=1
  return(served_totals)
#=======================================================================================================================
def startCoding(options, cookies, buckets):
  global PERCENT_OF_SERVED, COUNT_OF_SERVED

  print LSS
  print "* HCC Url".ljust(25)+" = " + options['env_hosts']['hcchost']
  print "* Coder name".ljust(25)+ " = " + options['usr']
  print "* Coder pwd".ljust(25)+ " = " + options['pwd']
  print "* Max Opp(s)".ljust(25)+ " = " + str(options['max_opps'])
  print LSS
  nwiurl = options['env_hosts']['hcchost']+"api/next-work-item/"
  print "* HCC Url".ljust(25)+" = "+ nwiurl
  print "* csrftoken".ljust(25)+" = "+ cookies['csrftoken']
  print "* ApxToken".ljust(25)+" = "+ cookies['ApxToken']
  print "* sessionid".ljust(25)+" = "+ cookies['sessionid']
  headers = {'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"]}
  data = {}
  totals={}
  opps_totals={}
  served_totals={}
  det_totals={'hcc':{}, 'label_set_version':{}, 'sweep':{}, 'model_payment_year':{}}

  for coding_opp_current in range(1, (int(options['max_opps'])+1)):
    printSeparator("NEXT OPPORTUNITY")
    time.sleep(options['coding_delay_time'])
    print "* Url".ljust(25)+" = "+ nwiurl

    retries=0
    while retries < options['max_ret']:
        st = time.time()
        response = requests.get(nwiurl, data=data, headers=headers)
        dt = time.time() - st
        print "* Get coding opp".ljust(25)+" = "+str(response.status_code)+" "+stat_codes[response.status_code]


        if response.status_code == r_stat_codes['ok']:
            opportunity = response.json()
            retries = options['max_ret']
        else:
            retries += 1
            trackCount(str(nwiurl.split("/")[4])+"(retries)", totals, dt)
        trackCount(str(nwiurl.split("/")[4])+"("+str(response.status_code)+")", totals, dt)
    if response.status_code != r_stat_codes['ok']:
                return (totals, opps_totals)

    hcc = opportunity.get("code").get("hcc")
    det_totals = tallyDetails("hcc", hcc, det_totals)
    label_set_version = opportunity.get("code").get("labelSetVersion")
    det_totals = tallyDetails("label_set_version", label_set_version, det_totals)
    sweep = opportunity.get("code").get("sweep")
    det_totals = tallyDetails("sweep", sweep, det_totals)
    model_payment_year = opportunity.get("code").get("modelPaymentYear")
    det_totals = tallyDetails("model_payment_year", model_payment_year, det_totals)
    opp = str(hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year)
    trackOpps(opp, opps_totals)

    print SL
    print "* PATIENT OPP".ljust(25)+" = "+"%d OF %d" % (coding_opp_current, int(options['max_opps']))
    print "* HCC CODE".ljust(25)+" = "+str(hcc+"-"+label_set_version+"-"+sweep+"-"+model_payment_year)
    print "* PATIENT NAME".ljust(25)+" = "+str(opportunity.get("patient").get("first_name")[0:2]+" "+opportunity.get("patient").get("middle_name")[0:2]+" "+opportunity.get("patient").get("last_name")[0:2])
    print "* PATIENT DOB".ljust(25)+" = "+str(opportunity.get("patient").get("dob")[-4:])
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
    print "PATIENT OPP %d OF %d" % (coding_opp_current, int(options['max_opps']))
    served_totals = oppsServedTotals(options, coding_opp_current, opp, served_totals, buckets)

    doc_no_max = 1
    for doc_no in range (0,doc_no_max):
      finding = findings[doc_no]
      finding_id = finding_ids[doc_no]
      patient_org_id = finding.get("patient_org_id")  
      document_uuid = finding.get("sourceId")
      document_title = finding.get("document_title")
      date_of_service = finding.get("doc_date")
      mime_type = finding.get("mimeType")
      if mime_type == None:
        mime_type = "text/plain"
      printSeparator("GET NEXT FINDING")
      print "PATIENT DOC %d OF %d"    % (doc_no+1, doc_no_max)
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
        response = requests.get(dturl + document_uuid, data=data, headers=headers)
        dt = time.time() - st
        print "* GET SCRBLE DOC".ljust(25)+" = "+ str(response.status_code)+" "+stat_codes[response.status_code]
        if response.status_code == r_stat_codes['ok']:
          retries = options['max_ret']
        else:
          retries += 1
          trackCount(str(dturl.split("/")[4])+"(retries)", totals, dt)
          trackCount(str(dturl.split("/")[4])+" "+str(json.dumps(finding)), totals, dt)
        trackCount(str(dturl.split("/")[4])+"("+str(response.status_code)+")", totals, dt)
        if response.status_code != r_stat_codes['ok']:
          return (totals, opps_totals)

      action = WeightedRandomCodingAction(hcc, options)
      totals = act_on_doc(options['env_hosts']['hcchost'], cookies, opportunity, finding, finding_id, doc_no, action, totals, options['dos'])

  return (totals, opps_totals, det_totals, served_totals)
#=======================================================================================================================
def logout(options):
  print LS
  response = requests.get(options['env_hosts']['hcchost'] + "/account/logout")
  print "* LOGOUT".ljust(25) + " = " +str(response.status_code) + " " + stat_codes[response.status_code]
  if response.status_code != r_stat_codes['ok']:
    print "* CODER ACTION".ljust(25)+ " = " + "Logout"
    print "* HCC RESPONSE".ljust(25)+ " = " + "WARNING : Bad HCC Server Response " + str(response.status_code) + " " + stat_codes[response.status_code]
  return 0
#=======================================================================================================================
def tallyDetails(item, value, det_totals):
  if det_totals[item] == {}:
    det_totals[item][str(value)]=1
  else:
    if str(value) not in det_totals[item]:
      det_totals[item][str(value)]=1
    else:
      det_totals[item][str(value)]+=1
  return (det_totals)
#=======================================================================================================================
def WeightedRandomCodingAction(hcc_code, options):
  if hcc_code == options['target_hcc']:
    wkey='target'
  else:
    wkey='all'
  weights = {0: options['action_weights'][wkey]['vo'], \
             1: options['action_weights'][wkey]['va'], \
             2: options['action_weights'][wkey]['vr'], \
             3: options['action_weights'][wkey]['vs']}
  action = random.choice([w for w in weights for dummy in range(weights[w])])
  return (action)
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
  if options['max_opps']%options['buckets'] !=0:
    print "* Error".ljust(25)+" = Maximum number of opps " + str(options['max_opps'])+" must be divisible by 10"
    quit()
  print "* Buckets".ljust(25)+" = "+str(options['buckets'])
  print "* Opps per Bucket".ljust(25)+" = "+str(options['opps_per_bucket'])
  en_rout_stat =  str(setEnergyRoutingOn(options, cookies))
  print "* Energy Routing Status".ljust(25)+ " = " + en_rout_stat
  print "* TARGETED HCC".ljust(25)+ " = HCC-"+str(options['target_hcc'])
  print "* OVERALL ACCEPTS".ljust(25)+ " = "+ str(options['action_weights']['all']['va'])+"%"
  print "* OVERALL REJECT".ljust(25)+" = "+ str(options['action_weights']['all']['vr'])+"%"
  print ("* TARG HCC-"+str(options['target_hcc'])+" ACCEPT").ljust(25)+" = "+ str(options['action_weights']['target']['va'])+"%"
  print ("* TARG HCC-"+str(options['target_hcc'])+" REJECT").ljust(25)+" = "+ str(options['action_weights']['target']['vr'])+"%"
  print LS
  return(en_rout_stat)
#=======================================================================================================================
def drawGraph(srcedict, options, graph_title):
  global CURDAY
  img_name = str(CURDAY)
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
  title(graph_title)
  grid(True)
  savefig(img_name)
  return(img_name)
#=======================================================================================================================
def jsonToHtmlTable(sdict, sortby, hdr, col_width):
  lw=col_width.split("-")[0]
  rw=col_width.split("-")[1]
  report = "<table width='800' cellspacing='0' cellpadding='2' border='0'>"
  report += "<tr><td colspan='2' align='left'><b><font size='3'>"+str(hdr)+"</font></b></td></tr>"
  report += "<tr><td>"
  report += "<table width='800' cellspacing='0' cellpadding='2' border='1'>"
  if sortby == "value":
    sorteditems = sorted(sdict.items(), key=operator.itemgetter(1), reverse=True)
    ctr = 0
    for item in sorteditems:
      #if item[1] > 0:
        if ctr == 0:
          b_color = '#FFFF00'
          most_served = item[1]
        else:
          if (item[1] == most_served) or (item[0] == options['target_hcc']):
            b_color = '#FFFF00'
          else:
            b_color = '#FFFFFF'
        report += "<tr><td bgcolor='"+b_color+"' width='"+lw+"%'> HCC-"+str(item[0])+"</td><td bgcolor='"+b_color+"' width='"+rw+"%'><b>"+str(item[1])+"</b></td></tr>"
        ctr += 1
  else:
    sorteditems = sorted(sdict.items(), key=operator.itemgetter(0), reverse=False)
    for item in sorteditems:
      #if item[1] > 0:
        report +="<tr><td width='"+lw+"%'>"+str(item[0])+"</td><td width='"+rw+"%'><b>"+str(item[1])+"</b></td></tr>"
  report += "</table>"
  report += "</td></tr></table>"
  return (report)
#=======================================================================================================================
def extractTargetedHccData(targhcc, srcedict):
  extrdict = {}
  for k, v in sorted(srcedict.iteritems()):
    if v != 0:
      if targhcc in v.keys():
        extrdict.update({k: v[targhcc]})
      else:
        extrdict.update({k: 0})
  return (extrdict)
#=======================================================================================================================
def writeReport(options, totals, opps_totals, start_time, en_rout_stat, det_totals, served_totals, per_served_per_bucket, targ_hcc_per_serv_per_bucket):
  hours, minuts, seconds = checkDuration(start_time)
  end_time = time.time()

  r = ""
  r += "<h2>Apixio HCC Energy Routing Test Report</h2>"
  r += "Test Start (date & time): <b>"+strftime("%m/%d/%Y %H:%M:%S<br>", gmtime(start_time))+"</b>"
  r += "Test End (date & time): <b>"+strftime("%m/%d/%Y %H:%M:%S<br>", gmtime(end_time))+"</b>"
  r += "Test Duration: <b>"+"%s hours, %s minutes, %s seconds<br>"% (int(round(hours)), int(round(minuts)), int(round(seconds)))+"</b><br>"
  r += "Report type: <b>%s</b><br>" % (options['rep_type'])
  r += "HCC user name: <b>%s</b><br>" % (options['usr'])
  r += "HCC host url: <b>%s</b><br>" % (options['env_hosts']['hcchost'])
  r += "Enviromnent: <b><font color='red'>%s</font></b><br><br>" % (options['env'])
  r += "Max. # of Opps: <b>%s</b><br>"%(options['max_opps'])
  r += "Total # of Buckets: <b>%s</b><br>"%(options['buckets'])
  r += "Opps per Bucket: <b>%s</b><br>"%(options['opps_per_bucket'])
  r += "Max. # of Retries: <b>%s</b><br>"%(options['max_ret'])
  r += "Coding Delay Time: <b>%s sec</b><br>"%(options['coding_delay_time'])
  r += "Accepts Date of Service: <b>%s</b><br>"%(options['dos'])
  r += "Energy Routing Status: <b>%s</b><br><br>"%("<font color='green'>ON</color>" if en_rout_stat else "<font color='red'>OFF</color>")
  r += "<table align='left' width='800' cellpadding='1' cellspacing='1'><tr><td>"
  r += "<table align='left' width='800' cellpadding='1' cellspacing='1'>"
  printSeparator("ENERGY ROUTING TEST RESULTS SUMMARY")
  r +=  "<tr><td bgcolor='"+getBgColor('(heading)')+"'>ENERGY ROUTING TEST RESULTS SUMMARY</td><td bgcolor='"+getBgColor('(heading)')+"'>TOT#</td><td bgcolor='"+getBgColor('(heading)')+"'>AVE</td><td bgcolor='"+getBgColor('(heading)')+"'>MIN</td><td bgcolor='"+getBgColor('(heading)')+"'>MAX</td></tr>"
  for total in sorted(totals, key=lambda x:x[0].upper()):
    r +=  ("<tr><td width='650' bgcolor='"+getBgColor(total)+"'> "+ total[0].upper())+total[1:]+"</td><td bgcolor='"+getBgColor(total)+"'> " + str(totals[total][0])+"</td><td bgcolor='"+getBgColor(total)+"'> " + convTimeString(totals[total][1]/totals[total][0])+"</td><td bgcolor='"+getBgColor(total)+"'> " + convTimeString(totals[total][2])+"</td><td bgcolor='"+getBgColor(total)+"'> " + convTimeString(totals[total][3])+"</td></tr>"
  r +=  "<tr><td bgcolor='"+getBgColor('(heading)')+"' colspan='5'>ENERGY ROUTING TEST COMPLETE</td></tr>"
  r +=  "</table>"
  r += "<table align='left' width='800' cellpadding='1' cellspacing='1'>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td align='center'><font size='4'><b>TARGETED HCC-%s</b></font></td></tr>" % (options['target_hcc'])
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td>Overall Accept rate: <b>"+str(options['action_weights']['all']['va'])+"%</b></td></tr>"
  r += "<tr><td>Overall Reject rate: <b>"+str(options['action_weights']['all']['vr'])+"%</b></td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td>HCC-"+str(options['target_hcc'])+" Accept rate: <b>"+str(options['action_weights']['target']['va'])+"%</b></td></tr>"
  r += "<tr><td>HCC-"+str(options['target_hcc'])+" Reject rate: <b>"+str(options['action_weights']['target']['vr'])+"%</b></td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(det_totals['hcc'], "key", "HCCs", "30-80")+"</td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(det_totals['model_payment_year'], "key", "Model payment year", "30-80")+"</td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(det_totals['sweep'], "key", "Sweep", "30-80")+"</td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(det_totals['label_set_version'], "key", "Label set version", "30-80")+"</td></tr>"
  r += "<tr><td><hr></td></tr>"

  r += "<tr><td>"+jsonToHtmlTable(opps_totals, "value", "Total count of individual HCCs served", "30-80")+"</td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(served_totals, "key", "Number of HCCs served per bucket", "5-95")+"</td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(per_served_per_bucket, "key", "% of HCCs served per bucket", "5-95")+"</td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td>"+jsonToHtmlTable(targ_hcc_per_serv_per_bucket, "key", "% of Targeted HCC-"+str(options['target_hcc'])+" served per bucket", "5-95")+"</td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td><img src='cid:picture@example.com' width='800' height='600'></td></tr>"
  r += "<tr><td><hr></td></tr>"
  r += "<tr><td><br>Start of %s - <b>%s</b></td></tr>" % (options['rep_type'], strftime("%m/%d/%Y %H:%M:%S<br>", gmtime(start_time)))
  r += "<tr><td>End of %s - <b>%s</b></td></tr>" % (options['rep_type'], strftime("%m/%d/%Y %H:%M:%S<br>", gmtime(end_time)))
  r += "<tr><td>Test Duration: <b>%s hrs %s min %s sec</b><br></td></tr>" % (int(round(hours)), int(round(minuts)), int(round(seconds)))
  r += "<tr><td><br><i>-- Apixio QA Team</i></td></tr>"
  r += "</table>"
  r += "</td></tr></table>"
  r += "</td></tr></table>"
  return(r)
#=======================================================================================================================
def archiveReport(report):
	global DEBUG_MODE, ENVIRONMENT, CURMONTH, CURDAY, IMAGEFILENAME
	if not DEBUG_MODE:
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
		REPORTFILE.write(report)
		REPORTFILE.close()
		os.chdir(REPORTFOLDER)
		REPORTFILE = open(REPORTFILENAME, 'w')
		REPORTFILE.write(report)
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
#=======================================================================================================================
def emailReport(options, report, img_name):
  imagefname=img_name+".png"
  message = MIMEMultipart('related')
  message.attach(MIMEText((report), 'html'))
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
  printSeparator("HCC ENERGY ROUTING TEST RESULTS SUMMARY")
  print "* Test Started".ljust(25)+" = "+strftime("%m/%d/%Y %H:%M:%S", gmtime(start_time))
  print "* Test Ended".ljust(25)+" = "+strftime("%m/%d/%Y %H:%M:%S", gmtime())
  print "* Test Duration".ljust(25)+" = "+"%s hours, %s minutes, %s seconds"% (int(round(hours)), int(round(minuts)), int(round(seconds)))
  for total in sorted(totals, key=lambda x:x[0].upper()):
    print ("* "+ total[0].upper()+total[1:]).ljust(25)+" = " + str(totals[total][0]) + ' ' + convTimeString(totals[total][1]/totals[total][0]) + ' ' + convTimeString(totals[total][2]) + ' ' + convTimeString(totals[total][3])
  printSeparator("HCC ENERGY ROUTING TEST COMPLETE")
  return()
#=======================================================================================================================
def trackOpps(opp, opps_totals):
  if opp not in opps_totals:
    opps_totals[opp]=1
  else:
    opps_totals[opp] += 1
  return(opps_totals)
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
def pauseBreak():
  user_response = raw_input(">>> Press [Enter] to Proceed or [Q] to Quit: ")
  if user_response.upper() == "Q":
    print "exiting ..."
    quit()
  return ()
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
  global stat_codes, r_stat_codes
  global START_TIME, TIME_START, MONTH_FMN, CURDAY, CURMONTH

  START_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
  TIME_START=time.time()
  MONTH_FMN=strftime("%B", gmtime())
  CURDAY=strftime("%d", gmtime())
  CURMONTH=strftime("%m", gmtime())

  stat_codes = {200:'ok', 201:'created', 202:'accepted', 204:'nocontent', \
                301:'movedperm', 302:'redirect', \
                401:'unauthorized', 403:'forbidden', 404:'notfound', \
                500:'intservererror', 503:'survunavail'}
  r_stat_codes = {v: k for k, v in stat_codes.items()}

  LS  = "="*80
  LSS = "-"*80
  SL  = "*"*80
  ACTIONS = {0: "View Only", 1: "Accept", 2: "Reject", 3: "Skip"}

  if options['max_opps'] % 10 != 0:
      print "* Error".ljust(25)+" = Maximum number of opps "+str(options['max_opps'])+" must be divisible by 10"
      quit()

  return()
#=======================================================================================================================
def generateBuckets(options):
  buckets = []
  for i in range (1,options['max_opps'],options['opps_per_bucket']):
    l = []
    for j in range (options['opps_per_bucket']):
      l.append(i+j)
    buckets.append(l)
  return(buckets)
#=======================================================================================================================
def getBucket(coding_opp_current, buckets):
  bucket_number = 10
  for bucket in buckets:
    if coding_opp_current in bucket:
      bucket_number = buckets.index(bucket)+1
  return(bucket_number)
#=======================================================================================================================
def convertToPercentPerBucket(options, served_totals):
  per_served_per_bucket=deepcopy(served_totals)
  targ_hcc_per_serv_per_bucket={}
  for total in served_totals:
    targ_hcc_per_serv_per_bucket[total] = round(float(0.00),2)
    for hcc in served_totals[total]:
      per_served = round(float(served_totals[total][hcc])/float(options['opps_per_bucket']),2)
      per_served_per_bucket[total][hcc] = per_served
      if hcc.split("-")[0] == str(options['target_hcc']):
        targ_hcc_per_serv_per_bucket[total] = per_served
  return(per_served_per_bucket, targ_hcc_per_serv_per_bucket)
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
  #options['usr'] = sys.argv[2] if len(sys.argv) > 2 else "energyrouting@apixio.net"
  options['usr'] = sys.argv[2] if len(sys.argv) > 2 else "energyes@apixio.net"
  options['pwd'] = 'apixio.123'
  options['env_hosts'] = getEnvHosts(options['env'])
  options['max_opps'] = int(sys.argv[3]) if len(sys.argv) > 3 else 10
  options['max_ret'] = int(sys.argv[4]) if len(sys.argv) > 4 else 10
  options['coding_delay_time'] = int(sys.argv[5]) if len(sys.argv) > 5 else 0
  options['target_hcc'] = str(sys.argv[6]) if len(sys.argv) > 6 else "105"
  options['dos'] = str(sys.argv[7]) if len(sys.argv) > 7 else "04/04/2014"
  options['report_recepients'] = [str(sys.argv[8])] if len(sys.argv) > 8 else ["ishekhtman@apixio.com"]
  options['action_weights'] = {'all':{'vo':0, 'va':10, 'vr':90, 'vs':0}, 'target':{'vo':0, 'va':95, 'vr':5, 'vs':0}}

  options['buckets'] = 10
  if options['max_opps']%options['buckets'] != 0:
    print "* Error".ljust(25)+" = Maximum number of opps " + str(options['max_opps'])+" must be divisible by 10"
    quit()
  else:
    options['opps_per_bucket'] =  options['max_opps']/options['buckets']


  defineGlobals(options)
  cookies = loginHCC(options)
  en_rout_stat = confirmSettings(options, cookies)
  #pauseBreak()
  buckets = generateBuckets(options)
  totals, opps_totals, det_totals, served_totals = startCoding(options, cookies, buckets)
  per_served_per_bucket, targ_hcc_per_serv_per_bucket = convertToPercentPerBucket(options, served_totals)
  img_name = drawGraph(targ_hcc_per_serv_per_bucket, options, "HCC Energy Routing Test")

  printResults(options, start_time, totals)
  logout(options)
  report = writeReport(options, totals, opps_totals, start_time, \
                             en_rout_stat, det_totals, served_totals, \
                             per_served_per_bucket, targ_hcc_per_serv_per_bucket)
  #archiveReport(report)
  emailReport(options, report, img_name)

if __name__ == "__main__":
  Main()
#=======================================================================================================================