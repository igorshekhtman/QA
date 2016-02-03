#=========================================================================================
#================================= hoisting_lookup.py ====================================
#=========================================================================================
#
# PROGRAM:         output_report.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    30-Oct-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 to determine Energy Routing Status:
#
# NOTES / COMMENTS:  python2.7 energyroutingstatus.py engineering
#
#
#
#
# COVERED TEST CASES:
#
#
# SETUP:
#		   * Assumes that Python2.7 is available 
#
# USAGE:
#
# MISC: 
#
#=========================================================================================
import requests
import time
import csv
import sys, os
import json
import pprint
import authentication
requests.packages.urllib3.disable_warnings()
#=========================================================================================
#================= Global Variable Initialization Section ================================
#=========================================================================================
	
ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
requestdenied = 400
unauthorized = 401
forbidden = 403
notfound = 404
intserveror = 500
servunavail = 503

#=========================================================================================
#===================== Helper Functions ==================================================
#=========================================================================================
def LogData(data):
	global REPORT
	print (data)
	REPORT = REPORT + str(data) + "<br>"

#=========================================================================================
def create_request(test, headers=None):
    request = HTTPRequest()
    if headers:
        request.headers = headers
        #print "headers = [%s]" % headers
    test.record(request)
    #print "request = [%s]" % request
    return request
