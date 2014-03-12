#! /bin/sh

export TZ=America/Los_Angeles

timestamp=$(date +'%s')

datestamp=$(date +'%m/%d/%y %r')

orgid=$1
environment=$2
logtype=$3
recipient=$4

#========================================
# parameter list and descriptions

# $1 - OrgID
# $2 - staing or production Environment
# $3 - 24 or epoch LogType
# $4 - Email Recepient
#========================================

#============================================================================================
#  Assign default values to the paramaters
#============================================================================================
if [ -z $1 ]; then
	echo ">>> OrgID not provided, assigning default orgid value of 55"
	echo ">>> "
	orgid="55"
fi
if [ -z $2 ]; then
	echo ">>> Environment not provided, assigning default environment value of staging"
	echo ">>> "
	environment="staging"
fi
if [ -z $3 ]; then
	echo ">>> LogType not provided, assigning default logtype value of epoch"
	echo ">>> "
	logtype="epoch"
fi
if [ -z $4 ]; then
	echo ">>> Recipient email address not provided, assigning value of ishekhtman@apixio.com"
	echo ">>> "
	recipient="ishekhtman@apixio.com"
fi

indexerlogfile="indexer_manifest_epoch"
docreceiverlogfile=$environment"_logs_docreceiver_"$logtype
coordinatorlogfile=$environment"_logs_coordinator_"$logtype
parserlogfile=$environment"_logs_parserjob_"$logtype
ocrlogfile=$environment"_logs_ocrjob_"$logtype
persistlogfile=$environment"_logs_persistjob_"$logtype

#============================================================================================

filename=qa_report_$timestamp.txt

echo " "
echo "Connecting to Hive ..."
echo "Running Hive queries, please wait ..."
echo " "

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver >> $filename << EOF
set mapred.job.queue.name=hive;


SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded_to_s3,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $docreceiverlogfile
WHERE get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.upload.document.status') = "success" and
get_json_object(line, '$.upload.document.orgid') = "$orgid";

EOF

mail -s "Pipeline QA Report for orgID $orgid - $datestamp" -r ishekhtman@apixio.com $recipient < $filename

rm $filename
echo " "
echo "Please check your email for results ..."