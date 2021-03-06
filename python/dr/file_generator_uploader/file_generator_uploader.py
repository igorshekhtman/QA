import pyhs2
import os
import subprocess
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
# Send report emails and archive report html file
DEBUG_MODE=bool(1)
# specific number of documents to push to Doc-Receiver
NUMBER_OF_DOCS_TO_UPLOAD = 100
# size of each uploaded document in Kb
DOCUMENT_SIZE = 10
# number of active threads pushing documents to DR
NUMBER_OF_ACTIVE_THREADS = 5
# time limit in seconds for how long to keep uploading data
UPLOAD_TIME_LIMIT = 1
# count of how many documents were actually pushed to DR
DOCUMENTCOUNTER = 0
EXPECTED_CODE = "200"
LOGDATA = ""
RTDATA = ""


DIR="/mnt/testdata/DR/returnedstatuscode/Documents"
PIPELINE_MODULE="DR"
TEST_TYPE="LoadTesting"
PASSED = "<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED = "<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR = "<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"
QUERY_DESC=""
COMPONENT_STATUS="PASSED"
REPORT = ""
RETURNCODE = "200"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
YEAR=strftime("%Y", gmtime())
MONTH_FMN=strftime("%B", gmtime())

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
#================================ DOC-RECEIVER LOAD TESTING COMPONENTS =========================================================================
#

def checkEnvironment():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - username
	# Arg3 - orgID
	# Arg4 - # of documents to upload
	
	global USERNAME, ORGID, PASSWORD, HOST, BATCHID, TOKEN_URL, UPLOAD_URL
	global BATCH, DRBATCH, MANIFEST_FILENAME, RECEIVERS, RECEIVERS_HTML
	global ENVIRONMENT, NUMBER_OF_DOCS_TO_UPLOAD, THREAD_NUMBER, LOGDATA
	if ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "P")):
		USERNAME=str(sys.argv[2])
		ORGID=str(sys.argv[3])
		PASSWORD="Hadoop.4522"
		HOST="https://dr.apixio.com:8443"
		ENVIRONMENT="Production"
	else:
		#USERNAME="apxdemot0182"
		#ORGID="190"
		USERNAME=str(sys.argv[2])
		ORGID=str(sys.argv[3])
		PASSWORD="Hadoop.4522"
		# main staging DR upload url
		# HOST="https://testdr.apixio.com:8443"
		# alternative staging DR upload url
		HOST="https://stagedr.apixio.com:8443"
		ENVIRONMENT="Staging"
	NUMBER_OF_DOCS_TO_UPLOAD = int(sys.argv[4])
	#THREAD_NUMBER = int(sys.argv[5])
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID)
	TOKEN_URL="%s/auth/token/" % (HOST)
	BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	MANIFEST_FILENAME=BATCH+"_manifest.txt"
	
	#if (len(sys.argv) > 2):
	#	RECEIVERS=str(sys.argv[2])
	#	RECEIVERS_HTML="""To: Igor <%s>\n""" % str(sys.argv[2])
	#else:
	#	RECEIVERS="ishekhtman@apixio.com"
	#	RECEIVERS_HTML="""To: Igor <ishekhtman@apixio.com>\n"""
	
	print ("ENVIRONMENT = %s") % ENVIRONMENT
	#print ("RECEIVERS = %s") % RECEIVERS
	#print ("RECEIVERS_HTML = %s") % RECEIVERS_HTML
	print ("NUMBER_OF_DOCS_TO_UPLOAD = %s") % NUMBER_OF_DOCS_TO_UPLOAD
	#time.sleep(15)
	


#def test(debug_type, debug_msg):
#    print "debug(%d): %s" % (debug_type, debug_msg)
	
	
def test(debug_type, debug_msg):
	global LOGDATA, RETURNCODE
	if debug_msg[ :4] == "HTTP" :
		RETURNCODE = debug_msg[9: ]
		#LOGDATA = LOGDATA + str(RETURNCODE)
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
			
def createTxtDocument(doc_number):
	global TXT_FILE, TXT_FILE_NAME
	TXT_FILE = ""
	print ("Creating document ...\n")
	for i in range(0, 1000):
		TXT_FILE = TXT_FILE + "Sample text used for %s %s\n\nDocument number: %s\n\nLine number: %s\n\n" % (PIPELINE_MODULE, TEST_TYPE, doc_number, i)
	TXT_FILE_NAME = "sample_text_file%s.txt" % doc_number
	print ("Done creating document ...\n")
			
