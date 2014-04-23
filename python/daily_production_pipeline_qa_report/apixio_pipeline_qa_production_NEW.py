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
LOGTYPE = "epoch"
SENDER="donotreply@apixio.com"
REPORT=""

PASSED="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
TIMESTAMP=strftime("%s", gmtime())
DATESTAMP=strftime("%m/%d/%y %r", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR=strftime("%Y", gmtime())
DAYSBACK=1
# DAYSBACK=1
CURDAY=("%d", gmtime())
CURMONTH=("%m", gmtime())
CURYEAR=strftime("%Y", gmtime())
DATERANGE=""
CURDAY=gmtime().tm_mday
CURMONTH=gmtime().tm_mon
#BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
#DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
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
ORGID="N/A"
BATCHID="N/A"
USERNAME="N/A"
UPLOADED_DR = 0
ARCHTOS3 = 0
ADDTOSF = 0

#=== ORGID - ORGNAME MAP ========================================================================

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
	"CCHCA":"CCHCA", \
	"HILL":"Hill Physicians", \
	"MMG":"MMG", \
	"ONLOK":"ONLOK", \
	"None":"Missing Orgname", \
}
#===================================================================================

def checkEnvironmentandReceivers():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	print ("Setting environment ...\n")
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
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS2=str(sys.argv[3])
		HTML_RECEIVERS="""To: Eng <%s>,Ops <%s>\n""" % (str(sys.argv[2]), str(sys.argv[3]))
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS2="ishekhtman@apixio.com"
		HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""

				
	# overwite any previous ENVIRONMENT settings
	ENVIRONMENT = "Production"
	print ("Version 1.0.1\n")
	print ("ENVIRONMENT = %s\n") % ENVIRONMENT
	print ("Completed setting of enviroment and report receivers ...\n")
			

def identifyReportDayandMonth():
#======== obtain day and month for previous from current day and month ===========================================
	global DAYSBACK, DATERANGE, CURDAY, CURMONTH, DAY, MONTH, YEAR, CURYEAR
	print ("Day and month values before %s day(s) back adjustment ...") % (DAYSBACK)
	print ("DAY = %s, MONTH = %s, YEAR = %s\n") % (CURDAY, CURMONTH, CURYEAR)
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
					CURDAY=28
				else:
					CURDAY=31

	DAY = CURDAY
	MONTH = CURMONTH
	print ("Day and month values after %s day(s) back adjustment ...") % (DAYSBACK)
	print ("DAY: %s, MONTH: %s, YEAR: %s\n") % (DAY, MONTH, YEAR)
	#time.sleep(15)
	

def test(debug_type, debug_msg):
	print "debug(%d): %s" % (debug_type, debug_msg)

#========================================================================================================================================================

def writeReportHeader ():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Begin writing report header ...\n")
	REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	REPORT = REPORT + HTML_RECEIVERS
	REPORT = REPORT + """MIME-Version: 1.0\n"""
	REPORT = REPORT + """Content-type: text/html\n"""
	REPORT = REPORT + """Subject: Daily %s Pipeline QA Report - %s\n\n""" % (ENVIRONMENT, CUR_TIME)

	REPORT = REPORT + """<h1>Apixio %s Pipeline QA Report</h1>\n""" % (ENVIRONMENT)
	REPORT = REPORT + """Date & Time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s</font></b><br><br>\n""" % (ENVIRONMENT)
	print ("End writing report header ...\n")
	

def connectToHive():
	print ("Connecing to Hive ...\n")
	global cur, conn
	conn = pyhs2.connect(host='10.196.47.205', \
		port=10000, authMechanism="PLAIN", \
		user='hive', password='', \
		database='default')
	cur = conn.cursor()
	print ("Connection to Hive established ...\n")


