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
print ("Version 1.1.1")

#================================================================================================
#=== ORGID - ORGNAME MAP ========================================================================
#================================================================================================
ORGMAP = { \
	"190":"Test Org", \
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
	"10000279":"Production Test Org", \
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
	"__HIVE_DEFAULT_PARTITION__":"__HIVE_DEFAULT_PARTITION__", \
	"None":"Missing Orgname", \
}

#========================================================================================================
#=== COMPONENT - COMPLIST ARRAY =========================================================================
#========================================================================================================
COMPLIST = ["indexer", "docreceiver", "coordinator", "parserjob", "ocr", "persist"]
#========================================================================================================


#============ INITIALIZE DEFAULT VALUES - GLOBAL VALIABLES =========================
print ("Start initializing global variables ...\n")
TEST_TYPE="N/A"
REPORT_TYPE="Engineering QA"
ORGID = "190"
ENVIRONMENT = "Staging"
LOGTYPE = "24"
RECEIVERS = "ishekhtman@apixio.com"
# set to all to QA all components
COMPONENT = "docreceiver"
#COMPONENT = "coordinator"
#COMPONENT = "parserjob"
#COMPONENT = "all"
HTML_RECEIVERS = """To: Igor <ishekhtman@apixio.com>\n"""
DATERANGE = ""
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
BATCHID="N/A"
USERNAME="N/A"
UPLOADED_DR = 0
ARCHTOS3 = 0
ADDTOSF = 0
PASSED="<table align='left' width='800' cellspacing='0' cellpadding='2'><tr><td bgcolor='#00A303' align='center' ><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED="<table align='left' width='800' cellspacing='0' cellpadding='2'><tr><td bgcolor='#DF1000' align='center' ><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SENDER="donotreply@apixio.com"
TEST_TYPE="N/A"
REPORT_TYPE="Engineering QA"
SENDER="donotreply@apixio.com"
REPORT=""
print ("Finished initializing global variables ...\n")
#===================================================================================	

def checkEnvntnRepRcvrs():
	global RECEIVERS, HTML_RECEIVERS, LOGTYPE
	global ENVIRONMENT, USERNAME, ORGID, PASSWORD, HOST
	global STMON, STDAY, ENMON, ENDAY
	# If no paramaters are passed, default values are chosen
	# apixio_pipeline_qa.py 280 Staging epoch eng@apixio.com 05 04 05 06
	# sys.argv[1] = ORGID = "280" (default 190)
	# sys.argv[2] = ENVIRONMENT = "Staging" or "Production" (default Staging)
	# sys.argv[3] = LOGTYPE = "24" or "epoch" (default 24)
	# sys.argv[4] = RECEIVERS = "ishekhtman@apixio.com" (default)
	# sys.argv[5] = STMON = "05" (default current month)
	# sys.argv[6] = STDAY = "04" (default current day)
	# sys.argv[7] = ENMON = "05" (default current month)
	# sys.argv[8] = ENDAY = "06" (default current day)
	# sys.argv[8] = COMPONENT = "docreceiver" (default docreceiver)

	print ("Start aquiring environment varibales ...\n")
	
	if len(sys.argv) >= 2:
		ORGID = str(sys.argv[1])
	
	if len(sys.argv) >= 3:
		if (str(sys.argv[2])[0:1].upper() == "P"):
			USERNAME="apxdemot0138"
			PASSWORD="Hadoop.4522"
			HOST="https://dr.apixio.com:8443"
			ENVIRONMENT="Production"
		elif (str(sys.argv[2])[0:1].upper() == "S"):
			USERNAME="apxdemot0182"
			PASSWORD="Hadoop.4522"
			HOST="https://supload.apixio.com:8443"
			ENVIRONMENT="Staging"
			
	if len(sys.argv) >= 4:
		if (str(sys.argv[3])[0:1].upper() == "2"):
			LOGTYPE = "24"
		elif (str(sys.argv[3])[0:1].upper() == "E"):
			LOGTYPE = "epoch"
	
	if len(sys.argv) >= 5:
		if len(str(sys.argv[4])) > 6:
			if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", str(sys.argv[4])) != None:
				RECEIVERS=str(sys.argv[4])
				HTML_RECEIVERS="""To: """+str(sys.argv[4])[0:3].upper()+""" <"""+str(sys.argv[4])+""">\n"""
			else:	
				RECEIVERS="ishekhtman@apixio.com"
				HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""

	if len(sys.argv) >= 6:
		if (int(sys.argv[5]) > 0) and (int(sys.argv[5]) < 13):
			STMON = str(sys.argv[5])
	if len(sys.argv) >= 7:
		if (int(sys.argv[6]) > 0) and (int(sys.argv[6]) < 32):
			STDAY = str(sys.argv[6])
	if len(sys.argv) >= 8:
		if (int(sys.argv[7]) > 0) and (int(sys.argv[5]) <= int(sys.argv[7])):
			ENMON = str(sys.argv[7])
		else:
			ENMON = STMON
	if len(sys.argv) >= 9:
		if (((int(sys.argv[7]) == int(sys.argv[5])) and (int(sys.argv[6]) <= int(sys.argv[8]))) or (int(sys.argv[7]) > int(sys.argv[5]))):
			ENDAY = str(sys.argv[8])
		else:
			ENDAY = STDAY
			
	if len(sys.argv) >= 10:
		if (str(sys.argv[9])[0:2].upper() == "IN"):
			COMPONENT = "indexer"
		elif (str(sys.argv[9])[0:2].upper() == "DO"):
			COMPONENT = "docreceiver"
		elif (str(sys.argv[9])[0:2].upper() == "CO"):
			COMPONENT = "coordinator"
		elif (str(sys.argv[9])[0:2].upper() == "PA"):
			COMPONENT = "parser"
		elif (str(sys.argv[9])[0:2].upper() == "OC"):
			COMPONENT = "ocr"
		elif (str(sys.argv[9])[0:2].upper() == "PE"):
			COMPONENT = "persist"

		
