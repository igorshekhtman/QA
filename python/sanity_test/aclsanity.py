#=========================================================================================
#================== ALC_COMPLETE_TEST.PY =================================================
#=========================================================================================
#
# PROGRAM:         acl_complete_test.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    15-Oct-2014
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Grinder for testing ACL functionality:
#			* Log into ACL
#			* Obtain and save token
#			* Create new unique Coding Org(s) and save org_uuid(s)
#				- Multiple Coding Orgs allowed (NUMBER_OF_ORGS_TO_CREATE) 
#			* Create new unique HCC user(s) and save user_uuid(s) 
#				- Multiple HCC Users allowed (NUMBER_OF_USERS_TO_CREATE)
#			* Create new unique ALC Group and save GRP_UUID
#				- Multiple ACL Groups are allowed (NUMBER_OF_GRPS_TO_CREATE)
#			* Activate newly created HCC user
#			* Deactivate a specific HCC user
#			* Assign newly created user pre-defined password (HCC_PASSWORD)
#			* Assign newly created HCC user coding org
#				- Either pre-defined coding org or newly created coding org
#			* Assign specific or newly created coding org to a user
#			* Add list of members to a newly created Group
#			* Remove specific member(s) from a Group
#			* Add specific rules to a Group
#			* Delete specific rules from a Group
#			* Log into HCC with newly created user/org
#			* Store each of the newly created users in an array (HCCUSERSLIST[])
#			* Store each of the newly created coding orgs in an array (HCCORGLIST[])
#			* Report total number of retries, failures and successes
#
# SETUP:
#          * Assumes a ACL and HCC environments are available
#          * Assumes a Grinder environment is available
#          * For further details, see http://grinder.sourceforge.net
#
# USAGE:
#          * Ensure Grinder is configured to execute acl_complete_test.py
#          * Set the global variables, see below (Global Test Environment Selection)
#          * Run acl_complete_test.py
#          * Results will be printed on Grinder Agent and in Grinder Console log files
#
#=========================================================================================
# Global Paramaters descriptions and possible values:
# These are defined in CSV_CONFIG_FILE_NAME = "ACLConfig.csv", 
# Which is located in CSV_CONFIG_FILE_PATH folder
#
# ENVIRONMENT - "Staging" or "Production"
# NUMBER_OF_USERS_TO_CREATE - integer (0 through x) - total number of HCC users to create
# NUMBER_OF_ORGS_TO_CREATE - integer (0 through x) - total number of coding orgs to create
# CODINGORGANIZATION - any organization from CDGORGMAP list below
# HCCPASSWORD - default password to be assigned to every HCC user
#
# CSV_FILE_PATH - path for output csv file (content: environment, username, password)
# CSV_FILE_PATH - name for output csv file 
#
# MAX_NUM_RETRIES - global limit for number of retries (statuscode = 500)
#=========================================================================================
# Revision 1: 1.0.1
# Author: Igor Shekhtman ishekhtman@apixio.com 
# Specifics: Introduction of Program Flow Control
#=========================================================================================
# Revision 2: 1.0.2
# Author: Igor Shekhtman ishekhtman@apixio.com
# Specifics: Introduction of external ACLConfig.csv configuration file
#=========================================================================================
# Revision 3:
# Author:
# Specifics:
#=========================================================================================
import requests
import time
import datetime
import csv
import operator
import random
import re
import sys, os
import json
#=========================================================================================
#=== CODING ORG MAP: ORG_NAME - ORG_UUID =================================================
#=========================================================================================
CDGORGMAP = { \
	"AE & Associates":"UO_7ffb36bb-26c1-439e-b259-9a6db503aa11", \
	"Scripps":"UO_609aa5c3-4bff-4aec-a629-1da4f0be144e", \
	"Coding Org 1":"UO_5c83fcf7-d216-42ca-859d-9908e74049e5", \
	"Coding Org 2":"UO_c2fee803-b169-4bfb-9e46-137295379b46", \
	"Coding Org 3":"UO_fb540446-a07d-4e2f-b2a2-6caf1179d455", \
	"HealthCare Partners":"UO_62eb7683-e42b-4cf4-a7cf-e91dcaf68bbb", \
	"Apixio Coders":"UO_059c7bbd-7ecc-4172-8d81-6ea2dadb6e76", \
	"CCHCA":"UO_6cbe9df5-cdfb-414f-b1f0-f44c7b519bcb", \
	"Load Test Coders":"UO_149af107-1ef7-49a0-923e-be4b2de174b3", \
	"org0420":"UO_7c6cf5ea-b35c-4ecf-866f-915f70269d34", \
	"test Coding org":"UO_ee2a6959-bc38-40c3-813b-d3e7a9cc681b", \
	"Test Org2":"UO_8f2082b8-5060-4e90-bd6e-3db8f97659a6", \
	"Test Org 1000":"UO_45dcce68-47a8-4e0f-9cf4-467476021337", \
	"Test Org 1000":"UO_1296f532-2605-4e63-9d09-e5e992bd07ea", \
	"Test Org 1000":"UO_6add7125-0eb0-472c-9840-47e24867f5ea", \
	"test org1":"UO_9010f837-0ac7-41fa-abbf-16c82b1c9032", \
	}

