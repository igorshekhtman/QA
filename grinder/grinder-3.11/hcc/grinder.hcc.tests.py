####################################################################################################
#
# PROGRAM: grinder.py
# AUTHOR:  Alex Beyk abeyk@apixio.com
# DATE:    2014.10.16
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

# LIBRARIES ####################################################################################################

from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
import time
import datetime

# GLOBAL VARIABLES ####################################################################################################

DOMAIN           = "hcc.apixio.com"
URL              = "https://%s" % DOMAIN
USERNAME         = "root@api.apixio.com"
PASSWORD         = "thePassword"
#USERNAME        = "hillroot@apixio.net"
#PASSWORD        = "multiplexor"
#USERNAME        = "hcpnvroot@apixio.net" # Simulate No Opportunities
#PASSWORD        = "multiplexor"          # Simulate No Opportunities
CODE_OPPS        = 1 # 0 means Do NOT code Opps, 1 means code Opps
CODE_OPPS_ACTION = 1 # 0 means Do NOT Accept or Reject Doc, 1 means Accept Doc, 2 means Reject Doc, 3 means Skip Opp
CODE_OPPS_MAX    = 2 # Number of Opps to Code
VIEW_HISTORY     = 1 # 0 means Do NOT select View History, 1 means select View History
VIEW_HISTORY_MAX = 2 # Number of View History Reports to View
QA_REPORT        = 1 # 0 means Do NOT select QA Report, 1 means select QA Report
QA_REPORT_MAX    = 2 # Number of QA Reports to View
LOGOUT           = 1 # 0 means Do NOT select Logout, 1 means Logout

# MAIN FUNCTIONS ####################################################################################################

