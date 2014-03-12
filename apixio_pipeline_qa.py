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
import datetime as DT

os.system('clear')
<<<<<<< HEAD
# =======================================================================================================================================================================
# =======================================================================================================================================================================
# ================================= CONTROLS TO WORK ON ONE SPECIFIC QUERY AND DEBUG SPECIFIC SECTIONS OF CODE ==========================================================
# =======================================================================================================================================================================
# =======================================================================================================================================================================

# Specific Query Number to Run
QNTORUN=3

# Run one or all queries
PROCESS_ALL_QUERIES=bool(0)

# Send report emails and archive report html file
DEBUG_MODE=bool(1)

# =======================================================================================================================================================================
# =======================================================================================================================================================================
# ============================ INITIALIZING GLOBAL VARIABLES VALUES =====================================================================================================
# ============== Assigning default values ===============================================================================================================================

TEST_TYPE="N/A"
REPORT_TYPE="Engineering QA"

ORGID = "190"
ENVIRONMENT = "Staging"
LOGTYPE = "epoch"
RECIPIENT = "ishekhtman@apixio.com"
STARTINGMONTH = 3
STARTINGDAY = 9
ENDINGMONTH = 3
ENDINGDAY = 11

#============= Assign passed external paramater values ================================================================================================================

# assign passed external paramater values
if len(sys.argv) >= 2:
	ORGID = str(sys.argv[1])
if len(sys.argv) >= 3:
	ENVIRONMENT = str(sys.argv[2])
if len(sys.argv) >= 4:
	LOGTYPE = str(sys.argv[3])
if len(sys.argv) >= 5:
	RECIPIENT = str(sys.argv[4])
if len(sys.argv) >= 6:
	STARTINGMONTH = str(sys.argv[5])
if len(sys.argv) >= 7:
	STARTINGDAY = str(sys.argv[6])
if len(sys.argv) >= 8:
	ENDINGMONTH = str(sys.argv[7])
if len(sys.argv) == 9:
	ENDINGDAY = str(sys.argv[8])

# =======================================================================================================================================================================

print ("Version 1.0.0")

print ("TEST_TYPE = %s") % TEST_TYPE
print ("REPORT_TYPE = %s") % REPORT_TYPE
print ("ORGID = %s") % ORGID
print ("ENVIRONMANT = %s") % ENVIRONMENT
print ("LOGTYPE = %s") % LOGTYPE
print ("RECIPIENT = %s") % RECIPIENT
print ("STARTINGMONTH = %s") % STARTINGMONTH
print ("STARTINGDAY = %s") % STARTINGDAY
print ("ENDINGMONTH = %s") % ENDINGMONTH
print ("ENDINGDAY = %s") % ENDINGDAY

time.sleep(1)
=======

#================================= CONTROLS TO WORK ON ONE SPECIFIC QUERY AND DEBUG SPECIFIC SECTIONS OF CODE ===========================================================

# Specific Query Number to Run
QNTORUN=9

# Run one or all queries
PROCESS_ALL_QUERIES=bool(1)

# Send report emails and archive report html file
DEBUG_MODE=bool(0)

# ============================ INITIALIZING GLOBAL VARIABLES VALUES =====================================================================================================

TEST_TYPE="SanityTest"
REPORT_TYPE="Daily engineering QA"


# Environment for SanityTest is passed as a paramater. Staging is a default value
if len(sys.argv) < 2:
	ENVIRONMENT="Staging"
else:
	ENVIRONMENT=str(sys.argv[1])


if (ENVIRONMENT.upper() == "PRODUCTION"):
	USERNAME="apxdemot0138"
	ORGID="10000279"
	PASSWORD="Hadoop.4522"
	HOST="https://dr.apixio.com:8443"
else:
	USERNAME="apxdemot0182"
	ORGID="190"
	PASSWORD="Hadoop.4522"
	HOST="https://supload.apixio.com:8443"
	

ENVIRONMENT = "Production"
LOGTYPE = "epoch"

print ("Version 1.0.0")
print ("ENVIRONMANT = %s") % ENVIRONMENT
print ("LOGTYPE = %s") % LOGTYPE

