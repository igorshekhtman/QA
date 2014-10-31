from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
import time
import csv

HOST_DOMAIN = 'hccstage.apixio.com'
#HOST_DOMAIN = 'dfsasdfsd.asdfsdf.com'
HOST_URL = 'https://%s' % HOST_DOMAIN
#HOST_URL = 'http://%s' % HOST_DOMAIN
USERNAME = 'root@api.apixio.com'
PASSWORD = 'thePassword'
MAX_OPPS = 2

ok = 200
created = 201
accepted = 202
movedperm = 301
redirect = 302

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
        print "Starting HCC Front End Test"
        thread_context = HTTPPluginControl.getThreadHTTPClientContext()
	control = HTTPPluginControl.getConnectionDefaults()
	control.setFollowRedirects(1)
    
    
    

        print "Connecting to host..."
        result = create_request(Test(10000, 'Connect to host')).GET(HOST_URL + '/')
        print result.statusCode
        status_code_check(result.statusCode)


        print "Detecting login page..."
        result = create_request(Test(20000, 'Get login page')).GET(HOST_URL + '/account/login/?next=/')
        print result.statusCode
        status_code_check(result.statusCode)
        
        
        
        # Create login request. Referer appears to be necessary
        #login = create_request(Test(30000, 'Log in user'),[
        #    NVPair('Referer', HOST_URL + '/account/login/?next=/'),
        #])
        
        file_obj="/Users/ishekhtman/Documents/grinder/user-data/user_credentials-p250-stg.csv"
        f=open(file_obj, 'rb')
        reader=csv.reader(f)
        row_cntr = 0
        for row in reader:
            if row_cntr > 0:
                USERNAME = str(row[0])
                PASSWORD = str(row[1])
                print USERNAME+", "+PASSWORD
            row_cntr=row_cntr+1
            


        #Currently there is a bug, where username and password created through acl admin cannot be used to authenticate hccstage.apixio.com
        #Therefore, users and pwds obtained from .csv data feed are being overwritten by the following two lines of code
            USERNAME = 'root@api.apixio.com'
            PASSWORD = 'thePassword'

            print "Logging in to HCC Front End..."
            login = create_request(Test(30000, 'Log in user'),[
                NVPair('Referer', HOST_URL + '/account/login/?next=/'),
            ])


            response = login.POST(HOST_URL + '/account/login/?next=/', (
                NVPair('csrfmiddlewaretoken', get_csrf_token(thread_context)),
                NVPair('username', USERNAME),
                NVPair('password', PASSWORD),))
            print response.statusCode
            status_code_check(response.statusCode)
        f.close()







