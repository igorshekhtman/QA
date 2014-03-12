#! /bin/sh

export TZ=America/Los_Angeles
daysBack=$1

if [ -z $1 ]; then
	echo ">>> Days back not provided, assigning value of 1"
	echo ">>> "
	daysBack=1
fi
curDay=$(date +%d);
curMonth=$(date +%m);

dateRange="";

for (( c=1; c<=$daysBack; c++ ))
do
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

	if [ "$dateRange" == "" ];
	then
		dateRange="(month=$curMonth and day=$curDay)"
	else
		dateRange="$dateRange or (month=$curMonth and day=$curDay)"
	fi
done


echo "Updating partitioned summary tables with date range: $dateRange"
echo " "

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver  >> update_summary.log   << EOF
set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
set mapred.reduce.tasks=16;
set mapred.job.queue.name=default;
set hive.exec.max.dynamic.partitions.pernode = 1000;

insert overwrite table temp_partition_docreceiver_upload_document partition (month,day, org_id)
SELECT 
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.upload.document.docid') as upload_doc_id,
get_json_object(line, '$.upload.document.status') as status,
get_json_object(line, '$.message') as message,
month,
day,
get_json_object(line, '$.upload.document.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.upload.document') is not null    
and ($dateRange);

insert overwrite table temp_partition_docreceiver_seqfile_document partition (month,day, org_id)
SELECT 
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.seqfile.file.document.docid') as seqfile_doc_id,
get_json_object(line, '$.seqfile.file.add.directory') as seqfile_directory,
get_json_object(line, '$.seqfile.file.add.filename') as seqfile_file,
get_json_object(line, '$.seqfile.file.document.status') as document_status,
get_json_object(line, '$.seqfile.file.add.status') as seqfile_status,
month,
day,
get_json_object(line, '$.seqfile.file.document.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.seqfile.file') is not null           
and ($dateRange);

insert overwrite table temp_partition_coordinator_hdfsmove partition(month,day,org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.coordinator.hdfsmove.to') as move_to,
get_json_object(line, '$.coordinator.hdfsmove.from') as move_from,
month,
day,
get_json_object(line, '$.coordinator.hdfsmove.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.coordinator.hdfsmove') is not null
and ($dateRange);

insert overwrite table temp_partition_coordinator_job partition(month,day,org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.coordinator.job.workID') as work_id,
get_json_object(line, '$.coordinator.job.jobID') as job_id,
get_json_object(line, '$.coordinator.job.jobType') as job_type,
get_json_object(line, '$.coordinator.job.inputDir') as input_dir,
get_json_object(line, '$.coordinator.job.outputDir') as output_dir,
get_json_object(line, '$.coordinator.job.status') as status,
get_json_object(line, '$.coordinator.job.duration') as duration,
get_json_object(line, '$.coordinator.job.hadoopJobID') as hadoop_job_id,
month,
day,
get_json_object(line, '$.coordinator.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.coordinator.job') is not null
and ($dateRange);

insert overwrite table temp_partition_parser_tag partition(month, day,org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.tag.ocr.status') as ocr_tag_status,
get_json_object(line, '$.tag.persist.status') as persist_tag_status,
get_json_object(line, '$.inputSeqFilePath') as input_seqfile_path,
get_json_object(line, '$.inputSeqFileName') as input_seqfile_name,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
from production_logs_parserjob_epoch where get_json_object(line, '$.level') != "INFO"
and ($dateRange);
             

insert overwrite table temp_partition_ocr partition(month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.inputSeqFilePath') as input_seqfile_path,
get_json_object(line, '$.inputSeqFileName') as input_seqfile_name,
get_json_object(line, '$.status') as status,    
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
from production_logs_ocrjob_epoch where get_json_object(line, '$.level') != "INFO"
and ($dateRange);


insert overwrite table temp_partition_persist_mapper partition(month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.inputSeqFilePath') as input_seqfile_path,
get_json_object(line, '$.inputSeqFileName') as input_seqfile_name,
get_json_object(line, '$.persist.patientkey') as pat_key,
get_json_object(line, '$.status') as status,    
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
from production_logs_persistjob_epoch where get_json_object(line, '$.level') != "INFO" and get_json_object(line, '$.className') = "PersistMapper"
and ($dateRange);
     
insert overwrite table temp_partition_persist_reducer partition(month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.patient.uuid') as pat_id,
get_json_object(line, '$.patient.key') as pat_key,
get_json_object(line, '$.status') as status,       
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
from production_logs_persistjob_epoch where get_json_object(line, '$.level') != "INFO" and get_json_object(line, '$.className') = "PersistReducer"   
and ($dateRange);
         
insert overwrite table temp_partition_coordinator_stats partition(month, day)
select
get_json_object(line, '$.datestamp') time,
get_json_object(line, '$.coordinator.stats.running') running,
get_json_object(line, '$.coordinator.stats.toLaunch') tolaunch,
cast(get_json_object(line, '$.coordinator.stats.parser.queuedCount') as int) as parserQueue,
cast(get_json_object(line, '$.coordinator.stats.ocr.queuedCount') as int) as ocrQueue,
cast(get_json_object(line, '$.coordinator.stats.trace.queuedCount') as int) as traceQueue,
cast(get_json_object(line, '$.coordinator.stats.persist.queuedCount') as int) as persistQueue,
month,
day
from production_logs_coordinator_epoch
where get_json_object(line, '$.coordinator.stats.parser.queuedCount') is not null 

EOF