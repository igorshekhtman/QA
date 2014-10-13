import pyhs2
import os
import time
import datetime
import calendar
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

# Specific Report Section to Run:
#  0 - All
#  1 - failedJobsRD()
#  2 - errorMessagesRD()
#  3 - uploadSummaryRD()
#  4 - jobSummaryRD()
#  5 - careOptimizerErrorsRD()
#  6 - logsTrafficRD()
#  7 - eventsRD()
#  8 - dataOrchestratorRD()
#  9 - userAccountsRD()
# 10 - bundlerRD()
REPSECTORUN=0

# Email reports to eng@apixio.com and archive report html file:
# 0 - False
# 1 - True
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

#================================================================================================
#=== ORGID - ORGNAME MAP ========================================================================
#================================================================================================
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
	"10000318":"Cambia", \
	"10000320":"Health Net", \
	"10000331":"Hill Physicians Medical Group", \
	"10000367":"org0420", \
	"10000306":"batmed1", \
	"10000279":"Production Test Org", \
	"10000289":"Production Test Org", \
	"10000280":"Prosper Care Health", \
	"10000281":"Prosperity Health Care", \
	"10000282":"Apixio Coder Training", \
	"10000283":"RMC [Test]", \
	"10000284":"RMC", \
	"10000285":"Scripps [Test]", \
	"10000286":"Scripps", \
	"10000288":"UHS", \
	"10000291":"HCP of Nevada", \
	"10000298":"Theresas Hospital", \
	"10000299":"Erins Hospital", \
	"10000300":"Erics Hospital", \
	"190":"Staging Test Org", \
	"370":"Sanity Test Org", \
	"315":"Staging DR Perf Test Org", \
	"316":"Staging Test Org Dan", \
	"368":"batmed2", \
	"372":"MMG", \
	"377":"org0434", \
	"367":"org0420", \
	"331":"Hill Physicians Medical Group", \
	"243":"org0233", \
	"genManifest":"genManifest", \
	"defaultOrgID":"defaultOrgID", \
	"CCHCA":"CCHCA", \
	"HILL":"Hill Physicians", \
	"MMG":"MMG", \
	"ONLOK":"ONLOK", \
	"__HIVE_DEFAULT_PARTITION__":"__HIVE_DEFAULT_PARTITION__", \
	"None":"Missing Orgname", \
}
#===================================================================================
#===================================================================================
#===================================================================================

def checkEnvironmentandReceivers():
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	# Arg1 - environment
	# Arg2 - report recepient
	global RECEIVERS, RECEIVERS2, HTML_RECEIVERS
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST, POSTFIX
	# Environment for SanityTest is passed as a paramater. Staging is a default value
	print ("Setting environment ...\n")
	if len(sys.argv) < 2:
		ENVIRONMENT="staging"
	else:
		ENVIRONMENT=str(sys.argv[1])

	if (ENVIRONMENT.upper() == "PRODUCTION"):
		USERNAME="apxdemot0138"
		ORGID="10000279"
		PASSWORD="Hadoop.4522"
		HOST="https://dr.apixio.com:8443"
		ENVIRONMENT = "production"
		POSTFIX = ""
	else:
		USERNAME="apxdemot0182"
		ORGID="190"
		PASSWORD="Hadoop.4522"
		HOST="https://testdr.apixio.com:8443"
		ENVIRONMENT = "staging"
		POSTFIX = "_staging"
	
	if (len(sys.argv) > 2):
		RECEIVERS=str(sys.argv[2])
		RECEIVERS2=str(sys.argv[3])
		HTML_RECEIVERS="""To: Eng <%s>,Ops <%s>\n""" % (str(sys.argv[2]), str(sys.argv[3]))
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
		RECEIVERS2="ishekhtman@apixio.com"
		HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""

				
	# overwite any previous ENVIRONMENT settings
	#ENVIRONMENT = "Production"
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

	DAY = "\"%s\"" % (CURDAY)
	if (CURDAY < 10):
		DAY = "\"0%s\"" % (CURDAY)
	MONTH = "\"%s\"" % (CURMONTH)
	if (CURMONTH < 10):
		MONTH = "\"0%s\"" % (CURMONTH)
	MONTH_FMN = calendar.month_name[CURMONTH]
	print ("Day and month values after %s day(s) back adjustment ...") % (DAYSBACK)
	print ("DAY: %s, MONTH: %s, YEAR: %s, SPELLED MONTH: %s\n") % (DAY, MONTH, YEAR, MONTH_FMN)
	#time.sleep(45)
	

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
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s%s</font></b><br><br>\n""" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	print ("End writing report header ...\n")
	

def connectToHive():
	print ("Connecing to Hive ...\n")
	global cur, conn
	conn = pyhs2.connect(host='54.191.226.61', \
		port=10000, authMechanism="PLAIN", \
		user='hive', password='', \
		database='default')
	cur = conn.cursor()
	print ("Connection to Hive established ...\n")


def setHiveParameters():
	hadoopqueuename="hive"
	print ("Assigning Hive paramaters ...\n")
	# cur.execute("""SET mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.dynamic.partition=true""")
	cur.execute("""set hive.exec.dynamic.partition.mode=nonstrict""")
	cur.execute("""set mapred.reduce.tasks=16""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	if hadoopqueuename=="hive":
		cur.execute("""set mapred.job.queue.name=hive""")	
	else:
		cur.execute("""set mapred.job.queue.name=default""")
	print ("Hadoop queue was set to: %s\n") % hadoopqueuename	
	print ("Completed assigning Hive paramaters ...\n")


