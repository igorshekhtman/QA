#! /bin/sh

echo "Creating data for recovery..."
echo " "


/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver  >> create_recovery_data.log   << EOF

set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
set mapred.reduce.tasks=16;
set mapred.job.queue.name=default;
set hive.exec.max.dynamic.partitions.pernode = 1000;

drop table docrecovery_manifest;

create table docrecovery_manifest (doc_id string, seqfile_file string, time string) 
partitioned by (org_id string, queue_type string, month string, day string);

insert overwrite table docrecovery_manifest partition (org_id, queue_type, month, day)
select distinct(p.doc_id), p.seqfilename, p.org_id, "verification_queue", p.month, p.day
from summary_persist_mapper p
join summary_coordinator_jobfinish j on j.hadoop_job_id=p.hadoopjob_id and j.status="success"
left outer join summary_qafromseqfile v on v.doc_id=p.doc_id
where (v.doc_id is null or v.patient_key is null);

insert overwrite table docrecovery_manifest partition (org_id, queue_type, month, day)
select distinct(doc.doc_id), doc.seqfile_file, doc.time, doc.org_id, "docreceiver_queue", doc.month, doc.day
from summary_docreceiver_seqfile doc
left outer join summary_docreceiver_seqfile_post post on doc.seqfile_directory=post.seqfile_path and post.redis_queue_name is not null
left outer join (select d.doc_id from summary_afsdownload d join summary_coordinator_jobfinish b on d.hadoopjob_id = b.hadoop_job_id and b.status="success"
where d.status="success") r on r.doc_id=doc.doc_id
where post.seqfile_path is null and doc.seqfile_directory is not null and doc.status="success" and r.doc_id is null;


drop table docrecovery_manifest_staging;

create table docrecovery_manifest_staging (doc_id string, seqfile_file string, time string) 
partitioned by (org_id string, queue_type string, month string, day string);

insert overwrite table docrecovery_manifest_staging partition (org_id, queue_type, month, day)
select distinct(p.doc_id), p.seqfilename, p.org_id, "verification_queue", p.month, p.day
from summary_persist_mapper_staging p
join summary_coordinator_jobfinish_staging j on j.hadoop_job_id=p.hadoopjob_id and j.status="success"
left outer join summary_qafromseqfile_staging v on v.doc_id=p.doc_id
where (v.doc_id is null or v.patient_key is null);

insert overwrite table docrecovery_manifest_staging partition (org_id, queue_type, month, day)
select distinct(doc.doc_id), doc.seqfile_file, doc.time, doc.org_id, "docreceiver_queue", doc.month, doc.day
from summary_docreceiver_seqfile_staging doc
left outer join summary_docreceiver_seqfile_post_staging post on doc.seqfile_directory=post.seqfile_path and post.redis_queue_name is not null
left outer join (select d.doc_id from summary_afsdownload_staging d join summary_coordinator_jobfinish_staging b on d.hadoopjob_id = b.hadoop_job_id and b.status="success"
where d.status="success") r on r.doc_id=doc.doc_id
where post.seqfile_path is null and doc.seqfile_directory is not null and doc.status="success" and r.doc_id is null;

EOF

chmod 777 create_recovery_data.log