PERIMISSION_TYPES = [ \
	"canAnnotate", \
	"viewDocuments", \
	"viewReportsAnnotatedFor", \
	"viewReportsAnnotatedBy", \
	"viewAllAnnotations", \
	"canRelease" \
	]
	
#=========================================================================================
#===================== Initialization of the ACLConfig file ==============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/hcc/"
CSV_CONFIG_FILE_NAME = "aclsanity.csv"
VERSION = "1.0.3"
#=========================================================================================
#================== Global variable declaration, initialization ==========================
#=========================================================================================
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
	result={ }
	csvfile = open(filename, 'rb')
	reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
	for row in reader:
		if (str(row[0])[0:1] <> '#') and (str(row[0])[0:1] <> ' '):	
			result[row[0]] = row[1]
	globals().update(result)
	return result    	
#=========================================================================================
#================= Global Variable Initialization Section ================================
#=========================================================================================
	
ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
forbidden = 403
intserveror = 500
servunavail = 503

HCCUSERSLIST = [0]
HCCORGLIST = [0]
HCCGRPLIST = [0]
HCCGRPEMISSIONS = [0]
FAILED = 0
SUCCEEDED = 0
RETRIED = 0
#=========================================================================================
#===================== Helper Functions ==================================================
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
    print "cookies = [%s]" % cookies
    return cookies    
#=========================================================================================    
#def log(text):
#    grinder.logger.info(text)
#    print(text)
#=========================================================================================    
def get_new_hcc_user():
	global HCC_USERNAME_PREFIX, HCC_USERNAME_POSTFIX
	hccusernumber = str(int(time.time()))
	hccusername = HCC_USERNAME_PREFIX + hccusernumber + HCC_USERNAME_POSTFIX
	return hccusername
#=========================================================================================
def PrintGlobalParamaterSettings():
	print ("\nVersion: \t\t\t"+VERSION)
	print ("\nEnvironment: \t\t\t"+ENVIRONMENT)
	print ("ACL URL: \t\t\t"+ACL_URL)
	print ("HCC URL: \t\t\t"+HCC_URL)
	print ("ACL Admin User Name: \t\t"+ACLUSERNAME)
	print ("Coding Organization: \t\t"+CODING_ORGANIZATION)
	print ("HCC Users to Create: \t\t"+str(NUMBER_OF_USERS_TO_CREATE))
	print ("HCC Orgs to Create: \t\t"+str(NUMBER_OF_ORGS_TO_CREATE))
	print ("HCC Groups to Create: \t\t"+str(NUMBER_OF_GRPS_TO_CREATE))
#=========================================================================================
def IncrementTestResultsTotals(code):
	global FAILED, SUCCEEDED, RETRIED
	if (code == ok) or (code == nocontent):
		SUCCEEDED = SUCCEEDED+1
	elif code == intserveror:
		RETRIED = RETRIED+1
	else:	
		FAILED = FAILED+1 
