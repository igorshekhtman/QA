#! /bin/sh

#=====================================================================================

export TZ=America/Los_Angeles

timestamp=$(date +'%s')
datestamp=$(date +'%m/%d/%y %r')
batchpostfix=$(date +'%m%d%y%H%M%S')

#==== Allowed values staging or production ===========================================
# default value is Staging
environment=$1
if [ -z $1 ]; then
	echo ">>> environment not provided, assigning default orgid value of Staging"
	echo ">>> "
	environment="Staging"
fi
#=====================================================================================

if [ "$environment" == "Staging" ];
then
	USERNAME=apxdemot0182;
	ORGID=190
	PASSWORD=Hadoop.4522;
	HOST=https://supload.apixio.com:8443;
	BATCH="SanityTestStaging_"$batchpostfix;
else
	USERNAME=apxdemot0138;
	ORGID=10000279
	PASSWORD=Hadoop.4522;
	HOST=https://dr.apixio.com:8443;	
	BATCH="SanityTestProduction_"$batchpostfix;
fi

DIR=/mnt/testdata/SanityTwentyDocuments/Documents;
manifestfilename=$ORGID"_SanityTest"$environment"_"$batchpostfix"_manifest.txt";

#=====================================================================================

echo "Authenticating..."
TOKEN=$(curl -s -k -d username=$USERNAME -d password=$PASSWORD "$HOST/auth/token/" | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["token"]');
echo "Got Token:" $TOKEN;

FILES=$DIR/*.*
echo "Processing files in: "$FILES;
for FILE in $FILES
do
	echo "Processing file: "$FILE
	DOCUMENT_ID=$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_ID=$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_ID_AA='RANDOM_UUID';
	PATIENT_FIRST_NAME=FIRST_$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_MIDDLE_NAME='';
	PATIENT_LAST_NAME=LAST_$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_DOB='19290809';
	PATIENT_GENDER='M';
	ORGANIZATION='Org_'$ORGID;
	PRACTICE_NAME='PRACTICE_NAME_VALUE';
	FILE_LOCATION=$FILE;
	FILE_FORMAT=$(echo "$FILE" | awk -F . '{print $NF}' | tr '[:lower:]' '[:upper:]');
	DOCUMENT_TYPE='DOCUMENT_TYPE_VALUE';
	CREATION_DATE='2010-05-11T10:00:47-07:00';
	MODIFIED_DATE='2010-05-11T10:00:47-07:00';
	DESCRIPTION=$FILE;
	METATAGS='METATAGS_VALUE';
	SOURCE_SYSTEM='SourceSystem_'$ORGID;

	CATALOG_FILE='<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>'$DOCUMENT_ID'</DocumentId><Patient><PatientId><Id>'$PATIENT_ID'</Id><AssignAuthority>'$PATIENT_ID_AA'</AssignAuthority></PatientId><PatientFirstName>'$PATIENT_FIRST_NAME'</PatientFirstName><PatientMiddleName>'$PATIENT_MIDDLE_NAME'</PatientMiddleName><PatientLastName>'$PATIENT_LAST_NAME'</PatientLastName><PatientDOB>'$PATIENT_DOB'</PatientDOB><PatientGender>'$PATIENT_GENDER'</PatientGender></Patient><Organization>'$ORGANIZATION'</Organization><PracticeName>'$PRACTICE_NAME'</PracticeName><FileLocation>'$FILE_LOCATION'</FileLocation><FileFormat>'$FILE_FORMAT'</FileFormat><DocumentType>'$DOCUMENT_TYPE'</DocumentType><CreationDate>'$CREATION_DATE'</CreationDate><ModifiedDate>'$MODIFIED_DATE'</ModifiedDate><Description>'$DESCRIPTION'</Description><MetaTags>'$METATAGS'</MetaTags><SourceSystem>'$SOURCE_SYSTEM'</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>';
	echo "Uploading..."
	UUID=$(echo $CATALOG_FILE | curl  -k --form document=@"$FILE" --form catalog=@- --form token=$TOKEN "$HOST/receiver/batch/$BATCH/document/upload" | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["uuid"]');
	echo "Uploaded Successfully. Document UUID: "$UUID;
	echo $DOCUMENT_ID'	'$SOURCE_SYSTEM'	'$USERNAME'	'$UUID'	'$ORGANIZATION'	'$ORGID'	'$ORGID'_'$BATCH'	'$FILE_FORMAT'	'$(date +'%m/%d/%y %r') >> $manifestfilename
done
echo "Closing Batch"
curl -s -k -X POST --form token=$TOKEN "$HOST/receiver/batch/$BATCH/status/flush?submit=true"
echo "Batch closed"
DATA=$manifestfilename
curl -3 -s -k -X PUT --form token=$TOKEN --form file=@$DATA  "$HOST/receiver/batch/$BATCH/manifest/$DATA/upload"
echo "Manifest file transmitted"

#============= Wait for 6 minutes for all Hadoop Jobs to Complete ==========================

sleep 6m

#=========================================== QA REPORT =====================================


logtype="24"
recipient="eng@apixio.com"
INDEXERBATCH="SanityTest"$environment"_"$batchpostfix
BATCH=$ORGID"_SanityTest"$environment"_"$batchpostfix;

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
SET mapred.job.queue.name=hive;

SELECT count(DISTINCT apixiouuid) as total_number_of_documents_indexer
FROM $indexerlogfile 
WHERE batchid = "$BATCH";

SELECT filetype, count(filetype) as qty_each
FROM $indexerlogfile  
WHERE batchid = "$BATCH"
GROUP BY filetype;

SELECT count(DISTINCT get_json_object(line, '$.upload.document.docid')) as documents_uploaded, get_json_object(line, '$.upload.document.status') as status
FROM $docreceiverlogfile
WHERE get_json_object(line, '$.level') = "EVENT" AND
get_json_object(line, '$.upload.document.batchid') = "$BATCH" 
GROUP BY get_json_object(line, '$.upload.document.status');

SELECT count(DISTINCT get_json_object(line, '$.archive.afs.docid')) as documents_archived_to_S3, get_json_object(line, '$.archive.afs.status') as status
FROM $docreceiverlogfile
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.archive.afs.batchid') = "$BATCH" 
GROUP BY get_json_object(line, '$.archive.afs.status');

SELECT count(DISTINCT get_json_object(line, '$.seqfile.file.document.docid')) as documents_added_to_seq_file, get_json_object(line, '$.seqfile.file.document.status') as status
FROM $docreceiverlogfile 
WHERE 
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.seqfile.file.document.batchid') = "$BATCH"
GROUP BY get_json_object(line, '$.seqfile.file.document.status');

SELECT get_json_object(line, '$.submit.post.numfiles') as seq_files_sent_to_redis, 
get_json_object(line, '$.submit.post.apxfiles.count') as ind_files, 
get_json_object(line, '$.submit.post.queue.name') as redis_queue_name
FROM $docreceiverlogfile
WHERE get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.submit.post.status') = "success" and
get_json_object(line, '$.submit.post.batchid') = "$BATCH";

SELECT count(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_jobs_by_coordinator, get_json_object(line, '$.coordinator.job.status') as status
FROM $coordinatorlogfile
WHERE
get_json_object(line, '$.context.batchID') = "$BATCH"
GROUP BY get_json_object(line, '$.coordinator.job.status');

SELECT  COUNT(DISTINCT get_json_object(line, '$.coordinator.job.jobID')) as number_of_failed_jobs, job_type
FROM
        (
            select  *, get_json_object(line, '$.coordinator.job.jobType') as job_type
            from    $coordinatorlogfile
            where   get_json_object(line, '$.coordinator.job.status') = "error" and
                    get_json_object(line, '$.context.batchID') = "$BATCH"
        ) sub
GROUP BY job_type;

SELECT get_json_object(line, '$.error.message') as parser_error_message, 
get_json_object(line, '$.className') as class_name, 
round((get_json_object(line, '$.file.bytes') / 1024 / 1024),2) as file_size_mb
FROM $parserlogfile
WHERE
get_json_object(line, '$.status') = "error" and
get_json_object(line, '$.jobname') LIKE "$BATCH%";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_OCR 
FROM $parserlogfile 
WHERE 
get_json_object(line, '$.tag.ocr.status') = "success" and
get_json_object(line, '$.batchId') = "$BATCH";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as Parser_distinct_UUIDs_tagged_to_Persist
FROM $parserlogfile  
WHERE 
get_json_object(line, '$.tag.persist.status') = "success" and
get_json_object(line, '$.batchId') = "$BATCH";

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Parser_distinct_UUIDs, get_json_object(line, '$.status') as status
FROM $parserlogfile 
WHERE
get_json_object(line, '$.batchId') = "$BATCH"
GROUP BY get_json_object(line, '$.status');

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  OCR_distinct_UUIDs, get_json_object(line, '$.status') as status
FROM $ocrlogfile
WHERE 
get_json_object(line, '$.batchId') = "$BATCH"
GROUP BY get_json_object(line, '$.status');

SELECT count(DISTINCT get_json_object(line, '$.documentuuid')) as  Persist_distinct_UUIDs, get_json_object(line, '$.status') as status
FROM $persistlogfile
WHERE 
get_json_object(line, '$.batchId') = "$BATCH"
GROUP BY get_json_object(line, '$.status');

SELECT get_json_object(line, '$.error.message') as persist_error_message, 
get_json_object(line, '$.className') as class_name, 
get_json_object(line, '$.file.bytes') as file_size_bytes
FROM $persistlogfile
WHERE
get_json_object(line, '$.status') = "error" and
get_json_object(line, '$.batchId') = "$BATCH";
EOF

mail -s "Pipeline QA Report $environment batchID $BATCH - $datestamp" -r ishekhtman@apixio.com $recipient < $filename

rm $filename
rm $manifestfilename
echo " "
echo "Please check your email for results ..."