def obtainStaticPatientInfo(fname, lname):
	global PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME
	global PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME
	print ("Start obtaining static patient info ...\n")
	PATIENT_ID=uuid.uuid1()
	PATIENT_ID_AA="RANDOM_UUID"
	PATIENT_FIRST_NAME=("%s_%s" % (fname, uuid.uuid1()))
	print ("PATIENT FIRST NAME:  %s\n") % (PATIENT_FIRST_NAME)
	PATIENT_MIDDLE_NAME="MiddleName"
	PATIENT_LAST_NAME=("%s_%s" % (lname, uuid.uuid1()))
	print ("PATIENT LAST NAME:  %s\n") % (PATIENT_LAST_NAME)
	PATIENT_DOB="19670810"
	PATIENT_GENDER="M"
	ORGANIZATION="ORGANIZATION_VALUE"
	PRACTICE_NAME="PRACTICE_NAME_VALUE"		
	print ("Finished obtaining static patient info ...\n")
			
			
def createCatalogFile():
	global CATALOG_FILE, FILE, FILES, TXT_FILE, TXT_FILE_NAME
	global DOCUMENT_ID, SOURCE_SYSTEM, ORGANIZATION, FILE_FORMAT
	global obj
	print ("Start creating catalog file ...\n")
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
	FILE_LOCATION="c:/FileLocation"
	FILE_FORMAT="TXT"
	DOCUMENT_TYPE="DOCUMENT_TYPE_VALUE"
	CREATION_DATE="%s-%s-%sT10:00:47-07:00" % (YEAR, MONTH, DAY)
	MODIFIED_DATE="%s-%s-%sT10:00:47-07:00" % (YEAR, MONTH, DAY)
	#DESCRIPTION=("%s" % (FILE))
	DESCRIPTION=TXT_FILE_NAME
	METATAGS="METATAGS_VALUE"
	SOURCE_SYSTEM="SOURCE_SYSTEM_VALUE"
	TOKEN_URL="%s/auth/token/" % (HOST)
	CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
	print ("Ended creating catalog file ...\n")

	
		
def uploadDocument():
	global MANIFEST_FILE, ENVIRONMENT, TOKEN, RETURNCODE, UUID
	global CATALOG_FILE, FILE, FILES, TXT_FILE, DOCUMENTCOUNTER
	global obju, bufu, obj
	
	print ("Start uploading to DR ...\n")
	
	DOCUMENTCOUNTER=DOCUMENTCOUNTER+1
	UPLOAD_URL="%s/receiver/batch/%s/document/upload?operation=simple-pipeline" % (HOST, DRBATCH)
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

	MANIFEST_FILE = MANIFEST_FILE+("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t02/22/14 02:02:37 AM\n") % (DOCUMENT_ID, SOURCE_SYSTEM, USERNAME, UUID, ORGANIZATION, ORGID, BATCH, FILE_FORMAT)
	print ("End uploading to DR ...\n")	
	print ("Total number of documents uploaded: %s\n" % (DOCUMENTCOUNTER))

def storeUUID():
	global obju, bufu, UUID, LOGDATA
	obju=json.loads(bufu.getvalue())
	UUID=obju["uuid"]
	LOGDATA = LOGDATA + str(UUID) + "\n"
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
	

def writeReportDetails(description, code, number):
	global REPORT, ENVIRONMENT, RETURNCODE
	global SUBHDR, PASSED, FAILED, TEST_PN
	#REPORT = REPORT+SUBHDR % description
	#REPORT = REPORT+"<table><tr><td>EXPECTED CODE: <b>"+code+"</b></td></tr></table>"
	#REPORT = REPORT+"<table><tr><td>RETURNED CODE: <b>"+RETURNCODE+"</b></td></tr></table>"
	#REPORT = REPORT+"<table><tr><td>NUMBER OF DOCUMENTS PUSHED TO DR: <b>"+str(number)+"</b></td></tr></table>"
	#if (RETURNCODE[ :3] == code):
	#	REPORT = REPORT+PASSED
	#else:
	#	REPORT = REPORT+FAILED
	#REPORT = REPORT+"<br><br>"	
		
	
