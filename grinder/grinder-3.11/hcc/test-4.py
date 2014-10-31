from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
from jarray import zeros
import time

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

# This script uses the HTTPClient.Codecs class to post itself to the
# server as a multi-part form. Thanks to Marc Gemis.
#from net.grinder.script.Grinder import grinder
#from net.grinder.script import Test
#from net.grinder.plugin.http import HTTPRequest
#from HTTPClient import Codecs, NVPair
#from jarray import zeros

test1 = Test(5000, "Igor - Upload Image")
request1 = HTTPRequest(url = HOST_URL)
test1.record(request1)
class TestRunner:
    def __call__(self):
        files = ( NVPair("self", "form.py"), )
        parameters = ( NVPair("run number", str(grinder.runNumber)), )
        # This is the Jython way of creating an NVPair[] Java array
        # with one element.
        headers = zeros(1, NVPair)
        # Create a multi-part form encoded byte array.
        data = Codecs.mpFormDataEncode(parameters, files, headers)
        grinder.logger.output("Content type set to %s" % headers[0].value)
        # Call the version of POST that takes a byte array.
        result = request1.POST("/upload", data, headers)