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
#			* Assign newly created user pre-defined password (HCC_PASSWORD)
#			* Assign newly created HCC user coding org
#				- Either pre-defined coding org or newly created coding org
#			* Assign specific or newly created coding org to a user
#			* Add list of members to a newly created Group
#			* Log into HCC with newly created user/org
#			* Store each of the newly created users in an array (HCCUSERSLIST[])
#			* Store each of the newly created coding orgs in an array (HCCORGLIST[])
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
# ENVIRONMENT - "Staging" or "Production"
# NUMBER_OF_USERS_TO_CREATE - integer (0 through x) - total number of HCC users to create
# NUMBER_OF_ORGS_TO_CREATE - integer (0 through x) - total number of coding orgs to create
# CODINGORGANIZATION - any organization from CDGORGMAP list below
# HCCPASSWORD - default password to be assigned to every HCC user
#=========================================================================================
# Revision 1: 1.0.1
# Author: Igor Shekhtman ishekhtman@apixio.com 
# Specifics: Introduction of Program Flow Control
#=========================================================================================
# Revision 2:
# Author:
# Specifics:
#=========================================================================================
# Revision 3:
# Author:
# Specifics:
#=========================================================================================
from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Codecs, Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
from jarray import zeros
import time
import csv
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
#===================== Program Version ===================================================
VERSION = '1.0.1'
#===================== Global Test Environment Selection =================================
#ENVIRONMENT = 'Production'
ENVIRONMENT = 'Staging'

NUMBER_OF_USERS_TO_CREATE = 1
NUMBER_OF_ORGS_TO_CREATE = 1
NUMBER_OF_GRPS_TO_CREATE = 1

CODING_ORGANIZATION = "Load Test Coders"
HCC_PASSWORD = "apixio.123"
HCC_USERNAME_PREFIX = "grinderU"
HCC_USERNAME_POSTFIX = "@apixio.net"
ACL_CODNG_ORG_PREFIX = "grinderO"
ACL_GROUP_PREFIX = "grinderG"
#=========================================================================================

#============ Global variable declaration, initialization ================================

if (ENVIRONMENT == "Production"):
	aclpostfix = "-prd"
	hccpostfix = ""
else:
	aclpostfix = "-stg"
	hccpostfix = "stage"
	
	
ok = 200
created = 201
accepted = 202
nocontent = 204
movedperm = 301
redirect = 302
forbidden = 403
intserveror = 500
servunavail = 503

PROTOCOL = "https://"

ACL_DOMAIN = "acladmin" +aclpostfix+ ".apixio.com"
ACL_URL = PROTOCOL + ACL_DOMAIN

HCC_DOMAIN = "hcc" +hccpostfix+ ".apixio.com"
HCC_URL = PROTOCOL + HCC_DOMAIN

ACLUSERNAME = "root@api.apixio.com"
ACLPASSWORD = "thePassword"
USR_UUID = ""
ORG_UUID = CDGORGMAP[CODING_ORGANIZATION]
GRP_UUID = ""
TOKEN = ""
HCCUSERNAME = ""
ACLGROUPNAME = ""
HCCUSERSLIST = [0]
HCCORGLIST = [0]
HCCGRPLIST = [0]



def create_request(test, headers=None):
    request = HTTPRequest()
    if headers:
        request.headers = headers
        #print "headers = [%s]" % headers
    test.record(request)
    #print "request = [%s]" % request
    return request

