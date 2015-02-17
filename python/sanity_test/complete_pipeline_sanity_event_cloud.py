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
import mmap
import readline
import requests
import tabulate
import uuid
import cStringIO

#============================================================================================
#============================ MAIN FUNCTIONS ================================================
#============================================================================================

def initializeGlobalVars():
	global TEST_TYPE, YEAR, CURMONTH, MONTH_FMN, CURDAY, START_TIME, TIME_START
	global USERNAME, ORGID, PASSWORD, HOST, ENVIRONMENT, DIR, CUR_TIME, BATCHID
	global MONTH, DAY, UPLOAD_URL, TOKEN_URL, BATCH, DRBATCH, MANIFEST_FILENAME
	global DOCUMENTCOUNTER, NUMBEROFDOCUMENTS, DOCUMENTS_TRANSMITTED, DOCUMENTS_TO_OCR
	global DOCUMENTS_TO_PERSIST, MANIFEST_FILE, GLOBAL_STATUS, OPERATION, CATEGORY
	global QUERY_NUMBER, PROCESS_ALL_QUERIES, PASSED, FAILED, SUBHDR, QUERY_DESC
	global COMPONENT_STATUS, LOGTYPE, INDEXERLOGFILE, DOCRECEIVERLOGFILE
	global COORDINATORLOGFILE, PARSERLOGFILE, OCRLOGFILE, PERSISTLOGFILE, EVENTSLOGFILE
	global SENDER, RECEIVERS, EVENT_CLOUD_URL, observed_durations
	
	TEST_TYPE="PipelineSanityTest"
	YEAR=strftime("%Y", gmtime())
	CURMONTH=strftime("%m", gmtime())
	MONTH_FMN=strftime("%B", gmtime())
	CURDAY=strftime("%d", gmtime())
	START_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	TIME_START=time.time()
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	if ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "P")):
		# PRODUCTION ==================
		USERNAME="apxdemot0138"
		ORGID="10000279"
		PASSWORD="Hadoop.4522"
		HOST="https://dr.apixio.com"
		ENVIRONMENT="Production"
		EVENT_CLOUD_URL="http://54.177.153.168:8076/event/query"
	else:
		# STAGING =====================
		USERNAME="sanitytest1"
		ORGID="370"
		PASSWORD="Hadoop.4522"
		HOST="https://stagedr.apixio.com:8443"
		ENVIRONMENT="Staging"
		EVENT_CLOUD_URL="http://dashboard-development.apixio.net:8075/event/query"
	#==================================
	print ("ENVIRONMANT = %s") % ENVIRONMENT
	# time.sleep(15)
	DIR="/mnt/testdata/SanityTwentyDocuments/Documents"
	CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
	DAY=strftime("%d", gmtime())
	MONTH=strftime("%m", gmtime())
	DAY = "\"%s\"" % (CURDAY)
	if (CURDAY < 10):
		DAY = "\"0%s\"" % (CURDAY)
	MONTH = "\"%s\"" % (CURMONTH)
	if (CURMONTH < 10):
		MONTH = "\"0%s\"" % (CURMONTH)
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID)
	TOKEN_URL="%s/auth/token/" % (HOST)
	BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
	MANIFEST_FILENAME=BATCH+"_manifest.txt"
	DOCUMENTCOUNTER=0
	DOCUMENTCOUNTER = 0
	NUMBEROFDOCUMENTS=0
	DOCUMENTS_TRANSMITTED=13
	DOCUMENTS_TO_OCR=0
	DOCUMENTS_TO_PERSIST=0
	MANIFEST_FILE=""
	GLOBAL_STATUS="success"
	OPERATION=""
	CATEGORY=""
	observed_durations = {}
	#=============== debugging =========
	QUERY_NUMBER=18
	PROCESS_ALL_QUERIES=bool(1)
	#===================================
	PASSED="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
	FAILED="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
	SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"
	QUERY_DESC=""
	COMPONENT_STATUS="PASSED"
	LOGTYPE="24"
	INDEXERLOGFILE="indexer_manifest_epoch"
	DOCRECEIVERLOGFILE=ENVIRONMENT.lower()+"_logs_docreceiver_"+LOGTYPE
	COORDINATORLOGFILE=ENVIRONMENT.lower()+"_logs_coordinator_"+LOGTYPE
	PARSERLOGFILE=ENVIRONMENT.lower()+"_logs_parserjob_"+LOGTYPE
	OCRLOGFILE=ENVIRONMENT.lower()+"_logs_ocrjob_"+LOGTYPE
	PERSISTLOGFILE=ENVIRONMENT.lower()+"_logs_persistjob_"+LOGTYPE
	EVENTSLOGFILE=ENVIRONMENT.lower()+"_logs_eventJob_"+LOGTYPE
	# staging_logs_eventJob_24
	SENDER="donotreply@apixio.com"
	RECEIVERS="eng@apixio.com"
	
# =================================================================================================================

def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)
    
# =================================================================================================================    