def prntVarValues():		
	print ("=========================================================================\n")
	print ("TEST_TYPE = %s") % TEST_TYPE
	print ("REPORT_TYPE = %s") % REPORT_TYPE
	print ("ORGID = %s") % ORGID
	print ("ENVIRONMENT = %s") % ENVIRONMENT
	print ("LOGTYPE = %s") % LOGTYPE
	print ("RECEIVERS = %s") % RECEIVERS
	print ("HTML_RECEIVERS = %s") % HTML_RECEIVERS
	print ("STARTINGMONTH = %s") % STMON
	print ("STARTINGDAY = %s") % STDAY
	print ("ENDINGMONTH = %s") % ENMON
	print ("ENDINGDAY = %s") % ENDAY
	print ("PIPELINE COMPONENT = %s") % COMPONENT
	print ("=========================================================================\n")
	#time.sleep(15)

	
def constructLogFileName(component):
	global ENVIRONMENT, LOGTYPE
	if component == "indexer":
		logfilename="indexer_manifest_epoch"
	else:
		logfilename=ENVIRONMENT.lower()+"_logs_"+component+"_"+LOGTYPE
	return(logfilename)
	
		
def flowControl():	
	# !!! currently not being used !!!!!!!!!!
	# Specific Query Number to Run
	QNTORUN=3
	# Run one or all queries
	PROCESS_ALL_QUERIES=bool(0)
	# Send report emails and archive report html file
	DEBUG_MODE=bool(1)



def identifyRepDaynMnth():
	global STMON, STDAY, ENMON, ENDAY
	global DATERANGE, DAYSBACK, CURDAY, CURMONTH

	ENMON = strftime("%m", gmtime())
	ENDAY = strftime("%d", gmtime())
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


	DAY=CURDAY
	MONTH=CURMONTH
	STMON = CURMONTH
	STDAY = CURDAY
	# override for testing purposes
	STMON = ENMON
	STDAY = ENDAY


def test(debug_type, debug_msg):
	print "debug(%d): %s" % (debug_type, debug_msg)
	
