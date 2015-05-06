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

os.system('clear')


# ============================ INITIALIZING GLOBAL VARIABLES VALUES ===============================================

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
elif ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "O")):
	# OREGON ==================
	USERNAME="oreg005"
	ORGID="10000351"
	PASSWORD="apixio.123"
	HOST="https://docreceiver-or.apixio.com"
	ENVIRONMENT="Oregon"			
else:
	# STAGING =====================
	USERNAME="sanitytest1"
	ORGID="370"
	PASSWORD="Hadoop.4522"
	HOST="https://stagedr.apixio.com:8443"
	ENVIRONMENT="Staging"
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
NUMBEROFDOCUMENTS=0

DOCUMENTS_TRANSMITTED=13
DOCUMENTS_TO_OCR=0
DOCUMENTS_TO_PERSIST=0

MANIFEST_FILE=""
GLOBAL_STATUS="success"
OPERATION=""
CATEGORY=""

# =================================================================================================================



def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)

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
	
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()
obj=json.loads(buf.getvalue())	
TOKEN=obj["token"]
# print (obj)

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

# ========================================================================= Assign Values =======================================================
FILES = os.listdir(DIR)

# FILE = FILES[0]

# print (FILES)
# print ('Processing files in: ', DIR);

print ("\nUploading ...\n")

# if (NUMBEROFDOCUMENTS > 0):
# elif:
#for DOCUMENTCOUNTER in range(NUMBEROFDOCUMENTS):

for FILE in FILES:
		import uuid
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
		import cStringIO
		import pycurl
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

		MANIFEST_FILE=MANIFEST_FILE+("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t02/22/14 02:02:37 AM\n") % (DOCUMENT_ID, SOURCE_SYSTEM, USERNAME, UUID, ORGANIZATION, ORGID, BATCH, FILE_FORMAT)


		#print (TOKEN), (ORGANIZATION), (ORGID), (CODE), (USER_ID), (S3_BUCKET), (ROLES), (TRACE_COLFAM), (DOCUMENT_ID)
		#print (PATIENT_ID), (PATIENT_ID_AA), (PATIENT_FIRST_NAME), (PATIENT_LAST_NAME), (PATIENT_MIDDLE_NAME), (PATIENT_DOB), (PATIENT_GENDER), (ORGANIZATION)
		#print (PRACTICE_NAME), (FILE_LOCATION), (FILE_FORMAT), (DOCUMENT_TYPE), (CREATION_DATE), (MODIFIED_DATE), (DESCRIPTION), (METATAGS), (SOURCE_SYSTEM)
		#print (TOKEN_URL), (UPLOAD_URL)
		#print (" ")
		#print (CATALOG_FILE)
		#print (" ")
		#print (MANIFEST_FILE)
		#print (" ")

# ========================================================== Finish by closing batch ======================================================================================


# print (MANIFEST_FILE)
	
print ("\nTOTAL NUMBER OF DOCUMENTS UPLOADED: %s\n" % (DOCUMENTCOUNTER));
print ("Closing Batch ...\n")
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
print ("Batch Closed, Upload Completed ...\n")
# ========================================================== Transmitting Manifest File ======================================================================================

# Currently this is only working on Staging
if ENVIRONMENT == "Staging":
	print ("Transmitting Manifest File ...\n")

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
	print ("Manifest file transmitted ...\n")


# =========================================================================================================================================================================

# print ("ORGID = %s") % ORGID
# print ("TEST_TYPE = %s") % TEST_TYPE
# print ("ENVIRONMANT = %s") % ENVIRONMENT
# print ("BATCHID = %s") % BATCHID
# print ("")
# print ("BATCH = %s") % BATCH
# MANIFEST_FILENAME=BATCH+"_manifest.txt"
# print ("")
# print ("UPLOAD_URL = %s") % UPLOAD_URL
# print ("TOKEN_URL = %s") % TOKEN_URL
# print ("USERNAME = %s") % USERNAME
# print ("PASSWORD = %s") % PASSWORD
# print ("HOST = %s") % HOST
# print ("DIR = %s") % DIR