def outputVarValues():
	print ("ORGID = %s") % ORGID
	print ("TEST_TYPE = %s") % TEST_TYPE
	print ("ENVIRONMANT = %s") % ENVIRONMENT
	print ("BATCHID = %s") % BATCHID
	print ("CUR_TIME = %s") % CUR_TIME
	print ("")
	print ("BATCH = %s") % BATCH
	print ("MANIFEST_FILENAME = %s") % MANIFEST_FILENAME
	print ("")
	print ("UPLOAD_URL = %s") % UPLOAD_URL
	print ("TOKEN_URL = %s") % TOKEN_URL
	print ("USERNAME = %s") % USERNAME
	print ("PASSWORD = %s") % PASSWORD
	print ("HOST = %s") % HOST
	print ("DIR = %s") % DIR
	# time.sleep(15)

# =================================================================================================================

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
	# c.setopt(pycurl.DEBUGFUNCTION, test)
	c.perform()

# =================================================================================================================

def obtainToken():	
	global TOKEN, post, buf, obj
	print ("Start obtaining user token ...")
	buf = io.BytesIO()
	data = {'username':USERNAME, 'password':PASSWORD}
	post = urllib.urlencode(data)
	getUserData()
	obj=json.loads(buf.getvalue())	
	TOKEN=obj["token"]
	# print (obj)
	print ("* TOKEN               = %s" % TOKEN)
	print ("End obtaining user token ...")

# =================================================================================================================

def uploadData():
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID);
	c = pycurl.Curl()
	c.setopt(pycurl.URL, UPLOAD_URL)
	c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/x-www-form-urlencoded'])
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.POSTFIELDS, post)
	c.setopt(pycurl.WRITEFUNCTION, buf.write)
	c.setopt(pycurl.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 0)
	c.setopt(pycurl.DEBUGFUNCTION, test)
	c.setopt(c.HTTPPOST, [("document", (c.FORM_FILE, "%s%s" % (DIR, FILE))), ("catalog", (c.FORM_FILE, "%s" % (CATALOG_FILE))) ])
	c.perform()	

#=========================================================== Assign Values =======================================================

def uploadFiles():
	global DOCUMENTCOUNTER, obj, MANIFEST_FILE
	
	FILES = os.listdir(DIR)
	print ("Uploading Files ...\n")
	for FILE in FILES:
		DOCUMENTCOUNTER += 1
		#DOCUMENTCOUNTER+1
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
		
		#============================== Uploading Data =====================================================================================

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
		# print (obju)
		print ("Document UUID: %s" % (UUID))

		MANIFEST_FILE = MANIFEST_FILE+("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t02/22/14 02:02:37 AM\n") % (DOCUMENT_ID, SOURCE_SYSTEM, USERNAME, UUID, ORGANIZATION, ORGID, BATCH, FILE_FORMAT)

	#========================================================== Finish by closing batch ======================================================================================

	print ("\nTOTAL NUMBER OF DOCUMENTS UPLOADED: %s\n" % (DOCUMENTCOUNTER));
	print ("Closing Batch ...\n")

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
	print ("Batch Closed, Upload Completed ...\n")
	
	#========================================================== Transmitting Manifest File ======================================================================================

	# Currently this is only working on Staging
	if ENVIRONMENT == "Staging":
		print ("Transmitting Manifest File ...\n")

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
		print ("Manifest file transmitted ...\n")

#=========================================================================================

def pauseForUploadToComplete():
	PAUSE_LIMIT = 300
	#Increased for the time being of cluster being 100% occupied ... 10-13-14 Igor
	#PAUSE_LIMIT = 600
	# wait for PAUSE_LIMIT seconds
	print ("Pausing for %s seconds for all jobs to complete ...\n") % (PAUSE_LIMIT)
	time.sleep(PAUSE_LIMIT)

#=========================================================================================

def obtainOperationAndCategory():
	global REPORT
	print ("Obtaining operation and category ...\n")
	cur.execute("""SELECT get_json_object(line, '$.submit.post.operation') as operation, \
		get_json_object(line, '$.submit.post.category') as category \
		FROM %s \
		WHERE \
		get_json_object(line, '$.submit.post.batchid') = '%s'""" %(DOCRECEIVERLOGFILE, BATCH))
	ROW = 0	
	for i in cur.fetch():
		ROW += 1
		print i
		REPORT = REPORT+"Operation: <b>"+str(i[0])+"</b><BR>"
		REPORT = REPORT+"Category: <b>"+str(i[1])+"</b><BR><BR>"
	print ("Finished obtaining operation and category ...\n")	

#=========================================================================================

