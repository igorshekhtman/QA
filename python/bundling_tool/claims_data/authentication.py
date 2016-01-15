__author__ = 'ishekhtman'
import requests
import json
requests.packages.urllib3.disable_warnings()

#=======================================================================================================================
def defineGlobals():
    global LS, LSS, SL, ACTIONS
    LS  = "="*80
    LSS = "-"*80
    SL  = "*"*80
    return()
#=======================================================================================================================
def obtainExternalToken(un, pw, hlist):

  #url = 'https://useraccount-dev.apixio.com:7076/auths'
  url = hlist['uahost']+hlist['uaport']+'/auths'
  #print url
  #quit()
  data =    {'email': un, 'password': pw}
  headers = {}

  print LS
  print "* User Accounts Url".ljust(25)+" = "+ url
  print "* Username".ljust(25)+" = "+ un
  print "* Password".ljust(25)+" = "+ pw


  response = requests.post(url, data=data, headers=headers)

  statuscode = response.status_code
  if statuscode != 200:
    print "* Ext. token status code".ljust(25)+" = "+ str(statuscode)
    quit()
  external_token = response.json().get("token")
  print "* External token".ljust(25)+" = "+ response.json().get("token")
  print "* Ext. token status code".ljust(25)+" = "+ str(statuscode)
  return (external_token)
#=========================================================================================
def obtainInternalToken(un, pw, hlist):

  external_token = obtainExternalToken(un, pw, hlist)
  url = hlist['tokenhost']
  data =    {}
  headers = {'Authorization': 'Apixio ' + external_token}

  response = requests.post(url, data=json.dumps(data), headers=headers)
  if (response.status_code != 201):
    print ("* Failed to create internal token: %s. Exiting now ..." % response.status_code)
    quit()
  else:
    userjson = response.json()
    if userjson is not None:
      token = userjson.get("token")
      apixio_token = 'Apixio '+str(token)
      print "* Tokenizer Url".ljust(25) + " = " + url
      print "* Internal Token".ljust(25) + " = " + token
      print "* Apixio Token".ljust(25) + " = " + apixio_token
      print "* Int. Token status code".ljust(25) + " = " + str(response.status_code)
      print LS

  return(apixio_token)
#=======================================================================================================================
def authenticateSetHeaders(un, pw, hlist):
  defineGlobals()
  apixio_token = obtainInternalToken(un, pw, hlist)
  headers = {'Content-Type':'application/json', 'Authorization': apixio_token}
  return(headers)
#=======================================================================================================================