#=========================================================================================							
def WriteToCsvFile():
	file_obj = CSV_FILE_PATH + CSV_FILE_NAME
	f = open(file_obj, 'w')
	file_writer=csv.writer(f, delimiter=',')
	# write headers row
	file_writer.writerow (["Status", "Environment", "UserName", "Password", \
		"CodingOrg", "Group", "canAnnotate", "viewDocuments", \
		"viewReportsAnnotatedFor", "viewReportsAnnotatedBy", \
		"viewAllAnnotations"])
	for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
		file_writer.writerow (["1", HCC_DOMAIN, str(HCCUSERSLIST[i]), \
			HCC_PASSWORD, HCCORGLIST[0], HCCGRPLIST[0], HCCGRPEMISSIONS[0], \
			HCCGRPEMISSIONS[1], HCCGRPEMISSIONS[2], \
			HCCGRPEMISSIONS[3], HCCGRPEMISSIONS[4]])
	#f.write('\n')
	f.close()	
#=========================================================================================	
def ListUserGroupOrg():
	print ("\n")
	if int(NUMBER_OF_USERS_TO_CREATE) > 0:
		print ("=================================")
		print ("List of newly created HCC Users:")
		print ("=================================")
		for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
			print (HCCUSERSLIST[i])
	print ("=================================")
	print ("List of newly created HCC Orgs:")
	print ("=================================")
	for i in range (0, int(NUMBER_OF_ORGS_TO_CREATE)):
		print (HCCORGLIST[i])
	print ("=================================")
	print ("List of newly created HCC Groups:")
	print ("=================================")
	for i in range (0, int(NUMBER_OF_GRPS_TO_CREATE)):
		print (HCCGRPLIST[i])	
	print ("=================================")
	print ("Test execution results summary:")
	print ("=================================")	
	print ("RETRIED: %s\t" % RETRIED)			
	print ("FAILED: %s\t" % FAILED)
	print ("SUCCEEDED: %s\t" % SUCCEEDED)
	print ("TOTAL: %s\t" % (RETRIED+FAILED+SUCCEEDED)) 							
	print ("=================================")				
#=========================================================================================
#===================== Main Functions ====================================================
#=========================================================================================	
def logInToACL():
	global TOKEN, ACL_URL, SESSID, DATA, HEADERS
	print ("\nACL Obtain Authorization...")
	print ("ACL_URL: " + ACL_URL)
	statuscode = 500
	# repeat until successful login is reached
	while statuscode != 200:
  		url = ACL_URL+'/auth'
  		referer = ACL_URL  				
  		DATA =    {'Referer': referer, 'email': ACLUSERNAME, 'password': ACLPASSWORD} 
  		HEADERS = {'Connection': 'keep-alive', 'Content-Length': '48', 'Referer': referer}
  		response = requests.post(url, data=DATA, headers=HEADERS) 
  		SESSID = TOKEN = response.cookies["session"]
  		#TOKEN = response.cookies["csrftoken"]
  		print "* Log in user        = "+str(response.status_code)
		#TOKEN = get_session(thread_context)
		print ("ACL Username: %s" % ACLUSERNAME)
		print ("ACL Password: %s" % ACLPASSWORD)
		print ("ACL Session: %s" % SESSID)
		print ("ACL Token: %s" % TOKEN)
		statuscode = response.status_code
		print ("Status Code = [%s]\t\t" % statuscode)
		IncrementTestResultsTotals(statuscode)	
#=========================================================================================
def ACLCreateNewUser(retries):
	global USR_UUID, HCCUSERNAME, TOKEN, ACL_URL
	print ("\nACL Create New User...")
	HCCUSERNAME = get_new_hcc_user()	
	url = ACL_URL+'/access/user'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'email': HCCUSERNAME, 'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	userjson = response.json()
	if userjson is not None:
		USR_UUID = userjson.get("id")
		#print ("User UUID: " + USR_UUID)
	print ("HCC Username: %s" % HCCUSERNAME)
	print ("HCC User UUID: %s" % USR_UUID)
	print ("ACL Token: %s" % TOKEN)	
	statuscode = response.status_code
	print ("Status Code = [%s]\t\t" % statuscode)
	IncrementTestResultsTotals(statuscode)
	if (statuscode == 500) and (retries <= int(MAX_NUM_RETRIES)):
		print (">>> Failure occured: username already exists <<<")
		retries = retries + 1
		ACLCreateNewUser(retries)				
