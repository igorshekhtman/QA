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
import cStringIO
import uuid

os.system('clear')

# ================== INITIALIZING GLOBAL VARIABLES VALUES ============================================

TEST_TYPE="QuickTest"

# Environment for SanityTest is passed as a paramater. Staging is a default value
if ((len(sys.argv) > 1) and (str(sys.argv[1])[:1].upper() == "P")):
	USERNAME="apxdemot0138"
	ORGID="10000279"
	PASSWORD="Hadoop.4522"
	HOST="https://dr.apixio.com:8443"
	ENVIRONMENT="Production"
else:
	USERNAME="apxdemot0245"
	ORGID="261"
	PASSWORD="Hadoop.4522"
	HOST="https://supload.apixio.com:8443"
	ENVIRONMENT="Staging"

print ("ENVIRONMANT = %s") % ENVIRONMENT

DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
BATCHID=strftime("%m%d%Y%H%M%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())

UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCHID)
TOKEN_URL="%s/auth/token/" % (HOST)

BATCH=ORGID+"_"+TEST_TYPE+ENVIRONMENT+"_"+BATCHID
DRBATCH=TEST_TYPE+ENVIRONMENT+"_"+BATCHID
MANIFEST_FILENAME=BATCH+"_manifest.txt"

CLOSE_URL="%s/receiver/batch/%s/status/flush" % (HOST, DRBATCH)
UPLOAD_URL_2="%s/receiver/batch/%s/document/upload" % (HOST, DRBATCH)

DOCUMENTCOUNTER=0
NUMBEROFDOCUMENTS=0

DOCUMENTS_TRANSMITTED=20
DOCUMENTS_TO_OCR=0
DOCUMENTS_TO_PERSIST=0

MANIFEST_FILE=""

PAUSE_LIMIT = 600

QUICK_QA=True

QUERY_DESC=""
COMPONENT_STATUS="PASSED"
LOGTYPE="24"

#INDEXERLOGFILE="indexer_manifest_epoch"
#DOCRECEIVERLOGFILE=ENVIRONMENT.lower()+"_logs_docreceiver_"+LOGTYPE
#COORDINATORLOGFILE=ENVIRONMENT.lower()+"_logs_coordinator_"+LOGTYPE
#PARSERLOGFILE=ENVIRONMENT.lower()+"_logs_parserjob_"+LOGTYPE
#OCRLOGFILE=ENVIRONMENT.lower()+"_logs_ocrjob_"+LOGTYPE
#PERSISTLOGFILE=ENVIRONMENT.lower()+"_logs_persistjob_"+LOGTYPE
QAFROMSEQFILELOGFILE=ENVIRONMENT.lower()+"_logs_qafromseqfile_"+LOGTYPE

SENDER="donotreply@apixio.com"

if (len(sys.argv) > 2):
    RECEIVERS = str(sys.argv[2])
else:
    RECEIVERS="eng@apixio.com"

categoryURL = "?category="
cat = "standard"
if (len(sys.argv) > 3):
    cat = str(sys.argv[3])
    categoryURL += cat
    UPLOAD_URL += categoryURL
    UPLOAD_URL_2 += categoryURL
    CLOSE_URL += categoryURL

# ====================================================================================================

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
print ("UPLOAD_URL_2 = %s") % UPLOAD_URL_2
print ("CLOSE_URL = %s") % CLOSE_URL
print ("TOKEN_URL = %s") % TOKEN_URL
print ("USERNAME = %s") % USERNAME
print ("PASSWORD = %s") % PASSWORD
print ("HOST = %s") % HOST
print ("DIR = %s") % DIR

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

def uploadData():
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

# ==================== Assign Values ==================================================================
FILES = os.listdir(DIR)


print ("\nUploading ...\n")


for FILE in FILES:
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
    CATALOG_FILE=("<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>%s</DocumentId><Patient><PatientId><Id>%s</Id><AssignAuthority>%s</AssignAuthority></PatientId><PatientFirstName>%s</PatientFirstName><PatientMiddleName>%s</PatientMiddleName><PatientLastName>%s</PatientLastName><PatientDOB>%s</PatientDOB><PatientGender>%s</PatientGender></Patient><Organization>%s</Organization><PracticeName>%s</PracticeName><FileLocation>%s</FileLocation><FileFormat>%s</FileFormat><DocumentType>%s</DocumentType><CreationDate>%s</CreationDate><ModifiedDate>%s</ModifiedDate><Description>%s</Description><MetaTags>%s</MetaTags><SourceSystem>%s</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>" % (DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, DESCRIPTION, METATAGS, SOURCE_SYSTEM))
		
    # =============== Uploading Data ==============================================================
    bufu = io.BytesIO()
    response = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, UPLOAD_URL_2)
    c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (pycurl.FORM_FILE, DIR+"/"+FILE)),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])
    c.setopt(c.WRITEFUNCTION, bufu.write)
    c.setopt(c.DEBUGFUNCTION, test)
    c.perform()
    # =============================================================================================
    obju=json.loads(bufu.getvalue())
    UUID=obju["uuid"]
    
    print ("Document UUID: %s" % (UUID))
    MANIFEST_FILE=MANIFEST_FILE+("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t02/22/14 02:02:37 AM\n") % (DOCUMENT_ID, SOURCE_SYSTEM, USERNAME, UUID, ORGANIZATION, ORGID, BATCH, FILE_FORMAT)


