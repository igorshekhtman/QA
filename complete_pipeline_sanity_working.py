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


TEST_TYPE="SanityTest"

# Environment for SanityTest is passed as a paramater. Assign Staging if none or wrong is passed
if len(sys.argv) < 2:
	ENVIRONMENT="Staging"
else:
	ENVIRONMENT=str(sys.argv[1])

if ENVIRONMENT == "":
	ENVIRONMENT="Staging"
elif ENVIRONMENT == "Production":
	ENVIRONMENT="Production"
elif ENVIRONMENT == "Staging":
	ENVIRONMENT="Staging"
else:
	ENVIRONMENT="Staging"

if ENVIRONMENT == "Staging":
	USERNAME="apxdemot0182"
	ORGID="190"
	PASSWORD="Hadoop.4522"
	HOST="https://supload.apixio.com:8443"
if ENVIRONMENT == "Production":
	USERNAME="apxdemot0138"
	ORGID="10000279"
	PASSWORD="Hadoop.4522"
	HOST="https://dr.apixio.com:8443"


print ("ENVIRONMANT = %s") % ENVIRONMENT


DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())

# batchpostfix=$(date +'%m%d%y%H%M%S')


UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID)
TOKEN_URL="%s/auth/token/" % (HOST)


#BATCHID=strftime("%d%m%Y%H%M%S", gmtime())
#bad - does not exist in any logs
#BATCHID="061914020232"
#old - missing pipeline logs but not indexer
#BATCHID="021914020236"
#good
#BATCHID="022114020236"

BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
MANIFEST_FILENAME=BATCH+"_manifest.txt"

DOCUMENTCOUNTER=0
NUMBEROFDOCUMENTS=0

DOCUMENTS_TRANSMITTED=20
MANIFEST_FILE=""

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

print ("Uploading ...")
print (" ")

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
print (" ")	
print ("TOTAL NUMBER OF DOCUMENTS UPLOADED: %s" % (DOCUMENTCOUNTER));
print (" ")
print ("Closing Batch ...")
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
print (" ")
print ("Batch Closed, Upload Completed ...")
# ========================================================== Transmitting Manifest File ======================================================================================
print (" ")
print ("Transmitting Manifest File ...")
print (" ")
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
print ("Manifest file transmitted ...")
print (" ")

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

# wait for 5 minutes - 60x6=300
time.sleep(300)
# time.sleep(15)

# =========================================================================================================================================================================


# ============== Initialize variables and assign values for QA Report======================================================================================================



#================ CONTROLS TO WORK ON ONE SPECIFIC QUERY =========================================================================

QUERY_NUMBER=13
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


SENDER="donotreply@apixio.com"
RECEIVERS="eng@apixio.com"


REPORT = """From: Apixio QA <QA@apixio.com>
To: Engineering <eng@apixio.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Pipeline QA Report Staging batchID %s - %s

<h1>Apixio Pipeline QA Report</h1>
Date & Time: <b>%s</b><br>
Test type: <b>%s</b><br>
Enviromnent: <b>%s</b><br>
OrgID: <b>%s</b><br>
BatchID: <b>%s</b><br>
User name: <b>%s</b><br><br>
""" % (BATCH, CUR_TIME, CUR_TIME, TEST_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)


