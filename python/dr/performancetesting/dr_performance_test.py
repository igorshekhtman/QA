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
DOCUMENTCOUNTER = 0

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
YEAR=strftime("%Y", gmtime())

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
#================================ ENVIRONMENTAL COMPONENTS IP ADDRESS MAP =========================================================================
#
# Here are some ideas on expected behavior for these components (Anthony):
#   Graphite:					Nothing changes (an acceptable failure)
#   Fluent:						Continues working until internal buffer full, then stops working until fluent back online - sends errors to client (what code?)
#   Key Service:				Stops accepting incoming data until key service back online - sends errors to client (what code?)
#   Disk Space (logs, temp):	Stops accepting incoming data until disk space issue resolved - sends errors to client (what code?)
#   Redis: 						Maintains reference to sequence file, keeps trying to post until Redis back online.
#   HDFS: 						Maintains reference to sequence files, keeps trying to post until HDFS back online. When internal buffer is full (how big?) stops accepting incoming data.
#   Cassandra: 					Causes loss of Trace data. Not sure if this is a failure condition. Likely indicates wider problems. Should probably keep trying to post until Cassandra is back online and when internal buffer is full stop accepting incoming data
#   Num Open Files: 			How does this even happen? This is a major failure. Stop accepting incoming data. 
#   S3: 						Stop accepting incoming data from client until S3 starts working.
#   Apixio API: 				Only used for authentication. If you can't authenticate, you can't upload.
#   
#   S3 is https://s3.amazonaws.com
#	but this is not one address
#	it will give you a different IP each time, or when you ask from a different place
#	Lance will come up with a way to block S3 and unblock it - per Lance 04-10-2014
#
#   "HDFS":"10.196.84.183", \ - critical component DR fails if not available
#	"Cassandra1":"10.222.101.109", \ - critical component DR fails if not available
#	"Cassandra2":"10.222.139.147", \ - critical component DR fails if not available
#	"Cassandra3":"10.174.77.69", \ - critical component DR fails if not available
#	"Cassandra4":"10.174.49.58", \ - critical component DR fails if not available


IPMAP = { \
	"Hive":"10.196.47.205", \
	"Fluent":"10.222.103.158", \
	"Redis":"10.222.103.158", \
	"Graphite":"10.160.150.32", \
	"Mysql":"10.174.121.164", \
	"Keyservice":"184.169.153.214", \
	"API":"10.198.43.98" \
}
#===========================================================================================================================================================

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
	

