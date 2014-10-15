#=========================================================================================
# Author: Igor Shekhtman
# Date Created: 15-Oct-2014
# Initial Version: 1.0.0
#=========================================================================================
# Global Paramaters:
# ENVIRONMENT - "Staging" or "Production"
# NUMBEROFUSERSTOCREATE - integer - total number of HCC users to create
# CODINGORGANIZATION - any organization from CDGORGMAP list below
# HCCPASSWORD - default password to be assigned to every HCC user
#=========================================================================================
# Revision 1:
# Author:
# Specifics:
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
#=========================================================================================
#===================== Global Test Environment Selection =================================
#ENVIRONMENT = 'Production'
ENVIRONMENT = 'Staging'

NUMBEROFUSERSTOCREATE = 3
CODINGORGANIZATION = "Load Test Coders"
HCCPASSWORD = "apixio.123"
HCCUSERNAMEPREFIX = "grinder"
HCCUSERNAMEPOSTFIX = "@apixio.net"
ACLCODNGORGPREFIX = "Grinder"
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


ACL_PROTOCOL = "https://"
ACL_DOMAIN = "acladmin" +aclpostfix+ ".apixio.com"
ACL_URL = ACL_PROTOCOL + ACL_DOMAIN

HCC_PROTOCOL = "https://"
HCC_DOMAIN = "hcc" +hccpostfix+ ".apixio.com"
HCC_URL = ACL_PROTOCOL + HCC_DOMAIN


ACLUSERNAME = "root@api.apixio.com"
ACLPASSWORD = "thePassword"
MAX_OPPS = 2
USR_UUID = ""
ORG_UUID = CDGORGMAP[CODINGORGANIZATION]
TOKEN = ""
HCCUSERNAME = ""
HCCUSERSLIST = [0]



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
	global HCCUSERNAMEPREFIX, HCCUSERNAMEPOSTFIX
	hccusernumber = str(int(time.time()))
	hccusername = HCCUSERNAMEPREFIX + hccusernumber + HCCUSERNAMEPOSTFIX
	return hccusername	


class TestRunner:
    def __call__(self):
		log ("\n\nStarting ACL-Admin New User Creation...\n")
		thread_context = HTTPPluginControl.getThreadHTTPClientContext()
		control = HTTPPluginControl.getConnectionDefaults()
		control.setFollowRedirects(1)
		
#=========================================================================================

		def PrintGlobalParamaterSettings():
			print "\nEnvironment: \t\t\t"+ENVIRONMENT
			print "ACL URL: \t\t\t"+ACL_URL
			print "HCC URL: \t\t\t"+HCC_URL
			print "ACL Admin User Name: \t\t"+ACLUSERNAME
			print "Coding Organization: \t\t"+CODINGORGANIZATION
			print "HCC Users to Create: \t\t"+str(NUMBEROFUSERSTOCREATE)
			
#=========================================================================================
		def ACLObtainAuthorization():
			global TOKEN, ACL_URL		
			print "\nACL Obtain Authorization..."
			#print "HOST_URL: " + HOST_URL
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
				print "Status Code = [%s]\t\t" % statuscode	
#=========================================================================================
		def ACLCreateNewUser():
			global USR_UUID, HCCUSERNAME, TOKEN, ACL_URL
			print "\nACL Create New User..."
			login = create_request(Test(1100, 'ACL Create new user'),[
    	        NVPair('Referer', ACL_URL+'/admin/'),
        	])

			HCCUSERNAME = get_new_hcc_user()
			result = login.POST(ACL_URL+"/access/user", (
				NVPair('email', HCCUSERNAME),
				NVPair('session', TOKEN),))
				
			userjson = JSONValue.parse(result.getText())
			if userjson is not None:
				USR_UUID = userjson.get("id")
				#print "User UUID: " + USR_UUID
			
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode
			if statuscode == 500:
				print ">>> Failure occured: username already exists <<<"
				exit()
