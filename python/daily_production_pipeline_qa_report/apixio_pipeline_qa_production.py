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

#================================= CONTROLS TO WORK ON ONE SPECIFIC QUERY AND DEBUG SPECIFIC SECTIONS OF CODE ===========================================================

# Specific Query Number to Run
QNTORUN=1

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


DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
TIMESTAMP=strftime("%s", gmtime())
DATESTAMP=strftime("%m/%d/%y %r", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR=strftime("%Y", gmtime())
DAYSBACK=1
CURDAY=("%d", gmtime())
CURMONTH=("%m", gmtime())
DATERANGE=""


CURDAY=gmtime().tm_mday
CURMONTH=gmtime().tm_mon


print ("MONTH_FMN = %s") % MONTH_FMN
print ("CURDAY = %s") % CURDAY
print ("CURMONTH = %s") % CURMONTH


BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID

DOCUMENTCOUNTER=0
NUMBEROFDOCUMENTS=0

DOCUMENTS_TRANSMITTED=20
DOCUMENTS_TO_OCR=0
DOCUMENTS_TO_PERSIST=0
TAGED_TO_OCR=0
TAGED_TO_PERSIST=0
TAGGED_TOTAL=0


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

print ("DAY: %s") % DAY
print ("MONTH: %s") % MONTH
print ("YEAR: %s") % YEAR
print ("ENVIRONMANT = %s") % ENVIRONMENT
print ("CUR_TIME = %s") % CUR_TIME
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
	"defaultOrgID":"defaultOrgID", \
	"None":"Missing Orgname", \
}

# print ORGMAP[ORGID]
#===================================================================================================================

#ORGID="10000246"
#print orgmap(ORGID)
#time.sleep(30)


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
Subject: Daily %s Pipeline QA Report - %s

<h1>Apixio Pipeline QA Report</h1>
Date & Time (run): <b>%s</b><br>
Date (logs & queries): <b>%s/%s/%s</b><br>
Report type: <b>%s</b><br>
Enviromnent: <b>%s</b><br>
OrgID: <b>%s</b><br>
BatchID: <b>%s</b><br>
User name: <b>%s</b><br><br>
""" % (ENVIRONMENT, CUR_TIME, CUR_TIME, MONTH, DAY, YEAR, REPORT_TYPE, ENVIRONMENT, ORGID, BATCHID, USERNAME)


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

	cur.execute("""SELECT count(DISTINCT doc_id) as total, status, org_id, \
		if(error_message like '/mnt%%','No space left on device', error_message) as message \
		FROM %s \
		WHERE \
		doc_id is not null and \
		day=%s and month=%s \
		GROUP BY \
		status, org_id, \
		if(error_message like '/mnt%%','No space left on device', error_message) \
		ORDER BY message ASC""" %("summary_docreceiver_upload", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td></tr>"
		if (str(i[1]) == 'error'):
			if (i[3] == None):
				REPORT = REPORT+"<tr><td colspan='4'>Error: <i>Missing</i></td></tr>"			
			else:
				REPORT = REPORT+"<tr><td colspan='4'>Error: <i>"+str(i[3])+"</i></td></tr>"
			
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


	cur.execute("""SELECT count(DISTINCT doc_id) as total, status, org_id, \
		if(error_message like '/mnt%%','No space left on device', error_message) as message \
		FROM %s \
		WHERE \
		doc_id is not null and \
		day=%s and month=%s \
		GROUP BY \
		status, org_id, if(error_message like '/mnt%%','No space left on device', error_message) \
		ORDER BY message ASC""" %("summary_docreceiver_archive", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td></tr>"
		if (str(i[1]) == 'error'):
			if (i[3] == None):
				REPORT = REPORT+"<tr><td colspan='4'>Error: <i>Missing</i></td></tr>"			
			else:
				REPORT = REPORT+"<tr><td colspan='4'>Error: <i>"+str(i[3])+"</i></td></tr>"

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


	cur.execute("""SELECT count(DISTINCT doc_id) as total, status, org_id, \
		if(error_message like '/mnt%%','No space left on device', error_message) as message \
		FROM %s \
		WHERE \
		doc_id is not null and \
		day=%s and month=%s \
		GROUP BY \
		status, org_id, \
		if(error_message like '/mnt%%','No space left on device', error_message) \
		ORDER BY message ASC""" %("summary_docreceiver_seqfile", DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0

	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td></tr>"
		if (str(i[1]) == 'error'):
			if (i[3] == None):
				REPORT = REPORT+"<tr><td colspan='4'>Error: <i>Missing</i></td></tr>"				
			else:
				REPORT = REPORT+"<tr><td colspan='4'>Error: <i>"+str(i[3])+"</i></td></tr>"

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


	cur.execute("""SELECT org_id, \
		redis_queue_name, \
		count(num_seq_files) as tot_seq_files, \
		sum(num_docs) as tot_ind_files \
		FROM %s \
		WHERE \
		status = 'success' and \
		redis_queue_name is not null and \
		day=%s and month=%s \
		GROUP BY org_id, redis_queue_name""" %("summary_docreceiver_seqfile_post", DAY, MONTH))


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
	QUERY_DESC="Number of workrequests by organization"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (DISTINCT work_id) as total, \
		org_id \
		FROM %s \
		WHERE \
		day=%s and month=%s \
		GROUP BY org_id \
		ORDER BY org_id ASC""" % ("summary_coordinator_workrequest", DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"



QN=6
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of seq files moved by coordinator"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as total, \
		activity, move_message, org_id \
		FROM %s \
		WHERE \
		day=%s and month=%s \
		GROUP BY activity, org_id, move_message \
		ORDER BY org_id, move_message ASC""" % ("summary_coordinator_movefiles", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[3])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"


QN=7
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of jobs requested by organization"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as total, \
		activity, org_id \
		FROM %s \
		WHERE \
		day=%s and month=%s \
		GROUP BY activity, org_id \
		ORDER BY org_id, activity ASC""" % ("summary_coordinator_jobrequest", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"


QN=8
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of jobs started by organization"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as total, \
		activity, org_id \
		FROM %s \
		WHERE \
		day=%s and month=%s \
		GROUP BY activity, org_id \
		ORDER BY org_id, activity ASC""" % ("summary_coordinator_jobstart", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"


QN=9
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of jobs succeeded or failed by coordinator"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(job_id) as total, \
		status, \
		activity, \
		org_id \
		FROM %s \
		WHERE \
		day=%s and month=%s and \
		status is not null and \
		status <> 'start' \
		GROUP BY status, \
		activity, \
		org_id \
		ORDER BY org_id, activity ASC""" % ("summary_coordinator_jobfinish", DAY, MONTH))



	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[3])]+"</td></tr>"
		if (str(i[1]).lower() == 'error'):
			print ("QUERY %s FAILED") % (QN)
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"				
	REPORT = REPORT+"</table><br>"