def generateReportHeader():
	global REPORT
	
	REPORT = """From: Apixio QA <QA@apixio.com>
	To: Engineering <eng@apixio.com>
	MIME-Version: 1.0
	Content-type: text/html
	Subject: Pipeline QA Report %s batchID %s - %s

	<h1>Apixio Pipeline QA Report</h1>
	Date & Time: <b>%s</b><br>
	Test type: <b>%s</b><br>
	Enviromnent: <b><font color='red'>%s</font></b><br>
	OrgID: <b>%s</b><br>
	BatchID: <b>%s</b><br>
	User name: <b>%s</b><br>
	""" % (ENVIRONMENT, BATCH, CUR_TIME, CUR_TIME, TEST_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)
	
	#obtainOperationAndCategory()
	
#=========================================================================================

def connectToHive():
	global conn, cur
	print ("Establishing Hive connection ...\n")
	conn = pyhs2.connect(host='54.149.166.25',
                   port=10000,
                   authMechanism="PLAIN",
                   user='hive',
                   password='',
                   database='default')

	cur = conn.cursor()
	print ("Assigning queue name to hive ...\n")
	cur.execute("""SET mapred.job.queue.name=hive""")

#=========================================================================================	

def labelPassOrFail(component_status):
	global REPORT, GLOBAL_STATUS
		
	if (component_status.upper() == "PASSED"):
		REPORT = REPORT+PASSED
		GLOBAL_STATUS="success"
	else:
		REPORT = REPORT+FAILED
		COMPONENT_STATUS="PASSED"
		GLOBAL_STATUS="failed"
	REPORT = REPORT+"<br><br>"

#=========================================================================================	
	
