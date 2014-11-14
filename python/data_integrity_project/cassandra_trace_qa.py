from cassandra.cluster import Cluster
import logging
import os
import json
import sys
import smtplib
from time import gmtime, strftime, localtime

ORGID = "382"
REPORT = ""
RECEIVERS="ishekhtman@apixio.com"
HTML_RECEIVERS="""To: Igor <ishekhtman@apixio.com>\n"""
ENVIRONMENT="staging"
CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR=strftime("%Y", gmtime())
REPORT_TYPE="Cassandra Trace Table per ORG"
SENDER="donotreply@apixio.com"

if len(sys.argv) < 2:
	ORGID = raw_input("Please enter OrgID: ")
	#ORGID = "382"
else:
	ORGID = str(sys.argv[1])


#"d12240a0-a67b-4fd6-969a-e17bcb3a022a"

os.system('clear')
log = logging.getLogger()
log.setLevel('INFO')


cluster = Cluster(['10.199.22.32', '10.196.81.90', '10.198.2.83', '10.196.100.53', '10.197.91.36', '10.199.52.19'], port=9042)
session = cluster.connect('apixio')
session_new = cluster.connect('apixio')

PROC_MAP = { \
	"docEntry":"DE", \
	"appendToSequenceFile":"ATSF", \
	"eventJob":"EJ", \
	"ocrJob":"OJ", \
	"parserJob":"PAJ", \
	"persistJob":"PEJ", \
	"submitToCoordinator":"STC", \
}

sentToOCRctr = sentToPersistctr = 0

# Initialize all global counters to zero
for i in PROC_MAP:
	exec("%s = %d" % (PROC_MAP[i],0)) in globals()	

def countNumberOfOccurrences(proc_name):
	if proc_name in PROC_MAP:
		exec("%s = %s + %d" % (PROC_MAP[proc_name],PROC_MAP[proc_name],1)) in globals()

def writeReportHeader():
	global REPORT, ENVIRONMENT, HTML_RECEIVERS, RECEIVERS
	print ("Begin writing report header ...\n")
	REPORT = """From: Apixio QA <QA@apixio.com>\n"""
	REPORT = REPORT + HTML_RECEIVERS
	REPORT = REPORT + """MIME-Version: 1.0\n"""
	REPORT = REPORT + """Content-type: text/html\n"""
	REPORT = REPORT + """Subject: Cassandra %s Data Integrity (ORGID: %s) - %s\n\n""" % (ENVIRONMENT, ORGID, CUR_TIME)
	REPORT = REPORT + """<h1>Cassandra Data Integrity QA Report</h1>\n"""
	REPORT = REPORT + """Date & Time (run): <b>%s</b><br>\n""" % (CUR_TIME)
	REPORT = REPORT + """Date (logs & queries): <b>%s/%s/%s</b><br>\n""" % (MONTH, DAY, YEAR)
	REPORT = REPORT + """Report type: <b>%s</b><br>\n""" % (REPORT_TYPE)
	REPORT = REPORT + """Enviromnent: <b><font color='red'>%s%s</font></b><br>\n""" % (ENVIRONMENT[:1].upper(), ENVIRONMENT[1:].lower())
	REPORT = REPORT + """Org ID: %s<br><br><br>""" % ORGID
	print ("End writing report header ...\n")

writeReportHeader()


def emailReport():
	global RECEIVERS, SENDER, REPORT, HTML_RECEIVERS
	print ("Emailing report ...\n")
	s=smtplib.SMTP()
	s.connect("smtp.gmail.com",587)
	s.starttls()
	s.login("donotreply@apixio.com", "apx.mail47")	        
	s.sendmail(SENDER, RECEIVERS, REPORT)	
	print "Report completed, successfully sent email to %s ..." % (RECEIVERS)


def checkForExistance (doc_uuid):
	global sentToOCRctr, sentToPersistctr
	results_new = session_new.execute("""SELECT * FROM trace"""+ORGID+""" where rowkey='"""+doc_uuid+"""';""")
	for row_new in results_new:
		data_new = json.loads(row_new.d)
		if row_new.col[:8] == "docentry":
			process_name = "docEntry"	
		else:
			process_name = str(data_new["processName"])
		countNumberOfOccurrences(process_name)
		if process_name == "parserJob":	
			print str(row_new)
			print "\n" + str(data_new["documentUUID"]) + "\t" + process_name + "\t" + str(data_new["processStatusMessage"])
			if str(data_new["processStatusMessage"]) == "sentToOCR":
				sentToOCRctr = sentToOCRctr + 1
			elif str(data_new["processStatusMessage"]) == "sentToPersist":
				sentToPersistctr = sentToPersistctr + 1
			

#trace as you can guess contains document trace objects
print "\n\n"
print "OrgID: "+ORGID
print "Cassandra Table Name: trace"+ORGID

#results = session.execute("""SELECT COUNT(*) as count FROM trace"""+ORGID+""";""")
results = session.execute("""SELECT COUNT(*) as count FROM trace"""+ORGID+""";""")
for row in results:
	print "Total number of non-unique DOC-UUIDs for ORG(%s): %s\n" % (ORGID, str(row.count))
	raw_input("Press enter to continue, <Ctrl-C> to break...\n")
	
counter = 0	
results = session.execute("""SELECT DISTINCT rowkey as rowkey FROM trace"""+ORGID+""";""")
for row in results:
	if str(row.rowkey)[:7] == "docuuid":
		print str(row.rowkey)
		counter = counter + 1
		checkForExistance(str(row.rowkey))
		print "\n================"
		print str(counter)
		print "================\n"

print "\n\n\n"
print "Org ID: "+ORGID
print "received from Doc-Receiver: " + str(counter)
REPORT = REPORT + "<table align='left' cellpadding='4' cellspacing='0' border='1'>"
REPORT = REPORT + "<tr>"
REPORT = REPORT + "<td>received from Doc-Receiver: </td><td>" + str(counter) + "</td></tr>"
REPORT = REPORT + "<tr><td colspan='2' bgcolor='grey'></td></tr>"
print "\n"

for i in PROC_MAP:
	print str(i) +  ": " + str(eval(PROC_MAP[i]))
	REPORT = REPORT + "<tr><td>"+str(i) +  ": " + "</td><td>"+str(eval(PROC_MAP[i])) + "</td></tr>"

print "\n"
#REPORT = REPORT + "<br><br>"
print "sentToOCR: " + str(sentToOCRctr)
print "sentToPersist: " + str(sentToPersistctr)	
REPORT = REPORT + "<tr><td colspan='2' bgcolor='grey'></td></tr>"
REPORT = REPORT + "<tr><td>sentToOCR: </td><td>" + str(sentToOCRctr)+"</td></tr>"
REPORT = REPORT + "<tr><td>sentToPersist: </td><td>" + str(sentToPersistctr)+"</td></tr>"
REPORT = REPORT + "</table>"	

print "\n\n"



#checkForExistance("docuuid_d12240a0-a67b-4fd6-969a-e17bcb3a022a")

emailReport()
cluster.shutdown()
print "\nThe End ..."