>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
TIMESTAMP=strftime("%s", gmtime())
DATESTAMP=strftime("%m/%d/%y %r", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
YEAR=strftime("%Y", gmtime())
DAYSBACK=1
CURDAY=("%d", gmtime())
CURMONTH=("%m", gmtime())
DATERANGE=""


CURDAY=gmtime().tm_mday
CURMONTH=gmtime().tm_mon

<<<<<<< HEAD
# print ("CURDAY = %s") % CURDAY
# print ("CURMONTH = %s") % CURMONTH
=======
print ("CURDAY = %s") % CURDAY
print ("CURMONTH = %s") % CURMONTH
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID

DOCUMENTCOUNTER=0
NUMBEROFDOCUMENTS=0

DOCUMENTS_TRANSMITTED=20
DOCUMENTS_TO_OCR=0
DOCUMENTS_TO_PERSIST=0
TAGED_TO_OCR=0
TAGED_TO_PERSIST=0


QUERY_DESC=""
COMPONENT_STATUS="PASSED"


INDEXERLOGFILE="indexer_manifest_epoch"
DOCRECEIVERLOGFILE=ENVIRONMENT.lower()+"_logs_docreceiver_"+LOGTYPE
COORDINATORLOGFILE=ENVIRONMENT.lower()+"_logs_coordinator_"+LOGTYPE
PARSERLOGFILE=ENVIRONMENT.lower()+"_logs_parserjob_"+LOGTYPE
OCRLOGFILE=ENVIRONMENT.lower()+"_logs_ocrjob_"+LOGTYPE
PERSISTLOGFILE=ENVIRONMENT.lower()+"_logs_persistjob_"+LOGTYPE

<<<<<<< HEAD
# ORGID="N/A"
=======
ORGID="N/A"
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504
BATCHID="N/A"
USERNAME="N/A"
UPLOADED_DR = 0
ARCHTOS3 = 0
ADDTOSF = 0




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

<<<<<<< HEAD
# print ("DAY: %s") % DAY
# print ("MONTH: %s") % MONTH
# print ("YEAR: %s") % YEAR
# print ("ENVIRONMANT = %s") % ENVIRONMENT
# print ("CUR_TIME = %s") % CUR_TIME
=======
print ("DAY: %s") % DAY
print ("MONTH: %s") % MONTH
print ("YEAR: %s") % YEAR
print ("ENVIRONMANT = %s") % ENVIRONMENT
print ("CUR_TIME = %s") % CUR_TIME
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504
# time.sleep(10)

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
	"genManifest":"genManifest", \
	"None":"Missing Orgname", \
}

# print ORGMAP[ORGID]
#===================================================================================================================

<<<<<<< HEAD
=======
#ORGID="10000246"
#print orgmap(ORGID)
#time.sleep(30)

>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

def test(debug_type, debug_msg):
	print "debug(%d): %s" % (debug_type, debug_msg)

#========================================================================================================================================================


PASSED="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"

# =============================== REPORT SENDER and RECEIVER CONFIGURATION ==============================================================================

SENDER="donotreply@apixio.com"
if DEBUG_MODE:
	RECEIVERS="ishekhtman@apixio.com"
else:
	RECEIVERS="eng@apixio.com"


REPORT = "From: Apixio QA <QA@apixio.com>\n"
if DEBUG_MODE:
	REPORT = REPORT + "To: Igor <ishekhtman@apixio.com>\n"
else:
	REPORT = REPORT + "To: Engineering <eng@apixio.com>\n"	


