#! /bin/sh

#=========================================== QA REPORT =====================================

export TZ=America/Los_Angeles

timestamp=$(date +'%s')
datestamp=$(date +'%m/%d/%y %r')
day=$(date +'%d')
month=$(date +'%m')
batchpostfix=$(date +'%m%d%y%H%M%S')
daysBack=1
curDay=$(date +%d);
curMonth=$(date +%m);
dateRange="";

#======== obtain day and month for previous from current day and month ===========================================
for (( c=1; c<=$daysBack; c++ ))
do
	if [ "$dateRange" == "" ];
	then
		dateRange="(month=$curMonth and day=$curDay)"
	else
		dateRange="$dateRange or (month=$curMonth and day=$curDay)"
	fi

	curDay=$(($curDay-1))
	if [ "$curDay" == "0" ];
	then
		curMonth=$(($curMonth - 1))
		if [ "$curMonth" == "0" ];
		then
			curMonth=12
		fi

		if [ "$curMonth" == "4" ] || [ "$curMonth" == "6" ] || [ "$curMonth" == "9" ] || [ "$curMonth" == "11" ];
		then
			curDay=30
		else 
			if [ "$curMonth" == "2" ];
			then
				curDay=28
			else
				curDay=31
			fi
		fi
	fi
done
#============ adjust day and month of the report =================================================================

day=$curDay
month=$curMonth
echo "Day: "$day
echo "Month: "$month

#=== production or staging ========================================================================================
environment="production"
#==================================================================================================================

#=== 24 or epoch ==================================================================================================
logtype="epoch"
#==================================================================================================================

#=== report email recepient address ===============================================================================
recipient="ishekhtman@apixio.com,alarocca@apixio.com,aaitken@apixio.com,jschneider@apixio.com,nkrishna@apixio.com,lschneider@apixio.com"
#recipient="ishekhtman@apixio.com"
#==================================================================================================================

indexerlogfile="indexer_manifest_epoch"
docreceiverlogfile=$environment"_logs_docreceiver_"$logtype
coordinatorlogfile=$environment"_logs_coordinator_"$logtype
parserlogfile=$environment"_logs_parserjob_"$logtype
ocrlogfile=$environment"_logs_ocrjob_"$logtype
persistlogfile=$environment"_logs_persistjob_"$logtype

INDEXERBATCH="SanityTestProduction_"$batchpostfix
BATCH=$ORGID"_SanityTestProduction_"$batchpostfix;

USERNAME=apxdemot0138;
ORGID=10000279
PASSWORD=Hadoop.4522;
HOST=https://dr.apixio.com:8443;
DIR=/mnt/testdata/SanityTwentyDocuments/Documents;
BATCH="SanityTestProduction_"$batchpostfix;

manifestfilename=$ORGID"_SanityTestProduction_"$batchpostfix"_manifest.txt";


#============================================================================================


filename=qa_report_$timestamp.txt

echo " "
echo "Connecting to Hive ..."
echo " "
echo "Running Hive queries, please wait ..."
echo " "

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver >> $filename << EOF
SET mapred.job.queue.name=hive;

SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, get_json_object(line, '$.upload.document.status') as status
FROM $docreceiverlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" AND
day=$day AND month=$month
GROUP BY get_json_object(line, '$.upload.document.status');

SELECT count(*) as number, get_json_object(line, '$.message') as error_message, get_json_object(line, '$.upload.document.orgid') as org_id
FROM $docreceiverlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.upload.document.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.message'), get_json_object(line, '$.upload.document.orgid');

SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, get_json_object(line, '$.archive.afs.status') as status
FROM $docreceiverlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.archive.afs.status');

SELECT count(*) as number, get_json_object(line, '$.message') as error_message, get_json_object(line, '$.archive.afs.orgid') as org_id
FROM $docreceiverlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.archive.afs.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.message'), get_json_object(line, '$.archive.afs.orgid');

SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, get_json_object(line, '$.seqfile.file.document.status') as status
FROM $docreceiverlogfile 
WHERE 
get_json_object(line, '$.level') = "EVENT" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.seqfile.file.document.status');

SELECT count(*) as number, get_json_object(line, '$.message') as error_message, get_json_object(line, '$.seqfile.file.document.orgid') as org_id
FROM $docreceiverlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.seqfile.file.document.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.message'), get_json_object(line, '$.seqfile.file.document.orgid');

SELECT count(DISTINCT get_json_object(line, '$.submit.post.files')) as number_of_seq_files_sent_to_redis, get_json_object(line, '$.submit.post.status') as status
FROM $docreceiverlogfile
WHERE get_json_object(line, '$.level') = "EVENT" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.submit.post.status');

SELECT count(*) as number, get_json_object(line, '$.message') as error_message, get_json_object(line, '$.submit.post.orgid') as org_id
FROM $docreceiverlogfile
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.submit.post.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.message'), get_json_object(line, '$.submit.post.orgid');

SELECT get_json_object(line, '$.upload.document.orgid') as org_id, 
count(DISTINCT get_json_object(line, '$.upload.document.docid')) as doc_receiver_uploaded_docs
FROM $docreceiverlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and 
get_json_object(line, '$.upload.document.status') = "success" and (day=$day and month=$month)
GROUP BY get_json_object(line, '$.upload.document.orgid');

