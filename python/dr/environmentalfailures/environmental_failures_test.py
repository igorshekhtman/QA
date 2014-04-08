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
TEST_TYPE="EnvironmentalFailures"
PASSED = "<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED = "<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR = "<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"
QUERY_DESC=""
COMPONENT_STATUS="PASSED"
REPORT = ""
RETURNCODE = ""

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())

UPLOAD_URL=""
STOP_URL=""
START_URL=""
TOKEN_URL=""
TOKEN=""
BATCH=""
DRBATCH=""
MANIFEST_FILENAME=""
MANIFEST_FILE=""
data=""
obj=""
obju=""
buf=""
bufu=""
UUID=""
FILES=""
FILES=""

SENDER="donotreply@apixio.com"
RECEIVERS="ishekhtman@apixio.com"
RECEIVERS_HTML="""To: Igor <ishekhtman@apixio.com>\n"""
# RECEIVERS="eng@apixio.com"
#
#================================ DONE ASSIGNING GLOBAL VARIABLES =======================================================================================
#

def checkEnvironment():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	global USERNAME, ORGID, PASSWORD, HOST, BATCHID, TOKEN_URL, UPLOAD_URL
	global BATCH, DRBATCH, MANIFEST_FILENAME, RECEIVERS, RECEIVERS_HTML
	global ENVIRONMENT
	if ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "P")):
		USERNAME="apxdemot0138"
		ORGID="10000279"
		PASSWORD="Hadoop.4522"
		HOST="https://dr.apixio.com:8443"
		ENVIRONMENT="Production"
	else:
		#USERNAME="apxdemot0182"
		#ORGID="190"
		USERNAME="apxdemot0240"
		ORGID="251"
		PASSWORD="Hadoop.4522"
		# main staging DR upload url
		#HOST="https://supload.apixio.com:8443"
		# alternative staging DR upload url
		HOST="https://supload2.apixio.com:8443"
		ENVIRONMENT="Staging"
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID)
	TOKEN_URL="%s/auth/token/" % (HOST)
	BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	MANIFEST_FILENAME=BATCH+"_manifest.txt"
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS_HTML="""To: Igor <%s>\n""" % str(sys.argv[2])
	else:
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS_HTML="""To: Igor <ishekhtman@apixio.com>\n"""
	
	print ("ENVIRONMENT = %s") % ENVIRONMENT
	print ("RECEIVERS = %s") % RECEIVERS
	print ("RECEIVERS_HTML = %s") % RECEIVERS_HTML
	# time.sleep(15)
	


#def test(debug_type, debug_msg):
#    print "debug(%d): %s" % (debug_type, debug_msg)
	
	
def test(debug_type, debug_msg):
	global RETURNCODE
	if debug_msg[ :4] == "HTTP" :
		RETURNCODE = debug_msg[9: ]
		print ("RETURN CODE: %s") % RETURNCODE		

		
