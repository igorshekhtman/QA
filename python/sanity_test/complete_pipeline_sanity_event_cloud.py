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
	global STARTED, INCOMPLETE, SUCCESS, FAIL, SUBHDR, REPORT_TYPE, RECEIVERS2
	
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
	#{"started", "inclomete", "fail", "success"}
	SUCCESS="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
	FAIL="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
	INCOMPLETE="<table><tr><td bgcolor='#FFFF00' align='center' width='800'><font size='3' color='#000000'><b>STATUS - INCOMPLETE</b></font></td></tr></table>"
	STARTED="<table><tr><td bgcolor='#FFFFFF' align='center' width='800'><font size='3' color='#000000'><b>STATUS - STARTED</b></font></td></tr></table>"
	SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s:&nbsp;%s</b></font></td></tr></table>"
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
	
	return (i)	

#=========================================================================================

def generateReportHeader():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	
	print ("Begin writing report header ...\n")
	# REPORT = MIMEMultipart()
	REPORT = ""
	REPORT = REPORT + "<h1>Apixio Pipeline QA Report</h1>"
	REPORT = REPORT + "Run date & time (run): <b>%s</b><br>\n" % (CUR_TIME)
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
	elif (component_status.upper() == "SUCCESS"):
		REPORT = REPORT+SUCCESS
		GLOBAL_STATUS="success"	
	else:
		REPORT = REPORT+FAIL
		COMPONENT_STATUS="fail"
		GLOBAL_STATUS="fail"
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
	
def batch_all_info_pipeline(batch):
	output(query("select stateName a_state, occurences b_count, successes c_successes, errors d_errors, numDocs e_docs, numPatients f_patients, numEvents g_events from AllBatchState where batchId = '%s'" % (batch)))	
	
#=========================================================================================

def logDetailsIntoReport(p_module, p_state, batch, status, count, successes, errors, docs, patients, events, duration, start, last, actual_duration):
	global REPORT
	
	#QUERY_DESC="Number of seq. files and individual documents sent to redis"
	#print ("Running DOC-RECEIVER query #6 - retrieve %s ...") % (QUERY_DESC)
	
	#REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+p_module.upper()+" - "+p_state.upper()+"</b></td></tr></table>"
	
	REPORT = REPORT+SUBHDR % (p_module.upper(), p_state)
	
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td>"
	
	REPORT = REPORT+"<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (p_module, p_state, batch)
	
	REPORT = REPORT+"<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (status, count, successes, errors)
	
	REPORT = REPORT+"<td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (docs, patients, events, duration)
	
	REPORT = REPORT+"<td>%s</td><td>%s</td><td>%s</td></tr>" % (start, last, actual_duration)
	
	REPORT = REPORT+"</table><br>"
	
	labelPassOrFail(status)

#=========================================================================================

