import pyhs2
import os
import time
import datetime
import sys
import subprocess
from time import gmtime, strftime, localtime
import pycurl
import io
import urllib
import urllib2
import urlparse
import json
import re
import smtplib
import string
from datetime import datetime

os.system('clear')


# ============================ INITIALIZING GLOBAL VARIABLES VALUES ===============================================

TEST_TYPE="SanityTest"
REPORT_TYPE="Daily engineering QA"

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


ENVIRONMENT = "Production"
LOGTYPE = "epoch"

print ("Version 1.0.0")
print ("ENVIRONMANT = %s") % ENVIRONMENT
print ("LOGTYPE = %s") % LOGTYPE


DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
TIMESTAMP=strftime("%s", gmtime())
DATESTAMP=strftime("%m/%d/%y %r", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
DAYSBACK=1
CURDAY=("%d", gmtime())
CURMONTH=("%m", gmtime())
DATERANGE=""


CURDAY=gmtime().tm_mday
CURMONTH=gmtime().tm_mon

print ("CURDAY = %s") % CURDAY
print ("CURMONTH = %s") % CURMONTH


BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID

DOCUMENTCOUNTER=0
NUMBEROFDOCUMENTS=0

DOCUMENTS_TRANSMITTED=20
DOCUMENTS_TO_OCR=0
DOCUMENTS_TO_PERSIST=0


QUERY_DESC=""
COMPONENT_STATUS="PASSED"


INDEXERLOGFILE="indexer_manifest_epoch"
DOCRECEIVERLOGFILE=ENVIRONMENT.lower()+"_logs_docreceiver_"+LOGTYPE
COORDINATORLOGFILE=ENVIRONMENT.lower()+"_logs_coordinator_"+LOGTYPE
PARSERLOGFILE=ENVIRONMENT.lower()+"_logs_parserjob_"+LOGTYPE
OCRLOGFILE=ENVIRONMENT.lower()+"_logs_ocrjob_"+LOGTYPE
PERSISTLOGFILE=ENVIRONMENT.lower()+"_logs_persistjob_"+LOGTYPE

ORGID="N/A"
BATCHID="N/A"
USERNAME="N/A"


#======== obtain day and month for previous from current day and month ===========================================

for C in range(0, DAYSBACK):
	if DATERANGE == "":
		DATERANGE="(MONTH=CURMONTH and DAY=CURDAY)"
	else:
		DATERANGE="DATERANGE or (MONTH=CURMONTH and DAY=CURDAY)"

	CURDAY=(CURDAY-1)
	if (CURDAY == 0):
		CURMONTH=(CURMONTH - 1)
		if ( CURMONTH == 0):
			CURMONTH=12

		if (( CURMONTH == 4 ) or ( CURMONTH == 6 ) or ( CURMONTH == 9 ) or ( CURMONTH == 11 )):
			CURDAY=30
		else: 
			if ( CURMONTH == 2 ):
				curDay=28
			else:
				curDay=31
			
#============ adjust day and month of the report =================================================================

DAY=CURDAY
MONTH=CURMONTH
print ("DAY: %s") % DAY
print ("MONTH: %s") % MONTH
print ("ENVIRONMANT = %s") % ENVIRONMENT
print ("CUR_TIME = %s") % CUR_TIME
#time.sleep(3)

#===================== ORGID - ORGNAME MAP ========================================================================
# ORGID="10000247"

ORGMAP = { \
	"10000230":"Sutter Health", \
	"10000232":"MMG", \
	"10000235":"GWU", \
	"10000236":"PMGV", \
	"10000237":"PHP", \
	"10000246":"CCHCA", \
	"10000247":"EHR Integration Services", \
	"10000248":"Apixio", \
	"10000249":"Apixio", \
	"10000250":"onlok", \
	"10000251":"PipelineTest3", \
	"10000252":"PipelineTest4", \
	"10000253":"RPN", \
	"10000254":"Pipeline Test5", \
	"10000255":"Pipeline Test6", \
	"10000256":"Apixio Pipeline Test 7", \
	"10000257":"Apixio Pipeline Test 8", \
	"10000259":"Monarch", \
	"10000260":"New Temple", \
	"10000261":"org1", \
	"10000262":"United Health Services", \
	"10000263":"CCHCA", \
	"10000264":"HCC Optimizer Demo", \
	"10000265":"Prosper Care Health", \
	"10000268":"Apixio", \
	"10000270":"Monarch", \
	"10000271":"org0001", \
	"10000272":"org0002", \
	"10000275":"org0005", \
	"10000278":"Hill Physicians", \
	"10000279":"org0138", \
	"10000280":"Prosper Care Health", \
	"10000281":"Prosperity Health Care", \
	"10000282":"Apixio Coder Training", \
	"10000283":"RMC [Test]", \
	"10000284":"RMC", \
	"10000285":"Scripps [Test]", \
	"10000286":"Scripps", \
	"10000288":"UHS", \
}

# print ORGMAP[ORGID]
#===================================================================================================================

#ORGID="10000246"
#print orgmap(ORGID)
#time.sleep(30)


def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)


