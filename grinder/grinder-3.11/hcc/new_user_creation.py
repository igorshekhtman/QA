from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Codecs, Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
from jarray import zeros
import time
import csv


#===================== Global Test Environment Selection ========================
#environment = 'Production'
environment = 'Staging'

numberofusers = 1
testduration = '10 seconds'
#================================================================================

#============ Variable declaration, initialization ==============================
userdatafn = "user_credentials-prd.csv"
patientdatafn = "patient_uuids-prd.csv"
documentdatafn = "document_uuids-prd.csv"
useraccount = "useraccount-prd.apixio.com"
tokenizer = "tokenizer-prd.apixio.com"
dataorchestrator = "dataorchestrator-prd.apixio.com"
postfix = "-prd"

if (environment == "Production"):
	postfix = "-prd"
else:
	postfix = "-stg"


userdatafn = "user_credentials" + postfix + ".csv"
patientdatafn = "patient_uuids" + postfix + ".csv"
documentdatafn = "document_uuids" + postfix + ".csv"

acladmin = "acladmin" + postfix + ".apixio.com"
useraccount = "useraccount" + postfix + ".apixio.com"
tokenizer = "tokenizer" + postfix + ".apixio.com"
dataorchestrator = "dataorchestrator" + postfix + ".apixio.com"

auth = "https://" + useraccount + ":7076/auths"
token = "https://" + tokenizer + ":7075/tokens"
document = "https://" + dataorchestrator + ":7085/document"
patient = dataorchestrator + ":7085/patient"
event = dataorchestrator + ":7085/events"
util = dataorchestrator + ":7085/util"

thinkTime = "6 seconds"
ok = 200
created = 201
accepted = 202
movedperm = 301
redirect = 302


HOST_DOMAIN = "acladmin" +postfix+ ".apixio.com"
HOST_URL = "https://" + HOST_DOMAIN
#HOST_URL = "https://%s" % HOST_DOMAIN
#Anthonys computer - used for testing
#HOST_URL = "http://10.19.220.51:8086"
USERNAME = "root@api.apixio.com"
PASSWORD = "thePassword"
MAX_OPPS = 2
NEWUSER  = "apxdemot1010@apixio.net"
USERPASSWORD = "apixio.123"
USR_UUID = ""
# Apixio Coders
# ORG_UUID = "UO_059c7bbd-7ecc-4172-8d81-6ea2dadb6e76"
# Load Test Coders
ORG_UUID = "UO_149af107-1ef7-49a0-923e-be4b2de174b3"


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