def obtainFailedJobs(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	print ("Executing failed jobs query ...\n")
	cur.execute("""SELECT activity, hadoop_job_id, batch_id, org_id, time \
		FROM %s \
		WHERE \
		day=%s and month=%s and \
		status = 'error' \
		ORDER BY org_id ASC""" % (table, DAY, MONTH))


	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	REPORT = REPORT+"<tr><td>Activity:</td><td>Hadoop job:</td><td>Batch ID:</td><td>Organization:</td><td>Failure Time:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME = DT.datetime.strptime(str(i[4])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		REPORT = REPORT+"<tr> \
			<td>"+str(i[0])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[1])+"&nbsp;&nbsp;</td> \
			<td>"+str(i[2])+"&nbsp;&nbsp;</td>"
		if str(i[3]) in ORGMAP:
			REPORT = REPORT + "<td>"+ORGMAP[str(i[3])]+" ("+str(i[3])+")</td>"
		else:
			REPORT = REPORT + "<td>"+str(i[3])+" ("+str(i[3])+")</td>"
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
		REPORT = REPORT+"<tr><td bgcolor='#FFFF00'>"+activity+" "+summary_table_name+"</td>"
		REPORT = REPORT+"<td bgcolor='#FFFF00'>"+str(i[0])+"</td>"
		if str(i[1]) in ORGMAP:
			REPORT = REPORT + "<td bgcolor='#FFFF00'>"+ORGMAP[str(i[1])]+" ("+str(i[1])+")</td></tr>"
		else:
			REPORT = REPORT + "<td bgcolor='#FFFF00'>"+str(i[1])+" ("+str(i[1])+")</td></tr>"
		REPORT = REPORT+"<tr><td colspan='4' bgcolor='#FFFF00'>Error: <i>"+str(i[2])+"</i></td></tr>"
		COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='4'>There were no "+activity+" "+summary_table_name+" specific errors</td></tr>"
	REPORT = REPORT+"</table><br>" 
	
def removeHtmlTags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
	

def dataOrchestratorAcls(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	# print (table)
	QUERY_DESC="""ACL(s) summary"""
	print ("Running DATA ORCHESTRATOR query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) as count, \
		permission, auth_status, status, error, org_id \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY org_id, permission, auth_status, status, error \
		ORDER BY count DESC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Permission:</td><td>Auth Status:</td><td>Status:</td><td>Error:</td><td>Org(ID):</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if (str(i[3]) == "error") or (str(i[2]) == "FORBIDDEN") :
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"

		if str(i[5]) in ORGMAP:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+"</td><td bgcolor='"+BG_COLOR+"'>"+ORGMAP[str(i[5])]+" ("+str(i[5])+")</td></tr>"
		else:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[5])+" ("+str(i[5])+")</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='6'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

def dataOrchestratorLookups(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	# print (table)
	QUERY_DESC="""Lookup(s) summary"""
	print ("Running DATA ORCHESTRATOR query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) as count, \
		endpoint, status, error, org_id \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY org_id, endpoint, status, error \
		ORDER BY count DESC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Endpoint:</td><td>Status:</td><td>Error:</td><td>Org(ID):</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[3]) == "error":
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"

		if str(i[4]) in ORGMAP:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+ORGMAP[str(i[4])]+" ("+str(i[4])+")</td></tr>"
		else:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+" ("+str(i[4])+")</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='5'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

def dataOrchestratorRequests(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	# print (table)
	QUERY_DESC="""Request(s) summary"""
	print ("Running DATA ORCHESTRATOR query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) as count, \
		response_code, endpoint, status, error, org_id \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY org_id, endpoint, status, error, response_code \
		ORDER BY count DESC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Response code:</td><td>Endpoint:</td><td>Status:</td><td>Error:</td><td>Org(ID):</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[3]) == "error":
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"

		if str(i[5]) in ORGMAP:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+"</td><td bgcolor='"+BG_COLOR+"'>"+ORGMAP[str(i[5])]+" ("+str(i[5])+")</td></tr>"
		else:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[5])+" ("+str(i[5])+")</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='6'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

def userAccountsRequests(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	#print (table)
	QUERY_DESC="""User Accounts Request(s) summary"""
	print ("Running USER ACCOUNTS query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) as count, \
		email, response_code, status, error \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY email, response_code, status, error \
		ORDER BY status, count DESC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Email:</td><td>Respose Code:</td><td>Status:</td><td>Error:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[3]) == "error":
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"

		REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='5'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

def bundlerSequence(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	#print (table)
	QUERY_DESC="""Bundler Sequence summary"""
	print ("Running BUNDLER query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) as count, \
		pattern, memory_total_bytes, status \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY pattern, status, memory_total_bytes \
		ORDER BY status, count ASC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Pattern:</td><td>Memory Total Bytes:</td><td>Status:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[3]) == "error":
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"

		REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='4'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
def bundlerHistorical(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	#print (table)
	QUERY_DESC="""Bundler Historical summary"""
	print ("Running BUNDLER query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) as count, \
		low, high, status, millis, memory_total_bytes \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY low, high, status, millis, memory_total_bytes \
		ORDER BY status, count ASC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Low:</td><td>High:</td><td>Status:</td><td>Millis:</td><td>Memory Total Bytes:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[3]) == "error":
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"

		REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[4])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[5])+" ("+str(i[5])+")</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='6'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
def bundlerDocuments(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	#print (table)
	QUERY_DESC="""Bundler Document(s) summary"""
	print ("Running BUNDLER query - retrieve %s ...\n") % (QUERY_DESC)

	
	cur.execute("""SELECT count(distinct doc_id) as count, \
		event_batch_id, org_id \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY org_id, event_batch_id \
		ORDER BY org_id, count DESC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Document count:</td><td>Event Batch ID:</td><td>Org(ID):</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		#if str(i[3]) == "error":
		#	COMPONENT_STATUS="FAILED"
		#	BG_COLOR="#FFFF00"
		#else:
		#	BG_COLOR="#FFFFFF"
		BG_COLOR="#FFFFFF"
		if str(i[2]) in ORGMAP:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+ORGMAP[str(i[2])]+" ("+str(i[2])+")</td></tr>"
		else:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+" ("+str(i[2])+")</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='3'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"


def eventAMR(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	#print (table)
	QUERY_DESC="Table: "+table+""
	print ("Running EVENTS query - retrieve %s ...\n") % (QUERY_DESC)

	
	cur.execute("""SELECT count(*) as count, \
		if (error_message like 'ERROR:/Patient/%%','ClinicalCode both codingSystemOID and codingSystem are null', error_message) as message, \
		org_id, status \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY org_id, \
		if (error_message like 'ERROR:/Patient/%%','ClinicalCode both codingSystemOID and codingSystem are null', error_message), \
		status \
		ORDER BY org_id, count DESC""" %(table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Event count:</td><td>Error message:</td><td>Status:</td><td>Org(ID):</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[3]) == "success":
			BG_COLOR="#FFFFFF"
		else:
			COMPONENT_STATUS="FAILED"
			BG_COLOR="#FFFF00"
		if str(i[2]) in ORGMAP:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+ORGMAP[str(i[2])]+" ("+str(i[2])+")</td></tr>"
		else:
			REPORT = REPORT+"<tr><td bgcolor='"+BG_COLOR+"'>"+str(i[0])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[1])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[3])+"</td><td bgcolor='"+BG_COLOR+"'>"+str(i[2])+" ("+str(i[2])+")</td></tr>"
		BG_COLOR="#FFFFFF"	
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='4'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
	
	
def careOptimizerErrors(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	#============================================================================
	#================= LIST OF CARE OPTIMIZER ERRORS ============================
	#============================================================================
	major_error_list = [ \
		'Unexpected error while preparing query', \
		'Patient not found' \
		]
	#============================================================================
	#============================================================================
	#============================================================================
	
	QUERY_DESC="""Error(s) summary"""
	print ("Running CARE OPTIMIZER query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT error_message, min(time) as first_occurence, \
		max(time) as last_occurence, count(*) as count \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY error_message \
		ORDER BY count DESC""" %(table, DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td width='5%'>Count:</td><td width='75%'>Message:</td><td width='10%'>1st Occur:</td><td width='10%'>Last Occur:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		#FORMATEDTIME1 = DT.datetime.strptime(str(i[1])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		#FORMATEDTIME2 = DT.datetime.strptime(str(i[2])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		if any((str(i[0])[:15]) in s for s in major_error_list):
			REPORT = REPORT+"<tr><td bgcolor='#FFFF00'>"+str(i[3])+"</td><td bgcolor='#FFFF00'>"+removeHtmlTags(str(i[0]))+"</td><td bgcolor='#FFFF00'>"+str(i[1])+"</td><td bgcolor='#FFFF00'>"+str(i[2])+"</td></tr>"
		else:
			REPORT = REPORT+"<tr><td>"+str(i[3])+"</td><td>"+removeHtmlTags(str(i[0]))+"</td><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td></tr>"
		COMPONENT_STATUS="FAILED"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='4'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"


def careOptimizerLoad(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	
	QUERY_DESC="""Load summary"""
	print ("Running CARE OPTIMIZER query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT count(*) num_loads,  \
		org_id, \
		avg(cassandra_load_millis) / 1000 as avg_load_time_seconds, \
		max(cassandra_load_millis) / 1000 as max_load_time_seconds, \
		percentile_approx(cassandra_load_millis / 1000, 0.05) as perc_5,
		percentile_approx(cassandra_load_millis / 1000, 0.5) as perc_50, 
		percentile_approx(cassandra_load_millis / 1000, 0.95) as perc_95,
		avg(patient_bytes) / 1048576 as avg_patient_mb, \
		max(patient_bytes) / 1048576 as max_patient_mb, \
		avg((patient_bytes / cassandra_load_millis) * 1000) / 1048576 avg_mb_per_second, \
		min(patient_cache_size) as min_patient_cache, \
		max(patient_cache_size) as max_patient_cache \
		FROM %s \
		WHERE day=%s and month=%s \
		GROUP BY org_id \
		ORDER BY max_load_time_seconds DESC""" %(table, DAY, MONTH))

	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td># Loads:</td><td>Organization:</td><td>Av Load sec:</td><td>Max Load sec:</td>"
	REPORT = REPORT+"<td>5% sec:</td><td>50% sec:</td><td>95% sec:</td>"
	REPORT = REPORT+"<td>Av Patient:</td><td>Max Patient</td>"
	REPORT = REPORT+"<td>Av Mb/Sec:</td><td>Min Pat Cache:</td><td>Max Pat Cache:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr><td>"+str(i[0])+"</td>"
		if str(i[1]) in ORGMAP:
			REPORT = REPORT + "<td>"+ORGMAP[str(i[1])]+" ("+str(i[1])+")</td>"
		else:
			REPORT = REPORT + "<td>"+str(i[1])+" ("+str(i[1])+")</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[2]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[3]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[4]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[5]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[6]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[7]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[8]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(round(float(i[9]),1))+"</td>"
		REPORT = REPORT+"<td>"+str(i[10])+"</td>"
		REPORT = REPORT+"<td>"+str(i[11])+"</td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='12'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

	
def careOptimizerSearch(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS	

	QUERY_DESC="""Search summary"""
	print ("Running CARE OPTIMIZER query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT org_id as org, \
		count(distinct split(username, "_")[0]) as end_users, \
		count(distinct patient_sql_id) as num_patients, \
		min(patient_access_millis) as min_time, \
		max(patient_access_millis) as max_time, \
		avg(patient_access_millis) as avg_time, \
		percentile_approx(patient_access_millis, 0.05) as perc_5,
		percentile_approx(patient_access_millis, 0.5) as perc_50, 
		percentile_approx(patient_access_millis, 0.95) as perc_95,  
		min(time) as first_access, \
		max(time) as last_access \
		FROM %s  \
		WHERE day=%s and month=%s \
		GROUP BY org_id, split(username, "_")[1] \
		ORDER BY max_time DESC""" %(table, DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Organization:</td><td># Users:</td><td># Pat:</td><td>Min mil:</td><td>Max mil:</td>"
	REPORT = REPORT+"<td>Av mil:</td>"
	REPORT = REPORT+"<td>5% mil:</td><td>50% mil:</td><td>95% mil:</td>"
	REPORT = REPORT+"<td>1st acc:</td><td>Lst acc:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		FORMATEDTIME1 = DT.datetime.strptime(str(i[9])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		FORMATEDTIME2 = DT.datetime.strptime(str(i[10])[:-5], "%Y-%m-%dT%H:%M:%S").strftime('%b %d %I:%M %p')
		if str(i[0]) in ORGMAP:
			REPORT = REPORT + "<tr><td>"+ORGMAP[str(i[0])]+" ("+str(i[0])+")</td>"
		else:
			REPORT = REPORT + "<tr><td>"+str(i[0])+" ("+str(i[0])+")</td>"
		REPORT = REPORT+"<td>"+str(i[1])+"</td>"
		REPORT = REPORT+"<td>"+str(i[2])+"</td>"
		REPORT = REPORT+"<td>"+str(i[3])+"</td>"
		REPORT = REPORT+"<td>"+str(i[4])+"</td>"
		REPORT = REPORT+"<td>"+str(i[5])+"</td>"
		REPORT = REPORT+"<td>"+str(i[6])+"</td>"
		REPORT = REPORT+"<td>"+str(i[7])+"</td>"
		REPORT = REPORT+"<td>"+str(i[8])+"</td>"
		REPORT = REPORT+"<td>"+FORMATEDTIME1+"</td>"
		REPORT = REPORT+"<td>"+FORMATEDTIME2+"</td></tr>"
			
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='11'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"

	
def summaryLogstrafficTotals(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS	

	QUERY_DESC="""Logstraffic summary"""
	print ("Running LOGSTRAFFIC SUMMARY query - retrieve %s ...\n") % (QUERY_DESC)

	cur.execute("""SELECT app_name, \
		discarded, infos, events, errors, total \
		FROM %s  \
		WHERE day=%s and month=%s \
		ORDER BY total DESC""" %(table, DAY, MONTH))


	REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
	REPORT = REPORT+"<table border='1' cellpadding='1' cellspacing='0' width='800'>"
	REPORT = REPORT+"<tr><td>Application:</td><td>Discarded:</td><td>Infos:</td><td>Events:</td><td>Errors:</td>"
	REPORT = REPORT+"<td>Total:</td></tr>"
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if (int(i[4]) > 0) or (int(i[1]) > 0):
			BG_COLOR="#FFFF00"
		else:
			BG_COLOR="#FFFFFF"		
		REPORT = REPORT + "<tr><td bgcolor="+BG_COLOR+">"+str(i[0])+"</td><td bgcolor="+BG_COLOR+">"+str(i[1])+"</td><td bgcolor="+BG_COLOR+">"+str(i[2])+"</td><td bgcolor="+BG_COLOR+">"+str(i[3])+"</td><td bgcolor="+BG_COLOR+">"+str(i[4])+"</td><td bgcolor="+BG_COLOR+">"+str(i[5])+"</td></tr>"	
		if (int(i[1]) > 0):
			COMPONENT_STATUS="FAILED"
			
	if (ROW == 0):
		REPORT = REPORT+"<tr><td align='center' colspan='11'><i>Logs data is missing</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	
	
	
def uploadSummary(activity, summary_table_name, unique_id):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	
	print ("Executing %s query %s ...\n") % (activity, summary_table_name)
	#REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	cur.execute("""SELECT count(DISTINCT %s) as count, status, org_id \
		FROM %s \
		WHERE \
		%s is not null and \
		day=%s and month=%s \
		GROUP BY org_id, status \
		ORDER BY org_id ASC""" %(unique_id, summary_table_name, unique_id, DAY, MONTH))
		
	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	REPORT = REPORT+"<tr><td>Activity:</td><td>Doc Count:</td><td>Status:</td><td>Organization:</td></tr>"	
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		if str(i[1]) == "error":
			REPORT = REPORT+"<tr><td width='50%' bgcolor='#FFFF00'>"+activity+"</td><td width='10%' bgcolor='#FFFF00'>"+str(i[0])+"</td>"
			REPORT = REPORT+"<td width='10%' bgcolor='#FFFF00'>"+str(i[1])+"</td>"
			if str(i[2]) in ORGMAP:
				REPORT = REPORT+"<td width='20%' bgcolor='#FFFF00'>"+ORGMAP[str(i[2])]+" ("+str(i[2])+")</td></tr>"
			else:
				REPORT = REPORT+"<td width='20%' bgcolor='#FFFF00'>"+str(i[2])+" ("+str(i[2])+")</td></tr>"
			COMPONENT_STATUS="FAILED"
		else:
			REPORT = REPORT+"<tr><td width='50%'>"+activity+"</td><td width='10%'>"+str(i[0])+"</td>"
			REPORT = REPORT+"<td width='10%'>"+str(i[1])+"</td>"
			if str(i[2]) in ORGMAP:
				REPORT = REPORT+"<td width='20%'>"+ORGMAP[str(i[2])]+" ("+str(i[2])+")</td></tr>"
			else:
				REPORT = REPORT+"<td width='20%'>"+str(i[2])+" ("+str(i[2])+")</td></tr>"

	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='5'><i>There were no "+activity+" "+summary_table_name+" errors</i></td></tr>"
	REPORT = REPORT+"</table><br>" 	


def jobSummary(table):
	global REPORT, cur, conn
	global DAY, MONTH, COMPONENT_STATUS
	jobs = 0
	failedjobs = 0
	succeededjobs = 0
	print ("Jobs summary query ...\n")
	#REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
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
		ORDER BY org_id, activity ASC""" % (table, DAY, MONTH))
		
	REPORT = REPORT+"<table border='1' width='800' cellspacing='0'>"
	REPORT = REPORT+"<tr><td>Count:</td><td>Status:</td><td>Activity:</td><td>Organization:</td></tr>"		
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		jobs = jobs + int(i[0])
		if str(i[1]) == "error":
			failedjobs = failedjobs + int(i[0])
			REPORT = REPORT+"<tr><td bgcolor='#FFFF00'>"+str(i[0])+"</td><td bgcolor='#FFFF00'>"+str(i[1])+"</td>"
			REPORT = REPORT+"<td bgcolor='#FFFF00'>"+str(i[2])+"</td>"
			if str(i[3]) in ORGMAP: 
				REPORT = REPORT+"<td bgcolor='#FFFF00'>"+ORGMAP[str(i[3])]+" ("+str(i[3])+")</td></tr>"
			else:
				REPORT = REPORT+"<td bgcolor='#FFFF00'>"+str(i[3])+" ("+str(i[3])+")</td></tr>"
			COMPONENT_STATUS="FAILED"
		else:
			REPORT = REPORT+"<tr><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td>"
			REPORT = REPORT+"<td>"+str(i[2])+"</td>"
			if str(i[3]) in ORGMAP: 
				REPORT = REPORT+"<td>"+ORGMAP[str(i[3])]+" ("+str(i[3])+")</td></tr>"
			else:
				REPORT = REPORT+"<td>"+str(i[3])+" ("+str(i[3])+")</td></tr>"
	REPORT = REPORT+"<tr><td colspan='4' align='left' bgcolor='#D0D0D0'><b> \
		"+str(jobs)+"</b> - Total number of Jobs processed, out of which <font color='#DF1000'><b>"+str(failedjobs)+" failed</b></font> and <font color='#00A303'><b>"+str(jobs-failedjobs)+" succeeded</b></font> \
		</font></td></tr>"
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='4'><i>There were no Jobs</i></td></tr>"
	REPORT = REPORT+"</table><br>" 	


def failedJobsRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT + SUBHDR % "FAILED JOBS"
	COMPONENT_STATUS="PASSED"
	obtainFailedJobs("summary_coordinator_jobfinish"+POSTFIX)

	if (COMPONENT_STATUS == "PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	print ("Completed failed jobs query ... \n")
	
def errorMessagesRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT + SUBHDR % "SPECIFIC ERRORS"
	COMPONENT_STATUS="PASSED"
	obtainErrors("DR","summary_docreceiver_upload"+POSTFIX, "doc_id")
	obtainErrors("DR","summary_docreceiver_archive"+POSTFIX, "doc_id")
	obtainErrors("DR","summary_docreceiver_seqfile"+POSTFIX, "doc_id")
	obtainErrors("Parser","summary_parser"+POSTFIX, "doc_id")
	obtainErrors("OCR","summary_ocr"+POSTFIX, "doc_id")
	obtainErrors("Persist Mapper","summary_persist_mapper"+POSTFIX, "doc_id")
	obtainErrors("Persist Reducer","summary_persist_reducer"+POSTFIX, "patient_uuid")
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

def uploadSummaryRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "UPLOAD SUMMARY"
	COMPONENT_STATUS="PASSED"
	uploadSummary("Doc-Receiver","summary_docreceiver_upload"+POSTFIX, "doc_id")
	uploadSummary("OCR","summary_ocr"+POSTFIX, "doc_id")
	uploadSummary("Persist Mapper","summary_persist_mapper"+POSTFIX, "doc_id")
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

def jobSummaryRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "JOB SUMMARY"
	COMPONENT_STATUS="PASSED"
	jobSummary("summary_coordinator_jobfinish"+POSTFIX)

	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

def careOptimizerErrorsRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "CARE OPTIMIZER"
	COMPONENT_STATUS="PASSED"
	careOptimizerErrors("summary_careopt_errors"+POSTFIX)
	careOptimizerLoad("summary_careopt_load"+POSTFIX)
	careOptimizerSearch("summary_careopt_search"+POSTFIX)
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	
def logsTrafficRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "LOGS TRAFFIC"
	COMPONENT_STATUS="PASSED"
	summaryLogstrafficTotals("summary_logstraffic"+POSTFIX)
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	
def dataOrchestratorRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "DATA ORCHESTRATOR"
	COMPONENT_STATUS="PASSED"
	dataOrchestratorAcls("summary_dataorchestrator_acl"+POSTFIX)
	dataOrchestratorLookups("summary_dataorchestrator_lookup"+POSTFIX)
	dataOrchestratorRequests("summary_dataorchestrator_request"+POSTFIX)
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"	

def userAccountsRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "USER ACCOUNTS"
	COMPONENT_STATUS="PASSED"
	userAccountsRequests("summary_useraccount_request"+POSTFIX)
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"	

def bundlerRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "BUNDLER"
	COMPONENT_STATUS="PASSED"
	bundlerSequence("summary_bundler_sequence"+POSTFIX)
	bundlerHistorical("summary_bundler_historical"+POSTFIX)
	bundlerDocuments("summary_bundler_document"+POSTFIX)
	
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"	
	
def eventsRD():
	global SUBHDR, COMPONENT_STATUS, REPORT, COMPONENT_STATUS, POSTFIX
	REPORT = REPORT+SUBHDR % "EVENTS"
	COMPONENT_STATUS="PASSED"
	eventAMR("summary_event_address"+POSTFIX)
	eventAMR("summary_event_mapper"+POSTFIX)
	eventAMR("summary_event_reducer"+POSTFIX)	
		
	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"		
	

def writeReportDetails():
	if (REPSECTORUN == 1) or (REPSECTORUN == 0):
		failedJobsRD()
	if (REPSECTORUN == 2) or (REPSECTORUN == 0):	
		errorMessagesRD()			
	if (REPSECTORUN == 3) or (REPSECTORUN == 0):
		uploadSummaryRD()
	if (REPSECTORUN == 4) or (REPSECTORUN == 0):
		jobSummaryRD()
	if (REPSECTORUN == 5) or (REPSECTORUN == 0):
		careOptimizerErrorsRD()
	if (REPSECTORUN == 6) or (REPSECTORUN == 0):
		logsTrafficRD()
	if (REPSECTORUN == 7) or (REPSECTORUN == 0):
		eventsRD()
	if (REPSECTORUN == 8) or (REPSECTORUN == 0):
		# currently 09/05/2014 only available for staging env
		# if ENVIRONMENT == "staging":
		# now 09/24/2014 available in both staging and production
		dataOrchestratorRD()
	if (REPSECTORUN == 9) or (REPSECTORUN == 0):
		# currently 09/08/2014 only available for staging env
		# if ENVIRONMENT == "staging":
		# now 09/24/2014 available in both staging and production
		userAccountsRD()
	if (REPSECTORUN == 10) or (REPSECTORUN == 0):
		bundlerRD()			

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
	global DEBUG_MODE, ENVIRONMENT
	if not DEBUG_MODE:
		print ("Archiving report ...\n")
		BACKUPREPORTFOLDER="/mnt/reports/"+ENVIRONMENT+"/pipeline/"+str(YEAR)+"/"+str(CURMONTH)
		REPORTFOLDER="/usr/lib/apx-reporting/html/assets/reports/"+ENVIRONMENT+"/pipeline/"+str(YEAR)+"/"+str(CURMONTH)
		# ------------- Create new folder if one does not exist already -------------------------------
		if not os.path.exists(BACKUPREPORTFOLDER):
			os.makedirs(BACKUPREPORTFOLDER)
			os.chmod(BACKUPREPORTFOLDER, 0777)	
		if not os.path.exists(REPORTFOLDER):
			os.makedirs(REPORTFOLDER)
			os.chmod(REPORTFOLDER, 0777)
		# ---------------------------------------------------------------------------------------------
		REPORTFILENAME=str(CURDAY)+".html"
		REPORTXTSTRING="Daily "+ENVIRONMENT[:1].upper()+ENVIRONMENT[1:].lower()+" Report - "+str(MONTH_FMN)+" "+str(CURDAY)+", "+str(YEAR)+"\t"+"reports/"+ENVIRONMENT+"/pipeline/"+str(YEAR)+"/"+str(CURMONTH)+"/"+REPORTFILENAME+"\n"
		REPORTXTFILENAME="reports.txt"
		# Old location 
		#REPORTXTFILEFOLDER="/usr/lib/apx-reporting/html/assets"
		# New location 
		REPORTXTFILEFOLDER="/usr/lib/apx-reporting/html"
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
