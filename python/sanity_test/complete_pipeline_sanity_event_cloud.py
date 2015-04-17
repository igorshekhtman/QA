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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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
	global STARTED, INCOMPLETE, PASSED, FAILED, SUBHDR, REPORT_TYPE, RECEIVERS2
	
	TEST_TYPE="PipelineSanityTest"
	REPORT_TYPE="PipelineSanityTest"
	YEAR=strftime("%Y", gmtime())
	CURMONTH=strftime("%m", gmtime())
	MONTH_FMN=strftime("%B", gmtime())
	CURDAY=strftime("%d", gmtime())
	START_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
	TIME_START=time.time()
	SENDER="donotreply@apixio.com"
	RECEIVERS="eng@apixio.com"
	RECEIVERS2="ops@apixio.com"
	
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	if ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "P")):
		# PRODUCTION ==================
		USERNAME="apxdemot0138"
		ORGID="10000279"
		PASSWORD="Hadoop.4522"
		HOST="https://dr.apixio.com"
		ENVIRONMENT="Production"
		#EVENT_CLOUD_URL="http://10.234.129.89:8076/event/query"
		EVENT_CLOUD_URL="http://eventcloud-pipeline.apixio.com:8076/event/query"
	else:
		# STAGING =====================
		USERNAME="sanitytest1"
		ORGID="370"
		PASSWORD="Hadoop.4522"
		HOST="https://stagedr.apixio.com:8443"
		ENVIRONMENT="Staging"
		#EVENT_CLOUD_URL="http://dashboard-development.apixio.net:8075/event/query"
		EVENT_CLOUD_URL="http://eventcloud-pipeline-stg.apixio.com:8076/event/query"
	#==================================
	if (len(sys.argv) > 3):
		RECEIVERS = str(sys.argv[2])
		RECEIVERS2 = str(sys.argv[3])
	else:
		RECEIVERS = "ishekhtman@apixio.com"
		RECEIVERS2 = "ishekhtman@apixio.com"	
	#==================================
	
	#print ("ENVIRONMANT = %s") % ENVIRONMENT
	#print RECEIVERS
	#print RECEIVERS2
	#quit()
	#time.sleep(15)
	DIR="/mnt/testdata/SanityThirteenDocuments/Documents"
	#DIR="/mnt/testdata/SanityTwentyDocuments/Documents"
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
	#{"started", "inclomete", "fail", "success"}
	PASSED="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
	FAILED="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
	INCOMPLETE="<table><tr><td bgcolor='#FFFF00' align='center' width='800'><font size='3' color='#000000'><b>STATUS - INCOMPLETE</b></font></td></tr></table>"
	STARTED="<table><tr><td bgcolor='#FFFFFF' align='center' width='800'><font size='3' color='#000000'><b>STATUS - STARTED</b></font></td></tr></table>"
	SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s:</b>&nbsp;%s:&nbsp;&nbsp;<b>BatchID:</b>&nbsp;%s</font></td></tr></table>"
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
	global TOKEN, post, buf, obj, USERNAME
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
	global BATCHID
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
	global DOCUMENTCOUNTER, obj, MANIFEST_FILE, USERNAME, BATCHID, BATCH
	
	FILES = os.listdir(DIR)
	print ("Uploading Files ...\n")
	for FILE in FILES:
		file_ext = FILE[len(FILE)-3:]
		DOCUMENTCOUNTER += 1
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
		if file_ext.upper() == "APO":
			CATALOG_FILE=("<ApxCatalog><CatalogEntry><Organization>%s</Organization><FileFormat>APO</FileFormat><OrgId>%s</OrgId><UserName>%s</UserName><DocumentUUID>%s</DocumentUUID><BatchId>%s</BatchId></CatalogEntry></ApxCatalog>" % (ORGANIZATION, ORGID, USERNAME, DOCUMENT_ID, BATCH))
		#	print CATALOG_FILE
		#	quit()
		#	CATALOG_FILE=("<?xml version='1.0' encoding='UTF-8' standalone='yes'?><ApxCatalog><CatalogEntry><Organization>%s</Organization><FileFormat>APO</FileFormat><OrgId>%s</OrgId><UserName>%s</UserName><DocumentUUID>%s</DocumentUUID><BatchId>%s</BatchId></CatalogEntry></ApxCatalog>" % (ORGANIZATION, ORGID, USERNAME, DOCUMENT_ID, BATCHID))
		else:	
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
	
	return (i)	