class TestRunner:
    def __call__(self):
		log ("\n\nStarting ACL-Admin New User Creation...\n")
		thread_context = HTTPPluginControl.getThreadHTTPClientContext()
		control = HTTPPluginControl.getConnectionDefaults()
		control.setFollowRedirects(1)
	
		print "\nEnvironment: \t\t\t"+environment
		print "User Account API URL: \t\t"+useraccount
		print "Tokenizer API URL: \t\t"+tokenizer
		print "Data Orchestrator API URL: \t"+dataorchestrator
		print "Host URL: \t\t\t"+HOST_URL
		print "Host Domain: \t\t\t"+HOST_DOMAIN+"\n\n"
		
		#=================================================================================
		
		print "\nObtain Authorization..."
		print "HOST_URL: " + HOST_URL
		statuscode = 500
		# repeat until successful login is reached
		while statuscode != 200:
		
			login = create_request(Test(1000, 'Log in admin'),[
            	NVPair('Referer', 'https://acladmin-stg.apixio.com/'),
        	])
			
			result = login.POST(HOST_URL+"/auth", (
				NVPair('session', get_session(thread_context)),
				NVPair('email', USERNAME),
				NVPair('password', PASSWORD),))
		
			token = get_session(thread_context)

			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode
				
		#=================================================================================
				
		print "\nSelect useres tab..."
		
		login = create_request(Test(2000, 'Select users'),[
            NVPair('Referer', 'https://acladmin-stg.apixio.com/admin/'),
        ])

		result = login.GET(HOST_URL+"/access/users", (
			NVPair('session', token),))

			
		statuscode = result.statusCode

		print "Status Code = [%s]\t\t" % statuscode
		
		#=================================================================================
		
		print "\nCreate New User..."
		
		login = create_request(Test(3000, 'Create new user'),[
            NVPair('Referer', 'https://acladmin-stg.apixio.com/admin/'),
        ])

		# main loop, designating number of users to create
		for i in range (0, 1):
			username = "apxdemot000093"+str(i)+"@apixio.net"
			print "Username = [%s]" % username
			result = login.POST(HOST_URL+"/access/user", (
				NVPair('email', username),
				NVPair('session', token),))
				
			userjson = JSONValue.parse(result.getText())
			json2 = result.getText()
			if userjson is not None:
				USR_UUID = userjson.get("id")
				print "User UUID: " + USR_UUID
			
			statuscode = result.statusCode
			print "Status Code = [%s]\t\t" % statuscode
		
		#=================================================================================
		
		print "\nActivate New User..."	
		print "User UUID: " + USR_UUID 
		json1 = '{\"password\"        :  \"apixio.123\"}'
		login = create_request(Test(4000, 'Activate new user'),[
            NVPair('Referer', 'https://acladmin-stg.apixio.com/admin/'),
        ])

		result = login.PUT(HOST_URL+"/access/user/"+USR_UUID, json2, (
			NVPair('session', token),))
			
		print_all_cookies(thread_context)
		
		statuscode = result.statusCode
		print "Status Code = [%s]\t\t" % statuscode		
		
		#=================================================================================
 
		print "\nAssign New User Password..."		
		print "User UUID: " + USR_UUID 
		print "Password: " + USERPASSWORD

		headers = [
            NVPair('Accept', 'application/json, text/plain, */*'),
            NVPair('Accept-Encoding', 'gzip,deflate,sdch'),
            NVPair('Accept-Language', 'en-US,en;q=0.8'),
            NVPair('Connection', 'keep-alive'),
            NVPair('Content-Length', '19'),
            NVPair('Content-Type', 'application/x-www-form-urlencoded'),
            NVPair('Host', 'acladmin-stg.apixio.com'),
            NVPair('Origin', 'https://acladmin-stg.apixio.com'),
            NVPair('Referer', 'https://acladmin-stg.apixio.com/admin/'),
            NVPair('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'),  
            NVPair('session', token),          
        ]
		login = create_request(Test(5000, 'Set Password'),headers)
		
		password_url = HOST_URL+"/access/user/"+USR_UUID+"/password"
		params = (NVPair('password', USERPASSWORD),)
		#data = Codecs.mpFormDataEncode(params,zeros(1,NVPair),headers)
		#result = login.PUT(HOST_URL+"/access/user/"+USR_UUID+"/password", data, headers)
		
		result = login.PUT(HOST_URL+"/access/user/"+USR_UUID+"/password", str.encode("password=apixio.123"), headers)
					
		statuscode = result.statusCode
		print "Status Code = [%s]\t\t" % statuscode	
		
		#=================================================================================
 
		print "\nAssign Coding Organization..."	
		print "User UUID: " + USR_UUID 
		print "Org UUID: " + ORG_UUID
			
		login = create_request(Test(6000, 'Add Coding Organization'),[
            NVPair('Referer', 'https://acladmin-stg.apixio.com/admin/'),
        ])
		result = login.POST(HOST_URL+"/access/userOrganization/"+ORG_UUID+"/"+USR_UUID, (
			NVPair('session', token),))
				
			
		statuscode = result.statusCode
		print "Status Code = [%s]\t\t" % statuscode
		
		#=================================================================================
		
		
		#HCC_REQUEST_URL = "https://hccstage.apixio.com/account/login/"
		#HCC_HOST_URL = "https://hccstage.apixio.com"
		HCC_HOST_DOMAIN = 'hccstage.apixio.com'
		HCC_HOST_URL = 'https://%s' % HCC_HOST_DOMAIN
		
		print "\nLog into HCC with newly created user..."	
		print "User name: " + username 
		print "Password: " + USERPASSWORD
		print "HCC Host Domain: " + HCC_HOST_DOMAIN
		print "HCC Host URL: " + HCC_HOST_URL
		
		print "\nConnecting to host..."
		create_request(Test(70000, 'HCC Connect to host')).GET(HCC_HOST_URL + '/')
		
		print "\nDetecting login page..."
		create_request(Test(71000, 'HCC Get login page')).GET(HCC_HOST_URL + '/account/login/?next=/')
		
		# Create login request. Referer appears to be necessary
		login = create_request(Test(72000, 'HCC Log in user'),[
			NVPair('Referer', HCC_HOST_URL + '/account/login/?next=/'),
		])
		
		print "\nLogging in to HCC Front End..."
		result = login.POST(HCC_HOST_URL + '/account/login/?next=/', (
			NVPair('csrfmiddlewaretoken', get_csrf_token(thread_context)),
			NVPair('username', username),
			NVPair('password', USERPASSWORD),))
			
		statuscode = result.statusCode
		print "Status Code = [%s]\t\t" % statuscode
		
		
		#=================================================================================
		
		
		print "\nThe End..."
		
		
		
		
		
		
		
		
		       
            