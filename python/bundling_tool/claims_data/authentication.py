__author__ = 'ishekhtman'
import requests
requests.packages.urllib3.disable_warnings()

#=======================================================================================================================
def defineGlobals():
    global LS, LSS, SL, ACTIONS
    LS  = "="*80
    LSS = "-"*80
    SL  = "*"*80
    return()
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

  defineGlobals()
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
  print "* Report Recepients".ljust(25)+" = "+str(options['report_recepients'])
  if response.status_code != 200:
    quit()
  print LS
  return(cookies)
#=======================================================================================================================