#=========================================================================================
def ACLActivateNewUser():
	global USR_UUID, TOKEN, ACL_URL
	print ("\nACL Activate New User...")	
	#print ("User UUID: " + USR_UUID)
	url = ACL_URL+'/access/user/'+USR_UUID
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.put(url, data=DATA, headers=HEADERS) 
	print ("HCC User UUID: %s" % USR_UUID)
	print ("ACL TOKEN: %s" % TOKEN) 	
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLDectivateUser(uuid):
	global USR_UUID, TOKEN, ACL_URL
	print ("\nACL Deactivate User...")	
	#print ("User UUID: " + USR_UUID)
	url = ACL_URL+'/access/user/'+uuid
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.delete(url, data=DATA, headers=HEADERS)	
	print ("HCC User UUID: %s" % uuid)
	print ("ACL TOKEN: %s" % TOKEN) 
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)					
#=========================================================================================
def ACLSetPassword():
	global USR_UUID, HCC_PASSWORD, TOKEN, ACL_URL
	print ("\nACL Assign New User Password...")	
	url = ACL_URL+'/access/user/'+USR_UUID+'/password'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'password': HCC_PASSWORD}
	HEADERS = { 'Origin': ACL_URL, 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.put(url, data=DATA, headers=HEADERS) 
	print ("HCC Password: %s" % HCC_PASSWORD)
	print ("HCC User UUID: %s" % USR_UUID)
	print ("ACL TOKEN: %s" % TOKEN) 				
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLCreateNewCodingOrg():
	global ACL_URL, TOKEN, ORG_UUID, ACL_CODNG_ORG_PREFIX, CODING_ORGANIZATION
	print ("\nACL Create New Coding Org...")
	conumber = str(int(time.time()))
	coname = ACL_CODNG_ORG_PREFIX + conumber
	CODING_ORGANIZATION = coname									
	#print ("Coding Org Name: "+coname)		
	url = ACL_URL+'/access/userOrganization'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'name': coname, 'key': conumber, 'description': coname}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	userjson = response.json()
	if userjson is not None:
		ORG_UUID = userjson.get("id")				
	print ("Coding Org Name: " + coname)
	print ("Coding Org UUID: " + ORG_UUID)
	print ("ACL TOKEN: %s" % TOKEN)			
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLCreateNewGroup():
	global ACL_URL, TOKEN, ACL_GROUP_PREFIX, GRP_UUID, ACLGROUPNAME
	print ("\nACL Create New Group...")
	gnumber = str(int(time.time()))
	gname = ACL_GROUP_PREFIX + gnumber
	ACLGROUPNAME = gname									
	#print ("Group Name: "+gname)
	url = ACL_URL+'/access/group'
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'name': gname}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	grpjson = response.json()
	if grpjson is not None:
		GRP_UUID = grpjson.get("id").get("id")
	print ("Group Name: " + gname)	
	print ("Group UUID: " + GRP_UUID)
	print ("ACL TOKEN: %s" % TOKEN)						
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLDeleteExistingGroup(group_uuid):									
	global ACL_URL, TOKEN
	print ("\nACL Delete Existing Group...")
	url = ACL_URL+'/access/group/'+group_uuid
  	referer = ACL_URL+'/admin/'  				
	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer} 
  	response = requests.delete(url, data=DATA, headers=HEADERS) 			
	print ("Group UUID: " + group_uuid)
	print ("ACL TOKEN: %s" % TOKEN)				
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLAddGroupPermission(per_type, group_uuid, org_uuid):
	global HCCGRPEMISSIONS
	print ("\nACL Add "+per_type+" Group Permission...")
	url = ACL_URL+'/access/permission/'+group_uuid+'/'+org_uuid+'/'+per_type
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	#grpjson = response.json()
	print ("Group UUID: %s" % group_uuid)
	print ("Org UUID: %s" % org_uuid)
	print ("Permission Type: %s" % per_type)		
	print ("ACL TOKEN: %s" % TOKEN)					
	statuscode = response.status_code	
	print ("Status Code = [%s]\t\t" % statuscode)
	IncrementTestResultsTotals(statuscode)
	if (statuscode == ok) or (statuscode == nocontent):
		if per_type == "canAnnotate":
			HCCGRPEMISSIONS[0] = "1"
		elif per_type == "viewDocuments":
			HCCGRPEMISSIONS.append(1)
			HCCGRPEMISSIONS[1] = "1"
		elif per_type == "viewReportsAnnotatedFor":
			HCCGRPEMISSIONS.append(2)
			HCCGRPEMISSIONS[2] = "1"
		elif per_type == "viewReportsAnnotatedBy":
			HCCGRPEMISSIONS.append(3)
			HCCGRPEMISSIONS[3] = "1"
		elif per_type == "viewAllAnnotations":
			HCCGRPEMISSIONS.append(4)
			HCCGRPEMISSIONS[4] = "1"
		elif per_type == "canRelease":
			HCCGRPEMISSIONS.append(5)
			HCCGRPEMISSIONS[5] = "1"	
