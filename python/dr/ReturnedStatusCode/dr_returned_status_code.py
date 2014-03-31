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
# RECEIVERS="eng@apixio.com"
#
#================================ DONE ASSIGNING GLOBAL VARIABLES =======================================================================================
#

def checkEnvironment():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	global USERNAME, ORGID, PASSWORD, HOST, BATCHID, TOKEN_URL, UPLOAD_URL
	global BATCH, DRBATCH, MANIFEST_FILENAME
	global ENVIRONMENT
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
	print ("ENVIRONMENT = %s") % ENVIRONMENT
	time.sleep(2)
	


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
	c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()	
	

def storeToken():
	global obj, buf, TOKEN
	obj=json.loads(buf.getvalue())
	TOKEN=obj["token"]
			

def createCatalogFile(type):
	# possible types: good, bad, empty
	global CATALOG_FILE, FILE, FILES
	global DOCUMENT_ID, SOURCE_SYSTEM, ORGANIZATION, FILE_FORMAT
	global obj
	FILES = os.listdir(DIR)
	FILE = FILES[0]	
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
	PATIENT_FIRST_NAME=("F_%s" % (uuid.uuid1()))
	PATIENT_MIDDLE_NAME="MiddleName"
	PATIENT_LAST_NAME=("L_%s" % (uuid.uuid1()))
	PATIENT_DOB="19670809"
	PATIENT_GENDER="M"
	ORGANIZATION="ORGANIZATION_VALUE"
	PRACTICE_NAME="PRACTICE_NAME_VALUE"
	FILE_LOCATION=("%s" % (FILE))
	FILE_FORMAT_TEMP=FILE.split(".")
	FILE_FORMAT=FILE_FORMAT_TEMP[1].upper()
	DOCUMENT_TYPE="DOCUMENT_TYPE_VALUE"
	CREATION_DATE="1967-05-11T10:00:47-07:00"
	MODIFIED_DATE="1967-05-11T10:00:47-07:00"
	DESCRIPTION=("%s" % (FILE))
	METATAGS="METATAGS_VALUE"
	SOURCE_SYSTEM="SOURCE_SYSTEM_VALUE"
	TOKEN_URL="%s/auth/token/" % (HOST)
	if type == "good":
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	elif type == "empty":
		CATALOG_FILE=""
	elif type == "nodocid":
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	elif type == "nopatientid":
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	elif type == "missingtags":		
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9<DocumentId>%s</DocumentId><Patient><PatientId><Id>%s<AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s<<SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>>>>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	elif type == "missingdocumentypetag":
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	elif type == "missingfileformatag":	
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	elif type == "nocatalogfile":
		CATALOG_FILE=None
	elif type == "nodocument":
		CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))

		
def uploadDocument(test_item):
	# test_item valies: nodocument, nocatalog, nodocandcat, docandcat, emptydocument
	global MANIFEST_FILE, ENVIRONMENT, TOKEN, RETURNCODE, UUID
	global CATALOG_FILE, FILE, FILES
	global obju, bufu, obj
	
	DOCUMENTCOUNTER=0
	
	print ("Start uploading to DR ...\n")
	
	DOCUMENTCOUNTER=DOCUMENTCOUNTER+1
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, DRBATCH)
	bufu = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, UPLOAD_URL)
	if test_item == "nodocument":
		c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])
	elif test_item == "nocatalog":
		c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (pycurl.FORM_FILE, DIR+"/"+FILE))])
	elif test_item == "nodocnocat":
		c.setopt(c.HTTPPOST, [("token", str(TOKEN))])	
	elif test_item == "emptydocument":
		c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (pycurl.FORM_CONTENTS, str(""))),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])
	else:
		c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (pycurl.FORM_FILE, DIR+"/"+FILE)),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])
		
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
	CLOSE_URL="%s/receiver/batch/%s/status/flush?submit=true" % (HOST, DRBATCH);
	bufc = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, CLOSE_URL)
	c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
	c.setopt(c.WRITEFUNCTION, bufc.write)
	c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	objc=json.loads(bufc.getvalue())
	# print (objc)
	print ("Batch closed. Upload completed ...\n")
	

