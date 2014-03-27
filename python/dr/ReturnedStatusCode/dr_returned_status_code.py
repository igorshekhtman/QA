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
import uuid
import cStringIO
os.system('clear')

#
#================================== INITIALIZING AND ASSIGN GLOBAL VARIABLES ============================================================================
#
DIR="/mnt/testdata/DR/returnedstatuscode/Documents"
PIPELINE_MODULE="DR"
TEST_TYPE="ReturnedStatusCode"
PASSED = """<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"""
FAILED = """<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"""
SUBHDR = """<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"""
QUERY_DESC=""
COMPONENT_STATUS="""PASSED"""
REPORT = """"""

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())

UPLOAD_URL=""
TOKEN_URL=""
BATCH=""
DRBATCH=""
MANIFEST_FILENAME=""
MANIFEST_FILE=""
#
#================================ DONE ASSIGNING GLOBAL VARIABLES =======================================================================================
#

def checkEnvironment():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	global USERNAME, ORGID, PASSWORD, HOST, BATCHID, TOKEN_URL, UPLOAD_URL
	global BATCH, DRBATCH, MANIFEST_FILENAME
	if ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "P")):
		USERNAME="apxdemot0138"
		ORGID="10000279"
		PASSWORD="Hadoop.4522"
		HOST="https://dr.apixio.com:8443"
		ENVIRONMENT="Production"
	else:
		USERNAME="apxdemot0182"
		ORGID="190"
		PASSWORD="Hadoop.4522"
		HOST="https://supload.apixio.com:8443"
		ENVIRONMENT="Staging"
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID)
	TOKEN_URL="%s/auth/token/" % (HOST)
	BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	MANIFEST_FILENAME=BATCH+"_manifest.txt"
	return ENVIRONMENT


ENVIRONMENT = checkEnvironment()	
print ("ENVIRONMENT = %s") % ENVIRONMENT
# time.sleep(15)





def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)

def getUserData():
	TOKEN_URL="%s/auth/token/" % (HOST);
	c = pycurl.Curl()
	c.setopt(pycurl.URL, TOKEN_URL)
	c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/x-www-form-urlencoded'])
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.POSTFIELDS, post)
	c.setopt(pycurl.WRITEFUNCTION, buf.write)
	c.setopt(pycurl.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	# c.setopt(pycurl.DEBUGFUNCTION, test)
	c.perform()
	
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()
obj=json.loads(buf.getvalue())	
TOKEN=obj["token"]

#def uploadData():
#	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID);
#	c = pycurl.Curl()
#	c.setopt(pycurl.URL, UPLOAD_URL)
#	c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/x-www-form-urlencoded'])
#	c.setopt(pycurl.POST, 1)
#	c.setopt(pycurl.POSTFIELDS, post)
#	c.setopt(pycurl.WRITEFUNCTION, buf.write)
#	c.setopt(pycurl.VERBOSE, True)
#	c.setopt(c.SSL_VERIFYPEER, 0)
#	c.setopt(pycurl.DEBUGFUNCTION, test)
#	c.setopt(c.HTTPPOST, [("document", (c.FORM_FILE, "%s%s" % (DIR, FILE))), ("catalog", (c.FORM_FILE, "%s" % (CATALOG_FILE))) ])
#	c.perform()	

	
	
	
FILES = os.listdir(DIR)
FILE = FILES[0]
print ("Start uploading to DR ...\n")
DOCUMENTCOUNTER=0

# ==================================================== Uploading a document ======================================================================


DOCUMENTCOUNTER=DOCUMENTCOUNTER+1
ORGANIZATION=obj["organization"]
ORGID=obj["org_id"]
CODE=obj["code"]
USER_ID=obj["user_id"]
S3_BUCKET=obj["s3_bucket"]
ROLES=obj["roles"]
TRACE_COLFAM=obj["trace_colFam"]
DOCUMENT_ID=uuid.uuid1()
PATIENT_ID=uuid.uuid1()
PATIENT_ID_AA="RANDOM_UUID"
PATIENT_FIRST_NAME=("F_%s" % (uuid.uuid1()));
PATIENT_MIDDLE_NAME="MiddleName";
PATIENT_LAST_NAME=("L_%s" % (uuid.uuid1()));
PATIENT_DOB="19670809";
PATIENT_GENDER="M";
ORGANIZATION="ORGANIZATION_VALUE";
PRACTICE_NAME="PRACTICE_NAME_VALUE";
FILE_LOCATION=("%s" % (FILE));
FILE_FORMAT_TEMP=FILE.split(".")
FILE_FORMAT=FILE_FORMAT_TEMP[1].upper()
DOCUMENT_TYPE="DOCUMENT_TYPE_VALUE";
CREATION_DATE="1967-05-11T10:00:47-07:00";
MODIFIED_DATE="1967-05-11T10:00:47-07:00";
DESCRIPTION=("%s" % (FILE));
METATAGS="METATAGS_VALUE";
SOURCE_SYSTEM="SOURCE_SYSTEM_VALUE";
TOKEN_URL="%s/auth/token/" % (HOST);
UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID);
CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
		