#=========================================================================================
def ACLDelGroupPermission(per_type, group_uuid, org_uuid):
	print ("\nACL Del "+per_type+" Group Permission...")
	#login = create_request(Test(1950, 'ACL del '+per_type+' permission'),[ \
	#	NVPair('Referer', ACL_URL+'/admin/'),])
	#result = login.DELETE(ACL_URL+"/access/permission/"+ \
	#	group_uuid+"/"+org_uuid+"/"+per_type, (NVPair('session', TOKEN),))			
	url = ACL_URL+'/access/permission/'+group_uuid+'/'+org_uuid+'/'+per_type
  	referer = ACL_URL+'/admin/'  				
	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer} 
  	response = requests.delete(url, data=DATA, headers=HEADERS) 		
	print ("Group UUID: %s" % group_uuid)
	print ("Org UUID: %s" % org_uuid)
	print ("Permission Type: %s" % per_type)		
	print ("ACL TOKEN: %s" % TOKEN)				
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)			
#=========================================================================================
def ACLAddMemberToGroup():
	global USR_UUID, GRP_UUID, ACL_URL
	print ("\nACL Add Member to Group...")	
	print ("User UUID: " + USR_UUID)
	print ("Group UUID: " + GRP_UUID)
	url = ACL_URL+'/access/groupMembership/'+GRP_UUID+'/'+USR_UUID
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 
	print ("ACL Group UUID: %s" % GRP_UUID)
	print ("HCC User UUID: %s" % USR_UUID)		
	print ("ACL TOKEN: %s" % TOKEN)						
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLDelMemberFromGroup(group_uuid, usr_uuid):
	print ("\nACL Del Member from Group...")	
	url = ACL_URL+'/access/groupMembership/'+group_uuid+'/'+usr_uuid
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.delete(url, data=DATA, headers=HEADERS) 	
	print ("HCC User UUID: " + usr_uuid)
	print ("ACL Group UUID: " + group_uuid)				
	print ("ACL TOKEN: %s" % TOKEN)			
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def ACLAssignCodingOrg():
	global USR_UUID, ORG_UUID, ACL_URL
	print ("\nACL Assign Coding Organization...")	
	#print ("User UUID: " + USR_UUID)
	#print ("Org UUID: " + ORG_UUID)
	url = ACL_URL+'/access/userOrganization/'+ORG_UUID+'/'+USR_UUID
  	referer = ACL_URL+'/admin/'  				
  	DATA = {'session': TOKEN}
	HEADERS = { 'Connection': 'keep-alive', 'Cookie': 'session='+TOKEN, 'Referer': referer}
  	response = requests.post(url, data=DATA, headers=HEADERS) 	
	print ("HCC User UUID: %s" % USR_UUID)
	print ("ACL Org UUID: %s" % ORG_UUID)				
	print ("ACL TOKEN: %s" % TOKEN)								
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)
#=========================================================================================
def logInToHCC(): 
	global TOKEN, SESSID, DATA, HEADERS
	global HCCUSERNAME, HCC_PASSWORD, HCC_URL
	global HCC_TOKEN, HCC_SESSID
	HCC_HOST_DOMAIN = 'hccstage.apixio.com'
	HCC_HOST_URL = 'https://%s' % HCC_HOST_DOMAIN
	response = requests.get(HCC_URL+'/')
	print "* Connect to host    = "+str(response.status_code)
	url = referer = HCC_URL+'/account/login/?next=/'
	response = requests.get(url)
	print "* Login page         = "+str(response.status_code)
	HCC_TOKEN = response.cookies["csrftoken"]
	HCC_SESSID = response.cookies["sessionid"]
	DATA =    {'csrfmiddlewaretoken': HCC_TOKEN, 'username': HCCUSERNAME, 'password': HCC_PASSWORD } 
	HEADERS = {'Connection': 'keep-alive', 'Content-Length': '115', \
				'Cookie': 'csrftoken='+HCC_TOKEN+'; sessionid='+HCC_SESSID+' ', \
				'Referer': referer}			
	response = requests.post(url, data=DATA, headers=HEADERS) 
	print "* Log in user        = "+str(response.status_code)
	print ("HCC Username: %s" % HCCUSERNAME)
	print ("HCC Password: %s" % HCC_PASSWORD)
	print ("HCC Token: %s" % HCC_TOKEN)
	print ("HCC Session ID: %s" % HCC_SESSID)
	print ("Status Code = [%s]\t\t" % response.status_code)
	IncrementTestResultsTotals(response.status_code)	