#=========================================================================================

def generateReportHeader():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	
	print ("Begin writing report header ...\n")
	# REPORT = MIMEMultipart()
	REPORT = ""
	REPORT = REPORT + "<h1>Apixio Pipeline QA Report</h1>"
	REPORT = REPORT + "Run date & time: <b>%s</b><br>\n" % (CUR_TIME)
	REPORT = REPORT + "Report type: <b>%s</b><br>\n" % (REPORT_TYPE)
	REPORT = REPORT + "Enviromnent: <b><font color='red'>%s%s</font></b><br>" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + "OrgID: <b>%s</b><br>" % (ORGID)
	REPORT = REPORT + "BatchID: <b>%s</b><br>" % (BATCHID)
	REPORT = REPORT + "User name: <b>%s</b><br>" % (USERNAME)
	#obtainOperationAndCategory()
	REPORT = REPORT + "Operation: <b>"+"n/a"+"</b><BR>"
	REPORT = REPORT + "Category: <b>"+"n/a"+"</b><BR><BR>"
	REPORT = REPORT + "<table align='left' width='800' cellpadding='1' cellspacing='1'><tr><td>"
	
	print ("End writing report header ...\n")	
	
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
		
	if (component_status.upper() == "STARTED"):
		REPORT = REPORT+STARTED
		GLOBAL_STATUS="started"
	elif (component_status.upper() == "INCOMPLETE"):
		REPORT = REPORT+INCOMPLETE
		GLOBAL_STATUS="incomplete"
	elif (component_status.upper() == "PASSED"):
		REPORT = REPORT+PASSED
		GLOBAL_STATUS="passed"	
	else:
		REPORT = REPORT+FAILED
		COMPONENT_STATUS="failed"
		GLOBAL_STATUS="failed"
	REPORT = REPORT+"<br><br>"

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

def logDetailsIntoReport(p_module, p_state, batch, status, successes, errors, docs, docswithe, patients, patientswithe, events, v5, dict, claims, duration, start, last, max_duration, actual_duration, bg_color):
	global REPORT
			
	REPORT = REPORT+SUBHDR % (p_module.upper(), p_state, batch)
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0' width='800'><tr><td>"
	
	#print bg_color
	#quit() 
		
	REPORT = REPORT+"<table border='0' width='100%%' ><tr>"
	
	REPORT = REPORT+" \
		<td width='50%%' bgcolor='%s'>Successes: %d</td> \
		<td width='50%%' bgcolor='%s'>Errors: %d</td> \
		</tr></table>" % (bg_color[0], successes, bg_color[1], errors)
	
	REPORT = REPORT+"<hr width='100%%'>"
	
	REPORT = REPORT+"<table border='0' width='100%%' ><tr>"
	REPORT = REPORT+" \
		<td bgcolor='%s'>Docs:</td> \
		<td bgcolor='%s'>Docs with Events:</td> \
		<td bgcolor='%s'>Patients:</td> \
		<td bgcolor='%s'>Patients with Events:</td> \
		<td bgcolor='%s'>Events:</td> \
		<td bgcolor='%s'>V5 Events:</td> \
		<td bgcolor='%s'>Dictionary Events:</td> \
		<td bgcolor='%s'>Claims:</td>" % (bg_color[2], bg_color[3], bg_color[4], bg_color[5], bg_color[6], bg_color[7], bg_color[8], bg_color[9])
	REPORT = REPORT+"</tr><tr>"
	REPORT = REPORT+" \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td> \
		<td bgcolor='%s'>%s</td>" % (bg_color[2], docs, bg_color[3], docswithe, bg_color[4], patients, bg_color[5], patientswithe, bg_color[6], events, bg_color[7], v5, bg_color[8], dict, bg_color[9], claims)
	REPORT = REPORT+"</tr></table>"
	
	REPORT = REPORT+"<hr width='100%%'>"
	
	REPORT = REPORT+"<table border='0' width='100%%' ><tr>"
	REPORT = REPORT+"<td>Duration (msec.):</td><td>Start Time:</td><td>End Time:</td><td bgcolor='%s'>Max Duration (sec.):</td><td bgcolor='%s'>Actual Duration (sec.):</td>" % (bg_color[10], bg_color[10])
	REPORT = REPORT+"</tr><tr>"
	REPORT = REPORT+"<td>%s</td><td>%s</td><td>%s</td><td bgcolor='%s'>%s</td><td bgcolor='%s'>%s</td>" % (duration, start, last, bg_color[10], max_duration, bg_color[10], actual_duration)
	REPORT = REPORT+"</tr></table>"
	
	REPORT = REPORT+"<hr width='100%%'>"
	
	REPORT = REPORT+"</td></tr></table><br>"
	
	labelPassOrFail(status)