#================ CONTROLS TO WORK ON ONE SPECIFIC QUERY ===============================================================================================

QUERY_NUMBER=8
PROCESS_ALL_QUERIES=bool(1)

#========================================================================================================================================================


PASSED="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"

# =============================== REPORT SENDER and RECEIVER CONFIGURATION ==============================================================================

SENDER="donotreply@apixio.com"
# RECEIVERS="ishekhtman@apixio.com"
RECEIVERS="eng@apixio.com"


REPORT = """From: Apixio QA <QA@apixio.com>
# TO: Engineering <ishekhtman@apixio.com, alarocca@apixio.com, aaitken@apixio.com, jschneider@apixio.com, nkrishna@apixio.com, lschneider@apixio.com>
To: Engineering <eng@apixio.com>
# To: Igor <ishekhtman@apixio.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Daily %s Pipeline QA Report - %s

<h1>Apixio Pipeline QA Report</h1>
Date & Time: <b>%s</b><br>
Report type: <b>%s</b><br>
Enviromnent: <b>%s</b><br>
OrgID: <b>%s</b><br>
BatchID: <b>%s</b><br>
User name: <b>%s</b><br><br>
""" % (ENVIRONMENT, CUR_TIME, CUR_TIME, REPORT_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)


conn = pyhs2.connect(host='10.196.47.205',
                   port=10000,
                   authMechanism="PLAIN",
                   user='hive',
                   password='',
                   database='default')

cur = conn.cursor()


print ("Assigning queue name to hive ...")
cur.execute("""SET mapred.job.queue.name=hive""")


# ===================================================================================================================================
# =============================== DOC-RECEIVER related queries ======================================================================
# ===================================================================================================================================

REPORT = REPORT+SUBHDR % "DOC-RECEIVER"