def queryIndexer():
	global REPORT
	
	query_status = "passed"
	component_status = "passed"
	
	REPORT = REPORT+SUBHDR % "INDEXER"

	if (QUERY_NUMBER == 1) or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of documents transmitted"
		print ("Running INDEXER query #1 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT apixiouuid) as total_number_of_documents_indexer \
			FROM %s \
			WHERE \
			batchid = '%s'""" %(INDEXERLOGFILE, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTCOUNTER:
			print ("QUERY 1 FAILED")
			component_status="FAILED"


	if (QUERY_NUMBER == 2) or PROCESS_ALL_QUERIES:
		QUERY_DESC="Document type(s) transmitted"
		print ("Running INDEXER query #2 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT filetype, count(filetype) as qty_each \
			FROM %s \
			WHERE \
			batchid = '%s' \
			GROUP BY filetype""" %(INDEXERLOGFILE, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		TOTAL = 0
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
			if (str(i[0]).upper() == "PDF"):
				DOCUMENTS_TO_OCR = int(i[1])
				# print DOCUMENTS_TO_OCR	
			TOTAL = TOTAL + int(i[1])
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if TOTAL < DOCUMENTCOUNTER:
			print ("QUERY 2 FAILED")
			component_status="FAILED"

	labelPassOrFail(component_status)

#=========================================================================================

def queryDocReceiver():
	global REPORT

	query_status = "passed"
	component_status = "passed"
	REPORT = REPORT+SUBHDR % "DOC-RECEIVER"

	if (QUERY_NUMBER) == 3 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of documents uploaded"
		print ("Running DOC-RECEIVER query #3 - retrieve %s ...") % (QUERY_DESC)
			
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, \
			get_json_object(line, '$.upload.document.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.upload.document.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.upload.document.status')""" %(DOCRECEIVERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTCOUNTER:
			print ("QUERY 3 FAILED")
			component_status="FAILED"



	if (QUERY_NUMBER) == 4 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of documents archived to S3"
		print ("Running DOC-RECEIVER query #4 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, \
			get_json_object(line, '$.archive.afs.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = "EVENT" and \
			day=%s and month=%s and \
			get_json_object(line, '$.archive.afs.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.archive.afs.status')""" %(DOCRECEIVERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTCOUNTER:
			print ("QUERY 4 FAILED")
			component_status="FAILED"


	if (QUERY_NUMBER) == 5 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of documents added to sequence file(s)"
		print ("Running DOC-RECEIVER query #5 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, \
			get_json_object(line, '$.seqfile.file.add.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = "EVENT" and \
			day=%s and month=%s and \
			get_json_object(line, '$.seqfile.file.document.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.seqfile.file.add.status')""" %(DOCRECEIVERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTCOUNTER:
			print ("QUERY 5 FAILED")
			component_status="FAILED"



	if (QUERY_NUMBER) == 6 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of seq. files and individual documents sent to redis"
		print ("Running DOC-RECEIVER query #6 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT get_json_object(line, '$.submit.post.numfiles') as seq_files_sent_to_redis, \
			get_json_object(line, '$.submit.post.apxfiles.count') as ind_files, \
			get_json_object(line, '$.submit.post.queue.name') as redis_queue_name \
			FROM %s \
			WHERE get_json_object(line, '$.level') = "EVENT" and \
			day=%s and month=%s and \
			get_json_object(line, '$.submit.post.status') = "success" and \
			get_json_object(line, '$.submit.post.batchid') = '%s'""" %(DOCRECEIVERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"&nbsp;-&nbsp;</td><td>"+str(i[2])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0', '0']
		REPORT = REPORT+"</table><br>"
		if int(i[1]) < DOCUMENTCOUNTER:
			print ("QUERY 6 FAILED")
			component_status="FAILED"

	labelPassOrFail(component_status)

#=========================================================================================

def queryCoordinator():
	global REPORT
	
	query_status = "passed"
	component_status = "passed"
	REPORT = REPORT+SUBHDR % "COORDINATOR"

	if (QUERY_NUMBER) == 7 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of job types succeeded and/or failed by coordinator"
		print ("Running COORDINATOR query #7 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT(get_json_object(line, '$.job.jobID'))) as count, \
			get_json_object(line, '$.job.activity') as activity, \
			get_json_object(line, '$.job.status') as status \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.job.context.batchID') = '%s' and \
			get_json_object(line, '$.job.status') is not null and \
			get_json_object(line, '$.job.status') <> 'start' \
			GROUP BY get_json_object(line, '$.job.status'), get_json_object(line, '$.job.activity')""" %(COORDINATORLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='left'>"+str(i[1])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[2])+"</td></tr>"
			if (str(i[2]).lower() == 'error'):
				print ("QUERY 7 FAILED")
				component_status="FAILED"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			print ("QUERY 7 FAILED")
			component_status="FAILED"				
		REPORT = REPORT+"</table><br>"

	labelPassOrFail(component_status)

#=========================================================================================

def queryParser():
	global REPORT
	
	query_status = "passed"
	component_status = "passed"
	REPORT = REPORT+SUBHDR % "PARSER"

	if (QUERY_NUMBER) == 8 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of distinct UUIDs tagged to OCR"
		print ("Running PARSER query #8 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_OCR \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.tag.ocr.status') = "success" and \
			get_json_object(line, '$.batchId') = '%s'""" %(PARSERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		TAGED_TO_OCR=0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'></td></tr>"
			TAGED_TO_OCR = int(i[0])
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if TAGED_TO_OCR < DOCUMENTS_TO_OCR:
			print ("QUERY 8 FAILED")
			component_status="FAILED"



	if (QUERY_NUMBER) == 9 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of distinct UUIDs tagged to Persist"
		print ("Running PARSER query #9 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_Persist \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.tag.persist.status') = "success" and \
			get_json_object(line, '$.batchId') = '%s'""" %(PARSERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		TAGED_TO_PERSIST=0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'></td></tr>"
			TAGED_TO_PERSIST = int(i[0])
			# print TAGED_TO_PERSIST
			# print TAGED_TO_PERSIST + TAGED_TO_OCR
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0']
		REPORT = REPORT+"</table><br>"
		if (TAGED_TO_OCR + TAGED_TO_PERSIST) < DOCUMENTCOUNTER:
			print ("QUERY 9 FAILED")
			component_status="FAILED"



	if (QUERY_NUMBER) == 10 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of distinct UUIDs succeeded or failed"
		print ("Running PARSER query #10 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Parser_distinct_UUIDs, \
			get_json_object(line, '$.status') as status \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.batchId') = '%s' \
			GROUP BY get_json_object(line, '$.status')""" %(PARSERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0', 'success']
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTCOUNTER:
			print ("QUERY 10 FAILED")
			component_status="FAILED"



	if (QUERY_NUMBER) == 11 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of Parser errors, class-name and specific error messages"
		print ("Running PARSER query #11 - retrieve %s ...") %  (QUERY_DESC)
		cur.execute("""SELECT get_json_object(line, '$.error.message') as parser_error_message, \
			get_json_object(line, '$.className') as class_name, \
			round((get_json_object(line, '$.file.bytes') / 1024 / 1024),2) as file_size_mb \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.status') = "error" and \
			get_json_object(line, '$.jobname') LIKE '%s%%'""" %(PARSERLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"&nbsp;-&nbsp;</td><td>"+str(i[2])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
			# component_status="PASSED"
		else:
			component_status="FAILED"
		REPORT = REPORT+"</table><br>"
		if ROW > 0:
			print ("QUERY 11 FAILED")
			component_status="FAILED"

	labelPassOrFail(component_status)

#=========================================================================================
def queryOCR():
	global REPORT
	
	query_status = "passed"
	component_status = "passed"
	REPORT = REPORT+SUBHDR % "OCR"

	if (QUERY_NUMBER) == 12 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of distinct UUIDs passed or failed by OCR"
		print ("Running OCR query #12 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  OCR_distinct_UUIDs, \
			get_json_object(line, '$.status') as status \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.batchId') = '%s' \
			GROUP BY get_json_object(line, '$.status')""" %(OCRLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			component_status="FAILED"
			print ("QUERY 12 FAILED")
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTS_TO_OCR:
			component_status="FAILED"


	if (QUERY_NUMBER) == 13 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of OCR errors and specific error messages"
		print ("Running PERSIST query #13 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT get_json_object(line, '$.error.message') as ocr_error_message, \
			get_json_object(line, '$.className') as class_name, \
			get_json_object(line, '$.file.bytes') as file_size_bytes \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.status') = "error" and \
			get_json_object(line, '$.batchId') = '%s'""" %(OCRLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'>"+str(i[1])+"</td><td align='center'>"+str(i[2])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
			# component_status="PASSED"
		else:
			component_status="FAILED"
		REPORT = REPORT+"</table><br>"
		if ROW > 0:
			print ("QUERY 13 FAILED")
			component_status="FAILED"

	labelPassOrFail(component_status)

#=========================================================================================
def queryPersist():
	global REPORT
	
	query_status = "passed"
	component_status = "passed"
	REPORT = REPORT+SUBHDR % "PERSIST"

	if (QUERY_NUMBER) == 14 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of distinct UUIDs passed or failed to Persist"
		print ("Running PERSIST query #14 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Persist_distinct_UUIDs, \
			get_json_object(line, '$.status') as status \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.batchId') = '%s' \
			GROUP BY get_json_object(line, '$.status')""" %(PERSISTLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
			i = ['0', 'success']
		REPORT = REPORT+"</table><br>"
		if int(i[0]) < DOCUMENTCOUNTER:
			print ("QUERY 14 FAILED")
			component_status="FAILED"



	if (QUERY_NUMBER) == 15 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of Persist errors and specific error messages"
		print ("Running PERSIST query #15 - retrieve %s ...") % (QUERY_DESC)
		cur.execute("""SELECT get_json_object(line, '$.error.message') as persist_error_message, \
			get_json_object(line, '$.className') as class_name, \
			get_json_object(line, '$.file.bytes') as file_size_bytes \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.status') = "error" and \
			get_json_object(line, '$.batchId') = '%s'""" %(PERSISTLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'>"+str(i[1])+"</td><td align='center'>"+str(i[2])+"</td></tr>"
		if (ROW == 0):
			REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
			# component_status="PASSED"
		else:
			component_status="FAILED"
		REPORT = REPORT+"</table><br>"
		if ROW > 0:
			print ("QUERY 15 FAILED")
			component_status="FAILED"

	labelPassOrFail(component_status)

#=========================================================================================

def queryEvents():
	global REPORT
	
	query_status = "passed"
	component_status = "passed"
	REPORT = REPORT+SUBHDR % "EVENTS"

	if (QUERY_NUMBER) == 16 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of EventsTotal and succeeded EventMapper"
		print ("Running EVENTS query #16 - retrieve %s ...") % (QUERY_DESC)
	
		cur.execute("""SELECT SUM(get_json_object(line, '$.event.count')) as Total_Mapper_Events_Count \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.batchId') = '%s' and \
			get_json_object(line, '$.event.count') is not null and \
			get_json_object(line, '$.className')  = 'com.apixio.jobs.event.mapper.EventMapper'""" %(EVENTSLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		TOTALEVENTMAPPER = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>&nbsp;"+str(i[0])+"&nbsp;</td></tr>"
		if (ROW == 0) :
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		REPORT = REPORT+"</table><br>"
	
		if i[0] is None:
			component_status="FAILED"
			print ("QUERY 16 FAILED")
		else:
			TOTALEVENTMAPPER=int(i[0])
				
		
	if (QUERY_NUMBER) == 17 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of EventsTotal and succeeded EventReducer"
		print ("Running EVENTS query #17 - retrieve %s ...") % (QUERY_DESC)
		
	
		cur.execute("""SELECT SUM(get_json_object(line, '$.eventBatch.count')) as Total_Reducer_Events_Count \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.batchId') = '%s' and \
			get_json_object(line, '$.eventBatch.count') is not null and
			get_json_object(line, '$.className')  = 'com.apixio.jobs.event.reducer.EventReducer'""" %(EVENTSLOGFILE, DAY, MONTH, BATCH))
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>&nbsp;"+str(i[0])+"&nbsp;</td></tr>"
		if (ROW == 0) :
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		REPORT = REPORT+"</table><br>"
	
		if i[0] is None:
			component_status="FAILED"
		elif (int(i[0]) <> TOTALEVENTMAPPER):
			print ("QUERY 17 FAILED")
			component_status="FAILED"		
		
	if (QUERY_NUMBER) == 18 or PROCESS_ALL_QUERIES:
		QUERY_DESC="Number of Events succeeded and/or failed"
		print ("Running EVENTS query #18 - retrieve %s ...") % (QUERY_DESC)
		
		cur.execute("""SELECT COUNT(line) as total, get_json_object(line, '$.status') as status \
			FROM %s \
			WHERE \
			day=%s and month=%s and \
			get_json_object(line, '$.batchId') = '%s' and \
			get_json_object(line, '$.status') is not null
			GROUP BY get_json_object(line, '$.status')""" %(EVENTSLOGFILE, DAY, MONTH, BATCH))		
		
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
		REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
		ROW = 0
		for i in cur.fetch():
			ROW += 1
			print i
			REPORT = REPORT+"<tr><td align='center'>&nbsp;"+str(i[0])+"&nbsp;</td><td align='center'>&nbsp;"+str(i[1])+"&nbsp;</td></tr>"
			if str(i[1]) == "error":
				component_status="FAILED"
		if (ROW == 0) :
			REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		REPORT = REPORT+"</table><br>"
	
	labelPassOrFail(component_status)

#=========================================================================================
	
class CEPException(Exception):
	pass

#=========================================================================================

def output(data):
	columns = sorted(reduce(lambda x, y: set(x) | set(y), [set(x.keys()) for x in data]))
	odata = [[x.split('_')[-1] for x in columns]]
	for row in data:
		odata.append([row.get(x) if type(row.get(x)) != float else '%.2f' % row.get(x) for x in columns])
	print tabulate.tabulate(odata, headers='firstrow', missingval='')
  
#=========================================================================================  

def query(stmt, url=None):
	
	url = EVENT_CLOUD_URL
	
	r = requests.get(url, params={'statement': stmt})
	if r.status_code != 200:
		raise CEPException(r.text)
	j = r.json()
	#if len(j) == 0:
	#	raise CEPException('JSON length 0')
	
	return j	

#=========================================================================================	
	
def batch_all_info_pipeline(batch):
	output(query("select stateName a_state, occurences b_count, successes c_successes, errors d_errors, numDocs e_docs, numPatients f_patients, numEvents g_events from AllBatchState where batchId = '%s'" % (batch)))	
	
#=========================================================================================
def componentUploadStatus(p_module, p_state, batch):
	global observed_durations

	component_upload_time_limit = 10
	
	
	components = { \
		"indexer", "docreceiver", "coordinator", "parser", "ocr", "persist", "event" \
		}
	states = { \
		"Archived", "Packaged", "Uploaded", "Submitted", "SentToOCR", "Parsed", "SentToPersist", "OCRed", "Coordinated", "PersistMapped", "PersistReduced", \
		"parser", "Checked", "EventMapped", "EventReduced", "EventChecked", "ocr", "persist", "dataCheckAndRecovery", "event", "trace", "qaAndRecoverEvent" \
		}
	counts = { \
		"Archived": 13, "Packaged": 13, "Uploaded": 13, "Submitted": 1, "SentToOCR": 1, "Parsed": 13, "SentToPersist": 12, "OCRed": 1, "Coordinated": 1, "PersistMapped": 13, "PersistReduced": 13, \
		"parser": 2, "Checked": 13, "EventMapped": 13, "EventReduced": 5, "EventChecked": 2, "ocr": 2, "persist": 4, "dataCheckAndRecovery": 4, "event": 4, "trace": 8, "qaAndRecoverEvent": 4 \
		}
	successes = { \
		"Archived": 13, "Packaged": 13, "Uploaded": 13, "Submitted": 1, "SentToOCR": 1, "Parsed": 13, "SentToPersist": 12, "OCRed": 1, "Coordinated": 1, "PersistMapped": 13, "PersistReduced": 13, \
		"parser": 1, "Checked": 13, "EventMapped": 13, "EventReduced": 5, "EventChecked": 2, "ocr": 1, "persist": 2, "dataCheckAndRecovery": 2, "event": 2, "trace": 4, "qaAndRecoverEvent": 2 \
		}
	errors = { \
		"Archived": 0, "Packaged": 0, "Uploaded": 0, "Submitted": 0, "SentToOCR": 0, "Parsed": 0, "SentToPersist": 0, "OCRed": 0, "Coordinated": 0, "PersistMapped": 0, "PersistReduced": 0, \
		"parser": 0, "Checked": 0, "EventMapped": 0, "EventReduced": 0, "EventChecked": 0, "ocr": 0, "persist": 0, "dataCheckAndRecovery": 0, "event": 0, "trace": 0, "qaAndRecoverEvent": 0 \
		}
	docs = { \
		"Archived": 13, "Packaged": 13, "Uploaded": 13, "Submitted": 13, "SentToOCR": 1, "Parsed": 13, "SentToPersist": 12, "OCRed": 1, "Coordinated": 0, "PersistMapped": 13, "PersistReduced": 13, \
		"parser": 0, "Checked": 13, "EventMapped": 13, "EventReduced": 5, "EventChecked": 0, "ocr": 0, "persist": 0, "dataCheckAndRecovery": 0, "event": 0, "trace": 0, "qaAndRecoverEvent": 0 \
		}
	#685	
	durations = 	{ \
		"Archived": 80, "Packaged": 97, "Uploaded": 1221, "Submitted": 60, "SentToOCR": 547, "Parsed": 9934, "SentToPersist": 9387, "OCRed": 206333, "Coordinated": 2, \
		"PersistMapped": 5448, "PersistReduced": 9089, "parser": 60553, "Checked": 5095, "EventMapped": 44228, "EventReduced": 860, "EventChecked": 1081, "ocr": 301006, "persist": 121555, \
		"dataCheckAndRecovery": 120613, "event": 241290, "trace": 242661, "qaAndRecoverEvent": 120665 \
		}	
	columns = {"state", "counts", "successes", "errors", "docs", "durations"}
			

	status = "started"	
	print ("-----------------------------------------------------------------------------")
	print ("Component        = %s" % p_module)
	print ("State            = %s" % p_state)
	print ("Batch            = %s" % batch)
	print ("Status           = %s" % status)
	print ("-----------------------------------------------------------------------------")
	
	#batch_all_info_pipeline(batch)
	for state in states:
		data = query("\
			SELECT stateName state, occurences counts, successes successes, errors errors, numDocs docs, duration durations \
			FROM AllBatchState \
			WHERE batchId = '%s' and stateName = '%s'" % (batch, state))
	
		#for row in data:
		#	for column in columns:
		#		print row[column]

	max_time = durations[p_state]
	count = 0
	print max_time
	#quit()
	start_time = time.time()  # remember when we started
	while (time.time() - start_time) < max_time :
		duration_time = (time.time() - start_time)
		print ("Module : State     = %s : %s" % (p_module, p_state))
		print ("Time passed        = %s" % (duration_time))
		print ("Limit              = %s\n" % (max_time))
		data = query("\
			SELECT stateName state, occurences counts, successes successes, errors errors, numDocs docs, duration durations \
			FROM AllBatchState \
			WHERE batchId = '%s' and stateName = '%s'" % (batch, p_state))
		for row in data:
			print ("Documents actually %s = %d" % (p_state, row["counts"]))
			print ("Documents expected %s = %d" % (p_state, counts[p_state]))
			if (row["counts"] == counts[p_state]) and (duration_time < max_time):
				print ("%d documents were successfully %s for batch %s completed in %s seconds ...\n" % (row["counts"], p_state, batch, duration_time))
				max_time = 0
				observed_durations.update({str(p_module+" "+p_state): duration_time})
			elif (row["counts"] < counts[p_state]) and (duration_time >= max_time):
				print ("Time limit of %s exceeded %d documents were %s ...\n" % (duration_time, row["counts"], p_state))
			
			
	if max_time >= duration_time:
		print ("Time limit of %s seconds excedded maximum execution time of %s seconds. FAILED QA\n" % (duration_time, max_time))
		status = "incomplete"

	else:
		print ("%d documents were successfully %s for batch %s completed in %s seconds ...\n" % (row["counts"], p_state, batch, duration_time))	 	
		status = "complete"
		#raw_input("Press Enter to continue...")
		
	
	#output (query("\
	#	select stateName a_state \
	#	from AllBatchState \
	#	where batchId = '%s'" % (batch)))
	
	#output(query("select * from AllBatchState where batchId = '%s' and stateName = 'Archived' " % (batch)))
		
	return (status)

#=========================================================================================

def generateReportDetails():
	global REPORT, cur, conn, BATCH, observed_durations
	states = { \
		"Archived", "Packaged", "Uploaded", "Submitted", "SentToOCR", "Parsed", "SentToPersist", \
		"OCRed", "Coordinated", "PersistMapped", "PersistReduced", \
		"parser", "Checked", "EventMapped", "EventReduced", "EventChecked", "ocr", "persist", \
		"dataCheckAndRecovery", "event", "trace", "qaAndRecoverEvent" \
		}
	components = { \
		"indexer", "docreceiver", "coordinator", "parser", "ocr", "persist", "event" \
		}	
		
	print ("Start querying individual pipeline components ...")
	print ("===================================================================================\n")
		
	
	modules_states = [ \
		["docreceiver", "Archived"], ["docreceiver", "Packaged"], ["docreceiver", "Uploaded"], ["docreceiver", "Submitted"], \
		["coordinator", "Coordinated"], \
		["parser", "Parsed"], ["parser", "SentToOCR"], ["parser", "SentToPersist"], \
		["ocr", "OCRed"], \
		["persist", "PersistMapped"], ["persist", "PersistReduced"], \
		["event", "EventMapped"], ["event", "EventReduced"], ["event", "EventChecked"], \
		["qa", "Checked"], ["qa", "qaAndRecoverEvent"], \
		["jobs", "parser"], ["jobs", "ocr"], ["jobs", "persist"], ["jobs", "event"], ["jobs", "trace"]]
	
	
	for module_state in modules_states:
			print module_state[0], module_state[1]
			status = componentUploadStatus(module_state[0], module_state[1], BATCH)
			print ("-----------------------------------------------------------------------------")
			print ("Component        = %s" % module_state[0])
			print ("State            = %s" % module_state[1])
			print ("Batch            = %s" % BATCH)
			print ("Status           = %s" % status)
			print ("-----------------------------------------------------------------------------")
	
	
	print observed_durations
	
	
	
	#if componentUploadStatus("docreceiver", "Archived", BATCH)	== "complete":
	#	print ("Docreceiver - Archive completed ...\n")
	
	#if componentUploadStatus("indexer", BATCH)	== "complete":
		#queryIndexer()
	#if componentUploadStatus("docreceiver", BATCH)	== "complete":
	#	queryDocReceiver()	
	#	if componentUploadStatus("coordinator", BATCH)	== "complete":
	#		queryCoordinator()	
	#		if componentUploadStatus("parser", BATCH)	== "complete":	
	#			queryParser()
	#			if componentUploadStatus("ocr", BATCH)	== "complete":
	#				queryOCR()
	#				if componentUploadStatus("persist", BATCH)	== "complete":
	#					queryPersist()
	#					if componentUploadStatus("event", BATCH)	== "complete":
	#						queryEvents()
	
	print ("\n===================================================================================")
	print ("End querying individual pipeline components ...\n")				
	cur.close()
	conn.close()
	quit()
	
#=========================================================================================

def generateReportFooter():
	global REPORT

	END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	REPORT = REPORT+"<table><tr><td><br>Start of %s - <b>%s</b></td></tr>" % (BATCH, START_TIME)
	REPORT = REPORT+"<tr><td>End of %s - <b>%s</b></td></tr>" % (BATCH, END_TIME)
	TIME_END = time.time()
	TIME_TAKEN = TIME_END - TIME_START
	hours, REST = divmod(TIME_TAKEN,3600)
	minutes, seconds = divmod(REST, 60)
	REPORT = REPORT+"<tr><td>Test Duration: <b>%s hours, %s minutes, %s seconds</b><br></td></tr>" % (hours, minutes, seconds)
	REPORT = REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"

#=========================================================================================

def emaiReport():
	global REPORT
	# CONTENT="Subject: %s<br><br>%s" % (SUBJECT, REPORT)
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")
	# s.sendmail(SENDER, RECEIVERS, CONTENT)
	# send report only if failure occured
	# GLOBAL_STATUS = "failed"
	if (GLOBAL_STATUS == "success"):
		print "Status report was NOT emailed ...\n"
		print "Sanity Test Passed ...\n"
	else:
		s.sendmail(SENDER, RECEIVERS, REPORT)	
		print "Report completed, email to %s ...\n" % (RECEIVERS)
		print ">>>>>>>>>>> Sanity Test Failed <<<<<<<<<<<\n"
	
#===================================== ARCHIVE REPORT ===================================================================================
def archiveReport():
	print ("Archiving report ...\n")
	BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/pipelinesanity/"+str(YEAR)+"/"+str(CURMONTH)
	REPORTFOLDER="/usr/lib/apx-reporting/assets/reports/"+ENVIRONMENT+"/pipelinesanity/"+str(YEAR)+"/"+str(CURMONTH)
	# ------------- Create new folder if one does not exist already -------------------------------
	if not os.path.exists(BACKUPREPORTFOLDER):
		os.makedirs(BACKUPREPORTFOLDER)
		os.chmod(BACKUPREPORTFOLDER, 0777)	
	if not os.path.exists(REPORTFOLDER):
		os.makedirs(REPORTFOLDER)
		os.chmod(REPORTFOLDER, 0777)
	# ---------------------------------------------------------------------------------------------
	REPORTFILENAME=str(CURDAY)+".html"
	REPORTXTSTRING="Pipeline Sanity "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/pipelinesanity/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
	REPORTXTFILENAME="pipeline_sanity_reports_"+ENVIRONMENT.lower()+".txt"
	# Old location 
	#REPORTXTFILEFOLDER="/usr/lib/apx-reporting/html/assets"
	# New location 
	REPORTXTFILEFOLDER="/usr/lib/apx-reporting/assets"
	os.chdir(BACKUPREPORTFOLDER)
	REPORTFILE = open(REPORTFILENAME, 'w')
	REPORTFILE.write(REPORT)
	REPORTFILE.close()
	os.chdir(REPORTFOLDER)
	REPORTFILE = open(REPORTFILENAME, 'w')
	REPORTFILE.write(REPORT)
	REPORTFILE.close()
	os.chdir(REPORTXTFILEFOLDER)
	f = open(REPORTXTFILENAME)
	s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
	if s.find(REPORTXTSTRING) != -1:
		print "Report entry found, skipping append ...\n"
	else:
		print "Report entry not found, appending new entry ...\n"
		REPORTFILETXT = open(REPORTXTFILENAME, 'a')
		REPORTFILETXT.write(REPORTXTSTRING)
		REPORTFILETXT.close()
	os.chdir("/mnt/automation/python/sanity_test")
	print ("Finished archiving report ... \n")	

###################################################################################################################
######################################### MAIN PROGRAM CALLS ######################################################
###################################################################################################################

os.system('clear')

initializeGlobalVars()

outputVarValues()

obtainToken()

uploadFiles()

#pauseForUploadToComplete()
#quit()

#BATCH="370_PipelineSanityTestStaging_02132015185431"

connectToHive()

generateReportHeader()

generateReportDetails()

generateReportFooter()

emaiReport()

archiveReport()