def writeReportFooter():
	global REPORT
	REPORT=REPORT+"<table><tr><td><br>End of %s - %s QA report<br><br></td></tr>" % (PIPELINE_MODULE, TEST_TYPE)
	REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"
	print ("End writing report ...\n")
	print ("PATIENT FIRST NAME:  %s\n") % (PATIENT_FIRST_NAME)
	print ("PATIENT LAST NAME:  %s\n") % (PATIENT_LAST_NAME)
	
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
	
def connectToHive():
	global cur, conn
	print ("Connecing to Hive ...\n")
	conn = pyhs2.connect(host='10.196.47.205', \
		port=10000, authMechanism="PLAIN", \
		user='hive', password='', \
		database='default')
	cur = conn.cursor()
	print ("Connection to Hive established ...\n")


def setHiveParameters():
	global cur, conn
	print ("Assigning Hive paramaters ...\n")
	# cur.execute("""SET mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.dynamic.partition=true""")
	cur.execute("""set hive.exec.dynamic.partition.mode=nonstrict""")
	cur.execute("""set mapred.reduce.tasks=16""")
	cur.execute("""set mapred.job.queue.name=default""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	print ("Completed assigning Hive paramaters ...\n")

def closeHiveConnection():
	global cur, conn
	print ("Closing Hive connection ... \n")
	cur.close()
	conn.close()	
	print ("Connection to Hive is now closed ... \n")

	
def runHiveQueries ():
	global REPORT, cur, conn, DAY, MONTH, BATCH
	global udb, udsm, udpm, udum, udem, udfb, udfm, udsb, udsm, udhm, udcb, udcm, udhm, udam, udsm1
	global aab, aam
	global sfdb, sfab, sfam
	global spb, spm
	print ("Running %s Hive queries ... \n") % (PIPELINE_MODULE)	
	if PIPELINE_MODULE == "DR":
		hive_table = ENVIRONMENT.lower()+"_logs_docreceiver_24"
		print ("Starting query 1 ...\n")
		REPORT = REPORT+SUBHDR % ("Upload Performance Test")
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, \
			get_json_object(line, '$.upload.document.status') as status, \
			sum (get_json_object(line, '$.upload.document.bytes')) as udb, \
			sum (get_json_object(line, '$.upload.document.save.millis')) as udsm, \
			sum (get_json_object(line, '$.upload.document.package.millis')) as udpm, \
			sum (get_json_object(line, '$.upload.document.upstream.millis')) as udum, \
			sum (get_json_object(line, '$.upload.document.encrypt.millis')) as udem, \
			sum (get_json_object(line, '$.upload.document.file.bytes')) as udfb, \
			sum (get_json_object(line, '$.upload.document.file.millis')) as udfm, \
			sum (get_json_object(line, '$.upload.document.serialize.bytes')) as udsb, \
			sum (get_json_object(line, '$.upload.document.serialize.millis')) as udsm1, \
			sum (get_json_object(line, '$.upload.document.hash.millis')) as udhm, \
			sum (get_json_object(line, '$.upload.document.catalog.bytes')) as udcb, \
			sum (get_json_object(line, '$.upload.document.catalog.millis')) as udcm, \
			sum (get_json_object(line, '$.upload.document.http.millis')) as udhm1, \
			sum (get_json_object(line, '$.upload.document.archive.millis')) as udam, \
			sum (get_json_object(line, '$.upload.document.seqfile.millis')) as udsm2, \
			
			stddev (cast(get_json_object(line, '$.upload.document.save.millis') as int)) as dudsm, \
			stddev (cast(get_json_object(line, '$.upload.document.package.millis') as int)) as dudpm, \
			stddev (cast(get_json_object(line, '$.upload.document.upstream.millis') as int)) as dudum, \
			stddev (cast(get_json_object(line, '$.upload.document.encrypt.millis') as int)) as dudem, \
			stddev (cast(get_json_object(line, '$.upload.document.file.millis') as int)) as dudfm, \
			stddev (cast(get_json_object(line, '$.upload.document.serialize.millis') as int)) as dudsm1, \
			stddev (cast(get_json_object(line, '$.upload.document.hash.millis') as int)) as dudhm, \
			stddev (cast(get_json_object(line, '$.upload.document.catalog.millis') as int)) as dudcm, \
			stddev (cast(get_json_object(line, '$.upload.document.http.millis') as int)) as dudhm1, \
			stddev (cast(get_json_object(line, '$.upload.document.archive.millis') as int)) as dudam, \
			stddev (cast(get_json_object(line, '$.upload.document.seqfile.millis') as int)) as dudsm2 \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.upload.document.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.upload.document.status')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td># OF DOCS:</td><td>AV APO SIZE:</td><td>AV DOC SIZE:</td><td>AV DOC+CAT SIZE:</td><td>AV CATALOG SIZE:</td><td>STATUS:</td></tr>"
			REPORT = REPORT+"<tr><td><b>"+str(i[0])+"</b></td><td><b>"+str(int(i[2]/i[0]))+" (bytes)</b></td><td><b>"+str(int(i[7]/i[0]))+" (bytes)</b></td><td><b>"+str(int(i[9]/i[0]))+" (bytes)</b></td><td><b>"+str(int(i[12]/i[0]))+" (bytes)</b></td><td><b>"+str(i[1])+"</b></td></tr>"
			REPORT = REPORT+"</table>"
			REPORT = REPORT+"<br>"
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td></td><td><b>BYTES:</b></td><td></td><td><b>MILLIS:</b></td><td><b>STD DEVTN:</b></td><td><b>KB/SEC:</b></td><td><b>DOCS/SEC:</b></td></tr>"
			if (i[14]/1000 > 0):
				REPORT = REPORT+"<tr><td>upload document serialize APO bytes:</td><td><b>"+str(int(i[9]))+"</b></td><td>upload document http millis:</td><td><b>"+str(int(i[14]))+"</b></td><td><b>"+str(int(i[25]))+"</b></td><td><b>"+str(int((i[9]/1024)/(i[14]/1000)))+"</b></td><td><b>"+str(int((i[9]/(i[14]/1000))/(i[9]/i[0])))+"</b></td></tr>"
			if (i[11]/1000 > 0):
				REPORT = REPORT+"<tr><td> </td><td><b></b></td><td>upload document SHA-1 hash millis:</td><td><b>"+str(int(i[11]))+"</b></td><td><b>"+str(int(i[23]))+"</b></td><td><b>"+str(int((i[9]/1024)/(i[11]/1000)))+"</b></td><td><b>"+str(int((i[9]/(i[11]/1000))/(i[9]/i[0])))+"</b></td></tr>"
			if (i[4]/1000 > 0):
				REPORT = REPORT+"<tr><td> </td><td><b></b></td><td>upload document package millis:</td><td><b>"+str(int(i[4]))+"</b></td><td><b>"+str(int(i[18]))+"</b></td><td><b>"+str(int((i[9]/1024)/(i[4]/1000)))+"</b></td><td><b>"+str(int((i[9]/(i[4]/1000))/(i[9]/i[0])))+"</b></td></tr>"
			if (i[10]/1000 > 0):
				REPORT = REPORT+"<tr><td>upload document bytes:</td><td><b>"+str(int(i[2]))+"</b></td><td>upload document serialize millis: </td><td><b>"+str(int(i[10]))+"</b></td><td><b>"+str(int(i[22]))+"</b></td><td><b>"+str(int((i[9]/1024)/(i[10]/1000)))+"</b></td><td><b>"+str(int((i[9]/(i[10]/1000))/(i[9]/i[0])))+"</b></td></tr>"
			if (i[6]/1000 > 0):
				REPORT = REPORT+"<tr><td> </td><td><b></b></td><td>upload document encrypt millis:</td><td><b>"+str(int(i[6]))+"</b></td><td><b>"+str(int(i[20]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[6]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[6]/1000))/(i[2]/i[0])))+"</b></td></tr>"
			if (i[3]/1000 > 0):
				REPORT = REPORT+"<tr><td></td><td></td><td>upload document save tmp millis:</td><td><b>"+str(int(i[3]))+"</b></td><td><b>"+str(int(i[17]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[3]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[3]/1000))/(i[2]/i[0])))+"</b></td></tr>"
			if (i[15]/1000 > 0):
				REPORT = REPORT+"<tr><td> </td><td><b></b></td><td>upload document archive to S3 millis:</td><td><b>"+str(int(i[15]))+"</b></td><td><b>"+str(int(i[26]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[15]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[15]/1000))/(i[2]/i[0])))+"</b></td></tr>"
			if (i[16]/1000 > 0):
				REPORT = REPORT+"<tr><td> </td><td><b></b></td><td>upload document add to seqfile millis:</td><td><b>"+str(int(i[16]))+"</b></td><td><b>"+str(int(i[27]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[16]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[16]/1000))/(i[2]/i[0])))+"</b></td></tr>"
			#if (i[5]/1000 > 0):	
			#	REPORT = REPORT+"<tr><td> </td><td><b></b></td><td>upload document upstream millis: </td><td><b>"+str(int(i[5]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[5]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[5]/1000))/(i[2]/i[0])))+"</b></td></tr>"
			#if (i[8]/1000 > 0):
			#	REPORT = REPORT+"<tr><td>upload document file bytes: </td><td><b>"+str(int(i[7]))+"</b></td><td>upload document file millis: </td><td><b>"+str(int(i[8]))+"</b></td><td><b>"+str(int((i[7]/1024)/(i[8]/1000)))+"</b></td><td><b>"+str(int((i[7]/(i[8]/1000))/(i[7]/i[0])))+"</b></td></tr>"
			if (i[13]/1000 > 0):
				REPORT = REPORT+"<tr><td>upload document catalog bytes:</td><td><b>"+str(int(i[12]))+"</b></td><td>upload document catalog millis:</td><td><b>"+str(int(i[13]))+"</b></td><td><b>"+str(int(i[24]))+"</b></td><td><b>"+str(int((i[12]/1024)/(i[13]/1000)))+"</b></td><td><b>"+str(int((i[12]/(i[13]/1000))/(i[12]/i[0])))+"</b></td></tr>"
			REPORT = REPORT+"</table>"
			
		#print ("Finished running %s Hive queries ... \n") % (PIPELINE_MODULE)
		#if (RETURNCODE[ :3] == code):
		REPORT = REPORT+PASSED
		#else:
		#	REPORT = REPORT+FAILED
		REPORT = REPORT+"<br><br>"

		print ("Starting query 2 ...\n")
		REPORT = REPORT+SUBHDR % ("Archive to S3 Performance Test")
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived, \
			get_json_object(line, '$.archive.afs.status') as status, \
			sum (get_json_object(line, '$.archive.afs.bytes')) as aab, \
			sum (get_json_object(line, '$.archive.afs.millis')) as aam, \
			stddev (cast(get_json_object(line, '$.archive.afs.millis') as int)) as daam \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.archive.afs.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.archive.afs.status')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td># OF DOCS:</td><td>STATUS:</td><td>AV. DOC SIZE:</td></tr>"
			REPORT = REPORT+"<tr><td><b>"+str(i[0])+"</b></td><td><b>"+str(i[1])+"</b></td><td><b>"+str(int(i[2]/i[0]))+" (bytes)</b></td></tr>"
			REPORT = REPORT+"</table>"
			REPORT = REPORT+"<br>"
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td></td><td><b>BYTES:</b></td><td></td><td><b>MILLIS:</b></td><td><b>STD DEVTN:</b></td><td><b>KB/SEC:</b></td><td><b>DOCS/SEC:</b></td></tr>"			
			if (i[3]/1000 > 0):
				REPORT = REPORT+"<tr><td>archive afs bytes: </td><td><b>"+str(int(i[2]))+"</b></td><td>archive afs millis: </td><td><b>"+str(int(i[3]))+"</b></td><td><b>"+str(int(i[4]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[3]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[3]/1000))/(i[2]/i[0])))+"</b></td></tr>"
			REPORT = REPORT+"</table>"
			
		#print ("Finished running %s Hive queries ... \n") % (PIPELINE_MODULE)
		#if (RETURNCODE[ :3] == code):
		REPORT = REPORT+PASSED
		#else:
		#	REPORT = REPORT+FAILED
		REPORT = REPORT+"<br><br>"
		
		print ("Starting query 3 ...\n")
		REPORT = REPORT+SUBHDR % ("Sequence File Generation Performance Test")
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seqfile, \
			get_json_object(line, '$.seqfile.file.document.status') as status, \
			sum (get_json_object(line, '$.seqfile.file.document.bytes')) as sfdb, \
			sum (get_json_object(line, '$.seqfile.file.add.bytes')) as sfab, \
			sum (get_json_object(line, '$.seqfile.file.add.millis')) as sfam, \
			stddev (cast(get_json_object(line, '$.seqfile.file.add.millis') as int)) as dsfam \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.seqfile.file.document.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.seqfile.file.document.status')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td># OF DOCS:</td><td>STATUS:</td><td>AV. DOC SIZE:</td></tr>"
			REPORT = REPORT+"<tr><td><b>"+str(i[0])+"</b></td><td><b>"+str(i[1])+"</b></td><td><b>"+str(int(i[2]/i[0]))+" (bytes)</b></td></tr>"
			REPORT = REPORT+"</table>"
			REPORT = REPORT+"<br>"
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td></td><td><b>BYTES:</b></td><td></td><td><b>MILLIS:</b></td><td><b>STD DEVTN:</b></td><td><b>KB/SEC:</b></td><td><b>DOCS/SEC:</b></td></tr>"
			REPORT = REPORT+"<tr><td>seqfile file document bytes: </td><td><b>"+str(int(i[2]))+"</b></td><td> </td><td></td><td><b> </b></td><td></td><td></td></tr>"
			if (i[4]/1000 > 0):
				REPORT = REPORT+"<tr><td>seqfile file add bytes: </td><td><b>"+str(int(i[3]))+"</b></td><td>seqfile file add millis: </td><td><b>"+str(int(i[4]))+"</b></td><td><b>"+str(int(i[5]))+"</b></td><td><b>"+str(int((i[3]/1024)/(i[4]/1000)))+"</b></td><td><b>"+str(int((i[3]/(i[4]/1000))/(i[3]/i[0])))+"</b></td></tr>"
			REPORT = REPORT+"</table>"
			
		#print ("Finished running %s Hive queries ... \n") % (PIPELINE_MODULE)
		#if (RETURNCODE[ :3] == code):
		REPORT = REPORT+PASSED
		#else:
		#	REPORT = REPORT+FAILED
		REPORT = REPORT+"<br><br>"
		
		print ("Starting query 4 ...\n")
		REPORT = REPORT+SUBHDR % ("Sequence File Close - push to HDFS Performance Test")
		cur.execute("""SELECT get_json_object(line, '$.seqfile.directory.close.numfiles') as documents_closed, \
			get_json_object(line, '$.seqfile.directory.close.status') as status, \
			get_json_object(line, '$.seqfile.directory.close.millis') as sdcm \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.seqfile.directory.close.batchid') = '%s'""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td># OF DOCS:</td><td>STATUS:</td><td>AV. DOC SIZE:</td></tr>"
			#REPORT = REPORT+"<tr><td><b>"+str(i[0])+"</b></td><td><b>"+str(i[1])+"</b></td><td><b>"+str(int(i[2]/i[0]))+" (bytes)</b></td></tr>"
			REPORT = REPORT+"<tr><td><b>"+str(i[0])+"</b></td><td><b>"+str(i[1])+"</b></td><td><b>"+"N/A"+" (bytes)</b></td></tr>"
			REPORT = REPORT+"</table>"
			REPORT = REPORT+"<br>"
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td></td><td><b>BYTES:</b></td><td></td><td><b>MILLIS:</b></td><td><b>STD DEVTN:</b></td><td><b>KB/SEC:</b></td><td><b>DOCS/SEC:</b></td></tr>"
			REPORT = REPORT+"<tr><td>seqfile file close bytes: </td><td><b>"+"N/A"+"</b></td><td>seqfile file close millis: </td><td><b>"+str(int(i[2]))+"</b></td><td><b>"+"N/A"+"</b></td><td><b>"+"N/A"+"</b></td><td><b>"+"N/A"+"</b></td></tr>"
			#REPORT = REPORT+"<tr><td>seqfile file add bytes: </td><td><b>"+str(int(i[3]))+"</b></td><td>seqfile file add millis: </td><td><b>"+str(int(i[4]))+"</b></td><td><b>"+str(int(i[5]))+"</b></td><td><b>"+str(int((i[3]/1024)/(i[4]/1000)))+"</b></td><td><b>"+str(int((i[3]/(i[4]/1000))/(i[3]/i[0])))+"</b></td></tr>"
			REPORT = REPORT+"</table>"
			
		#print ("Finished running %s Hive queries ... \n") % (PIPELINE_MODULE)
		#if (RETURNCODE[ :3] == code):
		REPORT = REPORT+PASSED
		#else:
		#	REPORT = REPORT+FAILED
		REPORT = REPORT+"<br><br>"
				
		
		print ("Starting query 5 ...\n")
		REPORT = REPORT+SUBHDR % ("Submit to REDIS Performance Test")
		cur.execute("""SELECT get_json_object(line, '$.submit.post.apxfiles.count') as documents_submit_post, \
			get_json_object(line, '$.submit.post.status') as status, \
			sum (get_json_object(line, '$.submit.post.bytes')) as spb, \
			sum (get_json_object(line, '$.submit.post.millis')) as spm, \
			stddev (cast(get_json_object(line, '$.submit.post.millis') as int)) as dspm \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.submit.post.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.submit.post.status'), \
			get_json_object(line, '$.submit.post.apxfiles.count')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td># OF DOCS:</td><td>STATUS:</td><td>AV. DOC SIZE:</td></tr>"
			REPORT = REPORT+"<tr><td><b>"+str(i[0])+"</b></td><td><b>"+str(i[1])+"</b></td><td><b>"+str(int(int(i[2])/int(i[0])))+" (bytes)</b></td></tr>"
			REPORT = REPORT+"</table>"
			REPORT = REPORT+"<br>"
			REPORT = REPORT+"<table border='1' cellspacing='0' cellpadding='2'>"
			REPORT = REPORT+"<tr><td></td><td><b>BYTES:</b></td><td></td><td><b>MILLIS:</b></td><td><b>STD DEVTN:</b></td><td><b>KB/SEC:</b></td><td><b>DOCS/SEC:</b></td></tr>"
			if (i[3]/1000 > 0):
				REPORT = REPORT+"<tr><td>submit post bytes: </td><td><b>"+str(int(i[2]))+"</b></td><td>submit post millis: </td><td><b>"+str(int(i[3]))+"</b></td><td><b>"+str(int(i[4]))+"</b></td><td><b>"+str(int((i[2]/1024)/(i[3]/1000)))+"</b></td><td><b>"+str(int((i[2]/(i[3]/1000))/(i[2]/int(i[0]))))+"</b></td></tr>"
			REPORT = REPORT+"</table>"
			
		#print ("Finished running %s Hive queries ... \n") % (PIPELINE_MODULE)
		#if (RETURNCODE[ :3] == code):
		REPORT = REPORT+PASSED
		#else:
		#	REPORT = REPORT+FAILED
		REPORT = REPORT+"<br><br>"
		

# ============================= ARCHIVE REPORT TO A FILE ============================================================================

# /usr/lib/apx-reporting/html/assets/reports/production/pipeline/2014/3


def archiveReport():
	global ENVIRONMENT, REPORT, PIPELINE_MODULE, MONTH_FMN
	print ("Archiving report ...\n")
	BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT.lower()+"/"+PIPELINE_MODULE.lower()+"/"+str(YEAR)+"/"+str(MONTH)
	REPORTFOLDER="/usr/lib/apx-reporting/html/assets/reports/"+ENVIRONMENT.lower()+"/"+PIPELINE_MODULE.lower()+"/"+str(YEAR)+"/"+str(MONTH)
	# ------------- Create new folder if one does not exist already -------------------------------
	if not os.path.exists(BACKUPREPORTFOLDER):
		os.makedirs(BACKUPREPORTFOLDER)
		os.chmod(BACKUPREPORTFOLDER, 0777)	
	if not os.path.exists(REPORTFOLDER):
		os.makedirs(REPORTFOLDER)
		os.chmod(REPORTFOLDER, 0777)
	# ---------------------------------------------------------------------------------------------
	REPORTFILENAME=str(DAY)+".html"
	REPORTXTSTRING="DR Performance Report ("+ENVIRONMENT.lower()+") - "+str(MONTH_FMN)+" "+str(DAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT.lower()+"/"+PIPELINE_MODULE.lower()+"/"+str(YEAR)+"/"+str(MONTH)+"/"+REPORTFILENAME+"\n"
	REPORTXTFILENAME=PIPELINE_MODULE.lower()+"_reports.txt"
	REPORTXTFILEFOLDER="/usr/lib/apx-reporting/html/assets"
	# print (REPORTFOLDER)
	# print (REPORTFILENAME)
	# print (REPORTXTSTRING)
	# print (REPORTXTFILENAME)
	# print (REPORTXTFILEFOLDER)
	os.chdir(BACKUPREPORTFOLDER)
	REPORTFILE = open(REPORTFILENAME, 'w')
	REPORTFILE.write(REPORT)
	REPORTFILE.close()
	os.chdir(REPORTFOLDER)
	REPORTFILE = open(REPORTFILENAME, 'w')
	REPORTFILE.write(REPORT)
	REPORTFILE.close()
	os.chdir(REPORTXTFILEFOLDER)
	REPORTFILETXT = open(REPORTXTFILENAME, 'a')
	REPORTFILETXT.write(REPORTXTSTRING)
	REPORTFILETXT.close()
	os.chdir("/mnt/automation/dr/performancetesting")
	print ("Completed archiving report %s in folder %s ...\n") % (REPORTFILENAME, REPORTFOLDER)

# ===================================================================================================================================

def archiveLogs():
	global LOGFILENAME, LOGDATA, LOGFILEFOLDER, BATCHID, THREAD_NUMBER
	global RTFILENAME, RTDATA, RTFILEFOLDER, UUID
	print ("Archiving logfile ...\n")
	milliseconds = datetime.datetime.now().strftime("%f")
	RTFILENAME = "failed_log_"+str(BATCHID)+"_"+str(milliseconds)+".txt"
	RTFILEFOLDER = "/mnt/automation/dr/file_generator_uploader/logs"
	LOGFILENAME = "uploader_log_"+str(BATCHID)+"_"+str(milliseconds)+".txt"
	LOGFILEFOLDER = "/mnt/automation/dr/file_generator_uploader/logs"
	os.chdir(LOGFILEFOLDER)
	LOGFILE = open(LOGFILENAME, 'w')
	LOGFILE.write(LOGDATA)
	LOGFILE.close()
	if RTDATA != "":
		os.chdir(RTFILEFOLDER)
		RTFILE = open(RTFILENAME, 'w')
		RTFILE.write(RTDATA)
		RTFILE.close()
	print ("Completed archiving logfile ...\n")

#====================================================================================================================================	
#===================== Start of the main body =======================================================================================
#====================================================================================================================================

checkEnvironment()
#writeReportHeader()
getUserData()
storeToken()
#used later as a prefix for First and Last name of the new patient
obtainStaticPatientInfo("DRStress", "Test")

for i in range(0, NUMBER_OF_DOCS_TO_UPLOAD):
	createTxtDocument(i)
	createCatalogFile()
	# print (RETURNCODE[:3])
	# time.sleep(25)
	# while (int(RETURNCODE[:3]) <> 200) or (int(RETURNCODE[:3]) <> 100):
	uploadDocument()
	LOGDATA = LOGDATA + str(RETURNCODE[:3]) + "\n"
	print (RETURNCODE[:3])
	# Retry uploading until Success or 200
	retry_limit = 50
	cntr = 0
	#while (RETURNCODE[:3] != "200") and (cntr < retry_limit):
	while (RETURNCODE[:3] != "200"):
		#cntr = cntr + 1
		#RTDATA = RTDATA + str(UUID) + "\n"
		#RTDATA = RTDATA + "failure code: "+ str(RETURNCODE[:3]) + "  number of re-tries: " + cntr + "\n"
		RTDATA = RTDATA + str(RETURNCODE[:3]) + "\n"
		uploadDocument()
		
	storeUUID()
	
closeBatch()
archiveLogs()
#if ENVIRONMENT.upper() == "STAGING":
#	transmitManifest()

#writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE, NUMBER_OF_DOCS_TO_UPLOAD)
#connectToHive()
#setHiveParameters()
# wait for PAUSE_LIMIT seconds
#PAUSE_LIMIT=20
#print ("Pausing for %s seconds for upload to DR to complete ...\n") % (PAUSE_LIMIT)
#time.sleep(PAUSE_LIMIT)
#writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE, NUMBER_OF_DOCS_TO_UPLOAD)
#runHiveQueries()
#closeHiveConnection()

# test_item valies: nodocument, nocatalog, nodocnocat, docandcat, emptydocument
#writeReportFooter()
#emailReport()
#archiveReport()