#! /bin/sh

#====================== checking for user provided args =======================================

export TZ=America/Los_Angeles

dateRange="";

if [ -z $1 ]; then
echo ">>> dateRange not provided, using current date"

curDay=$(date +%d);
curMonth=$(date +%m);
curYear=$(date +%Y);


echo "Current day: $curDay"
echo "Current month: $curMonth"
echo "Current year: $curYear"
echo " "


#=============== adjust date range of the report ==============================================

dateRange="${dateRange:-(month='$curMonth' and day='$curDay' and year='$curYear')}";

else
echo ">>> dateRange provided by user
"

dateRange="${dateRange:-($1)}";

fi


#===========================================================
#===========================================================


echo "Updating partitioned summary tables with date range: $dateRange"
echo " "

/usr/bin/hive --service beeline -u jdbc:hive2://10.0.0.10:10000 -n hive -d org.apache.hive.jdbc.HiveDriver  >> update_summary.log   << EOF
#The 2 new hive server addresses are: 10.0.0.10 and 10.0.2.12


set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
set mapred.reduce.tasks=16;
set mapred.job.queue.name=hive;
set hive.exec.max.dynamic.partitions.pernode = 10000;
-- compress all data 
set mapred.output.compress=true;
set hive.exec.compress.output=true;
set mapred.output.compression.codec=org.apache.hadoop.io.compress.GzipCodec;
set io.compression.codecs=org.apache.hadoop.io.compress.GzipCodec;
SET mapred.output.compression.type=BLOCK;

-- note: all partition values must be in order as well as by name

! echo Loading Production partitions