def getUserData():
	global ENVIRONMENT, HOST, USERNAME, PASSWORD, TOKEN_URL, TOKEN, RETURNCODE
	global data, obj, buf, TEST_PN
	
	TOKEN_URL="%s/auth/token/" % (HOST);
	data = {'username':USERNAME, 'password':PASSWORD}
	post = urllib.urlencode(data)
	buf = io.BytesIO()
	
	c = pycurl.Curl()
	c.setopt(c.URL, TOKEN_URL)
	c.setopt(c.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/x-www-form-urlencoded'])
	c.setopt(c.POST, 1)
	c.setopt(c.POSTFIELDS, post)
	c.setopt(c.WRITEFUNCTION, buf.write)
	#c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	#c.setopt(c.DEBUGFUNCTION, test)
	c.perform()	
	

def storeToken():
	global obj, buf, TOKEN
	obj=json.loads(buf.getvalue())
	TOKEN=obj["token"]
			
def createTxtDocument():
	global TXT_FILE, TXT_FILE_NAME
	TXT_FILE = "Sample text used for %s %s" % (PIPELINE_MODULE, TEST_TYPE)
	TXT_FILE_NAME = "sample_text_file.txt"
			
def obtainStaticPatientInfo():
	global PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME
	global PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME
	PATIENT_ID=uuid.uuid1()
	PATIENT_ID_AA="RANDOM_UUID"
	PATIENT_FIRST_NAME=("FIRST_%s" % (uuid.uuid1()))
	print ("PATIENT FIRST NAME:  %s\n") % (PATIENT_FIRST_NAME)
	PATIENT_MIDDLE_NAME="MiddleName"
	PATIENT_LAST_NAME=("LAST_%s" % (uuid.uuid1()))
	print ("PATIENT LAST NAME:  %s\n") % (PATIENT_LAST_NAME)
	PATIENT_DOB="19670810"
	PATIENT_GENDER="M"
	ORGANIZATION="ORGANIZATION_VALUE"
	PRACTICE_NAME="PRACTICE_NAME_VALUE"		
			
			
def createCatalogFile():
	global CATALOG_FILE, FILE, FILES, TXT_FILE, TXT_FILE_NAME
	global DOCUMENT_ID, SOURCE_SYSTEM, ORGANIZATION, FILE_FORMAT
	global obj
	#FILES = os.listdir(DIR)
	#FILE = FILES[0]	
	ORGANIZATION=obj["organization"]
	ORGID=obj["org_id"]
	CODE=obj["code"]
	USER_ID=obj["user_id"]
	S3_BUCKET=obj["s3_bucket"]
	ROLES=obj["roles"]
	TRACE_COLFAM=obj["trace_colFam"]
	DOCUMENT_ID=uuid.uuid1()
	#PATIENT_ID=uuid.uuid1()
	#PATIENT_ID_AA="RANDOM_UUID"
	#PATIENT_FIRST_NAME=("FIRST_%s" % (uuid.uuid1()))
	#print ("PATIENT FIRST NAME:  %s\n") % (PATIENT_FIRST_NAME)
	#PATIENT_MIDDLE_NAME="MiddleName"
	#PATIENT_LAST_NAME=("LAST_%s" % (uuid.uuid1()))
	#print ("PATIENT LAST NAME:  %s\n") % (PATIENT_LAST_NAME)
	#PATIENT_DOB="19670810"
	#PATIENT_GENDER="M"
	#ORGANIZATION="ORGANIZATION_VALUE"
	#PRACTICE_NAME="PRACTICE_NAME_VALUE"
	#FILE_LOCATION=("%s" % (FILE))
	#FILE_FORMAT_TEMP=FILE.split(".")
	#FILE_FORMAT=FILE_FORMAT_TEMP[1].upper()
	FILE_LOCATION="c:/FileLocation"
	FILE_FORMAT="TXT"
	DOCUMENT_TYPE="DOCUMENT_TYPE_VALUE"
	CREATION_DATE="1967-05-11T10:00:47-07:00"
	MODIFIED_DATE="1967-05-11T10:00:47-07:00"
	#DESCRIPTION=("%s" % (FILE))
	DESCRIPTION=TXT_FILE_NAME
	METATAGS="METATAGS_VALUE"
	SOURCE_SYSTEM="SOURCE_SYSTEM_VALUE"
	TOKEN_URL="%s/auth/token/" % (HOST)
	CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))

	
		
def uploadDocument():
	global MANIFEST_FILE, ENVIRONMENT, TOKEN, RETURNCODE, UUID
	global CATALOG_FILE, FILE, FILES, TXT_FILE
	global obju, bufu, obj
	
	DOCUMENTCOUNTER=0
	
	print ("Start uploading to DR ...\n")
	
	DOCUMENTCOUNTER=DOCUMENTCOUNTER+1
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, DRBATCH)
	bufu = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, UPLOAD_URL)
	# upload document from a folder
	# c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (c.FORM_FILE, DIR+"/"+FILE)),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])	
	# upload document from a createTextDocument()
	c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (c.FORM_CONTENTS, str(TXT_FILE))),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])	
	c.setopt(c.WRITEFUNCTION, bufu.write)
	c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()	

	MANIFEST_FILE=MANIFEST_FILE+("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t02/22/14 02:02:37 AM\n") % (DOCUMENT_ID, SOURCE_SYSTEM, USERNAME, UUID, ORGANIZATION, ORGID, BATCH, FILE_FORMAT)
	print ("End uploading to DR ...\n")	
	print ("Total number of documents uploaded: %s\n" % (DOCUMENTCOUNTER))

def storeUUID():
	global obju, bufu, UUID
	obju=json.loads(bufu.getvalue())
	UUID=obju["uuid"]	
	print ("Document UUID: %s" % (UUID))
	

def closeBatch():	
	global ENVIRONMENT, RETURNCODE
	print ("Closing batch ...\n")
	CLOSE_URL="%s/receiver/batch/%s/status/flush?submit=true&operation=simple-pipeline" % (HOST, DRBATCH);
	bufc = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, CLOSE_URL)
	c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
	c.setopt(c.WRITEFUNCTION, bufc.write)
	#c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	#c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	objc=json.loads(bufc.getvalue())
	# print (objc)
	print ("Batch closed. Upload completed ...\n")
	