# =================== Finish by closing batch =========================================================

	
print ("\nTOTAL NUMBER OF DOCUMENTS UPLOADED: %s\n" % (DOCUMENTCOUNTER));

print ("Closing Batch ...\n")

bufc = io.BytesIO()
response = cStringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, CLOSE_URL)
c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
c.setopt(c.WRITEFUNCTION, bufc.write)
c.setopt(c.DEBUGFUNCTION, test)
c.perform()
objc=json.loads(bufc.getvalue())

print ("Batch Closed, Upload Completed ...\n")
# ==================== Transmitting Manifest File =====================================================

# Currently this is only working on Staging
if ENVIRONMENT == "Staging":
	print ("Transmitting Manifest File ...\n")

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
	print ("Manifest file transmitted ...\n")


# =====================================================================================================
# ============ PAUSE FOR UPLOAD TO COMPLETE BEFORE PROCEEDING TO QUERIES ==============================

# wait for PAUSE_LIMIT seconds
print ("Pausing for %s seconds for all jobs to complete ...") % (PAUSE_LIMIT)
time.sleep(PAUSE_LIMIT)


# =====================================================================================================
# =============== Initialize variables and assign values for QA Report=================================


PASSED="<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED="<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"


REPORT = """From: Apixio QA <QA@apixio.com>
To: Engineering <eng@apixio.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Pipeline QA Report %s batchID %s - %s

<h1>Apixio Pipeline QA Report</h1>
Date & Time: <b>%s</b><br>
Test type: <b>%s</b><br>
Enviromnent: <b>%s</b><br>
Category: <b>%s</b><br>
OrgID: <b>%s</b><br>
BatchID: <b>%s</b><br>
User name: <b>%s</b><br><br>
""" % (ENVIRONMENT, BATCH, CUR_TIME, CUR_TIME, TEST_TYPE, ENVIRONMENT, cat, ORGID, BATCHID, USERNAME)


conn = pyhs2.connect(host='10.196.47.205',
                   port=10000,
                   authMechanism="PLAIN",
                   user='hive',
                   password='',
                   database='default')

cur = conn.cursor()

print (BATCH)

print ("Assigning queue name to hive ...")
cur.execute("""SET mapred.job.queue.name=hive""")


# =====================================================================================================
# ============================ QA From Sequence File Queries ==========================================
# =====================================================================================================

REPORT = REPORT+SUBHDR % "QA from Sequence File"

if QUICK_QA:
    QUERY_DESC=""