insert overwrite table summary_docreceiver_archive partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
coalesce(get_json_object(line, '$.archive.afs.docid'),get_json_object(line, '$.archive.aps.docid'))  as doc_id,
coalesce(get_json_object(line, '$.archive.afs.batchid'),get_json_object(line, '$.archive.aps.batchid')) as batch_id,
coalesce(cast(get_json_object(line, '$.archive.afs.bytes') as int),cast(get_json_object(line, '$.archive.aps.bytes') as int)) as file_size,
coalesce(get_json_object(line, '$.archive.afs.status'),get_json_object(line, '$.archive.aps.status')) as status,
coalesce(cast(get_json_object(line, '$.archive.afs.millis') as int),cast(get_json_object(line, '$.archive.aps.millis') as int)) as archive_time,
if( coalesce(get_json_object(line, '$.archive.afs.status'),get_json_object(line, '$.archive.aps.status')) != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null ) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
coalesce(get_json_object(line, '$.archive.afs.orgid'),get_json_object(line, '$.archive.aps.orgid')) as org_id
from production_logs_docreceiver_epoch
where get_json_object(line, '$.archive') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.seqfile.file.document.docid') as doc_id,
get_json_object(line, '$.seqfile.file.document.batchid') as batch_id,
cast(get_json_object(line, '$.seqfile.file.document.bytes') as int) as file_size,
get_json_object(line, '$.seqfile.file.add.status') as status,
regexp_extract(get_json_object(line, '$.seqfile.file.add.directory'), '^.*?(\/user.*?)$',1) as seqfile_directory,
regexp_replace(get_json_object(line, '$.seqfile.file.add.filename'), concat(get_json_object(line, '$.seqfile.file.add.directory'), '/'), '') as seqfile_file,
cast(get_json_object(line, '$.seqfile.file.add.millis') as int) as seqfile_time,
if( get_json_object(line, '$.seqfile.file.add.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null ) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.seqfile.file.document.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.seqfile.file.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_upload partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.upload.document.docid') as doc_id,
get_json_object(line, '$.upload.document.batchid') as batch_id,
cast(get_json_object(line, '$.upload.document.file.bytes') as int) as file_size,
get_json_object(line, '$.upload.document.status') as status,
cast(get_json_object(line, '$.upload.document.millis') as int) as total_time,
get_json_object(line, '$.upload.document.hash.sha1') as doc_hash,
get_json_object(line, '$.upload.document.filetype') as file_type,
if( get_json_object(line, '$.upload.document.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.upload.document.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.upload.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile_post partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
regexp_extract(get_json_object(line, '$.submit.post.path'), '^.*?(\/user.*?)$',1) as seqfile_path,
cast(get_json_object(line, '$.submit.post.numfiles') as int) as num_seq_files,
cast(get_json_object(line, '$.submit.post.bytes') as int) as seqfile_size,
cast(get_json_object(line, '$.submit.post.apxfiles.count') as int) as num_docs,
get_json_object(line, '$.submit.post.batchid') as batch_id,
get_json_object(line, '$.submit.post.queue.name') as redis_queue_name,
get_json_object(line, '$.submit.post.status') as status,
if( get_json_object(line, '$.submit.post.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.submit.post.orgid') as org_id
FROM production_logs_docreceiver_epoch
WHERE get_json_object(line, '$.submit.post') is not null
and ($dateRange);

insert overwrite table summary_coordinator_workrequest partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.work.context.batchID') as batch_id,
regexp_extract(get_json_object(line, '$.work.sourcedir'), '^.*?(\/user.*?)$',1) as source_dir,
regexp_replace(regexp_extract(get_json_object(line, '$.work.filesmoved'), '^.*?(\/user.*?)$',1), concat(regexp_extract(get_json_object(line, '$.work.sourcedir'), '^.*?(\/user.*?)$',1),'/'), '') as seqfile,
get_json_object(line, '$.work.destdir') as dest_dir,
get_json_object(line, '$.work.workID') as work_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.work.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.work') is not null
and ($dateRange);

insert overwrite table summary_coordinator_movefiles partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.filesmoved') is not null
and ($dateRange);

insert overwrite table summary_coordinator_jobrequest partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.sourcedir') as source_dir,
get_json_object(line, '$.job.files') as seqfile,
get_json_object(line, '$.job.destdir') as dest_dir,
get_json_object(line, '$.job.fromActivity') as from_activity,
get_json_object(line, '$.job.fromJob') as from_job_id,
if(get_json_object(line, '$.job.originalJobID') is null, get_json_object(line, '$.job.jobID'), get_json_object(line, '$.job.originalJobID')) as orig_job_id,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.files') is not null and get_json_object(line, '$.job.status') is null
and ($dateRange);

insert overwrite table summary_coordinator_jobstart partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.inputDir') as input_dir,
get_json_object(line, '$.job.outputDir') as output_dir,
if(get_json_object(line, '$.job.originalJobID') is null, get_json_object(line, '$.job.jobID'), get_json_object(line, '$.job.originalJobID')) as orig_job_id,
get_json_object(line, '$.job.hadoopJobID') as hadoop_job_id,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')='start'
and ($dateRange);

insert overwrite table summary_coordinator_jobfinish partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.job.context.batchID') as batch_id,
get_json_object(line, '$.job.activity') as activity,
get_json_object(line, '$.job.inputDir') as input_dir,
get_json_object(line, '$.job.outputDir') as output_dir,
if(get_json_object(line, '$.job.originalJobID') is null, get_json_object(line, '$.job.jobID'), get_json_object(line, '$.job.originalJobID')) as orig_job_id,
get_json_object(line, '$.job.hadoopJobID') as hadoop_job_id,
get_json_object(line, '$.job.status') as status,
get_json_object(line, '$.job.jobID') as job_id,
get_json_object(line, '$.job.workID') as work_id,
cast(get_json_object(line, '$.job.millis') as int) as total_time,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM production_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')!='start' and get_json_object(line, '$.job.status') is not null
and ($dateRange);

insert overwrite table summary_coordinator_stats partition(year, month, day)
select 
get_json_object(line, '$.datestamp') as time, 
get_json_object(line, '$.coordinator.stats') as stats_json, 
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, 
day
from production_logs_coordinator_epoch where get_json_object(line, '$.coordinator.stats.parser.queuedCount') is not null
and ($dateRange);

insert overwrite table summary_afsdownload partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.input.docuuid') as doc_id,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.download.millis') as int) as download_time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.input.orgId') as org_id
FROM production_logs_afsDownload_epoch
WHERE get_json_object(line, '$.level') != "INFO"
and ($dateRange);

insert overwrite table summary_parser partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.orgId') is null, 
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
FROM production_logs_parserjob_epoch
WHERE get_json_object(line, '$.level') != "INFO"
and (get_json_object(line, '$.documentuuid') is not null or get_json_object(line, '$.status') is not null)
and ($dateRange);

insert overwrite table summary_ocr partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.orgId') is null, 
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
FROM production_logs_ocrjob_epoch
WHERE get_json_object(line, '$.level') != "INFO"
and (get_json_object(line, '$.jobname') is not null or get_json_object(line, '$.orgId') is not null)
and ($dateRange);

insert overwrite table summary_persist_mapper partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.orgId') is null, 
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
FROM production_logs_persistjob_epoch
WHERE get_json_object(line, '$.level') != "INFO" and get_json_object(line, '$.className') like "%PersistMapper"
and ($dateRange);

insert overwrite table summary_persist_reducer partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.patient.millis') as int) as process_time,
get_json_object(line, '$.patient.key') as patient_key,
if(get_json_object(line, '$.patient.uuids') is null, get_json_object(line, '$.patient.uuid'), get_json_object(line, '$.patient.uuids')) as patient_uuid,
cast(get_json_object(line, '$.createuuid.cassandra.count') as int) as uuid_count,
cast(get_json_object(line, '$.lock.held.millis') as int) as mysql_lock_held_time,
cast(get_json_object(line, '$.patient.search.millis') as int) as mysql_patient_search_time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.autocorrection') as autocorrection,
get_json_object(line, '$.error.message') as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.orgId') is null, 
regexp_extract(get_json_object(line, '$.columnFamily'), '^cf(.*)$', 1),
get_json_object(line, '$.orgId')) as org_id
FROM production_logs_persistjob_epoch
WHERE get_json_object(line, '$.level') != "INFO" and get_json_object(line, '$.className') like "%PersistReducer"
and ($dateRange);

insert overwrite table summary_qafromseqfile partition(year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.input.orgid') as org_id
from production_logs_dataCheckAndRecover_epoch where get_json_object(line, '$.output') is not null
and ($dateRange);

insert overwrite table summary_qapatientuuid partition(year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.patient.uuids') as patient_uuids,
get_json_object(line, '$.patient.key') as patient_key,
get_json_object(line, '$.patient.info') as patient_info,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if( get_json_object(line, '$.orgId') is null,
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
from production_logs_qapatientuuid_epoch where get_json_object(line, '$.level')='EVENT'
and get_json_object(line, '$.writeTo') is null
and ($dateRange);

insert overwrite table summary_event_mapper partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientUUID') as patient_uuid,
get_json_object(line, '$.documentUUID') as doc_id,
get_json_object(line, '$.jobSubmitTime') as job_submit_time,
get_json_object(line, '$.propertyVersion') as property_version,
cast(get_json_object(line, '$.event.count') as int) as num_of_events_extracted,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
cast(if(get_json_object(line, '$.event.millis') is not null, get_json_object(line, '$.event.millis'), 
get_json_object(line, '$.file.millis')) as int) as extraction_time,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day,
get_json_object(line, '$.orgId') as org_id
from production_logs_eventJob_epoch
where get_json_object(line, '$.level')="EVENT" 
and get_json_object(line, '$.className') like "%EventMapper" 
and get_json_object(line, '$.eventAddress') is null
and ($dateRange);

insert overwrite table summary_event_reducer partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientUUID') as patient_uuid,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
cast(get_json_object(line, '$.patientevent.millis') as int) as process_time,
get_json_object(line, '$.eventBatchId') as event_batch_id,
cast(get_json_object(line, '$.eventBatch.count') as int) as event_batch_count,
get_json_object(line, '$.eventBatch.pubMessage') as published_message,
cast(get_json_object(line, '$.patientevent.count') as int) as num_of_events_persisted,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from production_logs_eventJob_epoch 
where get_json_object(line, '$.level')="EVENT" 
and get_json_object(line, '$.className') like "%EventReducer"
and get_json_object(line, '$.eventAddress') is null
and ($dateRange);

insert overwrite table summary_event_address partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientUUID') as patient_uuid,
get_json_object(line, '$.documentUUID') as doc_id,
get_json_object(line, '$.jobSubmitTime') as job_submit_time,
get_json_object(line, '$.propertyVersion') as property_version,
get_json_object(line, '$.eventAddress') as event_address,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as 	seqfilename,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from production_logs_eventJob_epoch
where get_json_object(line, '$.level')="EVENT" 
and get_json_object(line, '$.className') like "%EventMapper" 
and get_json_object(line, '$.eventAddress') is not null
and ($dateRange);

insert overwrite table summary_qa_event partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patient.info') as patient_info,
regexp_extract(get_json_object(line, '$.patient.info'), '^(.*)::.*::.*$', 1) as patient_uuid,
get_json_object(line, '$.qa.eventBatch.eventBatchId') as event_batch_id,
get_json_object(line, '$.qa.eventBatch.status')	as fetch_event_batch_status,
cast(get_json_object(line, '$.qa.eventBatch.millis') as int) as fetch_event_batch_millis,
cast(get_json_object(line, '$.qa.eventBatch.count') as int) as event_batch_count,
get_json_object(line, '$.decrypt.status') as decrypt_status,
cast(get_json_object(line, '$.decrypt.millis') as int) as decrypt_millis,
get_json_object(line, '$.qa.eventTypes.status') as qa_event_types_status,
cast(get_json_object(line, '$.qa.eventTypes.millis') as int) as qa_event_types_millis,
cast(get_json_object(line, '$.qa.eventTypes.count') as int) as event_type_count,
cast(get_json_object(line, '$.qa.failed.count') as int) as qa_failed_count,
cast(get_json_object(line, '$.qa.millis') as int) as qa_millis,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from production_logs_qaeventjob_epoch
where get_json_object(line, '$.level')="EVENT"
and ($dateRange);

insert overwrite table summary_loadapo partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
if( get_json_object(line, '$.input.key') is not null,
get_json_object(line, '$.input.key'),
get_json_object(line, '$.patient.key')) as input_key,
get_json_object(line, '$.patient.uuids') as patient_uuids,
if( get_json_object(line, '$.multipleUUIDs.count') is not null, 
cast(get_json_object(line, '$.multipleUUIDs.count') as int), 
1) as uuid_count,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.readColBufferSize') as read_buffer_size,
cast(get_json_object(line, '$.loadApo.millis') as int) as millis,
get_json_object(line, '$.className') as class_name,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from production_logs_loadapo_epoch
where get_json_object(line, '$.level') = "EVENT"
and ($dateRange);

insert overwrite table summary_doc_manifest partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.document.uuid') as apixio_uuid,
get_json_object(line, '$.document.id') as external_id,
get_json_object(line, '$.document.source') as doc_source,
get_json_object(line, '$.document.assignAuthority') as assign_authority,
get_json_object(line, '$.sourceSystem') as source_system,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.orgId') as org_id
from production_logs_datacheckandrecover_epoch
where get_json_object(line, '$.docManifest') is not null
and ($dateRange);


insert overwrite table summary_careopt_load partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patient.id') as patient_sql_id,
get_json_object(line, '$.patient.uuid') as patient_uuid,
cast(get_json_object(line, '$.patient.cassandraload.millis') as int) as cassandra_load_millis,
cast(get_json_object(line, '$.patient.size.bytes') as int) as patient_bytes,
get_json_object(line, '$.hostname') as hostname,
cast(get_json_object(line, '$.patientcache.size') as int) as patient_cache_size,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.patient.orgId') as org_id
from 
production_logs_careopt_epoch 
where get_json_object(line, '$.patient.cassandraload.millis') is not null 
and ($dateRange);

insert overwrite table summary_careopt_search partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientaccess.patient.id') as patient_sql_id,
get_json_object(line, '$.patientaccess.user.id') as user_id,
get_json_object(line, '$.patientaccess.user.username') as username,
get_json_object(line, '$.patientaccess.errorMessage') as error_message,
cast(get_json_object(line, '$.patientaccess.millis') as int) as patient_access_millis,
get_json_object(line, '$.hostname') as hostname,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.patientaccess.org.id') as org_id
from 
production_logs_careopt_epoch 
where get_json_object(line, '$.patientaccess.patient.id') is not null 
and ($dateRange);

insert overwrite table summary_careopt_errors partition (year, month, day)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.message') as error_message,
get_json_object(line, '$.loggerName') as source,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day
from 
production_logs_careopt_epoch 
where get_json_object(line, '$.level') = 'ERROR' 
and ($dateRange);

insert overwrite table summary_careopt_login partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
if(get_json_object(line, '$.logout.username') is not null,
get_json_object(line, '$.logout.username'),
get_json_object(line, '$.login.username')) as username,

if(get_json_object(line, '$.logout.userId') is not null, 
get_json_object(line, '$.logout.userId'),
get_json_object(line, '$.login.userId')) as user_id,

if(get_json_object(line, '$.logout.status') is not null,
get_json_object(line, '$.logout.status'),
get_json_object(line, '$.login.status')) as status,

if(get_json_object(line, '$.logout.userAgent') is not null,
get_json_object(line, '$.logout.userAgent'),
get_json_object(line, '$.login.userAgent')) as user_agent,

get_json_object(line, '$.hostname') as hostname,

if(get_json_object(line, '$.logout.millis') is not null,
cast(get_json_object(line, '$.logout.millis') as int),
cast(get_json_object(line, '$.login.millis') as int)) as processTime,

if(get_json_object(line, '$.logout') is not null,'logout','login') as event,

if(get_json_object(line, '$.logout.remoteAddr') is not null,
get_json_object(line, '$.logout.remoteAddr'),
get_json_object(line, '$.login.remoteAddr')) as remote_address,

substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.logout.orgId') is not null,
get_json_object(line, '$.logout.orgId'),
get_json_object(line, '$.login.orgId')) as org_id
from 
production_logs_careopt_epoch 
where (get_json_object(line, '$.logout') is not null or get_json_object(line, '$.login') is not null)  
and ($dateRange);


insert overwrite table summary_bundler_document partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hcc.bundler.receive.document') as doc_id,
get_json_object(line, '$.hcc.bundler.receive.patient') as patient_uuid,
get_json_object(line, '$.hcc.bundler.receive.event_address') as event_address,
get_json_object(line, '$.hcc.bundler.receive.event_batch_id') as event_batch_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day,
get_json_object(line, '$.hcc.bundler.receive.org_id') as org_id
from production_logs_bundler_epoch where get_json_object(line, '$.hcc.bundler.receive') is not null
and ($dateRange);

insert overwrite table summary_bundler_historical partition (year, month, day)
select
get_json_object(line, '$.datestamp') as time,
cast(get_json_object(line, '$.hcc.bundler.historicalEvents.lo') as bigint) as low,
cast(get_json_object(line, '$.hcc.bundler.historicalEvents.hi') as bigint) as high,
cast(get_json_object(line, '$.hcc.bundler.historicalEvents.count') as int) as count,
get_json_object(line, '$.hcc.bundler.historicalEvents.status') as status,
get_json_object(line, '$.hcc.bundler.historicalEvents.bytes') as bytes,
get_json_object(line, '$.hcc.bundler.historicalEvents.millis') as millis,
get_json_object(line, '$.jvm.memory.total.bytes') as memory_total_bytes,
get_json_object(line, '$.jvm.memory.free.bytes') as memory_free_bytes,
get_json_object(line, '$.hostname') as hostname,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day
from production_logs_bundler_epoch where
get_json_object(line, '$.level') = 'EVENT' and
get_json_object(line, '$.hcc.bundler.historicalEvents') is not null
and ($dateRange);

insert overwrite table summary_bundler_sequence partition (year, month, day)
select
get_json_object(line, '$.datestamp') as time,
cast(get_json_object(line, '$.hcc.bundler.get_sequence.count') as int) as count,
get_json_object(line, '$.hcc.bundler.get_sequence.pattern') as pattern,
get_json_object(line, '$.hcc.bundler.get_sequence.status') as status,
get_json_object(line, '$.hcc.bundler.get_sequence.millis') as millis,
get_json_object(line, '$.jvm.memory.total.bytes') as memory_total_bytes,
get_json_object(line, '$.jvm.memory.free.bytes') as memory_free_bytes,
get_json_object(line, '$.jvm.memory.max.bytes') as memory_max_bytes,
get_json_object(line, '$.hostname') as hostname,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day
from production_logs_bundler_epoch where
get_json_object(line, '$.level') = 'EVENT' and
get_json_object(line, '$.hcc.bundler.get_sequence') is not null
and ($dateRange);


insert overwrite table summary_dataorchestrator_request partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.data_orchestrator.request.id') as request_id,
get_json_object(line, '$.app.data_orchestrator.request.bulk') as is_bulk,
get_json_object(line, '$.app.data_orchestrator.request.parameters') as parameters,
get_json_object(line, '$.app.data_orchestrator.request.parameters.patientUUID') as patient_uuid,
get_json_object(line, '$.app.data_orchestrator.request.parameters.documentUUID') as doc_uuid,
if( get_json_object(line, '$.app.data_orchestrator.request.bulk') = 'true', 0,
cast(get_json_object(line, '$.app.data_orchestrator.request.parameters.count') as int)) as bulk_count,
get_json_object(line, '$.app.data_orchestrator.request.status') as status, 
get_json_object(line, '$.app.data_orchestrator.request.error') as error , 
get_json_object(line, '$.app.data_orchestrator.request.code') as response_code,
get_json_object(line, '$.app.data_orchestrator.request.millis') as response_time,
get_json_object(line, '$.app.data_orchestrator.request.bytes') as content_length,
get_json_object(line, '$.app.data_orchestrator.request.method') as method,
get_json_object(line, '$.app.data_orchestrator.request.endpoint') as endpoint,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.app.data_orchestrator.request.orgId') as org_id
FROM production_logs_dataorchestrator_epoch
WHERE get_json_object(line, '$.app.data_orchestrator.request') is not null
and ($dateRange);

insert overwrite table summary_dataorchestrator_lookup partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.data_orchestrator.lookup.request_id') as request_id,
get_json_object(line, '$.app.data_orchestrator.lookup.parameters') as parameters,
get_json_object(line, '$.app.data_orchestrator.lookup.parameters.patientUUID') as patient_uuid,
get_json_object(line, '$.app.data_orchestrator.lookup.parameters.documentUUID') as doc_uuid,
get_json_object(line, '$.app.data_orchestrator.lookup.status') as status, 
get_json_object(line, '$.app.data_orchestrator.lookup.error') as error , 
get_json_object(line, '$.app.data_orchestrator.lookup.endpoint') as endpoint,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.app.data_orchestrator.lookup.orgId') as org_id
FROM production_logs_dataorchestrator_epoch
WHERE get_json_object(line, '$.app.data_orchestrator.lookup') is not null
and ($dateRange);

insert overwrite table summary_dataorchestrator_acl partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.data_orchestrator.acl.request_id') as request_id,
get_json_object(line, '$.app.data_orchestrator.acl.permission') as permission,
get_json_object(line, '$.app.data_orchestrator.acl.userId')  as user_id,
get_json_object(line, '$.app.data_orchestrator.acl.authStatus') as auth_status, 
get_json_object(line, '$.app.data_orchestrator.acl.status') as status, 
get_json_object(line, '$.app.data_orchestrator.acl.error') as error , 
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.app.data_orchestrator.acl.orgId') as org_id
FROM production_logs_dataorchestrator_epoch
WHERE get_json_object(line, '$.app.data_orchestrator.acl') is not null
and ($dateRange);


insert overwrite table summary_useraccount_request partition (year, month, day)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.user_account.request.userId') as user_xuuid,
get_json_object(line, '$.app.user_account.request.parameters') as parameters,
get_json_object(line, '$.app.user_account.request.parameters.orgId') as org_id,
get_json_object(line, '$.app.user_account.request.parameters.userId') as user_id,
get_json_object(line, '$.app.user_account.request.parameters.detail') as detail,
get_json_object(line, '$.app.user_account.request.parameters.email') as email,
get_json_object(line, '$.app.user_account.request.parameters.name') as name,
get_json_object(line, '$.app.user_account.request.parameters.id') as id,
get_json_object(line, '$.app.user_account.request.status') as status, 
get_json_object(line, '$.app.user_account.request.error') as error, 
get_json_object(line, '$.app.user_account.request.failureReason') as failure_reason,
get_json_object(line, '$.app.user_account.request.code') as response_code,
get_json_object(line, '$.app.user_account.request.method') as method,
get_json_object(line, '$.app.user_account.request.endpoint') as endpoint,
get_json_object(line, '$.app.user_account.request.millis') as response_time,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day
FROM production_logs_useraccount_epoch
WHERE get_json_object(line, '$.app.user_account.request') is not null
and ($dateRange);

insert overwrite table summary_tokenizer_request partition (year, month, day)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.user_account.request.userId') as user_xuuid,
get_json_object(line, '$.app.user_account.request.parameters') as parameters,
get_json_object(line, '$.app.user_account.request.status') as status, 
get_json_object(line, '$.app.user_account.request.error') as error, 
get_json_object(line, '$.app.user_account.request.failureReason') as failure_reason,
get_json_object(line, '$.app.user_account.request.code') as response_code,
get_json_object(line, '$.app.user_account.request.method') as method,
get_json_object(line, '$.app.user_account.request.endpoint') as endpoint,
get_json_object(line, '$.app.user_account.request.millis') as response_time,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day
FROM production_logs_tokenizer_epoch
WHERE get_json_object(line, '$.app.user_account.request') is not null
and ($dateRange);


insert overwrite table summary_loader_upload partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.batch_name') as batch_name,
get_json_object(line, '$.user') as user,
cast(get_json_object(line, '$.success') as boolean) as success,
get_json_object(line, '$.primary_id') as primary_id,
get_json_object(line, '$.upload_id') as upload_id,
get_json_object(line, '$.uuid') as uuid,
cast(get_json_object(line, '$.size') as bigint) as size,
get_json_object(line, '$.payload') as payload,
cast(get_json_object(line, '$.attempts') as int) as attempts,
get_json_object(line, '$.original_id') as original_id,
get_json_object(line, '$.reference') as reference,
get_json_object(line, '$.message') as message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.org_id') as org_id 
FROM production_logs_loader_epoch
WHERE get_json_object(line, '$.level') = 'EVENT' and 
get_json_object(line, '$.org_id') is not NULL and
($dateRange);


###################################Staging#########################################################
! echo Loading Staging partitions

insert overwrite table summary_docreceiver_archive_staging partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.archive.afs.docid') as doc_id,
get_json_object(line, '$.archive.afs.batchid') as batch_id,
cast(get_json_object(line, '$.archive.afs.bytes') as int) as file_size,
get_json_object(line, '$.archive.afs.status') as status,
cast(get_json_object(line, '$.archive.afs.millis') as int) as archive_time,
if( get_json_object(line, '$.archive.afs.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null ) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.archive.afs.orgid') as org_id
from staging_logs_docreceiver_epoch
where get_json_object(line, '$.archive') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.seqfile.file.document.docid') as doc_id,
get_json_object(line, '$.seqfile.file.document.batchid') as batch_id,
cast(get_json_object(line, '$.seqfile.file.document.bytes') as int) as file_size,
get_json_object(line, '$.seqfile.file.add.status') as status,
regexp_extract(get_json_object(line, '$.seqfile.file.add.directory'), '^.*?(\/user.*?)$',1) as seqfile_directory,
regexp_replace(get_json_object(line, '$.seqfile.file.add.filename'), concat(get_json_object(line, '$.seqfile.file.add.directory'), '/'), '') as seqfile_file,
cast(get_json_object(line, '$.seqfile.file.add.millis') as int) as seqfile_time,
if( get_json_object(line, '$.seqfile.file.add.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null ) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.seqfile.file.document.orgid') as org_id
FROM staging_logs_docreceiver_epoch
WHERE get_json_object(line, '$.seqfile.file.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_upload_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.upload.document.docid') as doc_id,
get_json_object(line, '$.upload.document.batchid') as batch_id,
cast(get_json_object(line, '$.upload.document.file.bytes') as int) as file_size,
get_json_object(line, '$.upload.document.status') as status,
cast(get_json_object(line, '$.upload.document.millis') as int) as total_time,
get_json_object(line, '$.upload.document.hash.sha1') as doc_hash,
get_json_object(line, '$.upload.document.filetype') as file_type,
if( get_json_object(line, '$.upload.document.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.upload.document.orgid') as org_id
FROM staging_logs_docreceiver_epoch
WHERE get_json_object(line, '$.upload.document') is not null
and ($dateRange);

insert overwrite table summary_docreceiver_seqfile_post_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
regexp_extract(get_json_object(line, '$.submit.post.path'), '^.*?(\/user.*?)$',1) as seqfile_path,
cast(get_json_object(line, '$.submit.post.numfiles') as int) as num_seq_files,
cast(get_json_object(line, '$.submit.post.bytes') as int) as seqfile_size,
cast(get_json_object(line, '$.submit.post.apxfiles.count') as int) as num_docs,
get_json_object(line, '$.submit.post.batchid') as batch_id,
get_json_object(line, '$.submit.post.queue.name') as redis_queue_name,
get_json_object(line, '$.submit.post.status') as status,
if( get_json_object(line, '$.submit.post.status') != "success",
if( get_json_object(line, '$.error.message') is not null,
get_json_object(line, '$.error.message'),
regexp_extract(get_json_object(line, '$.message'), '^([^(\/0-9:]*).*$', 1) ),
null) as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.submit.post.orgid') as org_id
FROM staging_logs_docreceiver_epoch
WHERE get_json_object(line, '$.submit.post') is not null
and ($dateRange);

insert overwrite table summary_coordinator_workrequest_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.work.context.batchID') as batch_id,
regexp_extract(get_json_object(line, '$.work.sourcedir'), '^.*?(\/user.*?)$',1) as source_dir,
regexp_replace(regexp_extract(get_json_object(line, '$.work.filesmoved'), '^.*?(\/user.*?)$',1), concat(regexp_extract(get_json_object(line, '$.work.sourcedir'), '^.*?(\/user.*?)$',1),'/'), '') as seqfile,
get_json_object(line, '$.work.destdir') as dest_dir,
get_json_object(line, '$.work.workID') as work_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.work.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.work') is not null
and ($dateRange);

insert overwrite table summary_coordinator_movefiles_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.filesmoved') is not null
and ($dateRange);

insert overwrite table summary_coordinator_jobrequest_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.files') is not null and get_json_object(line, '$.job.status') is null
and ($dateRange);

insert overwrite table summary_coordinator_jobstart_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')='start'
and ($dateRange);

insert overwrite table summary_coordinator_jobfinish_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.job.context.organization') as org_id
FROM staging_logs_coordinator_epoch
WHERE get_json_object(line, '$.level')='EVENT' and get_json_object(line, '$.job.status')!='start' and get_json_object(line, '$.job.status') is not null
and ($dateRange);

insert overwrite table summary_coordinator_stats_staging partition(year, month, day)
select 
get_json_object(line, '$.datestamp') as time, 
get_json_object(line, '$.coordinator.stats') as stats_json, 
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, 
day
from staging_logs_coordinator_epoch where get_json_object(line, '$.coordinator.stats.parser.queuedCount') is not null
and ($dateRange);

insert overwrite table summary_afsdownload_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.input.docuuid') as doc_id,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.download.millis') as int) as download_time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.error.message') as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.input.orgId') as org_id
FROM staging_logs_afsDownload_epoch
WHERE get_json_object(line, '$.level') != "INFO"
and ($dateRange);

insert overwrite table summary_parser_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.orgId') is null, 
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
FROM staging_logs_parserjob_epoch
WHERE get_json_object(line, '$.level') != "INFO"
and (get_json_object(line, '$.documentuuid') is not null or get_json_object(line, '$.status') is not null)
and ($dateRange);

insert overwrite table summary_ocr_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM staging_logs_ocrjob_epoch
WHERE get_json_object(line, '$.level') != "INFO"
and get_json_object(line, '$.orgId') is not null
and ($dateRange);

insert overwrite table summary_persist_mapper_staging partition (year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.orgId') as org_id
FROM staging_logs_persistjob_epoch
WHERE get_json_object(line, '$.level') != "INFO" and get_json_object(line, '$.className') like "%PersistMapper"
and ($dateRange);

insert overwrite table summary_persist_reducer_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.status') as status,
cast(get_json_object(line, '$.patient.millis') as int) as process_time,
get_json_object(line, '$.patient.key') as patient_key,
if(get_json_object(line, '$.patient.uuids') is null, get_json_object(line, '$.patient.uuid'), get_json_object(line, '$.patient.uuids')) as patient_uuid,
cast(get_json_object(line, '$.createuuid.cassandra.count') as int) as uuid_count,
cast(get_json_object(line, '$.lock.held.millis') as int) as mysql_lock_held_time,
cast(get_json_object(line, '$.patient.search.millis') as int) as mysql_patient_search_time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.autocorrection') as autocorrection,
get_json_object(line, '$.error.message') as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.orgId') is null, 
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
FROM staging_logs_persistjob_epoch
WHERE get_json_object(line, '$.level') != "INFO" and get_json_object(line, '$.className') like "%PersistReducer"
and ($dateRange);

insert overwrite table summary_qafromseqfile_staging partition(year, month, day, org_id)
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
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.input.orgid') as org_id
from staging_logs_dataCheckAndRecover_epoch where get_json_object(line, '$.output') is not null
and ($dateRange);

insert overwrite table summary_event_mapper_staging partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientUUID') as patient_uuid,
get_json_object(line, '$.documentUUID') as doc_id,
get_json_object(line, '$.jobSubmitTime') as job_submit_time,
get_json_object(line, '$.propertyVersion') as property_version,
cast(get_json_object(line, '$.event.count') as int) as num_of_events_extracted,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
cast(if(get_json_object(line, '$.event.millis') is not null, get_json_object(line, '$.event.millis'), 
get_json_object(line, '$.file.millis')) as int) as extraction_time,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day,
get_json_object(line, '$.orgId') as org_id
from staging_logs_eventJob_epoch
where get_json_object(line, '$.level')="EVENT" 
and get_json_object(line, '$.className') like "%EventMapper" 
and get_json_object(line, '$.eventAddress') is null
and ($dateRange);

insert overwrite table summary_event_reducer_staging partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientUUID') as patient_uuid,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
cast(get_json_object(line, '$.patientevent.millis') as int) as process_time,
get_json_object(line, '$.eventBatchId') as event_batch_id,
cast(get_json_object(line, '$.eventBatch.count') as int) as event_batch_count,
get_json_object(line, '$.eventBatch.pubMessage') as published_message,
cast(get_json_object(line, '$.patientevent.count') as int) as num_of_events_persisted,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from staging_logs_eventJob_epoch 
where get_json_object(line, '$.level')="EVENT" 
and get_json_object(line, '$.className') like "%EventReducer"
and get_json_object(line, '$.eventAddress') is null
and ($dateRange);

insert overwrite table summary_event_address_staging partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientUUID') as patient_uuid,
get_json_object(line, '$.documentUUID') as doc_id,
get_json_object(line, '$.jobSubmitTime') as job_submit_time,
get_json_object(line, '$.propertyVersion') as property_version,
get_json_object(line, '$.eventAddress') as event_address,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as 	seqfilename,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from staging_logs_eventJob_epoch
where get_json_object(line, '$.level')="EVENT" 
and get_json_object(line, '$.className') like "%EventMapper" 
and get_json_object(line, '$.eventAddress') is not null
and ($dateRange);

insert overwrite table summary_qa_event_staging partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patient.info') as patient_info,
regexp_extract(get_json_object(line, '$.patient.info'), '^(.*)::.*::.*$', 1) as patient_uuid,
get_json_object(line, '$.qa.eventBatch.eventBatchId') as event_batch_id,
get_json_object(line, '$.qa.eventBatch.status')	as fetch_event_batch_status,
cast(get_json_object(line, '$.qa.eventBatch.millis') as int) as fetch_event_batch_millis,
cast(get_json_object(line, '$.qa.eventBatch.count') as int) as event_batch_count,
get_json_object(line, '$.decrypt.status') as decrypt_status,
cast(get_json_object(line, '$.decrypt.millis') as int) as decrypt_millis,
get_json_object(line, '$.qa.eventTypes.status') as qa_event_types_status,
cast(get_json_object(line, '$.qa.eventTypes.millis') as int) as qa_event_types_millis,
cast(get_json_object(line, '$.qa.eventTypes.count') as int) as event_type_count,
cast(get_json_object(line, '$.qa.failed.count') as int) as qa_failed_count,
cast(get_json_object(line, '$.qa.millis') as int) as qa_millis,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
get_json_object(line, '$.batchId') as batch_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from staging_logs_qaeventjob_epoch
where get_json_object(line, '$.level')="EVENT"
and ($dateRange);

insert overwrite table summary_loadapo_staging partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
if( get_json_object(line, '$.input.key') is not null,
get_json_object(line, '$.input.key'),
get_json_object(line, '$.patient.key')) as input_key,
get_json_object(line, '$.patient.uuids') as patient_uuids,
if( get_json_object(line, '$.multipleUUIDs.count') is not null, 
cast(get_json_object(line, '$.multipleUUIDs.count') as int), 
1) as uuid_count,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.inputSeqFileName') as seqfilename,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.readColBufferSize') as read_buffer_size,
cast(get_json_object(line, '$.loadApo.millis') as int) as millis,
get_json_object(line, '$.className') as class_name,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day, 
get_json_object(line, '$.orgId') as org_id
from staging_logs_loadapo_epoch
where get_json_object(line, '$.level') = "EVENT"
and ($dateRange);

insert overwrite table summary_qapatientuuid_staging partition(year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.jobId') as job_id,
get_json_object(line, '$.workId') as work_id,
get_json_object(line, '$.jobname') as jobname,
get_json_object(line, '$.session') as hadoopjob_id,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.patient.uuids') as patient_uuids,
get_json_object(line, '$.patient.key') as patient_key,
get_json_object(line, '$.patient.info') as patient_info,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if( get_json_object(line, '$.orgId') is null,
substr(get_json_object(line, '$.jobname'), 1, instr(get_json_object(line, '$.jobname'), "_")-1),
get_json_object(line, '$.orgId')) as org_id
from staging_logs_qapatientuuid_epoch where get_json_object(line, '$.level')='EVENT'
and get_json_object(line, '$.writeTo') is null
and ($dateRange);

insert overwrite table summary_doc_manifest_staging partition (year, month, day, org_id)
select get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.document.uuid') as apixio_uuid,
get_json_object(line, '$.document.id') as external_id,
get_json_object(line, '$.document.source') as doc_source,
get_json_object(line, '$.document.assignAuthority') as assign_authority,
get_json_object(line, '$.sourceSystem') as source_system,
get_json_object(line, '$.username') as username,
get_json_object(line, '$.status') as status,
get_json_object(line, '$.error.message') as error_message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.orgId') as org_id
from staging_logs_datacheckandrecover_epoch
where get_json_object(line, '$.docManifest') is not null
and ($dateRange);

insert overwrite table summary_careopt_load_staging partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patient.id') as patient_sql_id,
get_json_object(line, '$.patient.uuid') as patient_uuid,
cast(get_json_object(line, '$.patient.cassandraload.millis') as int) as cassandra_load_millis,
cast(get_json_object(line, '$.patient.size.bytes') as int) as patient_bytes,
get_json_object(line, '$.hostname') as hostname,
cast(get_json_object(line, '$.patientcache.size') as int) as patient_cache_size,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.patient.orgId') as org_id
from 
staging_logs_careopt_epoch 
where get_json_object(line, '$.patient.cassandraload.millis') is not null 
and ($dateRange);


insert overwrite table summary_careopt_search_staging partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.patientaccess.patient.id') as patient_sql_id,
get_json_object(line, '$.patientaccess.user.id') as user_id,
get_json_object(line, '$.patientaccess.user.username') as username,
get_json_object(line, '$.patientaccess.errorMessage') as error_message,
cast(get_json_object(line, '$.patientaccess.millis') as int) as patient_access_millis,
get_json_object(line, '$.hostname') as hostname,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.patientaccess.org.id') as org_id
from 
staging_logs_careopt_epoch 
where get_json_object(line, '$.patientaccess.patient.id') is not null 
and ($dateRange);

insert overwrite table summary_careopt_errors_staging partition (year, month, day)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.message') as error_message,
get_json_object(line, '$.loggerName') as source,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day
from 
staging_logs_careopt_epoch 
where get_json_object(line, '$.level') = 'ERROR' 
and ($dateRange);


insert overwrite table summary_careopt_login_staging partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
if(get_json_object(line, '$.logout.username') is not null,
get_json_object(line, '$.logout.username'),
get_json_object(line, '$.login.username')) as username,

if(get_json_object(line, '$.logout.userId') is not null, 
get_json_object(line, '$.logout.userId'),
get_json_object(line, '$.login.userId')) as user_id,

if(get_json_object(line, '$.logout.status') is not null,
get_json_object(line, '$.logout.status'),
get_json_object(line, '$.login.status')) as status,

if(get_json_object(line, '$.logout.userAgent') is not null,
get_json_object(line, '$.logout.userAgent'),
get_json_object(line, '$.login.userAgent')) as user_agent,

get_json_object(line, '$.hostname') as hostname,

if(get_json_object(line, '$.logout.millis') is not null,
cast(get_json_object(line, '$.logout.millis') as int),
cast(get_json_object(line, '$.login.millis') as int)) as processTime,

if(get_json_object(line, '$.logout') is not null,'logout','login') as event,

if(get_json_object(line, '$.logout.remoteAddr') is not null,
get_json_object(line, '$.logout.remoteAddr'),
get_json_object(line, '$.login.remoteAddr')) as remote_address,

substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
if(get_json_object(line, '$.logout.orgId') is not null,
get_json_object(line, '$.logout.orgId'),
get_json_object(line, '$.login.orgId')) as org_id
from 
staging_logs_careopt_epoch 
where (get_json_object(line, '$.logout') is not null or get_json_object(line, '$.login') is not null) 
and ($dateRange);


insert overwrite table summary_bundler_document_staging partition (year, month, day, org_id)
select
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hcc.bundler.receive.document') as doc_id,
get_json_object(line, '$.hcc.bundler.receive.patient') as patient_uuid,
get_json_object(line, '$.hcc.bundler.receive.event_address') as event_address,
get_json_object(line, '$.hcc.bundler.receive.event_batch_id') as event_batch_id,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day,
get_json_object(line, '$.hcc.bundler.receive.org_id') as org_id
from staging_logs_bundler_epoch where get_json_object(line, '$.hcc.bundler.receive') is not null
and ($dateRange);

insert overwrite table summary_bundler_historical_staging partition (year, month, day)
select
get_json_object(line, '$.datestamp') as time,
cast(get_json_object(line, '$.hcc.bundler.historicalEvents.lo') as bigint) as low,
cast(get_json_object(line, '$.hcc.bundler.historicalEvents.hi') as bigint) as high,
cast(get_json_object(line, '$.hcc.bundler.historicalEvents.count') as int) as count,
get_json_object(line, '$.hcc.bundler.historicalEvents.status') as status,
get_json_object(line, '$.hcc.bundler.historicalEvents.bytes') as bytes,
get_json_object(line, '$.hcc.bundler.historicalEvents.millis') as millis,
get_json_object(line, '$.jvm.memory.total.bytes') as memory_total_bytes,
get_json_object(line, '$.jvm.memory.free.bytes') as memory_free_bytes,
get_json_object(line, '$.hostname') as hostname,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day
from staging_logs_bundler_epoch where
get_json_object(line, '$.level') = 'EVENT' and
get_json_object(line, '$.hcc.bundler.historicalEvents') is not null
and ($dateRange);

insert overwrite table summary_bundler_sequence_staging partition (year, month, day)
select
get_json_object(line, '$.datestamp') as time,
cast(get_json_object(line, '$.hcc.bundler.get_sequence.count') as int) as count,
get_json_object(line, '$.hcc.bundler.get_sequence.pattern') as pattern,
get_json_object(line, '$.hcc.bundler.get_sequence.status') as status,
get_json_object(line, '$.hcc.bundler.get_sequence.millis') as millis,
get_json_object(line, '$.jvm.memory.total.bytes') as memory_total_bytes,
get_json_object(line, '$.jvm.memory.free.bytes') as memory_free_bytes,
get_json_object(line, '$.jvm.memory.max.bytes') as memory_max_bytes,
get_json_object(line, '$.hostname') as hostname,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month, day
from staging_logs_bundler_epoch where
get_json_object(line, '$.level') = 'EVENT' and
get_json_object(line, '$.hcc.bundler.get_sequence') is not null
and ($dateRange);


insert overwrite table summary_dataorchestrator_request_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.data_orchestrator.request.id') as request_id,
get_json_object(line, '$.app.data_orchestrator.request.bulk') as is_bulk,
get_json_object(line, '$.app.data_orchestrator.request.parameters') as parameters,
get_json_object(line, '$.app.data_orchestrator.request.parameters.patientUUID') as patient_uuid,
get_json_object(line, '$.app.data_orchestrator.request.parameters.documentUUID') as doc_uuid,
if( get_json_object(line, '$.app.data_orchestrator.request.bulk') = 'true', 0,
cast(get_json_object(line, '$.app.data_orchestrator.request.parameters.count') as int)) as bulk_count,
get_json_object(line, '$.app.data_orchestrator.request.status') as status, 
get_json_object(line, '$.app.data_orchestrator.request.error') as error , 
get_json_object(line, '$.app.data_orchestrator.request.code') as response_code,
get_json_object(line, '$.app.data_orchestrator.request.millis') as response_time,
get_json_object(line, '$.app.data_orchestrator.request.bytes') as content_length,
get_json_object(line, '$.app.data_orchestrator.request.method') as method,
get_json_object(line, '$.app.data_orchestrator.request.endpoint') as endpoint,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.app.data_orchestrator.request.orgId') as org_id
FROM staging_logs_dataorchestrator_epoch
WHERE get_json_object(line, '$.app.data_orchestrator.request') is not null
and ($dateRange);

insert overwrite table summary_dataorchestrator_lookup_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.data_orchestrator.lookup.request_id') as request_id,
get_json_object(line, '$.app.data_orchestrator.lookup.parameters') as parameters,
get_json_object(line, '$.app.data_orchestrator.lookup.parameters.patientUUID') as patient_uuid,
get_json_object(line, '$.app.data_orchestrator.lookup.parameters.documentUUID') as doc_uuid,
get_json_object(line, '$.app.data_orchestrator.lookup.status') as status, 
get_json_object(line, '$.app.data_orchestrator.lookup.error') as error , 
get_json_object(line, '$.app.data_orchestrator.lookup.endpoint') as endpoint,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.app.data_orchestrator.lookup.orgId') as org_id
FROM staging_logs_dataorchestrator_epoch
WHERE get_json_object(line, '$.app.data_orchestrator.lookup') is not null
and ($dateRange);

insert overwrite table summary_dataorchestrator_acl_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.data_orchestrator.acl.request_id') as request_id,
get_json_object(line, '$.app.data_orchestrator.acl.permission') as permission,
get_json_object(line, '$.app.data_orchestrator.acl.userId')  as user_id,
get_json_object(line, '$.app.data_orchestrator.acl.authStatus') as auth_status, 
get_json_object(line, '$.app.data_orchestrator.acl.status') as status, 
get_json_object(line, '$.app.data_orchestrator.acl.error') as error , 
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.app.data_orchestrator.acl.orgId') as org_id
FROM staging_logs_dataorchestrator_epoch
WHERE get_json_object(line, '$.app.data_orchestrator.acl') is not null
and ($dateRange);


insert overwrite table summary_useraccount_request_staging partition (year, month, day)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.user_account.request.userId') as user_xuuid,
get_json_object(line, '$.app.user_account.request.parameters') as parameters,
get_json_object(line, '$.app.user_account.request.parameters.orgId') as org_id,
get_json_object(line, '$.app.user_account.request.parameters.userId') as user_id,
get_json_object(line, '$.app.user_account.request.parameters.detail') as detail,
get_json_object(line, '$.app.user_account.request.parameters.email') as email,
get_json_object(line, '$.app.user_account.request.parameters.name') as name,
get_json_object(line, '$.app.user_account.request.parameters.id') as id,
get_json_object(line, '$.app.user_account.request.status') as status, 
get_json_object(line, '$.app.user_account.request.error') as error, 
get_json_object(line, '$.app.user_account.request.failureReason') as failure_reason,
get_json_object(line, '$.app.user_account.request.code') as response_code,
get_json_object(line, '$.app.user_account.request.method') as method,
get_json_object(line, '$.app.user_account.request.endpoint') as endpoint,
get_json_object(line, '$.app.user_account.request.millis') as response_time,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day
FROM staging_logs_useraccount_epoch
WHERE get_json_object(line, '$.app.user_account.request') is not null
and ($dateRange);

insert overwrite table summary_tokenizer_request_staging partition (year, month, day)
SELECT
get_json_object(line, '$.datestamp') as time,
get_json_object(line, '$.hostname') as hostname,
get_json_object(line, '$.client') as client,
get_json_object(line, '$.app.user_account.request.userId') as user_xuuid,
get_json_object(line, '$.app.user_account.request.parameters') as parameters,
get_json_object(line, '$.app.user_account.request.status') as status, 
get_json_object(line, '$.app.user_account.request.error') as error, 
get_json_object(line, '$.app.user_account.request.failureReason') as failure_reason,
get_json_object(line, '$.app.user_account.request.code') as response_code,
get_json_object(line, '$.app.user_account.request.method') as method,
get_json_object(line, '$.app.user_account.request.endpoint') as endpoint,
get_json_object(line, '$.app.user_account.request.millis') as response_time,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day
FROM staging_logs_tokenizer_epoch
WHERE get_json_object(line, '$.app.user_account.request') is not null
and ($dateRange);


insert overwrite table summary_loader_upload_staging partition (year, month, day, org_id)
SELECT
get_json_object(line, '$.batch_name') as batch_name,
get_json_object(line, '$.user') as user,
cast(get_json_object(line, '$.success') as boolean) as success,
get_json_object(line, '$.primary_id') as primary_id,
get_json_object(line, '$.upload_id') as upload_id,
get_json_object(line, '$.uuid') as uuid,
cast(get_json_object(line, '$.size') as bigint) as size,
get_json_object(line, '$.payload') as payload,
cast(get_json_object(line, '$.attempts') as int) as attempts,
get_json_object(line, '$.original_id') as original_id,
get_json_object(line, '$.reference') as reference,
get_json_object(line, '$.message') as message,
substr(get_json_object(line, '$.datestamp'),0,4) as year,
month,
day,
get_json_object(line, '$.org_id') as org_id 
FROM staging_logs_loader_epoch 
WHERE get_json_object(line, '$.level') = 'EVENT' and 
get_json_object(line, '$.org_id') is not NULL and
($dateRange);


EOF

chmod 777 update_summary.log