#=========================================================================================

def componentUploadStatus(p_module, p_state, batch):
	global observed_durations
	
	columns = ["state", "successes", "errors", "docs", "docsWithE", "patients", "patientsWithE", "events", "v5", "dict", "claims", "duration"]
	
	bg_color = ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"]

	exp_rslt = { \
		"Archived":                        [13, 0, 13, 0,     0,  0,     0, 0,     0,    0,     80], \
		"Packaged":                        [13, 0, 13, 0,     0,  0,     0, 0,     0,    0,     10], \
		"Uploaded":                        [13, 0, 13, 0,     0,  0,     0, 0,     0,    0,     10], \
		"Submitted":                        [1, 0, 13, None,  0,  None,  0, None,  None, None,  10], \
		"SentToPersist":                   [12, 0, 12, 0,     0,  0,     0, 0,     0,    0,    100], \
		"Parsed":                          [13, 0, 13, 0,     0,  0,     0, 0,     0,    0,    160], \
		"SentToOCR":                        [1, 0,  1, 0,     0,  0,     0, 0,     0,    0,    100], \
		"OCRed":                            [1, 0,  1, 0,     0,  0,     0, 0,     0,    0,    350], \
		"PersistMapped":                   [13, 0, 13, 0,     0,  0,     0, 0,     0,    0,    360], \
		"PersistReduced":                  [13, 0,  0, 0,    13,  0,     0, 0,     0,    0,    200], \
		"EventReduced":                     [5, 0,  0, 0,     5,  5,    15, 0,     0,    0,     50], \
		"Checked":                         [13, 0, 13, 0,    13,  0,     0, 0,     0,    0,     50], \
		"Coordinated":                      [1, 0,  0, None,  0,  None,  0, None,  None, None,  50], \
		"EventMapped":                     [13, 0, 13, 5,    13,  5,    15, 1,    13,    1,    440], \
		"parser_hadoop_job":                [1, 0,  0, 0,     0,  0,     0, 0,     0,    0,     10], \
		"ocr_hadoop_job":                   [1, 0,  0, 0,     0,  0,     0, 0,     0,    0,     80], \
		"persist_hadoop_job":               [2, 0,  0, 0,     0,  0,     0, 0,     0,    0,    160], \
		"dataCheckAndRecovery_hadoop_job":  [2, 0,  0, 0,     0,  0,     0, 0,     0,    0,     10], \
		"qaAndRecoverEvent_hadoop_job":     [1, 0,  0, 0,     0,  0,     0, 0,     0,    0,     10], \
		"event_hadoop_job":                 [2, 0,  0, 0,     0,  0,     0, 0,     0,    0,    240], \
		"trace_hadoop_job":                 [4, 0,  0, 0,     0,  0,     0, 0,     0,    0,     90] }
		
	
	statuses = {"started", "inclomete", "failed", "passed"}
			
	status = "started"	
	print ("-----------------------------------------------------------------------------")
	print ("Component        = %s" % p_module)
	print ("State            = %s" % p_state)
	print ("Batch            = %s" % batch)
	print ("Status           = %s" % status)
	print ("Max. Time        = %s" % exp_rslt[p_state][10])
	print ("-----------------------------------------------------------------------------")
	print ("Running, please wait ...\n")
	
	max_time = exp_rslt[p_state][10]
	#print max_time
	start_time = time.time()  # remember when we started
	row_ctr = 0
	while (time.time() - start_time) < max_time :
		duration_time = (time.time() - start_time)
		time.sleep(3)
		print ("Module : State     = %s : %s\nTime passed        = %s\nTime limit         = %s seconds\n" % (p_module, p_state, duration_time, max_time))
		data = query("\
			SELECT stateName a_state, successes b_successes, errors c_errors, numDocs d_docs, docsWE e_docsWithE, numPatients f_patients, patientsWE g_patientsWithE, \
			numEvents h_events, v5Events i_v5, dictEvents j_dict, claimEvents k_claims, duration l_duration, starttime.format() m_start, lasttime.format() n_last \
			FROM AllBatchState \
			WHERE batchId = '%s' and stateName = '%s'" % (batch, p_state))
		#time.sleep(2)	
		for row in data:
			#print ("Documents actually %s = %d" % (p_state, row["b_successes"]))
			#print ("Documents expected %s = %d" % (p_state, exp_rslt[p_state][0]))
			################
			# SUCCESS ######
			################
			row_ctr += 1
			if (row["b_successes"] == exp_rslt[p_state][0]) and (row["c_errors"] == exp_rslt[p_state][1]) and \
				(row["d_docs"] == exp_rslt[p_state][2]) and (row["e_docsWithE"] == exp_rslt[p_state][3]) and \
				(row["f_patients"] == exp_rslt[p_state][4]) and (row["g_patientsWithE"] == exp_rslt[p_state][5]) and \
				(row["h_events"] == exp_rslt[p_state][6]) and (row["i_v5"] == exp_rslt[p_state][7]) and \
				(row["j_dict"] == exp_rslt[p_state][8]) and (row["k_claims"] == exp_rslt[p_state][9]) and \
				((time.time() - start_time) < max_time):
				#print ("%d successes were %s for batch %s completed in %s seconds ...\n" % (row["b_successes"], p_state, batch, (time.time() - start_time)))
				max_time = 0
				observed_durations.update({str(p_module+" "+p_state): (time.time() - start_time)})
				status = "passed"
				bg_color = ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"]
			################
			# FAILURE ######
			################	
			#elif ((row["b_successes"] < exp_rslt[p_state][0]) and (duration_time >= max_time)) or (row["c_errors"] > 0):
			else:
				if (row["b_successes"] != exp_rslt[p_state][0]):
					bg_color[0] = "#FFFF00"
				if (row["c_errors"] != exp_rslt[p_state][1]):
					bg_color[1] = "#FFFF00"
				if (row["d_docs"] != exp_rslt[p_state][2]):
					bg_color[2] = "#FFFF00"
				if (row["e_docsWithE"] != exp_rslt[p_state][3]):
					bg_color[3] = "#FFFF00"
				if (row["f_patients"] != exp_rslt[p_state][4]):
					bg_color[4] = "#FFFF00"
				if (row["g_patientsWithE"] != exp_rslt[p_state][5]):
					bg_color[5] = "#FFFF00"
				if (row["h_events"] != exp_rslt[p_state][6]):
					bg_color[6] = "#FFFF00"
				if (row["i_v5"] != exp_rslt[p_state][7]):
					bg_color[7] = "#FFFF00"
				if (row["j_dict"] != exp_rslt[p_state][8]):
					bg_color[8] = "#FFFF00"
				if (row["k_claims"] != exp_rslt[p_state][9]):
					bg_color[9] = "#FFFF00"
				if ((time.time() - start_time) >= max_time):	
					bg_color[10] = "#FFFF00"
					#print ("Time limit-1 of %s exceeded maximum time of %s seconds - %d successes were %s ...\n" % ((time.time() - start_time), max_time, row["b_successes"], p_state))
				status = "failed"
					
	if ((time.time() - start_time) >= exp_rslt[p_state][10]):
		print ("Time limit-2 of %s seconds excedded maximum execution time of %s seconds. FAILED QA\n" % ((time.time() - start_time), exp_rslt[p_state][10]))
		#status = "incomplete"
		status = "failed"
		#logDetailsIntoReport(p_module, p_state, batch, status, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, exp_rslt[p_state][10], duration_time, bg_color)
	elif (row["b_successes"] < exp_rslt[p_state][0]) or (row["c_errors"] > 0):
		print (">>> Specific Component Failure Occured ...\n")
		status = "failed"
		#logDetailsIntoReport(p_module, p_state, batch, status, row["b_successes"], row["c_errors"], row["d_docs"], row["e_docsWithE"], row["f_patients"], \
		#	row["g_patientsWithE"], row["h_events"], row["i_v5"], row["j_dict"], row["k_claims"], row["l_duration"], row["m_start"], row["n_last"], exp_rslt[p_state][10], duration_time, bg_color)
	else:		
		print ("%d successes were %s for batch %s completed in %s seconds ...\n" % (row["b_successes"], p_state, batch, duration_time))	 	
		status = "passed"
		#logDetailsIntoReport(p_module, p_state, batch, status, row["b_successes"], row["c_errors"], row["d_docs"], row["e_docsWithE"], row["f_patients"], \
		#	row["g_patientsWithE"], row["h_events"], row["i_v5"], row["j_dict"], row["k_claims"], row["l_duration"], row["m_start"], row["n_last"], exp_rslt[p_state][10], duration_time, bg_color)
	
	if row_ctr == 0:
		logDetailsIntoReport(p_module, p_state, batch, status, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, exp_rslt[p_state][10], duration_time, bg_color)
	else:
		logDetailsIntoReport(p_module, p_state, batch, status, row["b_successes"], row["c_errors"], row["d_docs"], row["e_docsWithE"], row["f_patients"], \
			row["g_patientsWithE"], row["h_events"], row["i_v5"], row["j_dict"], row["k_claims"], row["l_duration"], row["m_start"], row["n_last"], exp_rslt[p_state][10], duration_time, bg_color)		
				
	return (status)

