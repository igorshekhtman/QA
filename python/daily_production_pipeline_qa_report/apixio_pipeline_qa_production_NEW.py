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
PROCESS_ALL_QUERIES=bool(0)

# Send report emails and archive report html file
DEBUG_MODE=bool(1)

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
DAYSBACK=7
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
	global RECEIVERS, HTML_RECEIVERS
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
		HTML_RECEIVERS="""To: Igor <%s>\n""" % str(sys.argv[2])
	elif ((len(sys.argv) < 3) or DEBUG_MODE):
		RECEIVERS="ishekhtman@apixio.com"
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
	global DAY, MONTH
	print ("Executing failed jobs query ...\n")
	cur.execute("""SELECT activity, hadoop_job_id, batch_id, org_id, time \
		FROM %s \
		WHERE \
		day=%s and month=%s and \
		status = 'error' \
		ORDER BY org_id ASC""" % ("summary_coordinator_jobfinish", DAY, MONTH))

	REPORT = REPORT + SUBHDR % "FAILED JOBS"
	COMPONENT_STATUS="PASSED"
	REPORT = REPORT+"<table border='1' width='800'>"
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
		REPORT = REPORT+"<tr><td align='center' colspan='6'><i>There were no failed jobs</i></td></tr>"
	REPORT = REPORT+"</table><br>"
	if (COMPONENT_STATUS == "PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	print ("Completed failed jobs query ... \n")
	

def writeReportDetails():
	global SUBHDR, COMPONENT_STATUS, REPORT
	

	obtainFailedJobs()

	
	REPORT = REPORT + SUBHDR % "SPECIFIC ERRORS"
	COMPONENT_STATUS="PASSED"

	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

	REPORT = REPORT+SUBHDR % "UPLOAD SUMMARY"
	COMPONENT_STATUS="PASSED"

	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

	REPORT = REPORT+SUBHDR % "JOB SUMMARY"
	COMPONENT_STATUS="PASSED"

	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

	REPORT = REPORT+SUBHDR % "CARE OPTIMIZER"
	COMPONENT_STATUS="PASSED"

	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"

	

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
	global RECEIVERS, SENDER, REPORT
	print ("Emailing report ...\n")
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, RECEIVERS, REPORT)	
	print "Report completed, successfully sent email to %s ..." % (RECEIVERS)
	
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