def componentUploadStatus(p_module, p_state, batch):
	global observed_durations

	component_upload_time_limit = 10
	
	
	components = { \
		"indexer", "docreceiver", "coordinator", "parser", "ocr", "persist", "event" \
		}
	states = { \
		"Archived", "Packaged", "Uploaded", "Submitted", "SentToOCR", "Parsed", "SentToPersist", "OCRed", "Coordinated", "PersistMapped", "PersistReduced", \
		"parser_hadoop_job", "Checked", "EventMapped", "EventReduced", "EventChecked", "ocr_hadoop_job", "persist_hadoop_job", "dataCheckAndRecovery_hadoop_job", "event_hadoop_job", "trace_hadoop_job", "qaAndRecoverEvent_hadoop_job" \
		}
	counts = { \
		"Archived": 13, "Packaged": 13, "Uploaded": 13, "Submitted": 1, "SentToOCR": 1, "Parsed": 13, "SentToPersist": 12, "OCRed": 1, "Coordinated": 1, "PersistMapped": 13, "PersistReduced": 13, \
		"parser_hadoop_job": 2, "Checked": 13, "EventMapped": 13, "EventReduced": 5, "EventChecked": 2, "ocr_hadoop_job": 2, "persist_hadoop_job": 4, "dataCheckAndRecovery_hadoop_job": 4, "event_hadoop_job": 4, "trace_hadoop_job": 8, "qaAndRecoverEvent_hadoop_job": 4 \
		}
	successes = { \
		"Archived": 13, "Packaged": 13, "Uploaded": 13, "Submitted": 1, "SentToOCR": 1, "Parsed": 13, "SentToPersist": 12, "OCRed": 1, "Coordinated": 1, "PersistMapped": 13, "PersistReduced": 13, \
		"parser_hadoop_job": 1, "Checked": 13, "EventMapped": 13, "EventReduced": 5, "EventChecked": 2, "ocr_hadoop_job": 1, "persist_hadoop_job": 2, "dataCheckAndRecovery_hadoop_job": 2, "event_hadoop_job": 2, "trace_hadoop_job": 4, "qaAndRecoverEvent_hadoop_job": 2 \
		}
	errors = { \
		"Archived": 0, "Packaged": 0, "Uploaded": 0, "Submitted": 0, "SentToOCR": 0, "Parsed": 0, "SentToPersist": 0, "OCRed": 0, "Coordinated": 0, "PersistMapped": 0, "PersistReduced": 0, \
		"parser_hadoop_job": 0, "Checked": 0, "EventMapped": 0, "EventReduced": 0, "EventChecked": 0, "ocr_hadoop_job": 0, "persist_hadoop_job": 0, "dataCheckAndRecovery_hadoop_job": 0, "event_hadoop_job": 0, "trace_hadoop_job": 0, "qaAndRecoverEvent_hadoop_job": 0 \
		}
	docs = { \
		"Archived": 13, "Packaged": 13, "Uploaded": 13, "Submitted": 13, "SentToOCR": 1, "Parsed": 13, "SentToPersist": 12, "OCRed": 1, "Coordinated": 0, "PersistMapped": 13, "PersistReduced": 13, \
		"parser_hadoop_job": 0, "Checked": 13, "EventMapped": 13, "EventReduced": 5, "EventChecked": 0, "ocr_hadoop_job": 0, "persist_hadoop_job": 0, "dataCheckAndRecovery_hadoop_job": 0, "event_hadoop_job": 0, "trace_hadoop_job": 0, "qaAndRecoverEvent_hadoop_job": 0 \
		}	
	durations = { \
		"Archived": 685, "Packaged": 97, "Uploaded": 1221, "Submitted": 60, "SentToOCR": 547, "Parsed": 9934, "SentToPersist": 9387, "OCRed": 206333, "Coordinated": 2, \
		"PersistMapped": 5448, "PersistReduced": 9089, "parser_hadoop_job": 60553, "Checked": 5095, "EventMapped": 44228, "EventReduced": 860, "EventChecked": 1081, "ocr_hadoop_job": 301006, "persist_hadoop_job": 121555, \
		"dataCheckAndRecovery_hadoop_job": 120613, "event_hadoop_job": 241290, "trace_hadoop_job": 242661, "qaAndRecoverEvent_hadoop_job": 120665 \
		}
	actual_durations = { \
		"Archived": 41, "Packaged": 1, "Uploaded": 1, "Submitted": 1, "SentToOCR": 1, "Parsed": 61, "SentToPersist": 1, "OCRed": 306, "Coordinated": 1, \
		"PersistMapped": 17, "PersistReduced": 52, "parser_hadoop_job": 2, "Checked": 2, "EventMapped": 113, "EventReduced": 1, "EventChecked": 60, "ocr_hadoop_job": 1, "persist_hadoop_job": 1, \
		"dataCheckAndRecovery_hadoop_job": 1, "event_hadoop_job": 1, "trace_hadoop_job": 1, "qaAndRecoverEvent_hadoop_job": 388 \
		}
	padded_durations = { \
		"Archived": 80, "Packaged": 10, "Uploaded": 10, "Submitted": 10, "SentToOCR": 10, "Parsed": 81, "SentToPersist": 10, "OCRed": 350, "Coordinated": 10, \
		"PersistMapped": 37, "PersistReduced": 72, "parser_hadoop_job": 10, "Checked": 10, "EventMapped": 133, "EventReduced": 10, "EventChecked": 80, "ocr_hadoop_job": 10, "persist_hadoop_job": 10, \
		"dataCheckAndRecovery_hadoop_job": 10, "event_hadoop_job": 10, "trace_hadoop_job": 10, "qaAndRecoverEvent_hadoop_job": 408 \
		}
				
	columns = {"state", "counts", "successes", "errors", "docs", "durations"}
	
	statuses = {"started", "inclomete", "fail", "success"}
			

	status = "started"	
	print ("-----------------------------------------------------------------------------")
	print ("Component        = %s" % p_module)
	print ("State            = %s" % p_state)
	print ("Batch            = %s" % batch)
	print ("Status           = %s" % status)
	print ("-----------------------------------------------------------------------------")
	
	
	#def batch_info_pipeline(args):
  	#	output(query("select stateName a_state, occurences b_count, successes c_successes, errors d_errors, numDocs e_docs, numPatients f_patients, numEvents g_events, duration h_duration, starttime.format() i_start, lasttime.format() j_last from AllBatchState where batchId = '%s' order by j_last" % (args[0],)))

	
	max_time = padded_durations[p_state]
	#count = 0
	print max_time
	#quit()
	start_time = time.time()  # remember when we started
	while (time.time() - start_time) < max_time :
		duration_time = (time.time() - start_time)
		print ("Module : State     = %s : %s" % (p_module, p_state))
		print ("Time passed        = %s" % (duration_time))
		print ("Time limit         = %s seconds\n" % (max_time))
		data = query("\
			SELECT stateName a_state, occurences b_count, successes c_successes, errors d_errors, numDocs e_docs, numPatients f_patients, \
			numEvents g_events, duration h_duration, starttime.format() i_start,  lasttime.format() j_last \
			FROM AllBatchState \
			WHERE batchId = '%s' and stateName = '%s'" % (batch, p_state))
		for row in data:
			print ("Documents actually %s = %d" % (p_state, row["b_count"]))
			print ("Documents expected %s = %d" % (p_state, counts[p_state]))
			################
			# SUCCESS ######
			################
			if (row["b_count"] == counts[p_state]) and (duration_time < max_time):
				print ("%d documents were successfully %s for batch %s completed in %s seconds ...\n" % (row["b_count"], p_state, batch, duration_time))
				max_time = 0
				observed_durations.update({str(p_module+" "+p_state): duration_time})
				#status = "success"
				#logDetailsIntoReport(p_module, p_state, batch, status, count, successes, errors, docs, patients, events, duration, start, last)
			################
			# FAILURE ######
			################	
			elif ((row["b_count"] < counts[p_state]) and (duration_time >= max_time)) or (row["d_errors"] > 0):
				print ("Time limit of %s exceeded maximum time of %s seconds - %d documents were %s ...\n" % (duration_time, max_time, row["b_count"], p_state))
				#status = "failure"
				#logDetailsIntoReport(p_module, p_state, batch, status, count, successes, errors, docs, patients, events, duration, start, last)
			
			
	if (max_time >= duration_time):
		print ("Time limit of %s seconds excedded maximum execution time of %s seconds. FAILED QA\n" % (duration_time, max_time))
		status = "incomplete"
		logDetailsIntoReport(p_module, p_state, batch, status, 0, 0, 0, 0, 0, 0, 0, 0, 0, duration_time)
	elif (row["b_count"] < counts[p_state]) or (row["d_errors"] > 0):
		print (">>> Specific Component Failure Occured ...\n")
		status = "fail"
		logDetailsIntoReport(p_module, p_state, batch, status, 0, 0, 0, 0, 0, 0, 0, 0, 0, duration_time)
	else:		
		print ("%d documents were successfully %s for batch %s completed in %s seconds ...\n" % (row["b_count"], p_state, batch, duration_time))	 	
		status = "success"
		logDetailsIntoReport(p_module, p_state, batch, status, row["b_count"], row["c_successes"], row["d_errors"], row["e_docs"], row["f_patients"], row["g_events"], row["h_duration"], row["i_start"], row["j_last"], duration_time)
		
		
	return (status)

