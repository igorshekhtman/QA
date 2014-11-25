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
#          * View QA Report
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

# LIBRARIES ########################################################################################

from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
import time
import datetime
import csv
import operator
import random

# GLOBAL VARIABLES #######################################################################

#CSV_CONFIG_FILE_PATH = "/mnt/automation/grinder/grinder5-file-store/incoming/"
#CSV_CONFIG_FILE_PATH = "c:\\!.alex\\!.grinder-3.11\\examples\\"
CSV_CONFIG_FILE_PATH = "/Users/ishekhtman/Documents/grinder/grinder-3.11/examples/"
CSV_CONFIG_FILE_NAME = "hccconfig.csv"

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
def ReadConfigurationFile(filename):
  global MAX_NUM_RETRIES

  result={ }
  csvfile = open(filename, 'rb')
  reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
  for row in reader:
    if (str(row[0])[0:1] <> '#') and (str(row[0])[0:1] <> ' '):
      result[row[0]] = row[1]
  globals().update(result)
  MAX_NUM_RETRIES = int(result["MAX_NUM_RETRIES"])
  return result
##########################################################################################

#ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))
ReadConfigurationFile(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME)

ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
forbidden = 403
intserveror = 500
servunavail = 503

FAILED = 0
SUCCEEDED = 0
RETRIED = 0

# MAIN FUNCTIONS ####################################################################################################

def code():
  global RANDOM_OPPS_ACTION, CODE_OPPS_ACTION
  log("-------------------------------------------------------------------------------")
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
  log("URL                = %s\nCODER USERNAME     = %s\nCODER PASSWORD     = %s\nCODER ACTION       = %s\nMAX PATIENT OPP(S) = %s" % (URL, USERNAME, PASSWORD, action, CODE_OPPS_MAX))
  thread_context = HTTPPluginControl.getThreadHTTPClientContext()
  control = HTTPPluginControl.getConnectionDefaults()
  control.setFollowRedirects(1)
  result = create_request(Test(1, "Connect to host")).GET(URL + "/")
  result = create_request(Test(2, "Get login page")).GET(URL + "/account/login/?next=/")
  login = create_request(Test(3, "Log in user"),[NVPair("Referer", URL + "/account/login/?next=/"),])
  response = login.POST(URL + "/account/login/?next=/", (NVPair("csrfmiddlewaretoken", get_csrf_token(thread_context)), NVPair("username", USERNAME), NVPair("password", PASSWORD),))
  coding_opp_current = 1
  for coding_opp_current in range(1, (int(CODE_OPPS_MAX)+1)):
    testCode = 10 + (1 * coding_opp_current)
    response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
    opportunity = JSONValue.parse(response.getText())
    patient_details = response.getText()
    IncrementTestResultsTotals(response.statusCode)
    if opportunity == None:
      log("ERROR : Login Failed or No More Opportunities For This Coder")
      return 1
    patient_uuid = ""
    patient_uuid = opportunity.get("patient_uuid")
    scorables = opportunity.get("scorables")
    log("-------------------------------------------------------------------------------")
    log("PATIENT OPP %d OF %d" % (coding_opp_current, int(CODE_OPPS_MAX)))
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
      log("PATIENT DOC %d OF %d\n* PATIENT ORG ID   = %s\n* PATIENT UUID     = %s\n* FINDING ID       = %s\n* DOC UUID         = %s\n* DOC TITLE        = %s\n* DOC DATE         = %s" % (doc_no_current, doc_no_max, patient_org_id, patient_uuid, finding_id, document_uuid, document_title, date_of_service))
      if patient_uuid    == "":
        log("WARNING : PATIENT UUID is Empty")
      if patient_org_id  == "":
        log("WARNING : ORG ID is Empty")
      if finding_id      == "":
        log("WARNING : FINDING ID is Empty")
      if document_uuid   == "":
        log("WARNING : DOC UUID is Empty")
      if document_title  == "":
        log("WARNING : DOC TITLE is Empty")
      if date_of_service == "":
        log("WARNING : DOC DATE is Empty")
      test_counter = test_counter + 1
      doc_request = create_request(Test(testCode + test_counter, "Get scorable document"),[NVPair("Referer", URL + "/"),NVPair("Host", DOMAIN),])
      response = doc_request.GET(URL + "/api/document/" + document_uuid)
# *AB*      log (str(response))
      IncrementTestResultsTotals(response.statusCode)
      test_counter = test_counter + 1
      if RANDOM_OPPS_ACTION == "1":
        CODE_OPPS_ACTION = str(random.randint(0,3)) 
      act_on_doc(opportunity, scorable, testCode + test_counter, doc_no_current, doc_no_max)
  return 0