#=========================================================================================
#============= ONE GROUP ONE CODING ORG MULTIPLE USERS ===================================
#=========================================================================================
def TestFlowControlOne():
	global HCCUSERSLIST, PERIMISSION_TYPES
	PrintGlobalParamaterSettings()
	logInToACL()
	ACLCreateNewCodingOrg()
	HCCORGLIST[0] = CODING_ORGANIZATION
	ACLCreateNewGroup()
	ACLDeleteExistingGroup(GRP_UUID)
	ACLCreateNewGroup()
	HCCGRPLIST[0] = ACLGROUPNAME
		
	for permission in PERIMISSION_TYPES:
		ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
		ACLDelGroupPermission(permission, GRP_UUID, ORG_UUID)
		ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
			
	for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
		ACLCreateNewUser(0)
		HCCUSERSLIST.append(i)
		HCCUSERSLIST[i] = HCCUSERNAME
		ACLActivateNewUser()
		ACLDectivateUser(USR_UUID)
		ACLActivateNewUser()
		ACLSetPassword()
		ACLAssignCodingOrg()
		ACLAddMemberToGroup()
		ACLDelMemberFromGroup(GRP_UUID, USR_UUID)
		ACLAddMemberToGroup()
		logInToHCC()
	#WriteToCsvFile()	
	ListUserGroupOrg()					
#=========================================================================================
#============= MULTIPLE GROUPS ONE CODING ORG MULTIPLE USERS =============================
#=========================================================================================
def TestFlowControlTwo():
	global HCCGRPLIST, HCCUSERSLIST
	PrintGlobalParamaterSettings()
	for i in range (0, int(NUMBER_OF_GRPS_TO_CREATE)):
		logInToACL()
		ACLCreateNewGroup()
		HCCGRPLIST.append(i)
		HCCGRPLIST[i] = ACLGROUPNAME
				
	for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
		ACLCreateNewUser(0)
		ACLActivateNewUser()
		ACLSetPassword()
		ACLCreateNewCodingOrg()
		HCCORGLIST[0] = CODING_ORGANIZATION
		ACLAssignCodingOrg()
		ACLAddMemberToGroup()
		logInToHCC()
		HCCUSERSLIST.append(i)
		HCCUSERSLIST[i] = HCCUSERNAME
	ListUserGroupOrg()			