#=========================================================================================

def generateReportDetails():
	global REPORT, cur, conn, BATCH, observed_durations
	states = { \
		"Archived", "Packaged", "Uploaded", "Submitted", "SentToOCR", "Parsed", "SentToPersist", \
		"OCRed", "Coordinated", "PersistMapped", "PersistReduced", \
		"parser_hadoop_job", "Checked", "EventMapped", "EventReduced", "EventChecked", "ocr_hadoop_job", "persist_hadoop_job", \
		"dataCheckAndRecovery_hadoop_job", "event_hadoop_job", "trace_hadoop_job", "qaAndRecoverEvent_hadoop_job" \
		}
	components = { \
		"indexer", "docreceiver", "coordinator", "parser", "ocr", "persist", "event" \
		}	
		
	print ("Start generating Report Details ...")
	print ("===================================================================================\n")
		
	
	modules_states = [ \
		["docreceiver", "Archived"], ["docreceiver", "Packaged"], ["docreceiver", "Uploaded"], ["docreceiver", "Submitted"], \
		["coordinator", "Coordinated"], \
		["parser", "Parsed"], ["parser", "SentToOCR"], ["parser", "SentToPersist"], \
		["ocr", "OCRed"], \
		["persist", "PersistMapped"], ["persist", "PersistReduced"], \
		["event", "EventMapped"], ["event", "EventReduced"], ["event", "EventChecked"], \
		["qa", "Checked"], \
		["jobs", "parser_hadoop_job"], ["jobs", "ocr_hadoop_job"], ["jobs", "persist_hadoop_job"], ["jobs", "event_hadoop_job"], \
		["jobs", "trace_hadoop_job"], ["job", "dataCheckAndRecovery_hadoop_job"], ["job", "qaAndRecoverEvent_hadoop_job"]]
		
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
	
	print ("\n===================================================================================")
	print ("End generating Report Details ...\n")				
	cur.close()
	conn.close()
	#quit()
	
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

#pauseForUploadToComplete()
#BATCH="370_PipelineSanityTestStaging_02132015185431"

connectToHive()

generateReportHeader()

generateReportDetails()

generateReportFooter()

emaiReport()

archiveReport()