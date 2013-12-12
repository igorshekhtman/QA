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
echo " "
echo "Running Hive queries, please wait ..."
echo " "

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver >> $filename << EOF
set mapred.job.queue.name=hive;

SELECT count(DISTINCT apixiouuid) as number_of_documents_indexer,
concat(substr(min(datestamp),0,10), "  ", substr(min(datestamp),12,8)) as start_Time,
concat(substr(max(datestamp),0,10), "  ", substr(max(datestamp),12,8)) as end_Time,
round(((UNIX_TIMESTAMP(concat(substr(max(datestamp),0,10), " ", substr(max(datestamp),12,8))) - UNIX_TIMESTAMP(concat(substr(min(datestamp),0,10), " ", substr(min(datestamp),12,8))))/60),2) as duration_in_min 
FROM $indexerlogfile 
WHERE orgid="$orgid";

SELECT filetype, count(filetype) as qty_each
FROM $indexerlogfile 
WHERE orgid="$orgid"
GROUP BY filetype;

SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded_to_s3,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $docreceiverlogfile
WHERE get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.upload.document.status') = "success" and
get_json_object(line, '$.upload.document.orgid') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.archive.aps.docid')) as documents_archived,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $docreceiverlogfile 
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.archive.aps.status') = "success" and
get_json_object(line, '$.archive.aps.orgid') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $docreceiverlogfile 
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.seqfile.file.document.status') = "success" and
get_json_object(line, '$.seqfile.file.document.orgid') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.submit.post.files')) as number_of_seq_files_sent_to_redis,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $docreceiverlogfile 
WHERE get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.submit.post.status') = "success" and
get_json_object(line, '$.submit.post.orgid') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_jobs_started_by_coordinator,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $coordinatorlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.coordinator.job.status') = "start" and
get_json_object(line, '$.coordinator.job.context.organization') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_jobs_succeeded_by_coordinator,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $coordinatorlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.coordinator.job.status') = "success" and
get_json_object(line, '$.coordinator.job.context.organization') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_jobs_failed_by_coordinator
FROM $coordinatorlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.coordinator.job.status') = "error" and
get_json_object(line, '$.coordinator.job.context.organization') = "$orgid";

SELECT  COUNT(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_failed_jobs, job_type
FROM
        (
            select  *, get_json_object(line, '$.coordinator.job.jobType') as job_type
            from    $coordinatorlogfile
            where   get_json_object(line, '$.level') = "EVENT" and 
                    get_json_object(line, '$.coordinator.job.status') = "error" and
                    get_json_object(line, '$.coordinator.job.context.organization') = "$orgid"
        ) sub
GROUP BY job_type;

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_OCR,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $parserlogfile 
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.tag.ocr.status') = "success" and
get_json_object(line, '$.orgId') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_Persist,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $parserlogfile 
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.tag.persist.status') = "success" and
get_json_object(line, '$.orgId') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Parser_Errors
FROM $parserlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and 
get_json_object(line, '$.status') <> "success" and
get_json_object(line, '$.orgId') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  OCR_distinct_UUIDs_succeeded,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $ocrlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.status') = "success" and
get_json_object(line, '$.orgId') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as OCR_distinct_UUIDs_failed
FROM $ocrlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.status') <> "success" and
get_json_object(line, '$.orgId') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Persist_distinct_UUIDs_succeeded,
concat(substr(min(get_json_object(line, '$.datestamp')),0,10), "  ", substr(min(get_json_object(line, '$.datestamp')),12,8)) as start_Time, 
concat(substr(max(get_json_object(line, '$.datestamp')),0,10), "  ", substr(max(get_json_object(line, '$.datestamp')),12,8)) as end_time,
round(((max(get_json_object(line, '$.time')) - min(get_json_object(line, '$.time'))) / 1000 / 60),2) as duration_In_min
FROM $persistlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.status') = "success" and
get_json_object(line, '$.orgId') = "$orgid";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Persist_distinct_UUIDs_failed
FROM $persistlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.status') <> "success" and
get_json_object(line, '$.orgId') = "$orgid";
EOF

mail -s "Pipeline QA Report $environment orgID $orgid - $datestamp" -r ishekhtman@apixio.com $recipient < $filename

rm $filename
echo " "
echo "Please check your email for results ..."