def transmitManifest():
	global ENVIRONMENT, RETURNCODE, MANIFEST_FILE
	
	print ("Begin transmitting manifest file ...\n")

	MANIFEST_URL="%s/receiver/batch/%s/manifest/%s/upload" % (HOST, DRBATCH, MANIFEST_FILENAME)
	bufm = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, MANIFEST_URL)
	c.setopt(c.CUSTOMREQUEST, "PUT")
	c.setopt(c.HTTPPOST, [("token", str(TOKEN)), ("file", (c.FORM_CONTENTS, str(MANIFEST_FILE)))])
	c.setopt(c.WRITEFUNCTION, bufm.write)
	#c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	#c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	print ("Finished transmitting manifest file ...\n")


def writeReportHeader():
	global REPORT, SUBHDR, PASSED, ENVIRONMENT, RETURNCODE

	print ("Begin writing report ...\n")
	REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	REPORT = REPORT + RECEIVERS_HTML
	REPORT = REPORT + """MIME-Version: 1.0\n"""
	REPORT = REPORT + """Content-type: text/html\n"""
	REPORT = REPORT + """Subject: %s %s Report %s - %s

	<h1>Apixio %s %s QA Report</h1>
	Date & Time: <b>%s</b><br>
	Pipeline module: <b>%s</b><br>
	Test type: <b>%s</b><br>
	Enviromnent: <b><font color='red'>%s</font></b><br>
	OrgID: <b>%s</b><br>
	BatchID: <b>%s</b><br>
	User name: <b>%s</b><br><br>
	""" % (PIPELINE_MODULE, TEST_TYPE, ENVIRONMENT, CUR_TIME, PIPELINE_MODULE, TEST_TYPE, CUR_TIME, PIPELINE_MODULE, TEST_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)
	

def writeReportDetails(description, code):
	global REPORT, ENVIRONMENT, RETURNCODE
	global SUBHDR, PASSED, FAILED, TEST_PN
	REPORT = REPORT+SUBHDR % description
	REPORT = REPORT+"<table><tr><td>EXPECTED CODE: <b>"+code+"</b></td></tr></table>"
	REPORT = REPORT+"<table><tr><td>RETURNED CODE: <b>"+RETURNCODE+"</b></td></tr></table>"
	if (RETURNCODE[ :3] == code):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"	
		
	
def writeReportFooter():
	global REPORT
	REPORT=REPORT+"<table><tr><td><br>End of %s - %s QA report<br><br></td></tr>" % (PIPELINE_MODULE, TEST_TYPE)
	REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"
	print ("End writing report ...\n")
	
def emailReport():
	global SENDER, RECEIVERS, REPORT, BATCH, RETURNCODE
	print ("Begin e-mailing report ...\n")
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")
	s.sendmail(SENDER, RECEIVERS, REPORT)	
	print ("E-mailing report completed ... Successfully sent email to %s ...\n") % (RECEIVERS)
	print ("Batch ID: %s\n") % BATCH
	
def stopDrService():
	print "Stopping Doc-Receiver Service ...\n"
	STOP_URL="%s/receiver/control/stopped" % (HOST);
	bufstp = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, STOP_URL)
	c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
	c.setopt(c.WRITEFUNCTION, bufstp.write)
	c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	print ("Doc-Receiver Service Stopped ...\n")
	
def startDrService():
	print "Starting Doc-Receiver Service ..."
	START_URL="%s/receiver/control/active" % (HOST);
	bufstr = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, START_URL)
	c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
	c.setopt(c.WRITEFUNCTION, bufstr.write)
	c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	print ("Doc-Receiver Service Started ...\n")

	
#============== Start of the main body =======================================================================================	

checkEnvironment()
writeReportHeader()

#======= CASE #1 ===========================================================================

TEST_DESCRIPTION = "Positive Test - valid credentials, valid document, valid catalog file"
EXPECTED_CODE = "200"
getUserData()
storeToken()
obtainStaticPatientInfo()
for i in range(0, 3):
	createTxtDocument()
	createCatalogFile()
	uploadDocument()
	storeUUID()
closeBatch()
if ENVIRONMENT == "Staging":
	transmitManifest()
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#==========================================================================================

# test_item valies: nodocument, nocatalog, nodocnocat, docandcat, emptydocument
writeReportFooter()
emailReport()