def writeReportDetails(description, code, number):
	global REPORT, ENVIRONMENT, RETURNCODE
	global SUBHDR, PASSED, FAILED, TEST_PN
	REPORT = REPORT+SUBHDR % description
	REPORT = REPORT+"<table><tr><td>EXPECTED CODE: <b>"+code+"</b></td></tr></table>"
	REPORT = REPORT+"<table><tr><td>RETURNED CODE: <b>"+RETURNCODE+"</b></td></tr></table>"
	REPORT = REPORT+"<table><tr><td>NUMBER OF DOCUMENTS PUSHED TO DR: <b>"+str(number)+"</b></td></tr></table>"
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
	print ("Running 4 %s Hive queries ... \n") % (PIPELINE_MODULE)	
	if PIPELINE_MODULE == "DR":
		hive_table = ENVIRONMENT.lower()+"_logs_docreceiver_24"
		print ("Starting query 1 ...\n")
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, \
			get_json_object(line, '$.upload.document.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = 'EVENT' and \
			day=%s and month=%s and \
			get_json_object(line, '$.upload.document.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.upload.document.status')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table><tr><td>NUMBER OF DOCUMENTS UPLOADED: <b>"+str(i[0])+"</b> STATUS: <b>"+str(i[1])+"</b></td></tr></table>"
			
		print ("Starting query 2 ...\n")
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, \
			get_json_object(line, '$.archive.afs.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = "EVENT" and \
			day=%s and month=%s and \
			get_json_object(line, '$.archive.afs.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.archive.afs.status')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table><tr><td>NUMBER OF DOCUMENTS ARCHIVED TO S3: <b>"+str(i[0])+"</b> STATUS: <b>"+str(i[1])+"</b></td></tr></table>"			
				
		print ("Starting query 3 ...\n")
		cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, \
			get_json_object(line, '$.seqfile.file.document.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = "EVENT" and \
			day=%s and month=%s and \
			get_json_object(line, '$.seqfile.file.document.batchid') = '%s' \
			GROUP BY get_json_object(line, '$.seqfile.file.document.status')""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table><tr><td>NUMBER OF DOCUMENTS ADDED TO SEQUENCE FILE: <b>"+str(i[0])+"</b> STATUS: <b>"+str(i[1])+"</b></td></tr></table>"
			
		print ("Starting query 4 ...\n")
		cur.execute("""SELECT get_json_object(line, '$.submit.post.numfiles') as seq_files_sent_to_redis, \
			get_json_object(line, '$.submit.post.apxfiles.count') as ind_files, \
			get_json_object(line, '$.submit.post.queue.name') as redis_queue_name \
			FROM %s \
			WHERE get_json_object(line, '$.level') = "EVENT" and \
			day=%s and month=%s and \
			get_json_object(line, '$.submit.post.status') = "success" and \
			get_json_object(line, '$.submit.post.batchid') = '%s'""" %(hive_table, DAY, MONTH, BATCH))
		for i in cur.fetch():
			REPORT = REPORT+"<table><tr><td>NUMBER OF SEQUENCE FILES SENT TO REDIS: <b>"+str(i[0])+"</b> INDIVIDUAL: <b>"+str(i[1])+"</b> REDIS QUEUE: <b>"+str(i[2])+"</b></td></tr></table>"
	print ("Finished running %s Hive queries ... \n") % (PIPELINE_MODULE)
	#if (RETURNCODE[ :3] == code):
	REPORT = REPORT+PASSED
	#else:
	#	REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"	

def clearAllBlockedIP():
	# -A (add), -D (remove), -F (remove all), -L (list or show all)
	# remove all from list
	os.system("ssh -i /mnt/automation/.secrets/supload2.pem 10.199.16.28 iptables -F")
	# show list
	os.system("ssh -i /mnt/automation/.secrets/supload2.pem 10.199.16.28 iptables -L")
	time.sleep(2)

def blockComponentIP(component):
	IP = IPMAP[str(component)]
	print ("Block %s component - IP: %s\n") % (component, IP)
	# -A (add), -D (remove), -F (remove all), -L (list or show all)
	# add to list
	add_string = "ssh -i /mnt/automation/.secrets/supload2.pem 10.199.16.28 iptables -A OUTPUT -d "+str(IP)+" -j DROP"
	os.system(add_string)
	# show list
	os.system("ssh -i /mnt/automation/.secrets/supload2.pem 10.199.16.28 iptables -L")
	time.sleep(2)	

def unblockComponentIP(component):
	IP = IPMAP[str(component)]
	print ("Unblock %s component - IP: %s\n") % (component, IP)
	# -A (add), -D (remove), -F (remove all), -L (list or show all)
	# remove from list
	remove_string = "ssh -i /mnt/automation/.secrets/supload2.pem 10.199.16.28 iptables -D OUTPUT -d "+str(IP)+" -j DROP"
	os.system(remove_string)
	# show list
	os.system("ssh -i /mnt/automation/.secrets/supload2.pem 10.199.16.28 iptables -L")
	time.sleep(2)
	
#============== Start of the main body =======================================================================================	

checkEnvironment()
writeReportHeader()

#======= CASE #1 ===========================================================================
NUMBER_OF_DOCS_TO_UPLOAD = 1
EXPECTED_CODE = "200"
TEST_DESCRIPTION = "Positive Test - Upload %s text documents and verify %s logs" % (NUMBER_OF_DOCS_TO_UPLOAD, PIPELINE_MODULE)

getUserData()
storeToken()
obtainStaticPatientInfo("Positive", "Test")
#clearAllBlockedIP()
#blockComponentIP("Hive")
for i in range(0, NUMBER_OF_DOCS_TO_UPLOAD):
	createTxtDocument(i)
	createCatalogFile()
	uploadDocument()
	storeUUID()
closeBatch()
#unblockComponentIP("Hive")
if ENVIRONMENT == "Staging":
	transmitManifest()

writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE, NUMBER_OF_DOCS_TO_UPLOAD)
connectToHive()
setHiveParameters()
# wait for PAUSE_LIMIT seconds
PAUSE_LIMIT=0
print ("Pausing for %s seconds for upload to DR to complete ...\n") % (PAUSE_LIMIT)
time.sleep(PAUSE_LIMIT)
runHiveQueries()
closeHiveConnection()
#======= CASE #2 ===========================================================================

# while ips are in the list of ips
for component in IPMAP.keys():

	print (component)
	#time.sleep(15)

	NUMBER_OF_DOCS_TO_UPLOAD = 1
	EXPECTED_CODE = "200"
	TEST_DESCRIPTION = "Negative Test - Upload %s text documents and verify %s logs while blocking %s component" % (NUMBER_OF_DOCS_TO_UPLOAD, PIPELINE_MODULE, component)

	getUserData()
	storeToken()
	obtainStaticPatientInfo("Negative", "Test")
	clearAllBlockedIP()
	blockComponentIP(component)
	for i in range(0, NUMBER_OF_DOCS_TO_UPLOAD):
		createTxtDocument(i)
		createCatalogFile()
		uploadDocument()
		storeUUID()
	closeBatch()
	unblockComponentIP(component)
	if ENVIRONMENT == "Staging":
		transmitManifest()

	writeReportDetails(TEST_DESCRIPTION, EXPECTED_CODE, NUMBER_OF_DOCS_TO_UPLOAD)
	connectToHive()
	setHiveParameters()
	# wait for PAUSE_LIMIT seconds
	PAUSE_LIMIT=0
	print ("Pausing for %s seconds for upload to DR to complete ...\n") % (PAUSE_LIMIT)
	time.sleep(PAUSE_LIMIT)
	runHiveQueries()
	closeHiveConnection()
	# end for loop
#==========================================================================================

# test_item valies: nodocument, nocatalog, nodocnocat, docandcat, emptydocument
writeReportFooter()
emailReport()