# ============================== Uploading Data =================================================================================================================

UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, DRBATCH)
bufu = io.BytesIO()
response = cStringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, UPLOAD_URL)
c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (pycurl.FORM_FILE, DIR+"/"+FILE)),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])
c.setopt(c.WRITEFUNCTION, bufu.write)
c.setopt(c.DEBUGFUNCTION, test)
c.perform()	
# ================================================================================================================================================================
obju=json.loads(bufu.getvalue())	
UUID=obju["uuid"]
print ("Document UUID: %s" % (UUID))

MANIFEST_FILE=MANIFEST_FILE+("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t02/22/14 02:02:37 AM\n") % (DOCUMENT_ID, SOURCE_SYSTEM, USERNAME, UUID, ORGANIZATION, ORGID, BATCH, FILE_FORMAT)

# ========================================================== Finish by closing batch ======================================================================================

print ("End uploading to DR ...\n")	
print ("Total number of documents uploaded: %s\n" % (DOCUMENTCOUNTER));

print ("Closing batch ...\n")
import cStringIO
import pycurl
CLOSE_URL="%s/receiver/batch/%s/status/flush?submit=true" % (HOST, DRBATCH);
bufc = io.BytesIO()
response = cStringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, CLOSE_URL)
c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
c.setopt(c.WRITEFUNCTION, bufc.write)
c.setopt(c.DEBUGFUNCTION, test)
c.perform()
objc=json.loads(bufc.getvalue())
# print (objc)
print ("Batch closed. Upload completed ...\n")
# ========================================================== Transmitting Manifest File ======================================================================================

# Currently this is only working on Staging
if ENVIRONMENT == "Staging":
	print ("Begin transmitting manifest file ...\n")

	import cStringIO
	import pycurl
	MANIFEST_URL="%s/receiver/batch/%s/manifest/%s/upload" % (HOST, DRBATCH, MANIFEST_FILENAME)
	bufm = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, MANIFEST_URL)
	c.setopt(c.CUSTOMREQUEST, "PUT")
	c.setopt(c.HTTPPOST, [("token", str(TOKEN)), ("file", (c.FORM_CONTENTS, str(MANIFEST_FILE)))])
	c.setopt(c.WRITEFUNCTION, bufm.write)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	# objm=json.loads(bufm.getvalue())
	# print (" ")
	print ("Finished transmitting manifest file ...\n")





SENDER="donotreply@apixio.com"
RECEIVERS="ishekhtman@apixio.com"
# RECEIVERS="eng@apixio.com"

print ("Begin writing report ...\n")

REPORT = """From: Apixio QA <QA@apixio.com>\n"""
# REPORT = REPORT + """To: Engineering <eng@apixio.com>\n"""
REPORT = REPORT + """To: Igor <ishekhtman@apixio.com>\n"""
REPORT = REPORT + """MIME-Version: 1.0\n"""
REPORT = REPORT + """Content-type: text/html\n"""
REPORT = REPORT + """Subject: %s %s Report %s - %s

<h1>Apixio %s %s QA Report</h1>
Date & Time: <b>%s</b><br>
Pipeline module: <b>%s</b><br>
Test type: <b>%s</b><br>
Enviromnent: <b>%s</b><br>
OrgID: <b>%s</b><br>
BatchID: <b>%s</b><br>
User name: <b>%s</b><br><br>
""" % (PIPELINE_MODULE, TEST_TYPE, ENVIRONMENT, CUR_TIME, PIPELINE_MODULE, TEST_TYPE, CUR_TIME, PIPELINE_MODULE, TEST_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)



# print (BATCH)
def printReportData(description):
	global REPORT, SUBHDR, PASSED
	REPORT = REPORT+SUBHDR % description
	REPORT = REPORT+PASSED
	REPORT = REPORT+"<br><br>"


ENVIRONMENT = checkEnvironment()
	
for i in range (0, 1):	
	printReportData("Bad Username")
	printReportData("Bad Password")
	printReportData("Bad Token")
	printReportData("Empty XML")
	printReportData("Malformed XML")
	


REPORT=REPORT+"<table><tr><td><br>End of %s - %s QA report<br><br></td></tr>" % (PIPELINE_MODULE, TEST_TYPE)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"
print ("End writing report ...\n")

print ("Begin sending report ...\n")
s=smtplib.SMTP()
s.connect("smtp.gmail.com",587)
s.starttls()
s.login("donotreply@apixio.com", "apx.mail47")
s.sendmail(SENDER, RECEIVERS, REPORT)	
print "Send report completed. Successfully sent email to %s ..." % (RECEIVERS)