#=========================================================================================    
def get_session(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    session = ''
    #print "cookies = [%s]" % cookies
    for cookie in cookies:
        if cookie.getName() == 'session':
            session = cookie.getValue()
            #print "cookie = [%s]" % cookie
    return session
#=========================================================================================    
def get_csrf_token(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    csrftoken = ''
    for cookie in cookies:
        if cookie.getName() == 'csrftoken':
            csrftoken = cookie.getValue()
    return csrftoken    
#=========================================================================================    
def print_all_cookies(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    print ("cookies = [%s]" % cookies)
    return cookies    
#=========================================================================================    
def get_new_hcc_user():
	global HCC_USERNAME_PREFIX, HCC_USERNAME_POSTFIX
	hccusernumber = str(int(time.time()))
	hccusername = HCC_USERNAME_PREFIX + hccusernumber + HCC_USERNAME_POSTFIX
	return hccusername
#=========================================================================================
def printGlobalParamaterSettings():
#with optional batch id: ?batch_id={batchId} if you want to limit bundling to a particular run of events

	print ("\n")
	#print ("* Version                = %s"%VERSION)
	print ("* Environment            = %s"%ENVIRONMENT)
	print ("* UA  URL                = %s"%UA_URL)
	print ("* ACL Admin User Name    = %s"%ACLUSERNAME)
	print ("* Code                   = %s"%CODE)
	print ("* Code System            = %s"%CODESYSTEM)
#=========================================================================================
def checkEnvironmentandReceivers():
	
	# Environment for hoisting lookup is passed as a paramater. Staging is a default value
	# Arg1 - environment (engineering)
	# Arg2 - code
	# Arg3 - codeSystem
	
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS, PROJECTID, BATCHID, BUNDL_URL
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX, MYSQLDOM, MYSQPW
	global PARMFILE, BNDL_URL, UA_URL, HCC_URL, ACLUSERNAME, ACLPASSWORD, TOKEN_URL
	global ENERGY_RTR_URL, ENERGY_SETNG, CODE, CODESYSTEM, HOISTING_URL, PROJECT
	
	CODE = ""
	CODESYSTEM = "2.16.840.1.113883.6.103"
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="engineering"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		#USERNAME="apxdemot0138"
		#PASSWORD="Hadoop.4522"
		ENVIRONMENT = "production"
		ACL_DOMAIN="acladmin.apixio.com"
		UA_URL="https://useraccount.apixio.com:7076"
		HCC_DOMAIN="hcc.apixio.com"
		HCC_URL="https://hcc.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="system_qa@apixio.com"
		ACLPASSWORD="9p2qa20.."
		BUNDL_URL="http://52.11.138.4:8087"
		BNDL_URL="https://bundler-2.apixio.com:8443/hcc/bundler/bundle"
		TOKEN_URL="https://tokenizer.apixio.com:7075/tokens"
		ENERGY_RTR_URL="https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode"
		HOISTING_URL="http://hcc-reports-2-stg2.apixio.com:8097"
	elif (ENVIRONMENT.upper() == "ENGINEERING"):
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "engineering"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://useraccount-stg.apixio.com:7076"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="ishekhtman@apixio.com"
		ACLPASSWORD="apixio.321"
		BUNDL_URL="http://52.11.138.4:8087"
		BNDL_URL="https://bundler-stg2.apixio.com:8443/hcc/bundler/bundle"
		TOKEN_URL="https://tokenizer-stg.apixio.com:7075/tokens"
		ENERGY_RTR_URL="https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode"
		HOISTING_URL="http://hcc-reports-2-stg2.apixio.com:8097"
	else:
		#USERNAME="grinderUSR1416591626@apixio.net"
		#PASSWORD="apixio.123"
		ENVIRONMENT = "staging"
		ACL_DOMAIN="acladmin-stg.apixio.com"
		UA_URL="https://useraccount-stg.apixio.com:7076"
		HCC_DOMAIN="hccstage2.apixio.com"
		HCC_URL="https://hccstage2.apixio.com"
		HCC_PASSWORD="apixio.123"
		PROTOCOL="https://"
		ACLUSERNAME="ishekhtman@apixio.com"
		ACLPASSWORD="apixio.123"
		BUNDL_URL="http://52.11.138.4:8087"
		BNDL_URL="https://bundler-stg2.apixio.com:8443/hcc/bundler/bundle"
		TOKEN_URL="https://tokenizer-stg.apixio.com:7075/tokens"
		ENERGY_RTR_URL="https://hcc-opprouter-stg2.apixio.com:8443/ctrl/router/energy/energyMode"
		HOISTING_URL="http://hcc-reports-2-stg2.apixio.com:8097"
			
	
	if (len(sys.argv) > 2):
		PROJECT=str(sys.argv[2])
	else:
		print "Missing Energy Setting paramater, aborting now ..."
		print "Proper use instructions:"
		print "python2.7 output_report.py <environment> <project (required)>"
		quit()


				
	# overwite any previous ENVIRONMENT settings
	#ENVIRONMENT = "Production"
	#print ("Version %s\n") % VERSION
	print ("ENVIRONMENT = %s\n") % ENVIRONMENT
	print ("Completed assignment enviroment settings ...\n")
#=======================================================================================================================
def getEnvHosts(env):
  if env.lower()[0] == 's':
    tokenhost = 'https://tokenizer-stg.apixio.com:7075/tokens'
    hcchost = 'https://hcceng.apixio.com/'
    ssohost = 'https://accounts-stg.apixio.com'
    uahost = 'https://useraccount-stg.apixio.com'
    uaport = ':7076'
    caller = 'hcc_stg'
    cmphost="http://cmp-stg2.apixio.com:8087"
  elif env.lower()[0] == 'd':
    tokenhost = 'https://tokenizer-dev.apixio.com:7075/tokens'
    hcchost = 'https://hccdev.apixio.com/'
    ssohost = 'https://accounts-dev.apixio.com'
    uahost = 'https://useraccount-dev.apixio.com'
    uaport = ':7076'
    caller = 'hcc_dev'
    cmphost="https://cmp-dev.apixio.com:7087"
  elif env.lower()[0] == 'e':
    tokenhost = 'https://tokenizer-eng.apixio.com:7075/tokens'
    hcchost = 'https://hcceng.apixio.com/'
    ssohost = 'https://accounts-eng.apixio.com'
    uahost = 'https://useraccount-eng.apixio.com'
    uaport = ':7076'
    caller = 'hcc_eng'
    cmphost="https://cmp-stg2.apixio.com:7087"
  hlist= {'cmphost':cmphost, 'tokenhost':tokenhost, 'hcchost':hcchost, 'ssohost':ssohost, 'uahost':uahost, 'uaport':uaport, 'caller':caller}
  return (hlist)
	
#=========================================================================================

def reportLookup(options, headers):
  #CP_d549bb0f-b4a9-4031-9e1b-b403a73a4ee5
  print ("\n----------------------------------------------------------------------------")
  print (">>> CHECKING OUTPUT REPORT FOR %s ENVIRONMENT <<<" % ENVIRONMENT)
  print (">>>                            %s PROJECT <<<" % PROJECT)
  print ("----------------------------------------------------------------------------")
  response = ""
  #URL = HOISTING_URL + "/hoists?codeSystem=" + CODESYSTEM + "&code=" + CODE
  URL = "https://hcc-reports-2-stg.apixio.com:7097/outputreport/"+PROJECT

	
  print ("\n")
  print ("* URL                    = %s" % URL)
  print ("* Project                = %s" % PROJECT)
  print ("* Environment            = %s" % ENVIRONMENT)
  print ("* Admin User Name        = %s" % ACLUSERNAME)
  #print ("* Internal Token         = %s" % TOKEN)
  #print ("* Apixio Token           = %s" % APIXIO_TOKEN)
	
  #DATA = json.load(open(PARMFILE))
  data = {}
  #FILES = {'file': (PARMFILE, open(PARMFILE, 'rb'), 'application/json', {'Expires': '0'})}


  #HEADERS = {"Content-Type": "application/json", "Authorization": APIXIO_TOKEN}
  #print URL
  #print DATA
  response = requests.get(URL, data=json.dumps(data), headers=headers)
  print ("* Status Code            = %s" % response.status_code)
  print ("\n================================ RESPONSE ==================================")

  print json.dumps(response.json())

  f = open('output_report.json', 'w')
  f.write(json.dumps(response.json()))
  f.close()
  print ("============================================================================")
  if response.status_code != ok:
    print "Failure occured, exiting now ..."
    quit()
  else:
    print "\nSuccessfully obtained output report ..."

  return()
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
def Main():
  global options
  reload(authentication)
  os.system('clear')

  authentication.defineGlobals()
  hlist = getEnvHosts('d')
  headers = authentication.authenticateSetHeaders('ishekhtman@apixio.com', 'apixio.321', hlist)

  reportLookup(options, headers)

  print authentication.LS
  return ()

if __name__ == "__main__":
  Main()
#=======================================================================================================================