def transmitManifest():
	global ENVIRONMENT, RETURNCODE
	
	print ("Begin transmitting manifest file ...\n")

	MANIFEST_URL="%s/receiver/batch/%s/manifest/%s/upload" % (HOST, DRBATCH, MANIFEST_FILENAME)
	bufm = io.BytesIO()
	response = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, MANIFEST_URL)
	c.setopt(c.CUSTOMREQUEST, "PUT")
	c.setopt(c.HTTPPOST, [("token", str(TOKEN)), ("file", (c.FORM_CONTENTS, str(MANIFEST_FILE)))])
	c.setopt(c.WRITEFUNCTION, bufm.write)
	c.setopt(c.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	c.setopt(c.DEBUGFUNCTION, test)
	c.perform()
	print ("Finished transmitting manifest file ...\n")


def writeReportHeader():
	global REPORT, SUBHDR, PASSED, ENVIRONMENT, RETURNCODE

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
	Enviromnent: <b><font color='red'>%s</font></b><br>
	OrgID: <b>%s</b><br>
	BatchID: <b>%s</b><br>
	User name: <b>%s</b><br><br>
	""" % (PIPELINE_MODULE, TEST_TYPE, ENVIRONMENT, CUR_TIME, PIPELINE_MODULE, TEST_TYPE, CUR_TIME, PIPELINE_MODULE, TEST_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)
	

def writeReportDetails(description, code):
	global REPORT, ENVIRONMENT, RETURNCODE
	global SUBHDR, PASSED, FAILED, TEST_PN
	REPORT = REPORT+SUBHDR % description
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

	
#============== Start of the main body =======================================================================================	

checkEnvironment()
writeReportHeader()

#======= CASE #1 ===========================================================================

TEST_DESCRIPTION = "Positive Test - valid credentials, valid document, valid catalog file"
EXPECTED_CODE = "200"
getUserData()
storeToken()
createCatalogFile("good")
uploadDocument("docandcat")
storeUUID()
closeBatch()
if ENVIRONMENT == "Staging":
	transmitManifest()
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#======== CASE #2 ==========================================================================

TEST_DESCRIPTION = "Negative Test - Bad Username"
EXPECTED_CODE = "401"
SAVED_USERNAME = USERNAME
USERNAME = USERNAME[4: ]+"-BAD"
getUserData()
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)
USERNAME = SAVED_USERNAME

#========= CASE #3 =========================================================================

TEST_DESCRIPTION = "Negative Test - Bad Password"
EXPECTED_CODE = "401"
SAVED_PASSWORD = PASSWORD
PASSWORD = PASSWORD[4: ]+"-BAD"
getUserData()
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)
PASSWORD = SAVED_PASSWORD

#========= CASE #4 ========================================================================

TEST_DESCRIPTION = "Negative Test - Bad Token"
EXPECTED_CODE = "401"
SAVED_TOKEN = TOKEN
TOKEN = TOKEN[4: ]+"-BAD"
createCatalogFile("good")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)
TOKEN = SAVED_TOKEN

#========= CASE #5 ========================================================================

TEST_DESCRIPTION = "Negative Test - Empty Catalog File"
EXPECTED_CODE = "500"
createCatalogFile("empty")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #6 ========================================================================

TEST_DESCRIPTION = "Negative Test - Catalog File missing DocID tag"
EXPECTED_CODE = "200"
createCatalogFile("nodocid")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #7 ========================================================================

TEST_DESCRIPTION = "Negative Test - Catalog File missing PatientID tag"
EXPECTED_CODE = "200"
createCatalogFile("nopatientid")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #8 ========================================================================

TEST_DESCRIPTION = "Negative Test - Corrupted Catalog File - missing random tags"
EXPECTED_CODE = "400"
createCatalogFile("missingtags")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #9 ========================================================================

TEST_DESCRIPTION = "Negative Test - Catalog File - missing document type tag"
EXPECTED_CODE = "200"
createCatalogFile("missingdocumentypetag")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #10 =======================================================================

TEST_DESCRIPTION = "Negative Test - Catalog File - missing file format tag"
EXPECTED_CODE = "400"
createCatalogFile("missingfileformatag")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #11 =======================================================================

TEST_DESCRIPTION = "Negative Test - Missing Catalog File"
EXPECTED_CODE = "400"
createCatalogFile("good")
uploadDocument("nocatalog")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #12 =======================================================================

TEST_DESCRIPTION = "Negative Test - Missing Document"
EXPECTED_CODE = "400"
createCatalogFile("good")
uploadDocument("nodocument")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #13 =======================================================================

TEST_DESCRIPTION = "Negative Test - Missing both Document and Catalog"
EXPECTED_CODE = "400"
createCatalogFile("good")
uploadDocument("nodocnocat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #14 =======================================================================

TEST_DESCRIPTION = "Negative Test - Empty Catalog but good Document"
EXPECTED_CODE = "400"
createCatalogFile("empty")
uploadDocument("docandcat")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #15 =======================================================================

TEST_DESCRIPTION = "Negative Test - Empty Document but good Catalog"
EXPECTED_CODE = "200"
createCatalogFile("good")
uploadDocument("emptydocument")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#========= CASE #16 =======================================================================

TEST_DESCRIPTION = "Negative Test - Empty Catalog File and Document"
EXPECTED_CODE = "400"
createCatalogFile("empty")
uploadDocument("emptydocument")
writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE)

#==========================================================================================

# test_item valies: nodocument, nocatalog, nodocnocat, docandcat, emptydocument
writeReportFooter()
emailReport()