def get_session(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    session = ''
    #print "cookies = [%s]" % cookies
    for cookie in cookies:
        if cookie.getName() == 'session':
            session = cookie.getValue()
            #print "cookie = [%s]" % cookie
    return session
    
def get_csrf_token(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    csrftoken = ''
    for cookie in cookies:
        if cookie.getName() == 'csrftoken':
            csrftoken = cookie.getValue()
    return csrftoken    
    
def print_all_cookies(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    print "cookies = [%s]" % cookies
    return cookies    
    
def log(text):
    grinder.logger.info(text)
    print(text)
    
def get_new_hcc_user():
	global HCC_USERNAME_PREFIX, HCC_USERNAME_POSTFIX
	hccusernumber = str(int(time.time()))
	hccusername = HCC_USERNAME_PREFIX + hccusernumber + HCC_USERNAME_POSTFIX
	return hccusername	


class TestRunner:
    def __call__(self):
		log ("\n\nStarting ACL-Admin New User Creation...\n")
		thread_context = HTTPPluginControl.getThreadHTTPClientContext()
		control = HTTPPluginControl.getConnectionDefaults()
		control.setFollowRedirects(1)
		
#=========================================================================================
		def PrintGlobalParamaterSettings():
			log ("\nVersion: \t\t\t"+VERSION)
			log ("\nEnvironment: \t\t\t"+ENVIRONMENT)
			log ("ACL URL: \t\t\t"+ACL_URL)
			log ("HCC URL: \t\t\t"+HCC_URL)
			log ("ACL Admin User Name: \t\t"+ACLUSERNAME)
			log ("Coding Organization: \t\t"+CODING_ORGANIZATION)
			log ("HCC Users to Create: \t\t"+str(NUMBER_OF_USERS_TO_CREATE))
			log ("HCC Orgs to Create: \t\t"+str(NUMBER_OF_ORGS_TO_CREATE))
			log ("HCC Groups to Create: \t\t"+str(NUMBER_OF_GRPS_TO_CREATE))
#=========================================================================================
		def ACLObtainAuthorization():
			global TOKEN, ACL_URL		
			log ("\nACL Obtain Authorization...")
			#log ("HOST_URL: " + HOST_URL)
			statuscode = 500
			# repeat until successful login is reached
			while statuscode != 200:
				login = create_request(Test(1000, 'ACL Log in admin'),[
            		NVPair('Referer', ACL_URL+'/'),
        		])
				result = login.POST(ACL_URL+"/auth", (
					NVPair('session', get_session(thread_context)),
					NVPair('email', ACLUSERNAME),
					NVPair('password', ACLPASSWORD),))
				TOKEN = get_session(thread_context)
				statuscode = result.statusCode
				log ("Status Code = [%s]\t\t" % statuscode)
#=========================================================================================
		def ACLCreateNewUser():
			global USR_UUID, HCCUSERNAME, TOKEN, ACL_URL
			log ("\nACL Create New User...")
			login = create_request(Test(1100, 'ACL Create new user'),[
    	        NVPair('Referer', ACL_URL+'/admin/'),])
			HCCUSERNAME = get_new_hcc_user()
			result = login.POST(ACL_URL+"/access/user", (
				NVPair('email', HCCUSERNAME),
				NVPair('session', TOKEN),))
			userjson = JSONValue.parse(result.getText())
			if userjson is not None:
				USR_UUID = userjson.get("id")
				#log ("User UUID: " + USR_UUID)
			statuscode = result.statusCode
			log ("Status Code = [%s]\t\t" % statuscode)
			if statuscode == 500:
				log (">>> Failure occured: username already exists <<<")
				exit()
#=========================================================================================
		def ACLActivateNewUser():
			global USR_UUID, TOKEN, ACL_URL
			log ("\nACL Activate New User...")	
			#log ("User UUID: " + USR_UUID)
			data = str.encode("session="+str(TOKEN))
			login = create_request(Test(1200, 'ACL Activate new user'),[
				NVPair('Referer', ACL_URL+'/admin/'),])
			result = login.PUT(ACL_URL+"/access/user/"+USR_UUID, data, (
				NVPair('session', TOKEN),))
			log ("Status Code = [%s]\t\t" % result.statusCode)		
#=========================================================================================
		def ACLSetPassword():
			global USR_UUID, HCC_PASSWORD, TOKEN, ACL_URL
			log ("\nACL Assign New User Password...")		
			#log ("User UUID: " + USR_UUID)
			#log ("Password: " + HCC_PASSWORD)
			headers = [
    	        NVPair('Origin', ACL_URL),
    	        NVPair('Referer', ACL_URL+'/admin/'),
    	        NVPair('session', TOKEN),]
			login = create_request(Test(1300, 'ACL Set Password'),headers)
			#PUT(uri, data, headers)
			data = str.encode("password=apixio.123")
			result = login.PUT(ACL_URL+"/access/user/"+USR_UUID+"/password", 
				data, headers)
			log ("Status Code = [%s]\t\t" % result.statusCode)			
#=========================================================================================
		def ACLCreateNewCodingOrg():
			global ACL_URL, TOKEN, ORG_UUID, ACL_CODNG_ORG_PREFIX, CODING_ORGANIZATION
			log ("\nACL Create New Coding Org...")
			conumber = str(int(time.time()))
			coname = ACL_CODNG_ORG_PREFIX + conumber
			CODING_ORGANIZATION = coname									
			#log ("Coding Org Name: "+coname)		
			login = create_request(Test(1400, 'ACL Create new coding org'),[
    	        NVPair('Referer', ACL_URL+'/admin/'),
        	])
			result = login.POST(ACL_URL+"/access/userOrganization", (
				NVPair('name', coname),
				NVPair('key', conumber),
				NVPair('description', coname),
				NVPair('session', TOKEN),))				
			userjson = JSONValue.parse(result.getText())
			if userjson is not None:
				ORG_UUID = userjson.get("id")
				#log ("Coding Org UUID: " + ORG_UUID)
				#log ("Coding Org Name: " + coname)
	
			log ("Status Code = [%s]\t\t" % result.statusCode)
#=========================================================================================
		def ACLCreateNewGroup():
			global ACL_URL, TOKEN, ACL_GROUP_PREFIX, GRP_UUID, ACLGROUPNAME
			log ("\nACL Create New Group...")
			gnumber = str(int(time.time()))
			gname = ACL_GROUP_PREFIX + gnumber
			ACLGROUPNAME = gname									
			#log ("Group Name: "+gname)		
			login = create_request(Test(1500, 'ACL Create new group'),[
    	        NVPair('Referer', ACL_URL+'/admin/'),
        	])
			result = login.POST(ACL_URL+"/access/group", (
				NVPair('name', gname),
				NVPair('session', TOKEN),))				
			grpjson = JSONValue.parse(result.getText())
			if grpjson is not None:
				GRP_UUID = grpjson.get("id").get("id")
				log ("Group UUID: " + GRP_UUID)
				log ("Group Name: " + gname)			
			log ("Status Code = [%s]\t\t" % result.statusCode)
#=========================================================================================
		def ACLDeleteExistingGroup(group_uuid):									
			global ACL_URL, TOKEN
			log ("\nACL Delete Existing Group...")		
			login = create_request(Test(1800, 'ACL Delete existing group'),[
    	        NVPair('Referer', ACL_URL+'/admin/'),
        	])
			result = login.DELETE(ACL_URL+"/access/group/"+group_uuid, (
				NVPair('session', TOKEN),))							
			log ("Status Code = [%s]\t\t" % result.statusCode)
#=========================================================================================
		def ACLAddMemberToGroup():
			global USR_UUID, GRP_UUID, ACL_URL
			log ("\nACL Add Member to Group...")	
			log ("User UUID: " + USR_UUID)
			log ("Group UUID: " + GRP_UUID)
			login = create_request(Test(1600, 'ACL Add Member to Group'),[
	   	         NVPair('Referer', ACL_URL+'/admin/'),])
			result = login. \
				POST(ACL_URL+"/access/groupMembership/"+GRP_UUID+"/"+USR_UUID, (
				NVPair('session', TOKEN),))
			log ("Status Code = [%s]\t\t" % result.statusCode)
#=========================================================================================
 		def ACLAssignCodingOrg():
 			global USR_UUID, ORG_UUID, ACL_URL
			log ("\nACL Assign Coding Organization...")	
			#log ("User UUID: " + USR_UUID)
			#log ("Org UUID: " + ORG_UUID)
			login = create_request(Test(1700, 'ACL Add Coding Organization'),[
	   	         NVPair('Referer', ACL_URL+'/admin/'),
	        ])
			result = login. \
				POST(ACL_URL+"/access/userOrganization/"+ORG_UUID+"/"+USR_UUID, (
				NVPair('session', TOKEN),))
			log ("Status Code = [%s]\t\t" % result.statusCode)
#=========================================================================================
		def HCCLogInto():
			global HCCUSERNAME, HCC_PASSWORD, HCC_URL
			HCC_HOST_DOMAIN = 'hccstage.apixio.com'
			HCC_HOST_URL = 'https://%s' % HCC_HOST_DOMAIN
			log ("\nHCC Connecting to host...")
			result = create_request(Test(2000, 'HCC Connect to host')) \
				.GET(HCC_URL + '/')
			log ("Status Code = [%s]\t\t" % result.statusCode)		
			log ("\nHCC Detecting login page...")
			result = create_request(Test(2100, 'HCC Get login page')) \
				.GET(HCC_URL + '/account/login/?next=/')
			log ("Status Code = [%s]\t\t" % result.statusCode)	
			# Create login request. Referer appears to be necessary
			login = create_request(Test(2200, 'HCC Log in user'),[
				NVPair('Referer', HCC_URL + '/account/login/?next=/'),
			])
			log ("\nLogging in to HCC Front End...")
			result = login.POST(HCC_URL + '/account/login/?next=/', (
				NVPair('csrfmiddlewaretoken', get_csrf_token(thread_context)),
				NVPair('username', HCCUSERNAME),
				NVPair('password', HCC_PASSWORD),))
			#log (HCCUSERNAME)
			#log (HCC_PASSWORD)	
			log ("Status Code = [%s]\t\t" % result.statusCode)	
#=========================================================================================
		def ListUserGroupOrg():
			log ("\n=================================")
			log ("List of newly created HCC Users:")
			log ("=================================")
			for i in range (0, NUMBER_OF_USERS_TO_CREATE):
				log (HCCUSERSLIST[i])
			log ("=================================")
			log ("List of newly created HCC Orgs:")
			log ("=================================")
			for i in range (0, NUMBER_OF_ORGS_TO_CREATE):
				log (HCCORGLIST[i])
			log ("=================================")
			log ("List of newly created HCC Groups:")
			log ("=================================")
			for i in range (0, NUMBER_OF_GRPS_TO_CREATE):
				log (HCCGRPLIST[i])			
			log ("=================================")	
			log ("\nThe End...")						
#=========================================================================================
#============= ONE GROUP ONE CODING ORG MULTIPLE USERS ===================================
#=========================================================================================
		def ProgramFlowControlOne():
			global HCCUSERSLIST
			PrintGlobalParamaterSettings()
			ACLObtainAuthorization()
			ACLCreateNewCodingOrg()
			HCCORGLIST[0] = CODING_ORGANIZATION
			ACLCreateNewGroup()
			ACLDeleteExistingGroup(GRP_UUID)
			ACLCreateNewGroup()
			HCCGRPLIST[0] = ACLGROUPNAME
			
			for i in range (0, NUMBER_OF_USERS_TO_CREATE):
				ACLCreateNewUser()
				HCCUSERSLIST.append(i)
				HCCUSERSLIST[i] = HCCUSERNAME
				ACLActivateNewUser()
				ACLSetPassword()
				ACLAssignCodingOrg()
				ACLAddMemberToGroup()
				HCCLogInto()
			ListUserGroupOrg()					
#=========================================================================================
#============= MULTIPLE GROUPS ONE CODING ORG MULTIPLE USERS =============================
#=========================================================================================
		def ProgramFlowControlTwo():
			global HCCGRPLIST, HCCUSERSLIST
			PrintGlobalParamaterSettings()
			for i in range (0, NUMBER_OF_GRPS_TO_CREATE):
				ACLObtainAuthorization()
				ACLCreateNewGroup()
				HCCGRPLIST.append(i)
				HCCGRPLIST[i] = ACLGROUPNAME
				
			for i in range (0, NUMBER_OF_USERS_TO_CREATE):
				ACLCreateNewUser()
				ACLActivateNewUser()
				ACLSetPassword()
				ACLCreateNewCodingOrg()
				HCCORGLIST[0] = CODING_ORGANIZATION
				ACLAssignCodingOrg()
				ACLAddMemberToGroup()
				HCCLogInto()
				HCCUSERSLIST.append(i)
				HCCUSERSLIST[i] = HCCUSERNAME
			ListUserGroupOrg()			
#=========================================================================================
#============= ONE GROUP MULTIPLE CODING ORGS MULTIPLE USERS =============================
#=========================================================================================
		def ProgramFlowControlThree():	
			global HCCORGLIST, HCCUSERSLIST
			PrintGlobalParamaterSettings()
			for i in range (0, NUMBER_OF_ORGS_TO_CREATE):
				ACLObtainAuthorization()
				ACLCreateNewCodingOrg()
				HCCORGLIST.append(i)
				HCCORGLIST[i] = CODING_ORGANIZATION			
			
			for i in range (0, NUMBER_OF_USERS_TO_CREATE):
				ACLCreateNewUser()
				ACLActivateNewUser()
				ACLSetPassword()
				ACLAssignCodingOrg()
				ACLCreateNewGroup()
				HCCGRPLIST[0] = ACLGROUPNAME
				ACLAddMemberToGroup()
				HCCLogInto()
				HCCUSERSLIST.append(i)
				HCCUSERSLIST[i] = HCCUSERNAME
			ListUserGroupOrg()						
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
		
		ProgramFlowControlOne()
		
		#ProgramFlowControlTwo()
		
		#ProgramFlowControlThree()
		
#=========================================================================================
		
		
		
		
		
		
		
		       
            