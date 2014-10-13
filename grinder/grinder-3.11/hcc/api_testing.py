from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
import time
import csv
#import json

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
useraccount = "useraccount" + postfix + ".apixio.com"
tokenizer = "tokenizer" + postfix + ".apixio.com"
dataorchestrator = "dataorchestrator" + postfix + ".apixio.com"

auth = useraccount + ":7076/auths"
token = tokenizer + ":7075/tokens"
document = dataorchestrator + ":7085/document"
patient = dataorchestrator + ":7085/patient"
event = dataorchestrator + ":7085/events"
util = dataorchestrator + ":7085/util"

thinkTime = '6 seconds'
ok = 200
created = 201
accepted = 202
movedperm = 301
redirect = 302

HOST_DOMAIN = 'hccstage.apixio.com'
HOST_URL = 'https://%s' % HOST_DOMAIN
USERNAME = 'root@api.apixio.com'
PASSWORD = 'thePassword'
MAX_OPPS = 2




def create_request(test, headers=None):
    request = HTTPRequest()
    if headers:
        request.headers = headers
    test.record(request)
    return request

def get_csrf_token(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    csrftoken = ''
    for cookie in cookies:
        if cookie.getName() == 'csrftoken':
            csrftoken = cookie.getValue()
    return csrftoken

def status_code_check(status_code):
    if (status_code == ok):
        print "Success ..."
    else:
        print "Failure occured ..."


class TestRunner:
    def __call__(self):
        print "\n\n\n\n\n\nStarting DataOrchestrator API Test\n\n\n"
        thread_context = HTTPPluginControl.getThreadHTTPClientContext()
	control = HTTPPluginControl.getConnectionDefaults()
	control.setFollowRedirects(1)
    
    
    	print('Environment: \t\t\t'+environment+'')
    	print('User Account API URL: \t\t'+useraccount+'')  
    	print('Tokenizer API URL: \t\t'+tokenizer+'') 
    	print('Data Orchestrator API URL: \t'+dataorchestrator+'\n')
    	
    	
    	print('Autorization...\n')
    	response = login.POST(auth, (
    		NVPair('email', USERNAME),
    		NVPair('password', PASSWORD),))
    	print response.statusCode
    	status_code_check(result.statusCode)
 		
 
# .group("Authorization") {
#    feed(csv(userdatafn))
#      .exec(
#        http("Submit authorization")
#          .post(auth)
#          .formParam("email", "${username}")
#          .formParam("password", "${password}")
#          .check(jsonPath("$.token").saveAs("externalToken"))
#          .check(jsonPath("$.token").transform { value: String => {
#          println("value = " + value.get)
#          value
#        }})
#          .check(status.is(ok)))
#      .pause(thinkTime)
#  }




        #print "Connecting to host...\n"
        #result = create_request(Test(10000, 'Connect to host')).GET(HOST_URL + '/')
        #print result.statusCode
        #status_code_check(result.statusCode)


        #print "Detecting login page...\n"
        #result = create_request(Test(20000, 'Get login page')).GET(HOST_URL + '/account/login/?next=/')
        #print result.statusCode
        #status_code_check(result.statusCode)
        
        
        
        # Create login request. Referer appears to be necessary
        #login = create_request(Test(30000, 'Log in user'),[
        #    NVPair('Referer', HOST_URL + '/account/login/?next=/'),
        #])
        
        #file_obj="/Users/ishekhtman/Documents/grinder/user-data/user_credentials-p250-stg.csv"
        #f=open(file_obj, 'rb')
        #reader=csv.reader(f)
        #row_cntr = 0
        #for row in reader:
        #    if row_cntr > 0:
        #        USERNAME = str(row[0])
        #        PASSWORD = str(row[1])
        #        print USERNAME+", "+PASSWORD
        #    row_cntr=row_cntr+1
            


        #Currently there is a bug, where username and password created through acl admin cannot be used to authenticate hccstage.apixio.com
        #Therefore, users and pwds obtained from .csv data feed are being overwritten by the following two lines of code
        #    USERNAME = 'root@api.apixio.com'
        #    PASSWORD = 'thePassword'

        #    print "Logging in to HCC Front End..."
        #    login = create_request(Test(30000, 'Log in user'),[
        #        NVPair('Referer', HOST_URL + '/account/login/?next=/'),
        #    ])


         #   response = login.POST(HOST_URL + '/account/login/?next=/', (
         #       NVPair('csrfmiddlewaretoken', get_csrf_token(thread_context)),
         #       NVPair('username', USERNAME),
         #       NVPair('password', PASSWORD),))
         #   print response.statusCode
         #   status_code_check(response.statusCode)
        #f.close()







