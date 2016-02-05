__author__ = 'ishekhtman'
########################################################################################################################
#
# PROGRAM: claims_data_subtraction.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    Jan. 12, 2015 - Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: Jan. 12, 2015
# SPECIFICS: None
#
# PURPOSE:
#          This program should be executed via Python 2.6 and is meant for testing Bundler Claims Data Subtraction mechanism:
#          * 1st Pass Project creation
#          * 2nd Pass Project creation
#          * Number of Opportunities generated by the Bundler verification
#          * 2nd Pass Project creation
#          * Number of Opportunities generation by the Bundler verification
#
# SETUP:
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.6 environment is available
#          * From QA server (qa.apixio.com) /mnt/automation/python/stress_test folder enter "python2.7 claims_data_subtraction.py"
#
# USAGE:   * Test Results will be printed on Console screen as well as mailed via QA report
#
########################################################################################################################
import os,sys,time
import collections
import authentication
import elasticsearch
import requests
import json
import time
reload(authentication)

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
#=======================================================================================================================
def createProject(dsID, projName, headers, hlist, passType):
  data={"name":             projName,\
        "description":      projName+" - Claims Data Subtraction Test",\
        "type":             "HCC",\
        "organizationID":   "UO_6ececf9e-2b54-4acf-893c-4c947a14d238",\
        "patientDataSetID": "O_00000000-0000-0000-0000-000000000506",\
        "dosStart":         "2014-01-01T00:00:00Z",\
        "dosEnd":           "2014-12-31T00:00:00Z",\
        "paymentYear":      "2015",\
        "sweep":            "finalReconciliation",\
        "passType":         passType,\
        "status":           True,\
        "state":            "new",\
        "rawRaf":           0.33,\
        "raf":              0,\
        "budget":           100000000,\
        "deadline":         "2017-12-31T08:00:00Z",\
        "datasource":       "Compound Documents",\
        "patientList":      "3b5ebf03-a32d-4bc4-8462-83c55890aefa",\
        "docFilterList":    ""}
  url = hlist['uahost']+hlist['uaport']+'/projects'
  response = requests.post(url, data=json.dumps(data), headers=headers)
  if response.status_code == 200:
    print "* Create new project".ljust(25)+" = "+str(response.status_code)
    print "* Project name".ljust(25)+" = " +str(projName)
    print "* Project ID".ljust(25)+" = " + str(response.json()['id'])
    print "* DataSet ID".ljust(25)+" = " +str(dsID)
    print "* Pass Type".ljust(25)+" = " + str(passType)
    print authentication.LSS
  else:
    print "* Failed create project".ljust(25)+ " = " + str(response.status_code)
    quit()
  return (response.json()['id'])
#=======================================================================================================================
def filterProjects(dsID, headers, hlist):
  data={}
  url = hlist['uahost']+hlist['uaport']+'/projects'
  response = requests.get(url, data=json.dumps(data), headers=headers)
  if response.status_code != 200:
    print response.status_code
    return ()
  projects = response.json()
  filtProjects = []
  for project in projects:
    if project['pdsExternalID'] == dsID:
      filtProjects.append(project)
  return(filtProjects)
#=======================================================================================================================
def deleteProject(projID, headers, hlist):
  data={}
  url = hlist['uahost']+hlist['uaport']+'/projects/'+projID
  response = requests.delete(url, data=json.dumps(data), headers=headers)
  print "* Delete project".ljust(25)+ " = " + str(response.status_code)
  if response.status_code != 200:
    print "* Failed to delete".ljust(25)+ " = " + str(response.status_code)
    return ()
  return()
#=======================================================================================================================
def bundleProject(projID, headers, hlist):
  data={}
  url = hlist['cmphost']+"/cmp/v1/project/"+projID+"/bundle"
  response = requests.post(url, data=json.dumps(data), headers=headers)
  print "* Bundle project".ljust(25)+ " = " + str(response.status_code)
  if response.status_code != 200:
    print "* Failed to bundle".ljust(25)+ " = " + str(response.status_code)
    deleteProject(projID, headers, hlist)
    return (1)
  return(0)
#=======================================================================================================================
def listProjects(projList):
  print "name:".ljust(30)+"id:".ljust(50)+"state:".ljust(30)
  for proj in projList:
    print proj['name'].ljust(30) + proj['id'].ljust(50) + proj['state'].ljust(30)
  return()
#=======================================================================================================================
def queryElasticSearchOpps(dsID, projID):
  es = elasticsearch.Elasticsearch('http://elasticsearch-stg.apixio.com:9200')
  body = {"query": {"bool": {"must": [{"terms": {"project": [projID]}}]}},"from": 0,"size": 1}
  resp = es.search(index='org-'+dsID+'-1', doc_type='opportunity', body=body)['hits']['total']
  return (resp)
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
def Main():
  global options
  reload(authentication)
  os.system('clear')

  authentication.defineGlobals()
  dsID = '506'
  hlist = getEnvHosts('d')
  headers = authentication.authenticateSetHeaders('ishekhtman@apixio.com', 'apixio.321', hlist)
  passTypes = ['firstPass', 'secondPass']
  #deleteProject("PRHCC_48ac6a38-31a2-4c95-9244-67f3be17c93f", headers, hlist)
  #quit()

  for passType in passTypes:
    projName = 'HealthNet_'+passType
    projID = createProject(dsID, projName, headers, hlist, passType)
    bundleProject(projID, headers, hlist)
    time.sleep(15)
    tot_opps = queryElasticSearchOpps(dsID, projID)
    print "* Opps generated".ljust(25)+" = " + str(tot_opps)
    print authentication.SL
    if passType == 'firstPass' and tot_opps != 211:
      print "* TEST RESULTS SUMMARY".ljust(25)+" = FAILED QA"
      state = 1
    elif passType == 'secondPass' and tot_opps != 195:
      print "* TEST RESULTS SUMMARY".ljust(25)+" = FAILED QA"
      state = 1
    else:
      print "* TEST RESULTS SUMMARY".ljust(25)+" = PASSED QA"
      state = 0
    print authentication.SL
    deleteProject(projID, headers, hlist)
    print authentication.LSS

  print authentication.LS
  return (state)

if __name__ == "__main__":
  Main()
#=======================================================================================================================