def code():
  log("-------------------------------------------------------------------------------")
  if CODE_OPPS_ACTION == 0: # Do NOT Accept or Reject Doc
    action = "Do NOT Accept or Reject Doc"
  elif CODE_OPPS_ACTION == 1: # Accept Doc
    action = "Accept Docs"
  elif CODE_OPPS_ACTION == 2: # Reject Doc
    action = "Reject Docs"
  elif CODE_OPPS_ACTION == 3: # Skip Opp
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
  for coding_opp_current in range(1, (CODE_OPPS_MAX+1)):
    testCode = 10 + (1 * coding_opp_current)
    response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
    opportunity = JSONValue.parse(response.getText())
    patient_details = response.getText()
    if opportunity == None:
      log("ERROR : Login Failed or No More Opportunities For This Coder")
      return 1
    patient_uuid = ""
    patient_uuid = opportunity.get("patient_uuid")
    scorables = opportunity.get("scorables")
    log("-------------------------------------------------------------------------------")
    log("PATIENT OPP %d OF %d" % (coding_opp_current, CODE_OPPS_MAX))
    test_counter = 0
    doc_no_current = 0
    doc_no_max = len(scorables)
    for scorable in scorables:
      org_id          = ""
      finding_id      = ""
      document_uuid   = ""
      document_title  = ""
      date_of_service = ""
      doc_no_current = doc_no_current + 1
      org_id = scorable.get("org_id")
      finding_id = scorable.get("id")
      document_uuid = scorable.get("document_uuid")
      document_title = scorable.get("document_title")
      date_of_service = scorable.get("date_of_service")
      log("PATIENT DOC %d OF %d\n* ORG ID           = %s\n* PATIENT UUID     = %s\n* FINDING ID       = %s\n* DOC UUID         = %s\n* DOC TITLE        = %s\n* DOC DATE         = %s" % (doc_no_current, doc_no_max, org_id, patient_uuid, finding_id, document_uuid, document_title, date_of_service))
      if patient_uuid    == "":
        log("WARNING : PATIENT UUID is Empty")
      if org_id          == "":
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
      test_counter = test_counter + 1
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
  view_history_count = 1
  testCode = 10 + (1 * view_history_count)
  response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
  opportunity = JSONValue.parse(response.getText())
  patient_details = response.getText()
  if opportunity == None:
    log("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  for view_history_count in range(1, (VIEW_HISTORY_MAX+1)):
    log("-------------------------------------------------------------------------------")
    log("Report %d OF %d" % (view_history_count, VIEW_HISTORY_MAX))
    now = datetime.datetime.now()
    report_range = "/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z&user=%s" % (now.year, now.month, now.day, USERNAME)
    response = create_request(Test(testCode, "View History Report")).GET(URL + report_range)
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
  qa_report_count = 1
  testCode = 10 + (1 * qa_report_count)
  response = create_request(Test(testCode, "Get coding opportunity")).GET(URL + "/api/coding-opportunity/")
  opportunity = JSONValue.parse(response.getText())
  patient_details = response.getText()
  if opportunity == None:
    log("ERROR : Login Failed or No More Opportunities For This Coder")
    return 1
  for qa_report_count in range(1, (QA_REPORT_MAX+1)):
    log("-------------------------------------------------------------------------------")
    log("Report %d OF %d" % (qa_report_count, QA_REPORT_MAX))
    now = datetime.datetime.now()
    report_range = "/api/report/qa_report?page=1&result=all&start=2014-01-01T07%%3A00%%3A00.000Z&end=%d-%d-%dT06%%3A59%%3A59.999Z" % (now.year, now.month, now.day)
    response = create_request(Test(testCode, "QA Report")).GET(URL + report_range)
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

def act_on_doc(opportunity, scorable, testname, doc_no_current, doc_no_max):
  if CODE_OPPS_ACTION == 0: # Do NOT Accept or Reject Doc
    log("* CODER ACTION = Do NOT Accept or Reject Doc")
  elif CODE_OPPS_ACTION == 1: # Accept Doc
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
    NVPair("org_id",str(scorable.get("org_id"))),
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
    NVPair("list_position",str(doc_no_current)),
    NVPair("list_length",str(doc_no_max)),
    NVPair("document_date",scorable.get("date_of_service")),
    NVPair("snippets",str(scorable.get("snippets"))),
    NVPair("predicted_code[code_system_name]", "The Grinder"),
    NVPair("predicted_code[code]", "The Grinder"),
    NVPair("predicted_code[display_name]", "The Grinder"),
    NVPair("predicted_code[code_system]", "The Grinder"),
    NVPair("predicted_code[code_system_version]", "The Grinder"),
    NVPair("page_load_time",str(1000 * int(time.time()))),))
    if response.statusCode == 200:
      log("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = Accept Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  elif CODE_OPPS_ACTION == 2: # Reject Doc
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
    NVPair("org_id",str(scorable.get("org_id"))),
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
    NVPair("list_position",str(doc_no_current)),
    NVPair("list_length",str(doc_no_max)),
    NVPair("document_date",scorable.get("date_of_service")),
    NVPair("snippets",str(scorable.get("snippets"))),
    NVPair("predicted_code[code_system_name]", "The Grinder"),
    NVPair("predicted_code[code]", "The Grinder"),
    NVPair("predicted_code[display_name]", "The Grinder"),
    NVPair("predicted_code[code_system]", "The Grinder"),
    NVPair("predicted_code[code_system_version]", "The Grinder"),
    NVPair("page_load_time",str(1000 * int(time.time()))),))
    if response.statusCode == 200:
      log("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = 200 OK")
    else:
      log("* CODER ACTION     = Reject Doc\n* HCC RESPONSE     = WARNING : Bad HCC Server Response\n[%s]" % response)
  elif CODE_OPPS_ACTION == 3: # Skip Opp
    finding_id = scorable.get("id")
    annotation = create_request(Test(testname, "Annotate Finding"))
    response = annotation.POST(URL+ "/api/annotate/" + str(finding_id) + "/", (
    NVPair("user_id", USERNAME),
    NVPair("timestamp",str(1000 * int(time.time()))),
    NVPair("result","skipped"),
    NVPair("date_of_service",scorable.get("date_of_service")),
    NVPair("payment_year",str(opportunity.get("payment_year"))),
    NVPair("org_id",str(scorable.get("org_id"))),
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
    NVPair("list_position",str(doc_no_current)),
    NVPair("list_length",str(doc_no_max)),
    NVPair("document_date",scorable.get("date_of_service")),
    NVPair("snippets",str(scorable.get("snippets"))),
    NVPair("predicted_code[code_system_name]", "The Grinder"),
    NVPair("predicted_code[code]", "The Grinder"),
    NVPair("predicted_code[display_name]", "The Grinder"),
    NVPair("predicted_code[code_system]", "The Grinder"),
    NVPair("predicted_code[code_system_version]", "The Grinder"),
    NVPair("page_load_time",str(1000 * int(time.time()))),))
    if response.statusCode == 200:
      log("* CODER ACTION = Skip Opp\n* HCC RESPONSE = 200 OK")
    else:
      log("* CODER ACTION = Skip Opp\n* HCC RESPONSE = WARNING : Bad HCC Server Response\n[%s]" % response)
  else:
    log("* CODER ACTION = Unknown\n")
  return 0

# MAIN FUNCTION CALLER ####################################################################################################

class TestRunner:
  def __call__(self):
    log("============================= START GRINDER TEST ============================")
    if CODE_OPPS    == 1:
      code()
    if VIEW_HISTORY == 1:
      history()
    if QA_REPORT    == 1:
      report()
    if LOGOUT       == 1:
      logout()
    log("============================== END GRINDER TEST =============================")