#=========================================================================================
#============= ONE GROUP MULTIPLE CODING ORGS MULTIPLE USERS =============================
#=========================================================================================
def TestFlowControlThree():	
	global HCCORGLIST, HCCUSERSLIST
	PrintGlobalParamaterSettings()
	for i in range (0, int(NUMBER_OF_ORGS_TO_CREATE)):
		logInToACL()
		ACLCreateNewCodingOrg()
		HCCORGLIST.append(i)
		HCCORGLIST[i] = CODING_ORGANIZATION			
			
	for i in range (0, int(NUMBER_OF_USERS_TO_CREATE)):
		ACLCreateNewUser(0)
		ACLActivateNewUser()
		ACLSetPassword()
		ACLAssignCodingOrg()
		ACLCreateNewGroup()
		HCCGRPLIST[0] = ACLGROUPNAME
		ACLAddMemberToGroup()
		logInToHCC()
		HCCUSERSLIST.append(i)
		HCCUSERSLIST[i] = HCCUSERNAME
	ListUserGroupOrg()	
#=========================================================================================
#============= SIMPLE CREATE ONLY ONE USER, ORG, GROUP ===================================
#=========================================================================================
def TestFlowControlFour():
	global HCCUSERSLIST, HCCORGLIST, HCCGRPLIST
	PrintGlobalParamaterSettings()
	logInToACL()
	ACLCreateNewCodingOrg()
	HCCORGLIST[0] = CODING_ORGANIZATION
	ACLCreateNewGroup()
	HCCGRPLIST[0] = ACLGROUPNAME
	ACLCreateNewUser(0)
	HCCUSERSLIST[0] = HCCUSERNAME
	ACLActivateNewUser()
	ACLSetPassword()
	ACLAssignCodingOrg()
	ACLAddMemberToGroup()
	logInToHCC()
	#WriteToCsvFile()	
	ListUserGroupOrg()		
#=========================================================================================
#============= STRESSING ADD DELETE PERMISSIONS ==========================================
#=========================================================================================
def TestFlowControlFive():
	global HCCUSERSLIST, PERIMISSION_TYPES
	PrintGlobalParamaterSettings()
	logInToACL()
	ACLCreateNewCodingOrg()
	HCCORGLIST[0] = CODING_ORGANIZATION
	ACLCreateNewGroup()
	HCCGRPLIST[0] = ACLGROUPNAME

	for i in range(0, 100):
		for permission in PERIMISSION_TYPES:
			ACLAddGroupPermission(permission, GRP_UUID, ORG_UUID)
			ACLDelGroupPermission(permission, GRP_UUID, ORG_UUID)
	#WriteToCsvFile()	
	ListUserGroupOrg()																	
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
os.system('clear')

print ("\n\nStarting ACL-Admin New User Creation...\n")

ReadConfigurationFile(str(CSV_CONFIG_FILE_PATH+CSV_CONFIG_FILE_NAME))

if TEST_FLOW_CONTROL == "1":		
	TestFlowControlOne()
elif TEST_FLOW_CONTROL == "2":
	TestFlowControlTwo()
elif TEST_FLOW_CONTROL == "3":
	TestFlowControlThree()
elif TEST_FLOW_CONTROL == "4":
	TestFlowControlFour()
elif TEST_FLOW_CONTROL == "5":
	TestFlowControlFive()			
else:
	print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
	print (">>>>>>>>>>>>>>>>>>> TEST EXECUTION WAS ABORTED <<<<<<<<<<<<<<<<<<<<<<<")
	print (">>>>>>>>>>> SPECIFIC TEST FLOW NUMBER MUST BE SELECTED <<<<<<<<<<<<<<<")
	print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
	print ("\n")	
print ("\n\n=================================")	
print ("==== End of ACL Sanity Test =====")
print ("=================================")
#=========================================================================================
		
		
		
		
		
		
		
		       
            