<<<<<<< HEAD
    print ("Running QA query #16 - retrieve %s ...") % (QUERY_DESC)
    cur.execute("""SELECT count (distinct get_json_object(line, '$.input.uuid')) as docUUID_count, \
		get_json_object(line, '$.output.uploadedToS3') as saved_to_s3, \
        get_json_object(line, '$.output.documentEntry.orgId') as confirm_docentry, \
        get_json_object(line, '$.output.trace.parserJob') as parser_trace, \
        get_json_object(line, '$.output.trace.ocrJob') as ocr_trace, \
        get_json_object(line, '$.output.trace.persistJob') as persist_trace, \
        get_json_object(line, '$.output.trace.appendToSequenceFile') as seqfile_trace, \
        get_json_object(line, '$.output.trace.submitToCoordinator') as sent_to_coordinator_trace, \
        get_json_object(line, '$.output.link.orgIdByDocUUID') as doc_link, \
        get_json_object(line, '$.output.link.orgIdByPatientUUID') as pat_link, \
        if( get_json_object(line, '$.output.apo.uuid') is not null, 'found', 'not found') as apo_status \
=======
    print ("Running QA query - retrieve %s ...") % (QUERY_DESC)
    cur.execute("""SELECT count (distinct get_json_object(line, '$.input.uuid')) as col_0, \
		get_json_object(line, '$.output.uploadedToS3') as col_1, \
        get_json_object(line, '$.output.documentEntry.orgId') as col_2, \
        get_json_object(line, '$.output.trace.parserJob') as col_3, \
        get_json_object(line, '$.output.trace.ocrJob') as col_4, \
        get_json_object(line, '$.output.trace.persistJob') as col_5, \
        get_json_object(line, '$.output.trace.appendToSequenceFile') as col_6, \
        get_json_object(line, '$.output.trace.submitToCoordinator') as col_7, \
        get_json_object(line, '$.output.link.orgIdByDocUUID') as col_8, \
        get_json_object(line, '$.output.link.orgIdByPatientUUID') as col_9, \
        if( get_json_object(line, '$.output.apo.patientKey') is not null, 'found', 'none') as col_10, \
        if( get_json_object(line, '$.output.apo.uuid') is not null, 'found', 'none') as col_11 \
>>>>>>> branch 'master' of https://github.com/Apixio/QA.git
		FROM %s \
		WHERE get_json_object(line, '$.jobname') like "%s%%" \
		and get_json_object(line, '$.output') is not null \
		and day=%s and month=%s \
		GROUP BY get_json_object(line, '$.output.uploadedToS3'), \
        get_json_object(line, '$.output.documentEntry.orgId'), \
        get_json_object(line, '$.output.trace.parserJob'), \
        get_json_object(line, '$.output.trace.ocrJob'), \
        get_json_object(line, '$.output.trace.persistJob'), \
        get_json_object(line, '$.output.trace.appendToSequenceFile'), \
        get_json_object(line, '$.output.trace.submitToCoordinator'), \
        get_json_object(line, '$.output.link.orgIdByDocUUID'), \
        get_json_object(line, '$.output.link.orgIdByPatientUUID'), \
<<<<<<< HEAD
=======
        if( get_json_object(line, '$.output.apo.patientKey') is not null, 'found', 'none'), \
>>>>>>> branch 'master' of https://github.com/Apixio/QA.git
        if( get_json_object(line, '$.output.apo.uuid') is not null, 'found', 'none')""" %(QAFROMSEQFILELOGFILE, BATCH, DAY, MONTH))
    REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'><tr><td><b>"+QUERY_DESC+"</b></td></tr></table>"
    REPORT = REPORT+"<table border='0' cellpadding='1' cellspacing='0'>"
    
<<<<<<< HEAD
    REPORT = REPORT+"<tr><th>docCount</th><th>archived</th><th>docEntry</th><th>parserTrace</th><th>ocrTrace</th><th>persistTrace</th><th>seqFileTrace</th><th>sentTrace</th><th>docLink</th><th>patLink</th><th>apoUUID</th></tr>"
=======
    REPORT = REPORT+"<tr><th>docCount</th><th>archived</th><th>docEntry</th><th>parserTrace</th><th>ocrTrace</th><th>persistTrace</th><th>seqFileTrace</th><th>sentTrace</th><th>docLink</th><th>patLink</th><th>apo</th><th>patUUID</th></tr>"
>>>>>>> branch 'master' of https://github.com/Apixio/QA.git
    ROW = 0
    sum = 0
    result = []
    for resultRow in cur.fetch():
        ROW = ROW + 1
        print resultRow
        result.append(resultRow)
        if (ROW <= 2):
            sum += int(resultRow[0])
        REPORT = REPORT + "<tr>"
        for col in resultRow:
            if (str(col) == ORGID):
                REPORT = REPORT + "<td align='center'>found</td>"
            else:
                REPORT = REPORT + "<td align='center'>" + str(col) + "</td>"
        REPORT = REPORT + "</tr>"
    if (sum == DOCUMENTS_TRANSMITTED):
        COMPONENT_STATUS="PASSED"
    else:
        COMPONENT_STATUS="FAILED"
    REPORT = REPORT+"</table><br>"

    reportResults = {"total":0,
        "verified":0,
        "failedArchive":0,
        "noParserTrace":0,
        "noOCRTrace":0,
        "noPersistTrace":0,
        "noDocEntry":0,
        "noSeqfileTrace":0,
        "noSentTrace":0,
        "noDocLink":0,
        "noPatLink":0,
        "failedReducer":0}

    for line in result:
        count = line[0]
        reportResults["total"] += count
        if line[1] != "true":
            reportResults["failedArchive"] += count
        if line[2] != ORGID:
            reportResults["noDocEntry"] += count
        if line[3] != "sentToOCR" and line[3] != "sentToPersist":
            reportResults["noParserTrace"] += count
        if line[3] == "sentToOCR" and line[4] != "sentToPersist":
            reportResults["noOCRTrace"] += count
        if line[5] != "persisted":
            reportResults["noPersistTrace"] += count
        if line[6] != "success":
            reportResults["noSeqfileTrace"] += count
        if line[7] != "success":
            reportResults["noSentTrace"] += count
        if line[8] != ORGID:
            reportResults["noDocLink"] += count
        if line[9] != ORGID:
            reportResults["noPatLink"] += count
        if line[10] == "found":
            reportResults["verified"] += count
        if line[11] != "found":
            reportResults["failedReducer"] += count

    startCountTable = "<table border='0' cellpadding='1' cellspacing='0'>"
    startCountTable = startCountTable + "<tr><th>  </th><th>Count</th></tr>"
    endCountTable = "</table>"
    countTableRow = "<tr><td align='right'>%s: </td><td align='center'>%s</td></tr>"
    for key,count in reportResults.items():
        print key + ": " + str(count)

    # ===========================================
    REPORT = REPORT+SUBHDR % "Data Verification"
    REPORT = REPORT+startCountTable
    mapperVerifiedCount = reportResults["verified"]
    reducerFailedCount = reportResults["failedReducer"]
    archiveFailedCount = reportResults["failedArchive"]
    REPORT = REPORT+countTableRow % ("Verified APOs Persisted", str(mapperVerifiedCount))
    REPORT = REPORT+countTableRow % ("Failed Archive to S3", str(archiveFailedCount))
    REPORT = REPORT+countTableRow % ("Failed Persist Reducer", str(reducerFailedCount))
    REPORT = REPORT+countTableRow % ("Total Documents", str(reportResults["total"]))
    REPORT = REPORT+endCountTable
    if (mapperVerifiedCount == DOCUMENTS_TRANSMITTED and reducerFailedCount == 0 and archiveFailedCount == 0):
        REPORT = REPORT+PASSED
    else:
        REPORT = REPORT+FAILED
    REPORT = REPORT+"<br>"
    # ===========================================

    # ===========================================
    REPORT = REPORT+SUBHDR % "Link Table Verification"
    REPORT = REPORT+startCountTable
    failedDocLinkCount = reportResults["noDocLink"]
    failedPatLinkCount = reportResults["noPatLink"]
    REPORT = REPORT+countTableRow % ("Missing Document UUID Link", str(failedDocLinkCount))
    REPORT = REPORT+countTableRow % ("Missing Patient UUID Link", str(failedPatLinkCount))
    REPORT = REPORT+endCountTable
    if (failedDocLinkCount == 0 and failedPatLinkCount == 0):
        REPORT = REPORT+PASSED
    else:
        REPORT = REPORT+FAILED
    REPORT = REPORT+"<br>"
    # ===========================================

    # ===========================================
    REPORT = REPORT+SUBHDR % "Trace Verification"
    REPORT = REPORT+startCountTable
    failedDocEntry = reportResults["noDocEntry"]
    failedTrace = 0
    REPORT = REPORT+countTableRow % ("Missing Document Entry", str(failedDocEntry))

    temp = reportResults["noSeqfileTrace"]
    REPORT = REPORT+countTableRow % ("Missing Sequence File Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noSentTrace"]
    REPORT = REPORT+countTableRow % ("Missing Sent to Coordinator Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noParserTrace"]
    REPORT = REPORT+countTableRow % ("Missing Parser Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noOCRTrace"]
    REPORT = REPORT+countTableRow % ("Missing OCR Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noPersistTrace"]
    REPORT = REPORT+countTableRow % ("Missing Persist Trace", str(temp))
    failedTrace += temp

    REPORT = REPORT+endCountTable
    if (failedDocEntry == 0 and failedTrace == 0):
        REPORT = REPORT+PASSED
    else:
        REPORT = REPORT+FAILED
    REPORT = REPORT+"<br>"
    # ===========================================

REPORT = REPORT+"<br><br>"


# ====================================================================================================
# ====================================================================================================
# ====================================================================================================

cur.close()
conn.close()

REPORT=REPORT+"<table><tr><td><br>End of %s - %s QA report<br><br></td></tr>" % (BATCH, CUR_TIME)
REPORT=REPORT+"<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"

s=smtplib.SMTP()
s.connect("smtp.gmail.com",587)
s.starttls()
s.login("donotreply@apixio.com", "apx.mail47")
s.sendmail(SENDER, RECEIVERS, REPORT)	
print "Report completed, successfully sent email to %s ..." % (RECEIVERS)