conn = pyhs2.connect(host='10.196.47.205',
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



# BATCH="190_SanityTestStaging_022214020236"

# print ("Good Batch - 190_SanityTestStaging_022214020236")
# print (" ")
# print ("Batch - %s") % BATCH
# time.sleep(15)


print ("Assigning queue name to hive ...")
cur.execute("""SET mapred.job.queue.name=hive""")

# ===================================================================================================================================
# =============================== INDEXER related queries ===========================================================================
# ===================================================================================================================================

REPORT = REPORT+SUBHDR % "INDEXER"

if (QUERY_NUMBER == 1) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents transmitted"
	print ("Running INDEXER query #1 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT count(DISTINCT apixiouuid) as total_number_of_documents_indexer \
		FROM %s \
		WHERE batchid = '%s'""" %(INDEXERLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW=ROW+1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTCOUNTER:
		COMPONENT_STATUS="FAILED"


if (QUERY_NUMBER == 2) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Document type(s) transmitted"
	print ("Running INDEXER query #2 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT filetype, count(filetype) as qty_each \
		FROM %s \
		WHERE batchid = '%s' \
		GROUP BY filetype""" %(INDEXERLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	TOTAL = 0
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"</td></tr>"
		TOTAL = TOTAL + int(i[1])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if TOTAL < DOCUMENTCOUNTER:
		COMPONENT_STATUS="FAILED"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"

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
		WHERE get_json_object(line, '$.level') = 'EVENT' and \
		get_json_object(line, '$.upload.document.batchid') = '%s' \
		GROUP BY get_json_object(line, '$.upload.document.status')""" %(DOCRECEIVERLOGFILE,BATCH))
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
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 4 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents archived to S3"
	print ("Running DOC-RECEIVER query #4 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, \
		get_json_object(line, '$.archive.afs.status') as status \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.archive.afs.batchid') = '%s' \
		GROUP BY get_json_object(line, '$.archive.afs.status')""" %(DOCRECEIVERLOGFILE,BATCH))
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
		COMPONENT_STATUS="FAILED"


if (QUERY_NUMBER) == 5 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents added to sequence file(s)"
	print ("Running DOC-RECEIVER query #5 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, \
		get_json_object(line, '$.seqfile.file.document.status') as status \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.seqfile.file.document.batchid') = '%s' \
		GROUP BY get_json_object(line, '$.seqfile.file.document.status')""" %(DOCRECEIVERLOGFILE,BATCH))
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
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 6 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of seq. files and individual documents sent to redis"
	print ("Running DOC-RECEIVER query #6 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT get_json_object(line, '$.submit.post.numfiles') as seq_files_sent_to_redis, \
		get_json_object(line, '$.submit.post.apxfiles.count') as ind_files, \
		get_json_object(line, '$.submit.post.queue.name') as redis_queue_name \
		FROM %s \
		WHERE get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.submit.post.status') = "success" and \
		get_json_object(line, '$.submit.post.batchid') = '%s'""" %(DOCRECEIVERLOGFILE,BATCH))
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
		COMPONENT_STATUS="FAILED"



if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
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
		get_json_object(line, '$.job.context.batchID') = '%s' and \
		get_json_object(line, '$.job.status') is not null and \
		get_json_object(line, '$.job.status') <> 'start' \
		GROUP BY get_json_object(line, '$.job.status'), get_json_object(line, '$.job.activity')""" %(COORDINATORLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='left'>"+str(i[1])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['1', ' ', 'error']		
	REPORT = REPORT+"</table><br>"
	if (str(i[2]) == 'error') and (int(i[0]) > 0):
		COMPONENT_STATUS="FAILED"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
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
		get_json_object(line, '$.tag.ocr.status') = "success" and \
		get_json_object(line, '$.batchId') = '%s'""" %(PARSERLOGFILE,BATCH))
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
	if TAGED_TO_OCR == 0:
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 9 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs tagged to Persist"
	print ("Running PARSER query #9 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_Persist \
		FROM %s \
		WHERE \
		get_json_object(line, '$.tag.persist.status') = "success" and \
		get_json_object(line, '$.batchId') = '%s'""" %(PARSERLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	TAGED_TO_PERSIST=0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'></td></tr>"
		TAGED_TO_PERSIST = int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if (TAGED_TO_OCR + TAGED_TO_PERSIST) < DOCUMENTCOUNTER:
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 10 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs succeeded or failed"
	print ("Running PARSER query #10 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Parser_distinct_UUIDs, \
		get_json_object(line, '$.status') as status \
		FROM %s \
		WHERE \
		get_json_object(line, '$.batchId') = '%s' \
		GROUP BY get_json_object(line, '$.status')""" %(PARSERLOGFILE,BATCH))
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
	if (int(i[0]) < DOCUMENTS_TRANSMITTED) and (str(i[1]) == "success") :
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 11 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of Parser errors, class-name and specific error messages"
	print ("Running PARSER query #11 - retrieve %s ...") %  (QUERY_DESC)
	cur.execute("""SELECT get_json_object(line, '$.error.message') as parser_error_message, \
		get_json_object(line, '$.className') as class_name, \
		round((get_json_object(line, '$.file.bytes') / 1024 / 1024),2) as file_size_mb \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
		get_json_object(line, '$.jobname') LIKE '%s%%'""" %(PARSERLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td><td align='center'>"+str(i[1])+"&nbsp;-&nbsp;</td><td>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"



if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
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
		get_json_object(line, '$.batchId') = '%s' \
		GROUP BY get_json_object(line, '$.status')""" %(OCRLOGFILE,BATCH))
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
	if int(i[0]) < TAGED_TO_OCR:
		COMPONENT_STATUS="FAILED"


if (QUERY_NUMBER) == 13 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of OCR errors and specific error messages"
	print ("Running PERSIST query #13 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT get_json_object(line, '$.error.message') as ocr_error_message, \
		get_json_object(line, '$.className') as class_name, \
		get_json_object(line, '$.file.bytes') as file_size_bytes \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
		get_json_object(line, '$.batchId') = '%s'""" %(OCRLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'>"+str(i[1])+"</td><td align='center'>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"



if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
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
		get_json_object(line, '$.batchId') = '%s' \
		GROUP BY get_json_object(line, '$.status')""" %(PERSISTLOGFILE,BATCH))
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
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 15 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of Persist errors and specific error messages"
	print ("Running PERSIST query #15 - retrieve %s ...") % (QUERY_DESC)
	cur.execute("""SELECT get_json_object(line, '$.error.message') as persist_error_message, \
		get_json_object(line, '$.className') as class_name, \
		get_json_object(line, '$.file.bytes') as file_size_bytes \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
		get_json_object(line, '$.batchId') = '%s'""" %(PERSISTLOGFILE,BATCH))
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"</td><td align='center'>"+str(i[1])+"</td><td align='center'>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"



if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
	COMPONENT_STATUS="PASSED"
REPORT = REPORT+"<br><br>"

cur.close()
conn.close()

# ===================================================================================================================================
# ===================================================================================================================================
# ===================================================================================================================================


REPORT=REPORT+"<table><tr><td><br>End of %s - %s QA report<br><br></td></tr>" % (BATCH, CUR_TIME)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"


# CONTENT="Subject: %s<br><br>%s" % (SUBJECT, REPORT)
s=smtplib.SMTP()
s.connect("smtp.gmail.com",587)
s.starttls()
s.login("donotreply@apixio.com", "apx.mail47")
# s.sendmail(SENDER, RECEIVERS, CONTENT)	        
s.sendmail(SENDER, RECEIVERS, REPORT)	
print "Report completed, successfully sent email to %s ..." % (RECEIVERS)