#=========================================================================================

def generateReportDetails():
	global REPORT, cur, conn, BATCH, observed_durations
	components = { \
		"indexer", "docreceiver", "coordinator", "parser", "ocr", "persist", "event" \
		}	
		
	print ("Start generating Report Details ...")
	print ("===================================================================================\n")
			
	modules_states = [ \
		["docreceiver", "Archived"], ["docreceiver", "Packaged"], ["docreceiver", "Uploaded"], ["docreceiver", "Submitted"], \
		["parser", "Parsed"], ["parser", "SentToOCR"], ["parser", "SentToPersist"], \
		["ocr", "OCRed"], \
		["persist", "PersistMapped"], ["persist", "PersistReduced"], \
		["event", "EventMapped"], ["event", "EventReduced"], ["event", "Checked"], \
		["coordinator", "Coordinated"]]
		# Additional Hadoop Job completion checks can be added at a later time
		#["jobs", "parser_hadoop_job"], ["jobs", "ocr_hadoop_job"], ["jobs", "persist_hadoop_job"], ["jobs", "event_hadoop_job"], \
		#["jobs", "trace_hadoop_job"], ["job", "dataCheckAndRecovery_hadoop_job"], ["job", "qaAndRecoverEvent_hadoop_job"]]
		
	for module_state in modules_states:
			print module_state[0], module_state[1]
			status = componentUploadStatus(module_state[0], module_state[1], BATCH)
			print ("-----------------------------------------------------------------------------")
			print ("Component        = %s" % module_state[0])
			print ("State            = %s" % module_state[1])
			print ("Batch            = %s" % BATCH)
			print ("Status           = %s" % status)
			print ("-----------------------------------------------------------------------------")
		
	#print observed_durations	
	
	print ("\n===================================================================================")
	print ("End generating Report Details ...\n")				
	cur.close()
	conn.close()
	
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
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2

	print ("Emailing report ...\n")
	IMAGEFILENAME=str(CURDAY)+".png" 
	message = MIMEMultipart('related')
	message.attach(MIMEText((REPORT), 'html'))
	#with open(IMAGEFILENAME, 'rb') as image_file:
	#	image = MIMEImage(image_file.read())
	#image.add_header('Content-ID', '<picture@example.com>')
	#image.add_header('Content-Disposition', 'inline', filename=IMAGEFILENAME)
	#message.attach(image)

	message['From'] = 'Apixio QA <QA@apixio.com>'
	message['To'] = 'To: Eng <eng@apixio.com>,Ops <ops@apixio.com>'
	message['Subject'] = 'Pipeline %s Sanity Test Report - %s\n\n' % (ENVIRONMENT, START_TIME)
	msg_full = message.as_string()
		
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, [RECEIVERS, RECEIVERS2], msg_full)	
	s.quit()
	# Delete graph image file from stress_test folder
	#os.remove(IMAGEFILENAME)
	print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)	
	
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

connectToHive()

generateReportHeader()

generateReportDetails()

generateReportFooter()

emaiReport()

archiveReport()