import pyhs2
import os
import time
import datetime
import sys
import subprocess
from time import gmtime, strftime
import pycurl
import io
import urllib
import urllib2
import urlparse
import json
import re
import smtplib
import string

os.system('clear')


# ============================ INITIALIZING GLOBAL VARIABLES VALUES ===============================================

TEST_TYPE="DRNegativeTest"
# USERNAME="apxdemot0182-BAD"
USERNAME="apxdemot0182"
# ORGID="190"
PASSWORD="Hadoop.4522"
HOST="https://supload.apixio.com:8443"
# ENVIRONMENT="Staging"
# RETURNCODE="Nothing"

# =================================================================================================================



def test(debug_type, debug_msg):
	RETURNCODE=""
	#print "debug(%d): %s" % (debug_type, debug_msg)
	#print (debug_msg)
	if debug_msg[ :4] == "HTTP" :
		RETURNCODE = debug_msg[9: ]
		print ("RETURN CODE: %s") % RETURNCODE



def getUserData():
	TOKEN_URL="%s/auth/token/" % (HOST);
	c = pycurl.Curl()
	c.setopt(pycurl.URL, TOKEN_URL)
	c.setopt(pycurl.HTTPHEADER, [
	'Accept: application/json',
	'Content-Type: application/x-www-form-urlencoded'        
	])
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.POSTFIELDS, post)
	c.setopt(pycurl.WRITEFUNCTION, buf.write)
	c.setopt(pycurl.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(pycurl.DEBUGFUNCTION, test)
	c.perform()
	

# Good credentials
print ("Good username and Good password")
USERNAME="apxdemot0182"
PASSWORD="Hadoop.4522"
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()

# Bad username
print ("Bad username and Good password")
USERNAME="apxdemot0182-BAD"
PASSWORD="Hadoop.4522"
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()

# Bad password
print ("Good username and Bad password")
USERNAME="apxdemot0182"
PASSWORD="Hadoop.4522-BAD"
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()