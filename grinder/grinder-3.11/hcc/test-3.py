from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
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

# This example shows how many HTTP interactions can be grouped as a
# single test by wrapping them in a function.
# We declare a default URL for the HTTPRequest.
request = HTTPRequest(url = HOST_URL)
def page1():
    request.GET('/console')
    request.GET('/console/login/LoginForm.jsp')
    request.GET('/console/login/bea_logo.gif')
Test(3000, "Igor - First page").record(page1)
class TestRunner:
    def __call__(self):
        page1()