#=========================================================================================
		def ACLActivateNewUser():
			global USR_UUID, TOKEN, ACL_URL
			print "\nACL Activate New User..."	
			#print "User UUID: " + USR_UUID 
			data = str.encode("session="+str(TOKEN))
			login = create_request(Test(1200, 'ACL Activate new user'),[
				NVPair('Referer', ACL_URL+'/admin/'),
       	     ])

			result = login.PUT(ACL_URL+"/access/user/"+USR_UUID, data, (
				NVPair('session', TOKEN),))
			
			#print_all_cookies(thread_context)
		
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode		
#=========================================================================================
		def ACLSetPassword():
			global USR_UUID, HCCPASSWORD, TOKEN, ACL_URL
			print "\nACL Assign New User Password..."		
			#print "User UUID: " + USR_UUID 
			#print "Password: " + HCCPASSWORD

			headers = [
    	        NVPair('Accept', 'application/json, text/plain, */*'),
    	        NVPair('Accept-Encoding', 'gzip,deflate,sdch'),
    	        NVPair('Accept-Language', 'en-US,en;q=0.8'),
    	        NVPair('Connection', 'keep-alive'),
    	        NVPair('Content-Length', '19'),
    	        NVPair('Content-Type', 'application/x-www-form-urlencoded'),
    	        NVPair('Host', 'acladmin-stg.apixio.com'),
    	        NVPair('Origin', ACL_URL),
    	        NVPair('Referer', ACL_URL+'/admin/'),
    	        NVPair('session', TOKEN),
    	    ]
			login = create_request(Test(1300, 'ACL Set Password'),headers)
		
			password_url = ACL_URL+"/access/user/"+USR_UUID+"/password"
			params = (NVPair('password', HCCPASSWORD),)
			
			#data = Codecs.mpFormDataEncode(params,zeros(1,NVPair),headers)
			
			#result = login.PUT(HOST_URL+"/access/user/"+USR_UUID+"/password", 
			#	data, headers)
		
			result = login.PUT(ACL_URL+"/access/user/"+USR_UUID+"/password", 
				str.encode("password=apixio.123"), headers)
					
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode	
			
#=========================================================================================
		def ACLCreateNewCodingOrg():
			global ACL_URL, TOKEN, ORG_UUID, ACLCODNGORGPREFIX, CODINGORGANIZATION
			print "\nACL Create New Coding Org..."
			 
			conumber = str(int(time.time()))
			coname = ACLCODNGORGPREFIX +"-"+ conumber
			CODINGORGANIZATION = coname									
			#print "Coding Org Name: "+coname
						
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
				#print "Coding Org UUID: " + ORG_UUID
				#print "Coding Org Name: " + coname
			
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode
		
#=========================================================================================
 		def ACLAssignCodingOrg():
 			global USR_UUID, ORG_UUID, ACL_URL
			print "\nACL Assign Coding Organization..."	
			#print "User UUID: " + USR_UUID 
			#print "Org UUID: " + ORG_UUID
			
			login = create_request(Test(1500, 'ACL Add Coding Organization'),[
	   	         NVPair('Referer', ACL_URL+'/admin/'),
	        ])
			result = login. \
				POST(ACL_URL+"/access/userOrganization/"+ORG_UUID+"/"+USR_UUID, (
				NVPair('session', TOKEN),))
				
			
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode
#=========================================================================================
		def HCCLogInto():
			global HCCUSERNAME, HCCPASSWORD, HCC_URL
			HCC_HOST_DOMAIN = 'hccstage.apixio.com'
			HCC_HOST_URL = 'https://%s' % HCC_HOST_DOMAIN
		
			#print "\nHCC Log into HCC with newly created user..."	
			#print "HCC Host Domain: " + HCC_HOST_DOMAIN
			#print "HCC Host URL: " + HCC_HOST_URL
		
			print "\nHCC Connecting to host..."
			result = create_request(Test(2000, 'HCC Connect to host')) \
				.GET(HCC_URL + '/')
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode		
		
			print "\nHCC Detecting login page..."
			result = create_request(Test(2100, 'HCC Get login page')) \
				.GET(HCC_URL + '/account/login/?next=/')
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode		
		
			# Create login request. Referer appears to be necessary
			login = create_request(Test(2200, 'HCC Log in user'),[
				NVPair('Referer', HCC_URL + '/account/login/?next=/'),
			])
		
			print "\nLogging in to HCC Front End..."
			result = login.POST(HCC_URL + '/account/login/?next=/', (
				NVPair('csrfmiddlewaretoken', get_csrf_token(thread_context)),
				NVPair('username', HCCUSERNAME),
				NVPair('password', HCCPASSWORD),))
		
			#print HCCUSERNAME 
			#print HCCPASSWORD	
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode	
			
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

		PrintGlobalParamaterSettings()
		ACLObtainAuthorization()
		ACLCreateNewCodingOrg()
		
		for i in range (0, NUMBEROFUSERSTOCREATE):
			ACLObtainAuthorization()
			ACLCreateNewUser()
			ACLActivateNewUser()
			ACLSetPassword()
			#ACLCreateNewCodingOrg()
			ACLAssignCodingOrg()
			HCCLogInto()
			HCCUSERSLIST.append(i)
			HCCUSERSLIST[i] = HCCUSERNAME
		
		print "\n================================"
		print "List of newly created HCC Users:"
		print "================================"
		for i in range (0, NUMBEROFUSERSTOCREATE):
			print HCCUSERSLIST[i]
		print "================================"
		print "Coding Org :"+CODINGORGANIZATION	
		print "================================"	
		print "\nThe End..."
#=========================================================================================
		
		
		
		
		
		
		
		       
            