SELECT count(distinct get_json_object(line, '$.seqfile.file.add.filename')) as no_of_seq_files_created
FROM $docreceiverlogfile
WHERE  
get_json_object(line, '$.seqfile.file.document.status') = "success" and
day=$day and month=$month;

SELECT count(distinct get_json_object(line, '$.inputSeqFileName')) as no_of_seq_files_processed
FROM $parserlogfile
WHERE
day=$day and month=$month;

SELECT count(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_jobs_started_by_coordinator, get_json_object(line, '$.coordinator.job.status') as status
FROM $coordinatorlogfile
WHERE
day=$day AND month=$month
GROUP BY get_json_object(line, '$.coordinator.job.status');

SELECT  COUNT(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_failed_jobs, job_type
FROM
        (
            select  *, get_json_object(line, '$.coordinator.job.jobType') as job_type
            from    $coordinatorlogfile
            where   get_json_object(line, '$.coordinator.job.status') = "error" and day=$day and month=$month
        ) sub
GROUP BY job_type;

SELECT  
get_json_object(line, '$.coordinator.job.jobType') as job_type, 
get_json_object(line, '$.coordinator.job.hadoopJobID') as hadoop_Job_ID, 
get_json_object(line, '$.coordinator.job.context.organization') as organization,
get_json_object(line, '$.datestamp') as date_and_time
FROM $coordinatorlogfile
WHERE   
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.coordinator.job.status') = "error" and day=$day and month=$month
ORDER BY job_type ASC;

SELECT 
get_json_object(line, '$.coordinator.job.context.organization') as org_id,
get_json_object(line, '$.coordinator.job.jobType') as job_type,
get_json_object(line, '$.coordinator.job.status') as job_status,
count(get_json_object(line, '$.coordinator.job.jobID')) as job_count 
FROM $coordinatorlogfile 
WHERE 
get_json_object(line, '$.coordinator.job') is not null
and (day=$day and month=$month)
GROUP BY
get_json_object(line, '$.coordinator.job.context.organization'),
get_json_object(line, '$.coordinator.job.jobType'),
get_json_object(line, '$.coordinator.job.status');

SELECT org_id, job_type, 
sum(case when job_status = 'start' then job_count else cast(0 as bigint) end) as start_count,
sum(case when job_status = 'success' then job_count else cast(0 as bigint) end) as success_count,
sum(case when job_status = 'error' then job_count else cast(0 as bigint) end) as error_count
FROM (
SELECT
get_json_object(line, '$.coordinator.job.context.organization') as org_id,
get_json_object(line, '$.coordinator.job.jobType') as job_type,
get_json_object(line, '$.coordinator.job.status') as job_status,
count(get_json_object(line, '$.coordinator.job.jobID')) as job_count 
FROM $coordinatorlogfile 
WHERE 
get_json_object(line, '$.coordinator.job') is not null
and (day=$day and month=$month)
GROUP BY
get_json_object(line, '$.coordinator.job.context.organization'),
get_json_object(line, '$.coordinator.job.jobType'),
get_json_object(line, '$.coordinator.job.status')) t
GROUP BY org_id, job_type;

SELECT get_json_object(line, '$.error.message') as ocr_error_message,
get_json_object(line, '$.jobname') as job_name,
COUNT (*) as error_count
FROM $parserlogfile
WHERE
get_json_object(line, '$.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.error.message'), get_json_object(line, '$.jobname');

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_OCR 
FROM $parserlogfile 
WHERE 
get_json_object(line, '$.tag.ocr.status') = "success" and
day=$day AND month=$month;

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_Persist
FROM $parserlogfile  
WHERE 
get_json_object(line, '$.tag.persist.status') = "success" and
day=$day AND month=$month;

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Parser_distinct_UUIDs, get_json_object(line, '$.status') as status
FROM $parserlogfile 
WHERE
day=$day AND month=$month
GROUP BY get_json_object(line, '$.status');

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  OCR_distinct_UUIDs, get_json_object(line, '$.status') as status
FROM $ocrlogfile
WHERE 
day=$day AND month=$month
GROUP BY get_json_object(line, '$.status');

SELECT get_json_object(line, '$.error.message') as ocr_error_message,
get_json_object(line, '$.orgId') as org_id,
get_json_object(line, '$.className') as class_name,
COUNT (*) as error_count
FROM $ocrlogfile
WHERE
get_json_object(line, '$.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.error.message'), get_json_object(line, '$.orgId'), get_json_object(line, '$.className');

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Persist_distinct_UUIDs, get_json_object(line, '$.status') as status
FROM $persistlogfile
WHERE 
day=$day AND month=$month
GROUP BY get_json_object(line, '$.status');

SELECT COUNT (*) as error_count,
get_json_object(line, '$.error.message') as persist_error_message,
get_json_object(line, '$.orgId') as org_id,
get_json_object(line, '$.columnFamily') as column_family,
get_json_object(line, '$.className') as class_name
FROM $persistlogfile
WHERE
get_json_object(line, '$.status') = "error" and
day=$day AND month=$month
GROUP BY get_json_object(line, '$.error.message'), get_json_object(line, '$.orgId'), get_json_object(line, '$.columnFamily'), get_json_object(line, '$.className');
EOF

mail -s "Daily Pipeline QA Report $environment - $datestamp" -r ishekhtman@apixio.com $recipient < $filename

rm $filename

echo " "
echo "Please check your email for results ..."