def connectToHive():
	print ("Connecing to Hive ...\n")
	global cur, conn
	conn = pyhs2.connect(host='10.196.47.205', \
		port=10000, authMechanism="PLAIN", \
		user='hive', password='', \
		database='default')
	cur = conn.cursor()
	print ("Connection to Hive established ...\n")


def setHiveParms():
	print ("Assigning Hive paramaters ...\n")
	cur.execute("""set hive.exec.dynamic.partition=true""")
	cur.execute("""set hive.exec.dynamic.partition.mode=nonstrict""")
	cur.execute("""set mapred.reduce.tasks=16""")
	#cur.execute("""set mapred.job.queue.name=default""")
	cur.execute("""set mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	print ("Completed assigning Hive paramaters ...\n")	
	
	
def wrtRepHdr():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Start writing report header ...\n")
	REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	REPORT = REPORT + HTML_RECEIVERS
	REPORT = REPORT + """MIME-Version: 1.0\n"""
	REPORT = REPORT + """Content-type: text/html\n"""
	REPORT = REPORT + """Subject: %s Pipeline QA Report - OrgID %s Time %s\n\n""" % (ENVIRONMENT, ORGID, CUR_TIME)

	REPORT = REPORT + """<h1>Apixio %s Pipeline QA Report</h1>\n""" % (ENVIRONMENT)
	REPORT = REPORT + """Date & Time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	REPORT = REPORT + """Report date-range: <b>from %s/%s/%s to %s/%s/%s</b><br>\n""" % (STMON, STDAY, YEAR, ENMON, ENDAY, YEAR)
	if str(ORGID) in ORGMAP:
		REPORT = REPORT + """Organization: <b>%s (%s)</b><br>\n""" % (ORGMAP[str(ORGID)], ORGID)
	else:
		REPORT = REPORT + """Organization: <b>%s (%s)</b><br>\n""" % (ORGID, ORGID)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s</font></b><br><br>\n""" % (ENVIRONMENT)
	print ("End writing report header ...\n")	

def buildQuery(component, subcomp):
	global ORGID, STMON, STDAY, ENMON, ENDAY
	
# if(error_message like '/mnt%%','No space left on device', error_message) as message \	

	logfile =(constructLogFileName(component))
	if component == "indexer":
		query="""\
			SELECT filetype, count(filetype) as qty_each \
			FROM %s \
			WHERE orgid=%s and \
			((substr(datestamp,0,2)>=%s and substr(datestamp,4,2)>=%s) and \
			(substr(datestamp,0,2)<=%s and substr(datestamp,4,2)<=%s)) \
			GROUP BY filetype""" % (constructLogFileName(component), ORGID, STMON, STDAY, ENMON, ENDAY)
		
	if component == "docreceiver" and subcomp == "upload":
		query="""\
			SELECT\
			count(DISTINCT get_json_object(line, '$.upload.document.docid')) as doc_count,\
			get_json_object(line, '$.upload.document.status') as status,\
			get_json_object(line, '$.error.message') as message\
			FROM %s\
			WHERE\
			get_json_object(line, '$.upload.document.orgid') = '%s' and\
			get_json_object(line, '$.level') = 'EVENT' and\
			month>=%s and day>=%s and\
			month<=%s and day<=%s\
			GROUP BY\
			get_json_object(line, '$.upload.document.status'),\
			get_json_object(line, '$.error.message')""" %\
			(logfile, ORGID, STMON, STDAY, ENMON, ENDAY)
				
		
	if component == "docreceiver" and subcomp == "archive":
		query="""\
			SELECT \
			count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as doc_count, \
			get_json_object(line, '$.archive.afs.status') as status, \
			get_json_object(line, '$.error.message') as message \
			FROM %s \
			WHERE \
			get_json_object(line, '$.archive.afs.orgid') = '%s' and \
			get_json_object(line, '$.level') = 'EVENT' and \
			month>=%s and day>=%s and \
			month<=%s and day<=%s \
			GROUP BY \
			get_json_object(line, '$.archive.afs.status'), \
			get_json_object(line, '$.error.message')""" % \
			(logfile, ORGID, STMON, STDAY, ENMON, ENDAY)					
			
	if component == "docreceiver" and subcomp == "seqfile":
		query="""\
			SELECT \
			count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as doc_count, \
			get_json_object(line, '$.seqfile.file.add.status') as status, \
			get_json_object(line, '$.error.message') as message \
			FROM %s \
			WHERE \
			get_json_object(line, '$.seqfile.file.document.orgid') = '%s' and \
			get_json_object(line, '$.level') = 'EVENT' and \
			month>=%s and day>=%s and \
			month<=%s and day<=%s \
			GROUP BY \
			get_json_object(line, '$.seqfile.file.add.status'), \
			get_json_object(line, '$.error.message')""" % \
			(logfile, ORGID, STMON, STDAY, ENMON, ENDAY)
	
	if component == "docreceiver" and subcomp == "submit":
		query="""\
			SELECT \
			get_json_object(line, '$.submit.post.apxfiles.count') as ind_files, \
			get_json_object(line, '$.submit.post.status') as status, \
			get_json_object(line, '$.error.message') as message, \
			get_json_object(line, '$.submit.post.numfiles') as seq_files_sent_to_redis, \
			get_json_object(line, '$.submit.post.queue.name') as redis_queue_name \
			FROM %s \
			WHERE \
			get_json_object(line, '$.level') = "EVENT" and \
			get_json_object(line, '$.submit.post.orgid') = '%s' and \
			month>=%s and day>=%s and \
			month<=%s and day<=%s \
			GROUP BY \
			get_json_object(line, '$.submit.post.status'), \
			get_json_object(line, '$.submit.post.numfiles'), \
			get_json_object(line, '$.error.message'), \
			get_json_object(line, '$.submit.post.apxfiles.count'), \
			get_json_object(line, '$.submit.post.queue.name')""" % \
			(logfile, ORGID, STMON, STDAY, ENMON, ENDAY)

	if component == "coordinator":
		query="""\
			SELECT \
			count(DISTINCT(get_json_object(line, '$.job.jobID'))) as count, \
			get_json_object(line, '$.job.activity') as activity, \
			get_json_object(line, '$.job.status') as status \
			FROM %s \
			WHERE \
			get_json_object(line, '$.job.context.orgid') = '%s' and \
			month>=%s and day>=%s and \
			month<=%s and day<=%s and \
			get_json_object(line, '$.job.status') is not null and \
			get_json_object(line, '$.job.status') <> 'start' \
			GROUP BY \
			get_json_object(line, '$.job.status'), \
			get_json_object(line, '$.job.activity')""" % \
			(logfile, ORGID, STMON, STDAY, ENMON, ENDAY)
	
	if component == "parserjob":
		query="""\
			SELECT \
			count(DISTINCT get_json_object(line, '$.documentuuid')) as  count, \
			get_json_object(line, '$.status') as status, \
			get_json_object(line, '$.error.message') as message \
			FROM %s \
			WHERE \
			get_json_object(line, '$.orgId') = '%s' and \
			month>=%s and day>=%s and \
			month<=%s and day<=%s \
			GROUP BY \
			get_json_object(line, '$.status'), \
			get_json_object(line, '$.error.message')""" %\
			(logfile, ORGID, STMON, STDAY, ENMON, ENDAY)
		
		
	
	return(query)
	

def runQueries(component, subcomp):
	global REPORT, SUBHDR
	if str(ORGID) in ORGMAP:
		SUBHDR="<table align='left' width='800' cellpadding='2'><tr><td bgcolor='#4E4E4E'><font size='3' color='white'>\
			<b>&nbsp;&nbsp;"+component.upper()+" ("+subcomp+") "+ORGMAP[str(ORGID)]+" ("+ORGID+")</b></font></td></tr></table>"
	else:
		SUBHDR="<table align='left' width='800' cellpadding='2'><tr><td bgcolor='#4E4E4E'><font size='3' color='white'>\
			<b>&nbsp;&nbsp;"+component.upper()+" ("+subcomp+") "+ORGID+" ("+ORGID+")</b></font></td></tr></table>"
	
	# possible component values: indexer, doc-receiver, coordinator, parser, ocr, persist-mapper, persist-reducer
	
	REPORT = REPORT + SUBHDR
	COMPONENT_STATUS="PASSED"
	
	#QUERY_DESC="Number of documents - %s" % (component)
	print ("Running %s - %s query ...\n") % (component, subcomp)
	print (buildQuery(component, subcomp))
	cur.execute(buildQuery(component, subcomp))
		
	REPORT = REPORT+"<table border='1' width='800' cellspacing='0' cellpadding='2'>"
	REPORT = REPORT+"<tr><td width='10%'>Doc Count:</td><td width='10%'>Status:</td><td width='80%'>Message:</td></tr>"	
	ROW = 0
	for i in cur.fetch():
		ROW = ROW + 1
		print i
		REPORT = REPORT+"<tr>"
		REPORT = REPORT+"<td>"+str(i[0])+"</td>"
		REPORT = REPORT+"<td>"+str(i[1])+"</td>"
		REPORT = REPORT+"<td>"+str(i[2])+"</td>"
		REPORT = REPORT+"</tr>"	
	
	if (ROW == 0):
		REPORT = REPORT+"<tr><td colspan='3'><i>There were no "+component+" "+subcomp+" logs</i></td></tr>"
	REPORT = REPORT+"</table><br>" 	
		
	

	if (COMPONENT_STATUS=="PASSED"):
		REPORT = REPORT+PASSED
	else:
		REPORT = REPORT+FAILED
	REPORT = REPORT+"<br><br>"
	

def wrtRepDtls():
	global COMPONENT
	# possible component values: indexer, docreceiver, coordinator, parser, ocr, persist, all
	#runQueries(COMPONENT)

	
	if COMPONENT == "docreceiver":
		runQueries(COMPONENT, "upload")
		runQueries(COMPONENT, "archive")
		runQueries(COMPONENT, "seqfile")
		runQueries(COMPONENT, "submit")
	elif COMPONENT == "persistjob":
		runQueries(COMPONENT, "mapper")
		runQueries(COMPONENT, "reducer")
	elif COMPONENT.upper() == "ALL":
		for COMP in COMPLIST:
			if COMP == "docreceiver":
				runQueries(COMPONENT, "upload")
				runQueries(COMPONENT, "archive")
				runQueries(COMPONENT, "seqfile")
				runQueries(COMPONENT, "submit")
			elif COMP == "persistjob":
				runQueries(COMPONENT, "mapper")
				runQueries(COMPONENT, "reducer")
			else:
				runQueries(COMPONENT, "")		
	else:
		runQueries(COMPONENT, "")
		



def closeHiveConnct():
	global cur, conn
	cur.close()
	conn.close()
	
def wrtRepFootr():
	print ("Write report footer ...\n")
	global REPORT
	REPORT = REPORT+"<table cellpadding='2'>"
	REPORT = REPORT+"<tr><td><br>End of %s - %s<br><br></td></tr>" % (REPORT_TYPE, CUR_TIME)
	REPORT = REPORT+"<tr><td><i>-- Apixio QA Team</i></td></tr>"
	REPORT = REPORT+"</table>"
	print ("Finished writing report ...\n")	
	
def archiveRep():
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


def emailRep():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS, RECEIVERS2
	print ("Emailing report ...\n")
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, RECEIVERS, REPORT)	
	#s.sendmail(SENDER, RECEIVERS2, REPORT)
	print "Report completed, successfully sent email to %s ..." % (RECEIVERS)	

# ====================================================================================================================================
# ======================================== MAIN BODY =================================================================================
# ====================================================================================================================================


identifyRepDaynMnth()

checkEnvntnRepRcvrs()	

prntVarValues()

wrtRepHdr()	

connectToHive()

setHiveParms()

wrtRepDtls()

closeHiveConnct()

wrtRepFootr()

#archiveRep()

emailRep()


# ======================================== END =======================================================================================