def setHiveParameters():
	print ("Assigning Hive paramaters ...\n")
	# cur.execute("""SET mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.dynamic.partition=true""")
	cur.execute("""set hive.exec.dynamic.partition.mode=nonstrict""")
	cur.execute("""set mapred.reduce.tasks=16""")
	cur.execute("""set mapred.job.queue.name=default""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	print ("Completed assigning Hive paramaters ...\n")


def obtainFailedJobs():
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	print ("Executing failed jobs query ...\n")
	cur.execute("""SELECT activity, hadoop_job_id, batch_id, org_id, time \
		FROM %s \
		WHERE \
		day=%s and month=%s and \
		status = 'error' \
		ORDER BY org_id ASC""" % ("summary_coordinator_jobfinish", DAY, MONTH))


	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	REPORT = REPORT+"<tr><td>Activity:</td><td>Hadoop job:</td><td>Batch ID:</td><td>Org ID:</td><td>Org Name:</td><td>Failure Time:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr> \
			<td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[3])+"&nbsp;&nbsp;</td>"
		if str(i[3]) in ORGMAP:
			REPORT = REPORT + "<td>"+ORGMAP[str(i[3])]+"</td>"
		else:
			REPORT = REPORT + "<td>"+str(i[3])+"</td>"
		REPORT = REPORT + "<td>"+FORMATEDTIME+"</td></tr>"	
		COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='6'><i>There were no failed jobs</i></td></tr>"
	REPORT = REPORT+"</table>"
	


def obtainErrors(activity, summary_table_name, unique_id):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	
	print ("Executing %s query %s ...\n") % (activity, summary_table_name)
	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	cur.execute("""SELECT count(DISTINCT %s) as count, org_id, \
		if (error_message like '/mnt%%','No space left on device', error_message) as message \
		FROM %s \
		WHERE \
		%s is not null and \
		status = 'error' and \
		day=%s and month=%s \
		GROUP BY org_id, \
		if(error_message like '/mnt%%','No space left on device', error_message) \
		ORDER BY message ASC""" %(unique_id, summary_table_name, unique_id, DAY, MONTH))
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+activity+" "+summary_table_name+"</td><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td><td>"+ORGMAP[str(i[1])]+"</td></tr>"
		REPORT = REPORT+"<tr><td colspan='4'>Error: <i>"+str(i[2])+"</i></td></tr>"
		COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='6'><i>There were no "+activity+" "+summary_table_name+" errors</i></td></tr>"
	REPORT = REPORT+"</table><br>" 
	

def careOptimizerDetails():
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	QUERY_DESC="""Error(s) summary"""
	print ("Running CARE OPTIMIZER query - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT error_message, min(time) as first_occurence, \
		max(time) as last_occurence, count(*) as count \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY error_message \
		ORDER BY count DESC""" %("summary_careopt_errors", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td width='75%'>Message:</td><td width='10%'>1st Occur:</td><td width='10%'>Last Occur:</td><td width='5%'>Count:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME1 = DT.datetime.strptime(str(i[1])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIME2 = DT.datetime.strptime(str(i[2])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"</td> \
			<td>"+FORMATEDTIME1+"</td> \
			<td>"+FORMATEDTIME2+"</td> \
			<td>"+str(i[3])+"</td></tr>"
		COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='4'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	

	QUERY_DESC="""Load summary"""
	print ("Running CARE OPTIMIZER query - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT count(*) num_loads,  \
		avg(cassandra_load_millis) / 1000 as avg_load_time_seconds, \
		max(cassandra_load_millis) / 1000 as max_load_time_seconds, \
		avg(patient_bytes) / 1048576 as avg_patient_mb, \
		max(patient_bytes) / 1048576 as max_patient_mb, \
		avg((patient_bytes / cassandra_load_millis) * 1000) / 1048576 avg_mb_per_second, \
		min(patient_cache_size) as min_patient_cache, \
		max(patient_cache_size) as max_patient_cache \
		FROM %s \
		WHERE day=%s and month=%s""" %("summary_careopt_load", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td># Loads:</td><td>Av Load:</td><td>Max Load:</td><td>Av Patient:</td><td>Max Patient</td>"
	REPORT = REPORT+"<td>Av Mb/Sec:</td><td>Min Pat Cache:</td><td>Max Pat Cache:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		#FORMATEDTIME1 = DT.datetime.strptime(str(i[1])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		#FORMATEDTIME2 = DT.datetime.strptime(str(i[2])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"</td> \
			<td>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+str(i[3])+"</td> \
			<td>"+str(i[4])+"</td> \
			<td>"+str(i[5])+"</td> \
			<td>"+str(i[6])+"</td> \
			<td>"+str(i[7])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='4'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"


	QUERY_DESC="""Search summary"""
	print ("Running CARE OPTIMIZER query - retrieve %s ...") % (QUERY_DESC)

	cur.execute("""SELECT split(username, "_")[1] as org, \
		count(distinct split(username, "_")[0]) as end_users, \
		count(distinct patient_sql_id) as num_patients, \
		min(patient_access_millis) as min_time, \
		max(patient_access_millis) as max_time, \
		avg(patient_access_millis) as avg_time, \
		min(time) as first_access, \
		max(time) as last_access \
		FROM %s  \
		WHERE day=%s and month=%s \
		GROUP BY split(username, "_")[1] \
		ORDER BY num_patients DESC""" %("summary_careopt_search", DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Org:</td><td>End users:</td><td># Pat:</td><td>Min time:</td><td>Max time:</td>"
	REPORT = REPORT+"<td>Av time:</td><td>1st acc:</td><td>Lst acc:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME1 = DT.datetime.strptime(str(i[6])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIME2 = DT.datetime.strptime(str(i[7])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr><td>"+str(i[0])+"</td> \
			<td>"+str(i[1])+"</td> \
			<td>"+str(i[2])+"</td> \
			<td>"+str(i[3])+"</td> \
			<td>"+str(i[4])+"</td> \
			<td>"+str(i[5])+"</td> \
			<td>"+FORMATEDTIME1+"</td> \
			<td>"+FORMATEDTIME2+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='4'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

def uploadSummary(activity, summary_table_name, unique_id):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	
	print ("Executing %s query %s ...\n") % (activity, summary_table_name)
	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	cur.execute("""SELECT count(DISTINCT %s) as count, status, org_id \
		FROM %s \
		WHERE \
		%s is not null and \
		day=%s and month=%s \
		GROUP BY org_id, status \
		ORDER BY org_id ASC""" %(unique_id, summary_table_name, unique_id, DAY, MONTH))
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+activity+" "+summary_table_name+"</td><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td><td>"+ORGMAP[str(i[2])]+"</td></tr>"
		if str(i[1]) == "error":
			COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='5'><i>There were no "+activity+" "+summary_table_name+" errors</i></td></tr>"
	REPORT = REPORT+"</table><br>" 	


def jobSummary():
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	print ("Jobs summary query ...\n")
	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
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
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[1]) == "error":
			REPORT = REPORT+"<tr><td bgcolor='#FFFF00'>"+str(i[0])+"</td><td bgcolor='#FFFF00'>"+str(i[1])+"</td><td bgcolor='#FFFF00'>"+str(i[2])+"</td><td bgcolor='#FFFF00'>"+str(i[3])+"</td><td bgcolor='#FFFF00'>"+ORGMAP[str(i[3])]+"</td></tr>"
			COMPONENT_STATUS="FAILED"
		else:
			REPORT = REPORT+"<tr><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td><td>"+str(i[3])+"</td><td>"+ORGMAP[str(i[3])]+"</td></tr>"			
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='5'><i>There were no Jobs</i></td></tr>"
	REPORT = REPORT+"</table><br>" 	
	

def writeReportDetails():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS
	
#============ 1st or Failed Jobs section of the report ======================
	
	REPORT = REPORT + SUBHDR % "FAILED JOBS"
	COMPONENT_STATUS="PASSED"
	obtainFailedJobs()
	if (COMPONENT_STATUS == "PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	print ("Completed failed jobs query ... \n")
	
#============ 2nd or Error Messages Received section of the report =============
			
	REPORT = REPORT + SUBHDR % "SPECIFIC ERRORS"
	COMPONENT_STATUS="PASSED"
	obtainErrors("DR","summary_docreceiver_upload", "doc_id")
	obtainErrors("DR","summary_docreceiver_archive", "doc_id")
	obtainErrors("DR","summary_docreceiver_seqfile", "doc_id")
	obtainErrors("Parser","summary_parser", "doc_id")
	obtainErrors("OCR","summary_ocr", "doc_id")
	obtainErrors("Persist Mapper","summary_persist_mapper", "doc_id")
	obtainErrors("Persist Reducer","summary_persist_reducer", "patient_uuid")
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	
#============ 3rd or Upload Summary section of the report ======================	
	
	REPORT = REPORT+SUBHDR % "UPLOAD SUMMARY"
	COMPONENT_STATUS="PASSED"
	uploadSummary("DR","summary_docreceiver_upload", "doc_id")
	uploadSummary("OCR","summary_ocr", "doc_id")
	uploadSummary("Persist Mapper","summary_persist_mapper", "doc_id")
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

#============ 4th or Job Summary section of the report =====================	
	
	REPORT = REPORT+SUBHDR % "JOB SUMMARY"
	COMPONENT_STATUS="PASSED"
	jobSummary()
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

#============ 5th or Care Optimizer Errors section of the report ==========
	
	REPORT = REPORT+SUBHDR % "CARE OPTIMIZER"
	COMPONENT_STATUS="PASSED"
	careOptimizerDetails()
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

#========================= END =============================================	

def closeHiveConnection():
	global cur, conn
	cur.close()
	conn.close()
		

def writeReportFooter():
	print ("Write report footer ...\n")
	global REPORT
	REPORT = REPORT+"<table>"
	REPORT = REPORT+"<tr><td><br>End of %s - %s<br><br></td></tr>" % (REPORT_TYPE, CUR_TIME)
	REPORT = REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr>"
	REPORT = REPORT+"</table>"
	print ("Finished writing report ...\n")


def archiveReport():
	global DEBUG_MODE
	if not DEBUG_MODE:
		print ("Archiving report ...\n")
		BACKUPREPORTFOLDER="/mnt/reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/html/assets/reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(DAY)+".html"
		REPORTXTSTRING="Daily Production Report - "+str(MONTH_FMN)+" "+str(DAY)+", "+str(YEAR)+"\t"+"reports/production/pipeline/"+str(YEAR)+"/"+str(MONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="reports.txt"
		REPORTXTFILEFOLDER="/usr/lib/apx-reporting/html/assets"
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
		print ("Finished archiving report ... \n")


def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2
	print ("Emailing report ...\n")
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, RECEIVERS, REPORT)	
	s.sendmail(SENDER, RECEIVERS2, REPORT)
	print "Report completed, successfully sent email to %s, %s ..." % (RECEIVERS, RECEIVERS2)
	
#================ START OF MAIN BODY =================================================================	
	
checkEnvironmentandReceivers()	

identifyReportDayandMonth()

writeReportHeader()	

connectToHive()

setHiveParameters()

writeReportDetails()

closeHiveConnection()

writeReportFooter()

archiveReport()

emailReport()

#================ END OF MAIN BODY ===================================================================