if (QUERY_NUMBER) == 3 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents uploaded"
	print ("Running DOC-RECEIVER query #3 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, \
		get_json_object(line, '$.upload.document.status') as status, \
		get_json_object(line, '$.upload.document.orgid') as orgid \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.upload.document.docid') is not null and \
		day=%s and month=%s \
		GROUP BY \
		get_json_object(line, '$.upload.document.status'), \
		get_json_object(line, '$.upload.document.orgid')""" %(DOCRECEIVERLOGFILE, DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	UPLOADED_DR = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;-&nbsp;</td> \
			<td>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
		UPLOADED_DR = UPLOADED_DR + int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	#if int(i[0]) < DOCUMENTCOUNTER:
		#print ("QUERY 3 FAILED")
		#COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 4 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents archived to S3"
	print ("Running DOC-RECEIVER query #4 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, \
		get_json_object(line, '$.archive.afs.status') as status, \
		get_json_object(line, '$.archive.afs.orgid') as orgid \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.archive.afs.docid') is not null and \
		day=%s and month=%s \
		GROUP BY \
		get_json_object(line, '$.archive.afs.status'), \
		get_json_object(line, '$.archive.afs.orgid')""" %(DOCRECEIVERLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	ARCHTOS3 = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;-&nbsp;</td> \
			<td>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
		ARCHTOS3 = ARCHTOS3 + int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if ARCHTOS3 < UPLOADED_DR:
		print ("QUERY 4 FAILED")
		COMPONENT_STATUS="FAILED"


if (QUERY_NUMBER) == 5 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents added to sequence file(s)"
	print ("Running DOC-RECEIVER query #5 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, \
		get_json_object(line, '$.seqfile.file.document.status') as status, \
		get_json_object(line, '$.seqfile.file.document.orgid') as orgid \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.seqfile.file.document.docid') is not null and \
		day=%s and month=%s \
		GROUP BY \
		get_json_object(line, '$.seqfile.file.document.status'), \
		get_json_object(line, '$.seqfile.file.document.orgid')""" %(DOCRECEIVERLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	ADDTOSF = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;-&nbsp;</td> \
			<td>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
		ADDTOSF = ADDTOSF + int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if ADDTOSF < UPLOADED_DR:
		print ("QUERY 5 FAILED")
		COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 6 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of seq. files and individual documents sent to redis per Org"
	print ("Running DOC-RECEIVER query #6 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.submit.post.orgid') as orgid, \
		get_json_object(line, '$.submit.post.queue.name') as redis_queue_name, \
		count(get_json_object(line, '$.submit.post.numfiles')) as seq_files_sent_to_redis, \
		count(get_json_object(line, '$.submit.post.apxfiles.count')) as ind_files \
		FROM %s \
		WHERE get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.submit.post.status') = "success" and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.submit.post.orgid'), get_json_object(line, '$.submit.post.queue.name')""" %(DOCRECEIVERLOGFILE, DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[0])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['10000250', 'prod-coordinator.highpriority', '0', '0']
	REPORT = REPORT+"</table><br>"
	#if int(i[3]) < DOCUMENTCOUNTER:
		#print ("QUERY 6 FAILED")
		#COMPONENT_STATUS="FAILED"



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
		day='%s' and month='%s' and \
		get_json_object(line, '$.job.status') is not null and \
		get_json_object(line, '$.job.status') <> 'start' \
		GROUP BY get_json_object(line, '$.job.status'), get_json_object(line, '$.job.activity')""" % (COORDINATORLOGFILE, DAY, MONTH))

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


if (QUERY_NUMBER) == 17 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Failed job types by coordinator per org"
	print ("Running COORDINATOR query #17 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.coordinator.job.jobType') as job_type, \
		get_json_object(line, '$.coordinator.job.hadoopJobID') as hadoop_Job_ID, \
		get_json_object(line, '$.coordinator.job.context.organization') as organization, \
		get_json_object(line, '$.datestamp') as date_and_time \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = 'EVENT' and \
		get_json_object(line, '$.coordinator.job.status') = 'error' and \
		day=%s and month=%s \
		ORDER BY job_type ASC""" % (COORDINATORLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY 17 FAILED")
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

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_OCR, \
		get_json_object(line, '$.orgId') as orgid \
		FROM %s \
		WHERE \
		get_json_object(line, '$.tag.ocr.status') = "success" and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.orgId')""" %(PARSERLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	TAGED_TO_OCR=0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
		TAGED_TO_OCR = TAGED_TO_OCR+int(i[0])
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

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_Persist, \
		get_json_object(line, '$.orgId') as orgid \
		FROM %s \
		WHERE \
		get_json_object(line, '$.tag.persist.status') = "success" and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.orgId')""" %(PARSERLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	TAGED_TO_PERSIST=0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
		TAGED_TO_PERSIST = TAGED_TO_PERSIST+int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	# if (TAGED_TO_OCR + TAGED_TO_PERSIST) < DOCUMENTCOUNTER:
		# print ("QUERY 9 FAILED")
		# COMPONENT_STATUS="FAILED"



if (QUERY_NUMBER) == 10 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs succeeded or failed"
	print ("Running PARSER query #10 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Parser_distinct_UUIDs, \
		get_json_object(line, '$.status') as status, \
		get_json_object(line, '$.orgId') as orgid \
		FROM %s \
		WHERE \
		get_json_object(line, '$.documentuuid') is not null and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId')""" %(PARSERLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0', 'success']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < (TAGED_TO_OCR + TAGED_TO_PERSIST):
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
		get_json_object(line, '$.status') = "error" and \
		day=%s and month=%s""" %(PARSERLOGFILE, DAY, MONTH))

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
		get_json_object(line, '$.documentuuid') is not null and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.status')""" %(OCRLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;-&nbsp;</td> \
			<td align='left'>"+str(i[1])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		COMPONENT_STATUS="FAILED"
		print ("QUERY 12 FAILED")
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < DOCUMENTS_TO_OCR:
		COMPONENT_STATUS="FAILED"


if (QUERY_NUMBER) == 13 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of OCR errors and specific error messages per org"
	print ("Running PERSIST query #13 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.error.message') as ocr_error_message, \
		get_json_object(line, '$.orgId') as org_id, \
		get_json_object(line, '$.className') as class_name, \
		COUNT (*) as error_count \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.error.message'), \
		get_json_object(line, '$.orgId'), \
		get_json_object(line, '$.className')""" %(OCRLOGFILE, DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
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
		get_json_object(line, '$.documentuuid') is not null and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.status')""" %(PERSISTLOGFILE, DAY, MONTH))

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
	QUERY_DESC="Persist errors and specific error messages per org per class_name"
	print ("Running PERSIST query #15 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as error_count, \
		get_json_object(line, '$.error.message') as persist_error_message, \
		get_json_object(line, '$.orgId') as org_id, \
		get_json_object(line, '$.columnFamily') as column_family, \
		get_json_object(line, '$.className') as class_name \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.error.message'), get_json_object(line, '$.orgId'), \
		get_json_object(line, '$.columnFamily'), \
		get_json_object(line, '$.className')""" %(PERSISTLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[4])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY 15 FAILED")
		COMPONENT_STATUS="FAILED"


if (QUERY_NUMBER) == 18 or PROCESS_ALL_QUERIES:
	QUERY_DESC="Persist autocorrections with org uuid and info"
	print ("Running PERSIST query #18 - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.orgId') as org, \
		get_json_object(line, '$.patient.uuid') as uuid, \
		get_json_object(line, '$.patient.info') as info \
		FROM %s \
		WHERE 
		get_json_object(line, '$.autocorrection') = 'true' and
		day=%s and month=%s""" % (PERSISTLOGFILE, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[0])]+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	#else:
		#COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	#if ROW > 0:
		#print ("QUERY 18 FAILED")
		#COMPONENT_STATUS="FAILED"




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


REPORT=REPORT+"<table><tr><td><br>End of %s - %s<br><br></td></tr>" % (REPORT_TYPE, CUR_TIME)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"


s=smtplib.SMTP()
s.connect("smtp.gmail.com",587)
s.starttls()
s.login("donotreply@apixio.com", "apx.mail47")	        
s.sendmail(SENDER, RECEIVERS, REPORT)	
print "Report completed, successfully sent email to %s ..." % (RECEIVERS)