# ================================ PAUSE FOR UPLOAD TO COMPLETE BEFORE PROCEEDING TO QUERIES ==============================================================================

PAUSE_LIMIT = 300
#Increased for the time being of cluster being 100% occupied ... 10-13-14 Igor
#PAUSE_LIMIT = 600


# wait for PAUSE_LIMIT seconds
print ("Pausing for %s seconds for all jobs to complete ...") % (PAUSE_LIMIT)
time.sleep(PAUSE_LIMIT)


# =========================================================================================================================================================================


# ============== Initialize variables and assign values for QA Report======================================================================================================



#================ CONTROLS TO WORK ON ONE SPECIFIC QUERY =========================================================================

QUERY_NUMBER=18
PROCESS_ALL_QUERIES=bool(1)

#=================================================================================================================================


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
# RECEIVERS="ishekhtman@apixio.com"
RECEIVERS="eng@apixio.com"


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


conn = pyhs2.connect(host='54.149.166.25',
                   port=10000,
                   authMechanism="PLAIN",
                   user='hive',
                   password='',
                   database='default')

cur = conn.cursor()



# print ("ORGID = %s") % ORGID
# print ("TEST_TYPE = %s") % TEST_TYPE
# print ("ENVIRONMANT = %s") % ENVIRONMENT
# print ("BATCHID = %s") % BATCHID
# print ("")
# print ("BATCH = %s") % BATCH
# print ("")
# print ("UPLOAD_URL = %s") % UPLOAD_URL
# print ("TOKEN_URL = %s") % TOKEN_URL
# print ("USERNAME = %s") % USERNAME
# print ("PASSWORD = %s") % PASSWORD
# print ("HOST = %s") % HOST
# print ("DIR = %s") % DIR
# print ("")
# print ("INDEXERLOGFILE = %s") % INDEXERLOGFILE
# print ("DOCRECEIVERLOGFILE = %s") % DOCRECEIVERLOGFILE
# print ("COORDINATORLOGFILE = %s") % COORDINATORLOGFILE
# print ("PARSERLOGFILE = %s") % PARSERLOGFILE
# print ("OCRLOGFILE = %s") % OCRLOGFILE
# print ("PERSISTLOGFILE = %s") % PERSISTLOGFILE


# time.sleep(15)


# for testing purposes this is a non-existing batch
# BATCH="190_SanityTestStaging_022220020236"
print (BATCH)
# time.sleep(3)

# print ("Good Batch - 190_SanityTestStaging_022214020236")
# print (" ")
# print ("Batch - %s") % BATCH
# time.sleep(15)

# This should fail all scripts. Used for testing purposes only
# DOCUMENTCOUNTER = 21


print ("Assigning queue name to hive ...")
cur.execute("""SET mapred.job.queue.name=hive""")

print ("Obtaining operation and category...")
cur.execute("""SELECT get_json_object(line, '$.submit.post.operation') as operation, \
	get_json_object(line, '$.submit.post.category') as category \
	FROM %s \
	WHERE \
	get_json_object(line, '$.submit.post.batchid') = '%s'""" %(DOCRECEIVERLOGFILE, BATCH))
ROW = 0	
for i in cur.fetch():
	ROW = ROW + 1
	print i
	REPORT = REPORT+"Operation: <b>"+str(i[0])+"</b><BR>"
	REPORT = REPORT+"Category: <b>"+str(i[1])+"</b><BR><BR>"		

# ===================================================================================================================================
# =============================== INDEXER related queries ===========================================================================
# ===================================================================================================================================

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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		print ("QUERY 1 FAILED")
		COMPONENT_STATUS="FAILED"


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
		ROW = ROW + 1
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
		COMPONENT_STATUS="FAILED"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"

REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== DOC-RECEIVER related queries ======================================================================
# ===================================================================================================================================

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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		print ("QUERY 3 FAILED")
		COMPONENT_STATUS="FAILED"



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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		print ("QUERY 4 FAILED")
		COMPONENT_STATUS="FAILED"


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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		print ("QUERY 5 FAILED")
		COMPONENT_STATUS="FAILED"



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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"&nbsp;-&nbsp;</td><td>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0', '0']
	REPORT = REPORT+"</table><br>"
	if int(i[1]) < DOCUMENTCOUNTER:
		print ("QUERY 6 FAILED")
		COMPONENT_STATUS="FAILED"



if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== COORDINATOR related queries =======================================================================
# ===================================================================================================================================


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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='left'>"+str(i[1])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[2])+"</td></tr>"
		if (str(i[2]).lower() == 'error'):
			print ("QUERY 7 FAILED")
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY 7 FAILED")
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"	
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== PARSER related queries ============================================================================
# ===================================================================================================================================

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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'></td></tr>"
		TAGED_TO_OCR = int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if TAGED_TO_OCR < DOCUMENTS_TO_OCR:
		print ("QUERY 8 FAILED")
		COMPONENT_STATUS="FAILED"



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
		ROW = ROW + 1
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
		COMPONENT_STATUS="FAILED"



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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0', 'success']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		print ("QUERY 10 FAILED")
		COMPONENT_STATUS="FAILED"



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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"&nbsp;-&nbsp;</td><td>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY 11 FAILED")
		COMPONENT_STATUS="FAILED"



if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== OCR related queries ===============================================================================
# ===================================================================================================================================

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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		COMPONENT_STATUS="FAILED"
		print ("QUERY 12 FAILED")
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTS_TO_OCR:
		COMPONENT_STATUS="FAILED"


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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'>"+str(i[1])+"</td><td align='center'>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY 13 FAILED")
		COMPONENT_STATUS="FAILED"




if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== PERSIST related queries ===========================================================================
# ===================================================================================================================================

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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0', 'success']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		print ("QUERY 14 FAILED")
		COMPONENT_STATUS="FAILED"



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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'>"+str(i[1])+"</td><td align='center'>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY 15 FAILED")
		COMPONENT_STATUS="FAILED"




if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"
REPORT = REPORT+"<br><br>"


# ===================================================================================================================================
# =============================== EVENTS related queries ===========================================================================
# ===================================================================================================================================

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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>&nbsp;"+str(i[0])+"&nbsp;</td></tr>"
	if (ROW == 0) :
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
	if i[0] is None:
		COMPONENT_STATUS="FAILED"
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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>&nbsp;"+str(i[0])+"&nbsp;</td></tr>"
	if (ROW == 0) :
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
	if i[0] is None:
		COMPONENT_STATUS="FAILED"
	elif (int(i[0]) <> TOTALEVENTMAPPER):
		print ("QUERY 17 FAILED")
		COMPONENT_STATUS="FAILED"		
		
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
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>&nbsp;"+str(i[0])+"&nbsp;</td><td align='center'>&nbsp;"+str(i[1])+"&nbsp;</td></tr>"
		if str(i[1]) == "error":
			COMPONENT_STATUS="FAILED"
	if (ROW == 0) :
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
	GLOBAL_STATUS="success"
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
	GLOBAL_STATUS="failed"
REPORT = REPORT+"<br><br>"


cur.close()
conn.close()

# ===================================================================================================================================
# ===================================================================================================================================
# ===================================================================================================================================


END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
REPORT = REPORT+"<table><tr><td><br>Start of %s - <b>%s</b></td></tr>" % (BATCH, START_TIME)
REPORT = REPORT+"<tr><td>End of %s - <b>%s</b></td></tr>" % (BATCH, END_TIME)
TIME_END = time.time()
TIME_TAKEN = TIME_END - TIME_START
hours, REST = divmod(TIME_TAKEN,3600)
minutes, seconds = divmod(REST, 60)
REPORT = REPORT+"<tr><td>Test Duration: <b>%s hours, %s minutes, %s seconds</b><br></td></tr>" % (hours, minutes, seconds)
REPORT = REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"


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
