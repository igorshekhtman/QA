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

# /mnt/automation; python2.6 qa_seqfile_report.py $BATCH $MONTH1 $MONTH2 $DAY1 $DAY2 $TYPE $ORG $MAILTO

if len(sys.argv) < 8 :
    print "ERROR: Missing Required Arguments"
elif str(sys.argv[1]) == "none" and str(sys.argv[7]) == "none" :
    print "ERROR: Requires either batch or org id"
else :
    batch = str(sys.argv[1])
    startMonth = str(sys.argv[2])
    endMonth = str(sys.argv[3])
    startDay = str(sys.argv[4])
    endDay = str(sys.argv[5])
    type = str(sys.argv[6]) # not currently used
    org = str(sys.argv[7])
    mailto = str(sys.argv[8])
    mailfrom = "donotreply@apixio.com"
    
    environment = "Staging" # could make this configurable
    
    qaFromSeqFile = environment.lower() + "_logs_qafromseqfile_epoch"

    report = """From: Apixio QA <QA@apixio.com>
    To: Engineering <%s>
    MIME-Version: 1.0
    Content-type: text/html
    Subject: Pipeline QA Batch Report %s
    
    <h1>Apixio Pipeline QA Report</h1>
    Month(s): <b>%s (-%s)</b><br>
    Day(s): <b>%s (-%s)</b><br>
    Enviromnent: <b>%s</b><br>
    OrgID: <b>%s</b><br>
    BatchID: <b>%s</b><br>
    """ % (mailto, environment, startMonth, endMonth, startDay, endDay, environment, org, batch)

    passed = "<table><tr><td bgcolor='#00A303' align='center' width='800'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
    failed = "<table><tr><td bgcolor='#DF1000' align='center' width='800'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
    subheadder = "<table><tr><td bgcolor='#4E4E4E' align='left' width='800'><font size='3' color='white'><b>&nbsp;&nbsp;%s</b></font></td></tr></table>"
    
    # ====================================================================================================

    conn = pyhs2.connect(host='10.196.47.205',
                     port=10000,
                     authMechanism="PLAIN",
                     user='hive',
                     password='',
                     database='default')

    cur = conn.cursor()

    print ("Assigning queue name to hive ...")
    cur.execute("""SET mapred.job.queue.name=hive""")

    dates = ""
    if endDay == "none" and endMonth == "none" :
        dates = "day=%s and month=%s" % (startDay, startMonth)
    elif endMonth == "none" :
        dates = "day>=%s and day<=%s and month=%s" % (startDay, endDay, startMonth)
    else :
        dates = "day>=%s and day<=%s and month>=%s and month<=%s" % (startDay, endDay, startMonth, endMonth)
    
    jobname = batch
    if batch == "none" : jobname = org
    
    query = """SELECT count (distinct get_json_object(line, '$.input.uuid')) as col_0, \
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
        FROM %s \
        WHERE get_json_object(line, '$.jobname') like "%s%%" \
        and get_json_object(line, '$.output') is not null \
        and %s \
        GROUP BY get_json_object(line, '$.output.uploadedToS3'), \
        get_json_object(line, '$.output.documentEntry.orgId'), \
        get_json_object(line, '$.output.trace.parserJob'), \
        get_json_object(line, '$.output.trace.ocrJob'), \
        get_json_object(line, '$.output.trace.persistJob'), \
        get_json_object(line, '$.output.trace.appendToSequenceFile'), \
        get_json_object(line, '$.output.trace.submitToCoordinator'), \
        get_json_object(line, '$.output.link.orgIdByDocUUID'), \
        get_json_object(line, '$.output.link.orgIdByPatientUUID'), \
        if( get_json_object(line, '$.output.apo.patientKey') is not null, 'found', 'none'), \
        if( get_json_object(line, '$.output.apo.uuid') is not null, 'found', 'none')""" %(qaFromSeqFile, jobname, dates)

    print ("\nRUNNING QUERY:")
    print (query)

    cur.execute(query)

    # ====================================================================================================

    report += subheadder % "QA from Sequence File"
    report += "<table border='0' cellpadding='1' cellspacing='0'><tr><td><b></b></td></tr></table>"
    report += "<table border='0' cellpadding='1' cellspacing='0'>"
    report += "<tr><th>docCount</th><th>archived</th><th>docEntry</th><th>parserTrace</th><th>ocrTrace</th><th>persistTrace</th><th>seqFileTrace</th><th>sentTrace</th><th>docLink</th><th>patLink</th><th>apo</th><th>patUUID</th></tr>"

    ROW = 0
    sum = 0
    result = []
    for resultRow in cur.fetch():
        ROW = ROW + 1
        print resultRow
        result.append(resultRow)
        if (ROW <= 2):
            sum += int(resultRow[0])
        report += "<tr>"
        for col in resultRow:
            if (str(col) == org):
                report += "<td align='center'>found</td>"
            else:
                report += "<td align='center'>" + str(col) + "</td>"
        report += "</tr>"
    report += "</table><br>"

    # ====================================================================================================

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

    # ====================================================================================================

    print ("\nANALYSIS:")
    for key,count in reportResults.items():
        print "\t" + key + ": " + str(count)

    startCountTable = "<table border='0' cellpadding='1' cellspacing='0'>"
    startCountTable = startCountTable + "<tr><th>  </th><th>Count</th></tr>"
    endCountTable = "</table>"
    countTableRow = "<tr><td align='right'>%s: </td><td align='center'>%s</td></tr>"

    # ===========================================
    report += subheadder % "Data Verification"
    report += startCountTable
    totalCount = reportResults["total"]
    mapperVerifiedCount = reportResults["verified"]
    reducerFailedCount = reportResults["failedReducer"]
    archiveFailedCount = reportResults["failedArchive"]
    report += countTableRow % ("Verified APOs Persisted", str(mapperVerifiedCount))
    report += countTableRow % ("Failed Archive to S3", str(archiveFailedCount))
    report += countTableRow % ("Failed Persist Reducer", str(reducerFailedCount))
    report += countTableRow % ("Total Documents", str(totalCount))
    report += endCountTable
    if (mapperVerifiedCount == totalCount and reducerFailedCount == 0 and archiveFailedCount == 0):
        report += passed
    else:
        report += failed
    report += "<br>"
    # ===========================================

    # ===========================================
    report += subheadder % "Link Table Verification"
    report += startCountTable
    failedDocLinkCount = reportResults["noDocLink"]
    failedPatLinkCount = reportResults["noPatLink"]
    report += countTableRow % ("Missing Document UUID Link", str(failedDocLinkCount))
    report += countTableRow % ("Missing Patient UUID Link", str(failedPatLinkCount))
    report += endCountTable
    if (failedDocLinkCount == 0 and failedPatLinkCount == 0):
        report += passed
    else:
        report += failed
    report += "<br>"
    # ===========================================

    # ===========================================
    report += subheadder % "Trace Verification"
    report += startCountTable
    failedDocEntry = reportResults["noDocEntry"]
    failedTrace = 0
    report += countTableRow % ("Missing Document Entry", str(failedDocEntry))

    temp = reportResults["noSeqfileTrace"]
    report += countTableRow % ("Missing Sequence File Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noSentTrace"]
    report += countTableRow % ("Missing Sent to Coordinator Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noParserTrace"]
    report += countTableRow % ("Missing Parser Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noOCRTrace"]
    report += countTableRow % ("Missing OCR Trace", str(temp))
    failedTrace += temp

    temp = reportResults["noPersistTrace"]
    report += countTableRow % ("Missing Persist Trace", str(temp))
    failedTrace += temp

    report += endCountTable
    if (failedDocEntry == 0 and failedTrace == 0):
        report += passed
    else:
        report += failed
    report += "<br>"
    # ===========================================

    report += "<br><br>"

    # ====================================================================================================

    cur.close()
    conn.close()

    report += "<table><tr><td><br>End of Batch QA Report<br><br></td></tr>"
    report += "<tr><td><br><i>-- Apixio QA Team</i></td></tr></table>"

    s=smtplib.SMTP()
    s.connect("smtp.gmail.com",587)
    s.starttls()
    s.login("donotreply@apixio.com", "apx.mail47")
    s.sendmail(mailfrom, mailto, report)
    print "\nReport completed, successfully sent email to %s ..." % (mailto)

    print (report)