def history():
  log("-------------------------------------------------------------------------------")
  log("URL                = %s\nCODER USERNAME     = %s\nCODER PASSWORD     = %s\nCODER ACTION       = View History Report" % (URL, USERNAME, PASSWORD))
  thread_context = HTTPPluginControl.getThreadHTTPClientContext()
  control = HTTPPluginControl.getConnectionDefaults()
  control.setFollowRedirects(1)
  result = create_request(Test(1, "Connect to host")).GET(URL + "/")
  result = create_request(Test(2, "Get login page")).GET(URL + "/account/login/?next=/")
  login = create_request(Test(3, "Log in user"),[NVPair("Referer", URL + "/account/login/?next=/"),])
  response = login.POST(URL + "/account/login/?next=/", (NVPair("csrfmiddlewaretoken", get_csrf_token(thread_context)), NVPair("username", USERNAME), NVPair("password", PASSWORD),))
  IncrementTestResultsTotals(response.statusCode)
  view_history_count = 1
  testCode = 10 + (1 * view_history_count)
  response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
  opportunity = JSONValue.parse(response.getText())
  patient_details = response.getText()
  if opportunity == None:
    log("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  for view_history_count in range(1, (int(VIEW_HISTORY_MAX)+1)):
    log("-------------------------------------------------------------------------------")
    log("Report %d OF %d" % (view_history_count, int(VIEW_HISTORY_MAX)))
    now = datetime.datetime.now()
    report_range = "/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z&user=%s" % (now.year, now.month, now.day, USERNAME)
    response = create_request(Test(testCode, "View History Report")).GET(URL + report_range)
    IncrementTestResultsTotals(response.statusCode)
    if response.statusCode == 200:
      log("* CODER ACTION     = View History Report\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = View History Report\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
    view_history_details = response.getText()
    view_history_details_length = len(view_history_details)
    log("* REPORT PAYLOAD   = %d KBytes" % view_history_details_length)
  return 0

def report():
  log("-------------------------------------------------------------------------------")
  log("URL                = %s\nCODER USERNAME     = %s\nCODER PASSWORD     = %s\nCODER ACTION       = QA Report" % (URL, USERNAME, PASSWORD))
  thread_context = HTTPPluginControl.getThreadHTTPClientContext()
  control = HTTPPluginControl.getConnectionDefaults()
  control.setFollowRedirects(1)
  result = create_request(Test(1, "Connect to host")).GET(URL + "/")
  result = create_request(Test(2, "Get login page")).GET(URL + "/account/login/?next=/")
  login = create_request(Test(3, "Log in user"),[NVPair("Referer", URL + "/account/login/?next=/"),])
  response = login.POST(URL + "/account/login/?next=/", (NVPair("csrfmiddlewaretoken", get_csrf_token(thread_context)), NVPair("username", USERNAME), NVPair("password", PASSWORD),))
  IncrementTestResultsTotals(response.statusCode)
  qa_report_count = 1
  testCode = 10 + (1 * qa_report_count)
  response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
  opportunity = JSONValue.parse(response.getText())
  patient_details = response.getText()
  if opportunity == None:
    log("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  for qa_report_count in range(1, (int(QA_REPORT_MAX)+1)):
    log("-------------------------------------------------------------------------------")
    log("Report %d OF %d" % (qa_report_count, int(QA_REPORT_MAX)))
    now = datetime.datetime.now()
    report_range = "/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z" % (now.year, now.month, now.day)
    response = create_request(Test(testCode, "QA Report")).GET(URL + report_range)
    IncrementTestResultsTotals(response.statusCode)
    if response.statusCode == 200:
      log("* CODER ACTION     = QA Report\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = QA Report\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
    qa_report_details = response.getText()
    qa_report_details_length = len(qa_report_details)
    log("* REPORT PAYLOAD   = %d KBytes" % qa_report_details_length)
  return 0

def logout():
  log("-------------------------------------------------------------------------------")
  testCode = 99
  response = create_request(Test(testCode, "Logout")).GET(URL + "/account/logout")
  IncrementTestResultsTotals(response.statusCode)
  if response.statusCode == 200:
    log("* CODER ACTION     = Logout\n* HCC RESPONSE     = 200 OK")
  else:
    log("* CODER ACTION     = Logout\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  return 0

# HELPER FUNCTIONS ####################################################################################################

def log(text):
  grinder.logger.info(text)
  print(text)
  return 0

def create_request(test, headers=None):
  request = HTTPRequest()
  if headers:
    request.headers = headers
  test.record(request)
  return request

def get_csrf_token(thread_context):
  cookies = CookieModule.listAllCookies(thread_context)
  csrftoken = ""
  for cookie in cookies:
    if cookie.getName() == "csrftoken":
      csrftoken = cookie.getValue()
  return csrftoken

def IncrementTestResultsTotals(code):
  global FAILED, SUCCEEDED, RETRIED
  if (code == ok) or (code == nocontent):
    SUCCEEDED = SUCCEEDED+1
  elif code == intserveror:
    RETRIED = RETRIED+1
  else:
    FAILED = FAILED+1

def act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max):
  global CODE_OPPS_ACTION
  if CODE_OPPS_ACTION == "0": # Do NOT Accept or Reject Doc
    log("* CODER ACTION     = Do NOT Accept or Reject Doc")
  elif CODE_OPPS_ACTION == "1": # Accept Doc
    finding_id = scorable.get("id")
    annotation = create_request(Test(testname, "Annotate Finding"))
    response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    NVPair("user_id", USERNAME),
    NVPair("timestamp",str(1000 * int(time.time()))),
    NVPair("result","accept"),
    NVPair("comment","Comment by The Grinder"),
    NVPair("date_of_service",scorable.get("date_of_service")),
    NVPair("flag_for_review","true"),
    NVPair("icd9[code_system_name]", opportunity.get("suggested_codes")[0].get("[code_system_name")),
    NVPair("icd9[code]", opportunity.get("suggested_codes")[0].get("[code")),
    NVPair("icd9[display_name]", opportunity.get("suggested_codes")[0].get("[display_name")),
    NVPair("icd9[code_system]", opportunity.get("suggested_codes")[0].get("[code_system")),
    NVPair("icd9[code_system_version]", opportunity.get("suggested_codes")[0].get("[code_system_version")),
    NVPair("provider[name]","The Grinder M.D."),
    NVPair("provider[id]","1992754832"),
    NVPair("provider[type]","Hospital Outpatient Setting"),
    NVPair("payment_year",str(opportunity.get("payment_year"))),
    NVPair("orig_date_of_service",scorable.get("date_of_service")),
    NVPair("opportunity_hash",opportunity.get("hash")),
    NVPair("rule_hash",opportunity.get("rule_hash")),
    NVPair("get_id",str(opportunity.get("get_id"))),
    NVPair("patient_uuid",opportunity.get("patient_uuid")),
    NVPair("patient_org_id",str(scorable.get("patient_org_id"))),
    NVPair("hcc[code]",str(opportunity.get("hcc"))),
    NVPair("hcc[model_run]",opportunity.get("model_run")),
    NVPair("hcc[model_year]",str(opportunity.get("model_year"))),
    NVPair("hcc[description]",opportunity.get("hcc_description")),
    NVPair("hcc[label_set_version]",opportunity.get("label_set_version")),
    NVPair("hcc[mapping_version]",str(opportunity.get("model_year")) + " " + opportunity.get("model_run")),
    NVPair("hcc[code_system]",str(opportunity.get("model_year")) + "PYFinal"),
    NVPair("finding_id",str(finding_id)),
    NVPair("document_uuid", scorable.get("document_uuid")),
    NVPair("list_position",str(doc_no_current)),
    NVPair("list_length",str(doc_no_max)),
    NVPair("document_date",scorable.get("date_of_service")),
    NVPair("predicted_code[code_system_name]", "The Grinder"),
    NVPair("predicted_code[code]", "The Grinder"),
    NVPair("predicted_code[display_name]", "The Grinder"),
    NVPair("predicted_code[code_system]", "The Grinder"),
    NVPair("predicted_code[code_system_version]", "The Grinder"),
    NVPair("page_load_time",str(1000 * int(time.time()))),
    NVPair("document_load_time",str(1000 * int(time.time()))),))
    IncrementTestResultsTotals(response.statusCode)
    if response.statusCode == 200:
      log("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  elif CODE_OPPS_ACTION == "2": # Reject Doc
    finding_id = scorable.get("id")
    annotation = create_request(Test(testname, "Annotate Finding"))
    response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    NVPair("user_id", USERNAME),
    NVPair("timestamp",str(1000 * int(time.time()))),
    NVPair("result","reject"),
    NVPair("reject_reason","Additional documentation needed to Accept the document for this HCC"),
    NVPair("comment","Comment by The Grinder"),
    NVPair("date_of_service",scorable.get("date_of_service")),
    NVPair("flag_for_review","true"),
    NVPair("payment_year",str(opportunity.get("payment_year"))),
    NVPair("orig_date_of_service",scorable.get("date_of_service")),
    NVPair("opportunity_hash",opportunity.get("hash")),
    NVPair("rule_hash",opportunity.get("rule_hash")),
    NVPair("get_id",str(opportunity.get("get_id"))),
    NVPair("patient_uuid",opportunity.get("patient_uuid")),
    NVPair("patient_org_id",str(scorable.get("patient_org_id"))),
    NVPair("hcc[code]",str(opportunity.get("hcc"))),
    NVPair("hcc[model_run]",opportunity.get("model_run")),
    NVPair("hcc[model_year]",str(opportunity.get("model_year"))),
    NVPair("hcc[description]",opportunity.get("hcc_description")),
    NVPair("hcc[label_set_version]",opportunity.get("label_set_version")),
    NVPair("hcc[mapping_version]",str(opportunity.get("model_year")) + " " + opportunity.get("model_run")),
    NVPair("hcc[code_system]",str(opportunity.get("model_year")) + "PYFinal"),
    NVPair("finding_id",str(finding_id)),
    NVPair("document_uuid", scorable.get("document_uuid")),
    NVPair("list_position",str(doc_no_current)),
    NVPair("list_length",str(doc_no_max)),
    NVPair("document_date",scorable.get("date_of_service")),
    NVPair("snippets",str(scorable.get("snippets"))),
    NVPair("predicted_code[code_system_name]", "The Grinder"),
    NVPair("predicted_code[code]", "The Grinder"),
    NVPair("predicted_code[display_name]", "The Grinder"),
    NVPair("predicted_code[code_system]", "The Grinder"),
    NVPair("predicted_code[code_system_version]", "The Grinder"),
    NVPair("page_load_time",str(1000 * int(time.time()))),
    NVPair("document_load_time",str(1000 * int(time.time()))),))
    if response.statusCode == 200:
      log("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  elif CODE_OPPS_ACTION == "3": # Skip Opp
    finding_id = scorable.get("id")
    annotation = create_request(Test(testname, "Annotate Finding"))
    response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    NVPair("user_id", USERNAME),
    NVPair("timestamp",str(1000 * int(time.time()))),
    NVPair("result","skipped"),
    NVPair("date_of_service",scorable.get("date_of_service")),
    NVPair("payment_year",str(opportunity.get("payment_year"))),
    NVPair("orig_date_of_service",scorable.get("date_of_service")),
    NVPair("opportunity_hash",opportunity.get("hash")),
    NVPair("rule_hash",opportunity.get("rule_hash")),
    NVPair("get_id",str(opportunity.get("get_id"))),
    NVPair("patient_uuid",opportunity.get("patient_uuid")),
    NVPair("hcc[code]",str(opportunity.get("hcc"))),
    NVPair("hcc[model_run]",opportunity.get("model_run")),
    NVPair("hcc[model_year]",str(opportunity.get("model_year"))),
    NVPair("hcc[description]",opportunity.get("hcc_description")),
    NVPair("hcc[label_set_version]",opportunity.get("label_set_version")),
    NVPair("hcc[mapping_version]",str(opportunity.get("model_year")) + " " + opportunity.get("model_run")),
    NVPair("hcc[code_system]",str(opportunity.get("model_year")) + "PYFinal"),
    NVPair("finding_id",str(finding_id)),
    NVPair("document_uuid", scorable.get("document_uuid")),
    NVPair("patient_org_id",str(scorable.get("patient_org_id"))),
    NVPair("list_position",str(doc_no_current)),
    NVPair("list_length",str(doc_no_max)),
    NVPair("document_date",scorable.get("date_of_service")),
    NVPair("snippets",str(scorable.get("snippets"))),
    NVPair("predicted_code[code_system_name]", "The Grinder"),
    NVPair("predicted_code[code]", "The Grinder"),
    NVPair("predicted_code[display_name]", "The Grinder"),
    NVPair("predicted_code[code_system]", "The Grinder"),
    NVPair("predicted_code[code_system_version]", "The Grinder"),
    NVPair("page_load_time",str(1000 * int(time.time()))),
    NVPair("document_load_time",str(1000 * int(time.time()))),))
    IncrementTestResultsTotals(response.statusCode)
    if response.statusCode == 200:
      log("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = Skip Opp\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  else:
    log("* CODER ACTION     = Unknown\n")
  return 0

# MAIN FUNCTION CALLER ####################################################################################################

class TestRunner:
  def __call__(self):
  	#i = random.randint(0,5)
  	#i = 100
  	#print "random number: %s" % i
    log("============================= START GRINDER TEST ============================")
    if CODE_OPPS    == "1":
      code()
    if VIEW_HISTORY == "1":
      history()
    if QA_REPORT    == "1":
      report()
    if LOGOUT       == "1":
      logout()
    log("=============================================================================")
    log("Test execution results summary:")
    log("=============================================================================")
    log("RETRIED: %s\t" % RETRIED)
    log("FAILED: %s\t" % FAILED)
    log("SUCCEEDED: %s\t" % SUCCEEDED)
    log("TOTAL: %s\t" % (RETRIED+FAILED+SUCCEEDED))
    log("=============================================================================")
    log("============================== END GRINDER TEST =============================")
    log("=============================================================================")
    log("\n")