REPORT = REPORT + """MIME-Version: 1.0
Content-type: text/html
<<<<<<< HEAD
Subject: %s Pipeline QA Report - %s
=======
Subject: Daily %s Pipeline QA Report - %s
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

<h1>Apixio Pipeline QA Report</h1>
Date & Time: <b>%s</b><br>
Report type: <b>%s</b><br>
Enviromnent: <b>%s</b><br>
OrgID: <b>%s</b><br>
BatchID: <b>%s</b><br>
<<<<<<< HEAD
User name: <b>%s</b><br>
Starting: <b>%s/%s</b><br>
Ending: <b>%s/%s</b><br><br>
""" % (ENVIRONMENT, CUR_TIME, CUR_TIME, REPORT_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY)
=======
User name: <b>%s</b><br><br>
""" % (ENVIRONMENT, CUR_TIME, CUR_TIME, REPORT_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


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
COMPONENT_STATUS="PASSED"


QN=1
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents uploaded"
	print ("Running DOC-RECEIVER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, \
		get_json_object(line, '$.upload.document.status') as status, \
		get_json_object(line, '$.upload.document.orgid') as orgid, \
		get_json_object(line, '$.message') as message \
		FROM %s \
		WHERE \
<<<<<<< HEAD
		get_json_object(line, '$.level') = 'EVENT' and \
		get_json_object(line, '$.upload.document.docid') is not null and \
		get_json_object(line, '$.upload.document.orgid')='%s' and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY \
		get_json_object(line, '$.upload.document.status'), \
		get_json_object(line, '$.upload.document.orgid'), \
		get_json_object(line, '$.message') ORDER BY message ASC""" %(DOCRECEIVERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.upload.document.docid') is not null and \
		day=%s and month=%s \
		GROUP BY \
		get_json_object(line, '$.upload.document.status'), \
		get_json_object(line, '$.upload.document.orgid'), \
		get_json_object(line, '$.message') ORDER BY message ASC""" %(DOCRECEIVERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td>"
		if (i[3] == None):
			REPORT = REPORT+"<td>&nbsp;</td></tr>"			
		else:
			REPORT = REPORT+"<td>"+str(i[3])+"</td></tr>"
			
		UPLOADED_DR = UPLOADED_DR + int(i[0])
		if str(i[1]) == "error":
			print ("QUERY %s FAILED") % (QN)
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	#if int(i[0]) < DOCUMENTCOUNTER:
		#print ("QUERY %s FAILED") % (QN)
		#COMPONENT_STATUS="FAILED"


QN=2
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents archived to S3"
	print ("Running DOC-RECEIVER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, \
		get_json_object(line, '$.archive.afs.status') as status, \
		get_json_object(line, '$.archive.afs.orgid') as orgid, \
		get_json_object(line, '$.message') as message \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.archive.afs.docid') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.archive.afs.orgid')='%s' and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY \
		get_json_object(line, '$.archive.afs.status'), \
		get_json_object(line, '$.archive.afs.orgid'), \
		get_json_object(line, '$.message') ORDER BY message ASC""" %(DOCRECEIVERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY \
		get_json_object(line, '$.archive.afs.status'), \
		get_json_object(line, '$.archive.afs.orgid'), \
		get_json_object(line, '$.message') ORDER BY message ASC""" %(DOCRECEIVERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td>"
		if (i[3] == None):
			REPORT = REPORT+"<td>&nbsp;</td></tr>"			
		else:
			REPORT = REPORT+"<td>"+str(i[3])+"</td></tr>"

		ARCHTOS3 = ARCHTOS3 + int(i[0])
		if str(i[1]) == "error":
			print ("QUERY %s FAILED") % (QN)
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if ARCHTOS3 < UPLOADED_DR:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"

QN=3
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of documents added to sequence file(s)"
	print ("Running DOC-RECEIVER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, \
		get_json_object(line, '$.seqfile.file.document.status') as status, \
		get_json_object(line, '$.seqfile.file.document.orgid') as orgid, \
		get_json_object(line, '$.message') as message \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.seqfile.file.document.docid') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.seqfile.file.document.orgid')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY \
		get_json_object(line, '$.seqfile.file.document.status'), \
		get_json_object(line, '$.seqfile.file.document.orgid'), \
		get_json_object(line, '$.message') ORDER BY message ASC""" %(DOCRECEIVERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY \
		get_json_object(line, '$.seqfile.file.document.status'), \
		get_json_object(line, '$.seqfile.file.document.orgid'), \
		get_json_object(line, '$.message') ORDER BY message ASC""" %(DOCRECEIVERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0

	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td>"
		if (i[3] == None):
			REPORT = REPORT+"<td>&nbsp;</td></tr>"			
		else:
			REPORT = REPORT+"<td>"+str(i[3])+"</td></tr>"

		ADDTOSF = ADDTOSF + int(i[0])
		if str(i[1]) == "error":
			print ("QUERY %s FAILED") % (QN)
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if ADDTOSF < UPLOADED_DR:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"


QN=4
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of seq. files and individual documents sent to redis per Org"
	print ("Running DOC-RECEIVER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.submit.post.orgid') as orgid, \
		get_json_object(line, '$.submit.post.queue.name') as redis_queue_name, \
		count(get_json_object(line, '$.submit.post.numfiles')) as seq_files_sent_to_redis, \
		sum(get_json_object(line, '$.submit.post.apxfiles.count')) as ind_files \
		FROM %s \
		WHERE get_json_object(line, '$.level') = "EVENT" and \
		get_json_object(line, '$.submit.post.status') = "success" and \
<<<<<<< HEAD
		get_json_object(line, '$.submit.post.orgid')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.submit.post.orgid'), \
		get_json_object(line, '$.submit.post.queue.name')""" %(DOCRECEIVERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.submit.post.orgid'), \
		get_json_object(line, '$.submit.post.queue.name')""" %(DOCRECEIVERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(int(i[3]))+"&nbsp;&nbsp;</td> \
			<td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[0])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['10000250', 'prod-coordinator.highpriority', '0', '0']
	REPORT = REPORT+"</table><br>"
	#if int(i[3]) < DOCUMENTCOUNTER:
		#print ("QUERY %s FAILED") % (QN)
		#COMPONENT_STATUS="FAILED"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== COORDINATOR related queries =======================================================================
# ===================================================================================================================================

REPORT = REPORT+SUBHDR % "COORDINATOR"
COMPONENT_STATUS="PASSED"

QN=5
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of job types succeeded and/or failed by coordinator"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT(get_json_object(line, '$.job.jobID'))) as count, \
		get_json_object(line, '$.job.activity') as activity, \
		get_json_object(line, '$.job.status') as status \
		FROM %s \
		WHERE \
<<<<<<< HEAD
		get_json_object(line, '$.job.status') is not null and \
		get_json_object(line, '$.job.status') <> 'start' and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.job.status'), \
		get_json_object(line, '$.job.activity')""" % (COORDINATORLOGFILE, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day='%s' and month='%s' and \
		get_json_object(line, '$.job.status') is not null and \
		get_json_object(line, '$.job.status') <> 'start' \
		GROUP BY get_json_object(line, '$.job.status'), \
		get_json_object(line, '$.job.activity')""" % (COORDINATORLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='center'>"+str(i[0])+"&nbsp;-&nbsp;</td> \
			<td align='left'>"+str(i[1])+"&nbsp;-&nbsp;</td> \
			<td align='center'>"+str(i[2])+"</td></tr>"
		if (str(i[2]).lower() == 'error'):
			print ("QUERY %s FAILED") % (QN)
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"


QN=6
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Failed job types by coordinator per org"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.coordinator.job.jobType') as job_type, \
		get_json_object(line, '$.coordinator.job.hadoopJobID') as hadoop_Job_ID, \
		get_json_object(line, '$.coordinator.job.context.organization') as orgid, \
		get_json_object(line, '$.datestamp') as datestamp \
		FROM %s \
		WHERE \
		get_json_object(line, '$.level') = 'EVENT' and \
		get_json_object(line, '$.coordinator.job.status') = 'error' and \
<<<<<<< HEAD
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		ORDER BY hadoop_Job_ID ASC""" % (COORDINATORLOGFILE, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		ORDER BY hadoop_Job_ID ASC""" % (COORDINATORLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME = DT.datetime.strptime(str(i[3])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIME+"</td></tr>"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"			
	

if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== PARSER related queries ============================================================================
# ===================================================================================================================================

REPORT = REPORT+SUBHDR % "PARSER"
COMPONENT_STATUS="PASSED"

QN=7
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs tagged to OCR"
	print ("Running PARSER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as number, \
		get_json_object(line, '$.orgId') as orgid,  \
		get_json_object(line, '$.tag.ocr.status') as tagged_to_OCR \
		FROM %s \
		WHERE \
		get_json_object(line, '$.tag.ocr.status') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.orgId'), get_json_object(line, '$.tag.ocr.status') \
		ORDER BY orgid, tagged_to_OCR ASC""" %(PARSERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.orgId'), get_json_object(line, '$.tag.ocr.status') \
		ORDER BY orgid, tagged_to_OCR ASC""" %(PARSERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	TAGED_TO_OCR=0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
		TAGED_TO_OCR = TAGED_TO_OCR+int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	if TAGED_TO_OCR < DOCUMENTS_TO_OCR:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"


QN=8
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs tagged to Persist"
	print ("Running PARSER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as number, \
		get_json_object(line, '$.orgId') as orgid,  \
		get_json_object(line, '$.tag.persist.status') as tagged_to_Persist \
		FROM %s \
		WHERE \
		get_json_object(line, '$.tag.persist.status') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.orgId'), get_json_object(line, '$.tag.persist.status') \
		ORDER BY orgid, tagged_to_Persist ASC""" %(PARSERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.orgId'), get_json_object(line, '$.tag.persist.status') \
		ORDER BY orgid, tagged_to_Persist ASC""" %(PARSERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	TAGED_TO_PERSIST=0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
		TAGED_TO_PERSIST = TAGED_TO_PERSIST+int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0']
	REPORT = REPORT+"</table><br>"
	# if (TAGED_TO_OCR + TAGED_TO_PERSIST) < DOCUMENTCOUNTER:
		# print ("QUERY %s FAILED") % (QN)
		# COMPONENT_STATUS="FAILED"


QN=9
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs succeeded or failed"
	print ("Running PARSER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  number, \
		get_json_object(line, '$.orgId') as orgid, \
		get_json_object(line, '$.status') as status \
		FROM %s \
		WHERE \
		get_json_object(line, '$.documentuuid') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId') \
		ORDER BY orgid, status ASC""" %(PARSERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId') \
		ORDER BY orgid, status ASC""" %(PARSERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0', 'success']
	REPORT = REPORT+"</table><br>"
	if int(i[0]) < (TAGED_TO_OCR + TAGED_TO_PERSIST):
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"


QN=10
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of Parser errors, class-name and specific error messages"
	print ("Running PARSER query #%s - retrieve %s ...") %  (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT(*) as number, 
		get_json_object(line, '$.error.message') as parser_error_message, \
		get_json_object(line, '$.className') as class_name, \
		get_json_object(line, '$.orgId') as orgid, \
		min(get_json_object(line, '$.datestamp')) as mindatestamp, \
		max(get_json_object(line, '$.datestamp')) as maxdatestamp \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.error.message'), \
		get_json_object(line, '$.className'), \
		get_json_object(line, '$.orgId')""" %(PARSERLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.error.message'), \
		get_json_object(line, '$.className'), \
		get_json_object(line, '$.orgId')""" %(PARSERLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[5])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[3])]+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMIN+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMAX+"</td></tr>"
		REPORT = REPORT+"<tr><td colspan='6'>Error: <i>"+str(i[1])+"</i></td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"

if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== OCR related queries ===============================================================================
# ===================================================================================================================================

REPORT = REPORT+SUBHDR % "OCR"
COMPONENT_STATUS="PASSED"

QN=11
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs passed or failed by OCR"
	print ("Running OCR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  OCR_distinct_UUIDs, \
		get_json_object(line, '$.status') as status, \
		get_json_object(line, '$.orgId') as org_id \
		FROM %s \
		WHERE \
		get_json_object(line, '$.documentuuid') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId')""" %(OCRLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId')""" %(OCRLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td align='left'>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
		if str(i[1]) == "error":
			COMPONENT_STATUS="FAILED"
			print ("QUERY 12 FAILED")
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		COMPONENT_STATUS="FAILED"
		print ("QUERY %s FAILED") % (QN)
	REPORT = REPORT+"</table><br>"
	#if int(i[0]) < DOCUMENTS_TO_OCR:
		#COMPONENT_STATUS="FAILED"


QN=12
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of OCR errors and specific error messages per org"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as number, \
		get_json_object(line, '$.error.message') as ocr_error_message, \
		get_json_object(line, '$.className') as class_name, \
		get_json_object(line, '$.orgId') as orgid, \
		min(get_json_object(line, '$.datestamp')) as mindatestamp, \
		max(get_json_object(line, '$.datestamp')) as maxdatestamp \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.error.message'), \
		get_json_object(line, '$.orgId'), \
		get_json_object(line, '$.className')""" % (OCRLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.error.message'), \
		get_json_object(line, '$.orgId'), \
		get_json_object(line, '$.className')""" % (OCRLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[5])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[3])]+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMIN+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMAX+"</td></tr>"
		REPORT = REPORT+"<tr><td colspan='6'>Error: <i>"+str(i[1])+"</i></td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
REPORT = REPORT+"<br><br>"

# ===================================================================================================================================
# =============================== PERSIST related queries ===========================================================================
# ===================================================================================================================================

REPORT = REPORT+SUBHDR % "PERSIST"
COMPONENT_STATUS="PASSED"

QN=13
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs passed or failed to Persist"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Persist_distinct_UUIDs, \
		get_json_object(line, '$.status') as status, \
		get_json_object(line, '$.orgId') as org_id \
		FROM %s \
		WHERE \
		get_json_object(line, '$.documentuuid') is not null and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId')""" %(PERSISTLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.status'), \
		get_json_object(line, '$.orgId')""" %(PERSISTLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td align='left'>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
		if str(i[1]) == "error":
			COMPONENT_STATUS="FAILED"
			print ("QUERY %s FAILED") % (QN)
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		i = ['0', 'success']
	REPORT = REPORT+"</table><br>"
	#if int(i[0]) < DOCUMENTCOUNTER:
		#print ("QUERY %s FAILED") % (QN)
		#COMPONENT_STATUS="FAILED"


QN=14
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Persist errors and specific error messages per org per class_name"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as error_count, \
		get_json_object(line, '$.error.message') as persist_error_message, \
		get_json_object(line, '$.className') as class_name, \
		get_json_object(line, '$.orgId') as org_id, \
		min(get_json_object(line, '$.datestamp')) as mindatestamp, \
		max(get_json_object(line, '$.datestamp')) as maxdatestamp \
		FROM %s \
		WHERE \
		get_json_object(line, '$.status') = "error" and \
<<<<<<< HEAD
		get_json_object(line, '$.orgId')=%s and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s)) \
		GROUP BY get_json_object(line, '$.error.message'), get_json_object(line, '$.orgId'), \
		get_json_object(line, '$.columnFamily'), \
		get_json_object(line, '$.className')""" %(PERSISTLOGFILE, ORGID, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		day=%s and month=%s \
		GROUP BY get_json_object(line, '$.error.message'), get_json_object(line, '$.orgId'), \
		get_json_object(line, '$.columnFamily'), \
		get_json_object(line, '$.className')""" %(PERSISTLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[5])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[3])]+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMIN+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMAX+"</td></tr>"
		REPORT = REPORT+"<tr><td colspan='6'>Error: <i>"+str(i[1])+"</i></td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
		# COMPONENT_STATUS="PASSED"
	else:
		COMPONENT_STATUS="FAILED"
	REPORT = REPORT+"</table><br>"
	if ROW > 0:
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"


QN=15
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Persist autocorrections with org uuid and info"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT get_json_object(line, '$.orgId') as org, \
		get_json_object(line, '$.patient.uuid') as uuid, \
		get_json_object(line, '$.patient.info') as info \
		FROM %s \
<<<<<<< HEAD
		WHERE \
		get_json_object(line, '$.autocorrection') = 'true' and \
		((month>=%s and day>=%s) and \
		(month<=%s and day<=%s))""" % (PERSISTLOGFILE, STARTINGMONTH, STARTINGDAY, ENDINGMONTH, ENDINGDAY))
=======
		WHERE 
		get_json_object(line, '$.autocorrection') = 'true' and
		day=%s and month=%s""" % (PERSISTLOGFILE, DAY, MONTH))
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504

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
		#print ("QUERY %s FAILED") % (QN)
		#COMPONENT_STATUS="FAILED"


if (COMPONENT_STATUS=="PASSED"):
	REPORT = REPORT+PASSED
else:
	REPORT = REPORT+FAILED
REPORT = REPORT+"<br><br>"

cur.close()
conn.close()

# ===================================================================================================================================
# ===================================================================================================================================
# ===================================================================================================================================


<<<<<<< HEAD
REPORT=REPORT+"<table><tr><td><br>End of %s report - %s<br><br></td></tr>" % (REPORT_TYPE, CUR_TIME)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"

# ============================= ARCHIVE REPORT TO A FILE ============================================================================
# if not DEBUG_MODE:
#	REPORTFOLDER="/mnt/reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)
#	REPORTFILENAME=str(DAY)+".html"
#	print (REPORTFOLDER)
#	print (REPORTFILENAME)
#	os.chdir(REPORTFOLDER)
#	REPORTFILE = open(REPORTFILENAME, 'w')
#	REPORTFILE.write(REPORT)
#	REPORTFILE.close()
#	os.chdir("/mnt/automation")
=======
REPORT=REPORT+"<table><tr><td><br>End of %s - %s<br><br></td></tr>" % (REPORT_TYPE, CUR_TIME)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"

# ============================= ARCHIVE REPORT TO A FILE ============================================================================
if not DEBUG_MODE:
	REPORTFOLDER="/mnt/reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)
	REPORTFILENAME=str(DAY)+".html"
	print (REPORTFOLDER)
	print (REPORTFILENAME)
	os.chdir(REPORTFOLDER)
	REPORTFILE = open(REPORTFILENAME, 'w')
	REPORTFILE.write(REPORT)
	REPORTFILE.close()
	os.chdir("/mnt/automation")
>>>>>>> eb97358a8a7e3a9b74c93b0ee7fb6d8e35e55504
# ===================================================================================================================================


s=smtplib.SMTP()
s.connect("smtp.gmail.com",587)
s.starttls()
s.login("donotreply@apixio.com", "apx.mail47")	        
s.sendmail(SENDER, RECEIVERS, REPORT)	
print "Report completed, successfully sent email to %s ..." % (RECEIVERS)
