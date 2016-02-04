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
def reportLookup(headers, options):
  print authentication.LS
  print ">>> CHECKING OUTPUT REPORT FOR %s <<<" % options['project']
  print authentication.LS
  url = "https://hcc-reports-2-stg.apixio.com:7097/outputreport/"+options['project']
  print "* Host Url".ljust(25)+ " = "+ url
  print "* Project".ljust(25)+ " = "+ options['project']
  print "* Token".ljust(25)+ " = "+headers['Authorization']
  print "* Environment".ljust(25)+" = "+options['env']
  data = {}
  response = requests.get(url, data=json.dumps(data), headers=headers)
  print "* Status Code".ljust(25)+ " = "+str(response.status_code)
  print authentication.LS
  if response.status_code != ok:
    print "Failure occured, exiting now ... "+str(response.status_code)
    quit()
  else:
    print "* Retrieved report".ljust(25)+ " = "+str(response.status_code)
    report = response.json()
  print authentication.LS
  return(report)
#=======================================================================================================================
def saveReport(report, options):
  print authentication.LS
  print "* File Name".ljust(25)+" = Saving "+"output_report_"+options['project']+".json"
  f = open('output_report_'+options['project']+'.json', 'w')
  f.write(json.dumps(report))
  f.close()
  print authentication.LS
  return()
#=======================================================================================================================
def printToConsole(report, options):
  print authentication.LS
  pp = pprint.PrettyPrinter(indent=4)
  for item in report:
    pp.pprint(item)
  print authentication.LS
  return()
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
def Main():
  global options
  reload(authentication)
  os.system('clear')
  options={}
  options['env'] = sys.argv[1] if len(sys.argv) > 1 else "Staging"
  options['project'] = sys.argv[2] if len(sys.argv) > 2 else "CP_492a247f-8f51-4665-b4fa-bbf2cc2bc963"

  authentication.defineGlobals()
  hlist = getEnvHosts(options['env'])
  headers = authentication.authenticateSetHeaders('ishekhtman@apixio.com', 'apixio.321', hlist)

  report = reportLookup(headers, options)
  printToConsole(report, options)
  saveReport(report, options)

  print authentication.LS
  return ()

if __name__ == "__main__":
  Main()
#=======================================================================================================================