QN=10
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Failed job types by coordinator per org"
	print ("Running COORDINATOR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT hadoop_job_id, \
		org_id, \
		time \
		FROM %s \
		WHERE \
		status = 'error' and  \
		day=%s and month=%s \
		ORDER BY hadoop_job_id ASC""" % ("summary_coordinator_jobfinish", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME = DT.datetime.strptime(str(i[2])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"&nbsp;&nbsp;</td> \
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

QN=11
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs tagged to OCR"
	print ("Running PARSER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT doc_id) as total, \
		org_id,  \
		sent_to_ocr \
		FROM %s \
		WHERE \
		sent_to_ocr is not null and \
		day=%s and month=%s \
		GROUP BY org_id, sent_to_ocr \
		ORDER BY org_id, sent_to_ocr ASC""" %("summary_parser", DAY, MONTH))


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


QN=12
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs tagged to Persist"
	print ("Running PARSER query #%s - retrieve %s ...") % (QN, QUERY_DESC)


	cur.execute("""SELECT count(DISTINCT doc_id) as total, \
		org_id,  \
		sent_to_persist \
		FROM %s \
		WHERE \
		sent_to_persist is not null and \
		day=%s and month=%s \
		GROUP BY org_id, sent_to_persist \
		ORDER BY org_id, sent_to_persist ASC""" %("summary_parser", DAY, MONTH))


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


QN=13
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs succeeded or failed"
	print ("Running PARSER query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT doc_id) as total, \
		org_id,  \
		status \
		FROM %s \
		WHERE \
		doc_id is not null and \
		day=%s and month=%s \
		GROUP BY status, org_id \
		ORDER BY org_id, status ASC""" %("summary_parser", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	TAGGED_TOTAL=0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td align='right'>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[1])]+"</td></tr>"
		TAGGED_TOTAL = TAGGED_TOTAL+int(i[0])
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	if TAGGED_TOTAL < (TAGED_TO_OCR + TAGED_TO_PERSIST):
		print ("QUERY %s FAILED") % (QN)
		COMPONENT_STATUS="FAILED"


QN=14
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of Parser errors and specific error messages"
	print ("Running PARSER query #%s - retrieve %s ...") %  (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT(*) as total, 
		error_message, \
		org_id, \
		min(time), \
		max(time) \
		FROM %s \
		WHERE \
		status = 'error' and \
		day=%s and month=%s \
		GROUP BY error_message, org_id""" %("summary_parser", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[3])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMIN+"&nbsp;&nbsp;</td> \
			<td>"+FORMATEDTIMEMAX+"</td></tr>"
		REPORT = REPORT+"<tr><td colspan='5'>Error: <i>"+str(i[1])+"</i></td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center'><i>None</i></td></tr>"
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

QN=15
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs passed or failed by OCR"
	print ("Running OCR query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT doc_id) as total, \
		status, \
		org_id \
		FROM %s \
		WHERE \
		doc_id is not null and \
		day=%s and month=%s \
		GROUP BY status, org_id""" %("summary_ocr", DAY, MONTH))


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


QN=16
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of OCR errors and specific error messages per org"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as total, \
		error_message, \
		org_id, \
		min(time), \
		max(time) \
		FROM %s \
		WHERE \
		status = 'error' and \
		day=%s and month=%s \
		GROUP BY error_message, org_id""" % ("summary_ocr", DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[3])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td> \
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

QN=17
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Number of distinct UUIDs passed or failed to Persist"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT count(DISTINCT doc_id) as total, \
		status, \
		org_id \
		FROM %s \
		WHERE \
		doc_id is not null and \
		day=%s and month=%s \
		GROUP BY status, org_id""" %("summary_persist_mapper", DAY, MONTH))



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


QN=18
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="PersistMapper errors and specific error messages per org"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as total, \
		error_message, \
		org_id, \
		min(time), \
		max(time) \
		FROM %s \
		WHERE \
		status = 'error' and \
		day=%s and month=%s \
		GROUP BY error_message, org_id""" %("summary_persist_mapper", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[3])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td> \
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

QN=19
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="PersistReducer errors and specific error messages per org"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT COUNT (*) as total, \
		error_message, \
		org_id, \
		min(time), \
		max(time) \
		FROM %s \
		WHERE \
		status = 'error' and \
		day=%s and month=%s \
		GROUP BY error_message, org_id""" %("summary_persist_reducer", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIMEMIN = DT.datetime.strptime(str(i[3])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIMEMAX = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+ORGMAP[str(i[2])]+"&nbsp;&nbsp;</td> \
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



QN=20
if (QNTORUN == QN) or PROCESS_ALL_QUERIES:
	QUERY_DESC="Persist autocorrections with org uuid and info"
	print ("Running PERSIST query #%s - retrieve %s ...") % (QN, QUERY_DESC)

	cur.execute("""SELECT org_id as org_id, \
		patient_uuid, \
		patient_key \
		FROM %s \
		WHERE \
		autocorrection = 'true' and \
		day=%s and month=%s""" % ("summary_persist_reducer", DAY, MONTH))


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


REPORT=REPORT+"<table><tr><td><br>End of %s - %s<br><br></td></tr>" % (REPORT_TYPE, CUR_TIME)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"

# ============================= ARCHIVE REPORT TO A FILE ============================================================================

# /usr/lib/apx-reporting/html/assets/reports/production/pipeline/2014/3


if not DEBUG_MODE:
	BACKUPREPORTFOLDER="/mnt/reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)
	REPORTFOLDER="/usr/lib/apx-reporting/html/assets/reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)
	# ------------- Create new folder if one does not exist already -------------------------------
	if not os.path.exists(BACKUPREPORTFOLDER):
    		os.makedirs(BACKUPREPORTFOLDER)	
	if not os.path.exists(REPORTFOLDER):
    		os.makedirs(REPORTFOLDER)
	# ---------------------------------------------------------------------------------------------
	REPORTFILENAME=str(DAY)+".html"
	REPORTXTSTRING="Daily Production Report - "+str(MONTH_FMN)+" "+str(DAY)+", "+str(YEAR)+"\t"+"reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)+"/"+REPORTFILENAME+"\n"
	REPORTXTFILENAME="reports.txt"
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
	os.chdir("/mnt/automation")

# ===================================================================================================================================


s=smtplib.SMTP()
s.connect("smtp.gmail.com",587)
s.starttls()
s.login("donotreply@apixio.com", "apx.mail47")	        
s.sendmail(SENDER, RECEIVERS, REPORT)	
print "Report completed, successfully sent email to %s ..." % (RECEIVERS)