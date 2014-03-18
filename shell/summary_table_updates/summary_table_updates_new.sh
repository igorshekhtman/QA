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



insert overwrite table summary_docreceiver_archive partition (month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.archive.afs.docid') as doc_id,
get_json_object(line, '$.archive.afs.batchid') as batch_id,
cast(get_json_object(line, '$.archive.afs.bytes') as int) as file_size,
get_json_object(line, '$.archive.afs.status') as status,
cast(get_json_object(line, '$.archive.afs.millis') as int) as archive_time,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.archive.afs.orgid') as org_id
from production_logs_docreceiver_epoch
where get_json_object(line, '$.archive') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.seqfile.file.document.docid') as doc_id,
get_json_object(line, '$.seqfile.file.document.batchid') as batch_id,
cast(get_json_object(line, '$.seqfile.file.document.bytes') as int) as file_size,
get_json_object(line, '$.seqfile.file.document.status') as status,
get_json_object(line, '$.seqfile.file.add.directory') as seqfile_directory,
regexp_replace(get_json_object(line, '$.seqfile.file.add.filename'), concat(get_json_object(line, '$.seqfile.file.add.directory'), '/'), '') as seqfile_file,
cast(get_json_object(line, '$.seqfile.file.add.millis') as int) as seqfile_time,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.seqfile.file.document.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.seqfile.file.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_upload partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.upload.document.docid') as doc_id,
get_json_object(line, '$.upload.document.batchid') as batch_id,
cast(get_json_object(line, '$.upload.document.file.bytes') as int) as file_size,
get_json_object(line, '$.upload.document.status') as status,
cast(get_json_object(line, '$.upload.document.millis') as int) as total_time,
get_json_object(line, '$.upload.document.hash.sha1') as doc_hash,
get_json_object(line, '$.upload.document.filetype') as file_type,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.upload.document.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.upload.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile_post partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.submit.post.path') as seqfile_path,
cast(get_json_object(line, '$.submit.post.bytes') as int) as seqfile_size,
cast(get_json_object(line, '$.submit.post.apxfiles.count') as int) as num_docs,
get_json_object(line, '$.submit.post.batchid') as batch_id,
get_json_object(line, '$.submit.post.status') as status,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.submit.post.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.submit.post') is not null
and ($dateRange);

insert overwrite table summary_coordinator_workrequest partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.work.sourcedir') as source_dir,
regexp_replace(get_json_object(line, '$.work.filesmoved'), concat(get_json_object(line, '$.work.sourcedir'),'/'), '') as seqfile,
get_json_object(line, '$.work.destdir') as dest_dir,
get_json_object(line, '$.work.context.batchID') as batch_id,
get_json_object(line, '$.work.workID') as work_id,
month,
day,
get_json_object(line, '$.work.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.work') is not null
and ($dateRange);

insert overwrite table summary_coordinator_movefiles partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.sourcedir') as source_dir,
get_json_object(line, '$.job.filesmoved') as files_moved,
get_json_object(line, '$.job.destdir') as dest_dir,
get_json_object(line, '$.job.reason') as move_message,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.filesmoved') is not null
and ($dateRange);

insert overwrite table summary_coordinator_jobrequest partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.sourcedir') as source_dir,
get_json_object(line, '$.job.files') as seqfile,
get_json_object(line, '$.job.destdir') as dest_dir,
get_json_object(line, '$.job.fromActivity') as from_activity,
get_json_object(line, '$.job.fromJob') as from_job_id,
get_json_object(line, '$.job.originalJobID') as orig_job_id,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.files') is not null and get_json_object(line, '$.job.status') is null
and ($dateRange);

insert overwrite table summary_coordinator_jobstart partition (month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.inputDir') as input_dir,
get_json_object(line, '$.job.outputDir') as output_dir,
get_json_object(line, '$.job.originalJobID') as orig_job_id,
get_json_object(line, '$.job.hadoopJobID') as hadoop_job_id,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')='start'
and ($dateRange);

insert overwrite table summary_coordinator_jobfinish partition (month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.inputDir') as input_dir,
get_json_object(line, '$.job.outputDir') as output_dir,
get_json_object(line, '$.job.originalJobID') as orig_job_id,
get_json_object(line, '$.job.hadoopJobID') as hadoop_job_id,
get_json_object(line, '$.job.status') as status,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
cast(get_json_object(line, '$.job.millis') as int) as total_time,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')!='start' and get_json_object(line, '$.job.status') is not null
and ($dateRange);

insert overwrite table summary_parser partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.batchId') as batch_id,
cast(get_json_object(line, '$.file.bytes') as int) as file_size,
get_json_object(line, '$.file.type') as file_type,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.file.millis') as int) as process_time,
get_json_object(line, '$.tag.persist.status') as sent_to_persist,
get_json_object(line, '$.tag.ocr.status') as sent_to_ocr,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM production_logs_parserjob_epoch
WHERE get_json_object(line, '$.level')='EVENT'
and ($dateRange);

insert overwrite table summary_ocr partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.batchId') as batch_id,
cast(get_json_object(line, '$.file.bytes') as int) as file_size,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.file.millis') as int) as process_time,
cast(get_json_object(line, '$.file.ocr.outputlength') as int) as output_size,
cast(get_json_object(line, '$.page.totalPages') as int) as total_pages,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM production_logs_ocrjob_epoch
WHERE get_json_object(line, '$.level')='EVENT'
and ($dateRange);

insert overwrite table summary_persist_mapper partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.batchId') as batch_id,
cast(get_json_object(line, '$.file.bytes') as int) as file_size,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.file.millis') as int) as process_time,
get_json_object(line, '$.persist.patientkey') as patient_key,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM production_logs_persistjob_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.className') = 'com.apixio.jobs.docimport.persist.mapper.PersistMapper'
and ($dateRange);

insert overwrite table summary_persist_reducer partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.patient.millis') as int) as process_time,
get_json_object(line, '$.patient.key') as patient_key,
get_json_object(line, '$.patient.uuid') as patient_uuid,
cast(get_json_object(line, '$.lock.held.millis') as int) as mysql_lock_held_time,
cast(get_json_object(line, '$.patient.search.millis') as int) as mysql_patient_search_time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM production_logs_persistjob_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.className') = 'PersistReducer'
and ($dateRange);

insert overwrite table summary_qafromseqfile partition(month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.runId') as run_id,
get_json_object(line, '$.input.batchid') as batch_id,
get_json_object(line, '$.input.doc_id') as doc_ext_id,
get_json_object(line, '$.input.uuid') as doc_id,
get_json_object(line, '$.input.filetype') as file_type,
get_json_object(line, '$.output.apo.patientKey') as patient_key,
get_json_object(line, '$.output.apo.uuid') as patient_uuid,
get_json_object(line, '$.output.uploadedToS3') as archived,
get_json_object(line, '$.output.trace.parserJob') as parser_status,
get_json_object(line, '$.output.trace.ocrJob') as ocr_status,
get_json_object(line, '$.output.trace.persistJob') as persist_status,
get_json_object(line, '$.output.trace.appendToSequenceFile') as append_to_seqfile,
get_json_object(line, '$.output.trace.submitToCoordinator') as submit_to_coordinator,
get_json_object(line, '$.output.documentEntry.username') as username_from_docentry,
get_json_object(line, '$.output.documentEntry.sourceSystem') as sourcesystem_from_docentry,
get_json_object(line, '$.output.documentEntry.documentHash') as doc_hash_from_docentry,
get_json_object(line, '$.output.documentEntry.documentId') as doc_ext_id_from_docentry,
month,
day,
get_json_object(line, '$.input.orgid') as org_id
from production_logs_qafromseqfile_epoch where get_json_object(line, '$.output') is not null
and ($dateRange);

insert overwrite table summary_qapatientuuid partition(month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.patient.uuids') as patient_uuids,
get_json_object(line, '$.patient.key') as patient_key,
get_json_object(line, '$.patient.info') as patient_info,
month,
day,
get_json_object(line, '$.orgId') as org_id
from production_logs_qafromseqfile_epoch where get_json_object(line, '$.level')='EVENT'
and ($dateRange);





insert overwrite table summary_docreceiver_archive_staging partition (month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.archive.afs.docid') as doc_id,
get_json_object(line, '$.archive.afs.batchid') as batch_id,
cast(get_json_object(line, '$.archive.afs.bytes') as int) as file_size,
get_json_object(line, '$.archive.afs.status') as status,
cast(get_json_object(line, '$.archive.afs.millis') as int) as archive_time,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.archive.afs.orgid') as org_id
from staging_logs_docreceiver_epoch
where get_json_object(line, '$.archive') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.seqfile.file.document.docid') as doc_id,
get_json_object(line, '$.seqfile.file.document.batchid') as batch_id,
cast(get_json_object(line, '$.seqfile.file.document.bytes') as int) as file_size,
get_json_object(line, '$.seqfile.file.document.status') as status,
get_json_object(line, '$.seqfile.file.add.directory') as seqfile_directory,
regexp_replace(get_json_object(line, '$.seqfile.file.add.filename'), concat(get_json_object(line, '$.seqfile.file.add.directory'), '/'), '') as seqfile_file,
cast(get_json_object(line, '$.seqfile.file.add.millis') as int) as seqfile_time,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.seqfile.file.document.orgid') as org_id
FROM staging_logs_docreceiver_epoch
WHERE get_json_object(line, '$.seqfile.file.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_upload_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.upload.document.docid') as doc_id,
get_json_object(line, '$.upload.document.batchid') as batch_id,
cast(get_json_object(line, '$.upload.document.file.bytes') as int) as file_size,
get_json_object(line, '$.upload.document.status') as status,
cast(get_json_object(line, '$.upload.document.millis') as int) as total_time,
get_json_object(line, '$.upload.document.hash.sha1') as doc_hash,
get_json_object(line, '$.upload.document.filetype') as file_type,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.upload.document.orgid') as org_id
FROM staging_logs_docreceiver_epoch
WHERE get_json_object(line, '$.upload.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile_post_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.submit.post.path') as seqfile_path,
cast(get_json_object(line, '$.submit.post.bytes') as int) as seqfile_size,
cast(get_json_object(line, '$.submit.post.apxfiles.count') as int) as num_docs,
get_json_object(line, '$.submit.post.batchid') as batch_id,
get_json_object(line, '$.submit.post.status') as status,
get_json_object(line, '$.message') as error_message,
month,
day,
get_json_object(line, '$.submit.post.orgid') as org_id
FROM staging_logs_docreceiver_epoch
WHERE get_json_object(line, '$.submit.post') is not null
and ($dateRange);

insert overwrite table summary_coordinator_workrequest_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.work.sourcedir') as source_dir,
regexp_replace(get_json_object(line, '$.work.filesmoved'), concat(get_json_object(line, '$.work.sourcedir'),'/'), '') as seqfile,
get_json_object(line, '$.work.destdir') as dest_dir,
get_json_object(line, '$.work.context.batchID') as batch_id,
get_json_object(line, '$.work.workID') as work_id,
month,
day,
get_json_object(line, '$.work.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.work') is not null
and ($dateRange);

insert overwrite table summary_coordinator_movefiles_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.sourcedir') as source_dir,
get_json_object(line, '$.job.filesmoved') as files_moved,
get_json_object(line, '$.job.destdir') as dest_dir,
get_json_object(line, '$.job.reason') as move_message,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.filesmoved') is not null
and ($dateRange);

insert overwrite table summary_coordinator_jobrequest_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.sourcedir') as source_dir,
get_json_object(line, '$.job.files') as seqfile,
get_json_object(line, '$.job.destdir') as dest_dir,
get_json_object(line, '$.job.fromActivity') as from_activity,
get_json_object(line, '$.job.fromJob') as from_job_id,
get_json_object(line, '$.job.originalJobID') as orig_job_id,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.files') is not null and get_json_object(line, '$.job.status') is null
and ($dateRange);

insert overwrite table summary_coordinator_jobstart_staging partition (month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.inputDir') as input_dir,
get_json_object(line, '$.job.outputDir') as output_dir,
get_json_object(line, '$.job.originalJobID') as orig_job_id,
get_json_object(line, '$.job.hadoopJobID') as hadoop_job_id,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')='start'
and ($dateRange);

insert overwrite table summary_coordinator_jobfinish_staging partition (month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.inputDir') as input_dir,
get_json_object(line, '$.job.outputDir') as output_dir,
get_json_object(line, '$.job.originalJobID') as orig_job_id,
get_json_object(line, '$.job.hadoopJobID') as hadoop_job_id,
get_json_object(line, '$.job.status') as status,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
cast(get_json_object(line, '$.job.millis') as int) as total_time,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')!='start' and get_json_object(line, '$.job.status') is not null
and ($dateRange);

insert overwrite table summary_parser_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.batchId') as batch_id,
cast(get_json_object(line, '$.file.bytes') as int) as file_size,
get_json_object(line, '$.file.type') as file_type,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.file.millis') as int) as process_time,
get_json_object(line, '$.tag.persist.status') as sent_to_persist,
get_json_object(line, '$.tag.ocr.status') as sent_to_ocr,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM staging_logs_parserjob_epoch
WHERE get_json_object(line, '$.level')='EVENT'
and ($dateRange);

insert overwrite table summary_ocr_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.batchId') as batch_id,
cast(get_json_object(line, '$.file.bytes') as int) as file_size,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.file.millis') as int) as process_time,
cast(get_json_object(line, '$.file.ocr.outputlength') as int) as output_size,
cast(get_json_object(line, '$.page.totalPages') as int) as total_pages,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM staging_logs_ocrjob_epoch
WHERE get_json_object(line, '$.level')='EVENT'
and ($dateRange);

insert overwrite table summary_persist_mapper_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.documentuuid') as doc_id,
get_json_object(line, '$.batchId') as batch_id,
cast(get_json_object(line, '$.file.bytes') as int) as file_size,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.file.millis') as int) as process_time,
get_json_object(line, '$.persist.patientkey') as patient_key,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM staging_logs_persistjob_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.className') = 'com.apixio.jobs.docimport.persist.mapper.PersistMapper'
and ($dateRange);

insert overwrite table summary_persist_reducer_staging partition (month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.patient.millis') as int) as process_time,
get_json_object(line, '$.patient.key') as patient_key,
get_json_object(line, '$.patient.uuid') as patient_uuid,
cast(get_json_object(line, '$.lock.held.millis') as int) as mysql_lock_held_time,
cast(get_json_object(line, '$.patient.search.millis') as int) as mysql_patient_search_time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.error.message') as error_message,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM staging_logs_persistjob_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.className') = 'PersistReducer'
and ($dateRange);

insert overwrite table summary_qafromseqfile_staging partition(month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.runId') as run_id,
get_json_object(line, '$.input.batchid') as batch_id,
get_json_object(line, '$.input.doc_id') as doc_ext_id,
get_json_object(line, '$.input.uuid') as doc_id,
get_json_object(line, '$.input.filetype') as file_type,
get_json_object(line, '$.output.apo.patientKey') as patient_key,
get_json_object(line, '$.output.apo.uuid') as patient_uuid,
get_json_object(line, '$.output.uploadedToS3') as archived,
get_json_object(line, '$.output.trace.parserJob') as parser_status,
get_json_object(line, '$.output.trace.ocrJob') as ocr_status,
get_json_object(line, '$.output.trace.persistJob') as persist_status,
get_json_object(line, '$.output.trace.appendToSequenceFile') as append_to_seqfile,
get_json_object(line, '$.output.trace.submitToCoordinator') as submit_to_coordinator,
get_json_object(line, '$.output.documentEntry.username') as username_from_docentry,
get_json_object(line, '$.output.documentEntry.sourceSystem') as sourcesystem_from_docentry,
get_json_object(line, '$.output.documentEntry.documentHash') as doc_hash_from_docentry,
get_json_object(line, '$.output.documentEntry.documentId') as doc_ext_id_from_docentry,
month,
day,
get_json_object(line, '$.input.orgid') as org_id
from staging_logs_qafromseqfile_epoch where get_json_object(line, '$.output') is not null
and ($dateRange);

insert overwrite table summary_qapatientuuid_staging partition(month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.patient.uuids') as patient_uuids,
get_json_object(line, '$.patient.key') as patient_key,
get_json_object(line, '$.patient.info') as patient_info,
month,
day,
get_json_object(line, '$.orgId') as org_id
from staging_logs_qafromseqfile_epoch where get_json_object(line, '$.level')='EVENT'
and ($dateRange);

EOF