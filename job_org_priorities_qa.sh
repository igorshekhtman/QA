#! /bin/sh

export TZ=America/Los_Angeles

timestamp=$(date +'%s')

datestamp=$(date +'%m/%d/%y %r')

OrgId1=$1
OrgId2=$2

if [ -z $1 ]; then
echo "No arguments supplied, assigning OrgId1 value of 63"
OrgId1=63
fi

if [ -z $2 ]; then
echo "No arguments supplied, assigning OrgId2 value of 64"
OrgId2=64
fi

filename=qa_report_$timestamp.txt

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver >> $filename << EOF

SELECT concat(substr(get_json_object(line, '$.coordinator.job.context'),10,12), substr(get_json_object(line, '$.coordinator.job.context'),30,15)) as priority_and_org_id, 
concat(substr(get_json_object(line, '$.datestamp'),0,10), "  ", substr(get_json_object(line, '$.datestamp'),12,8)) as date_time
FROM staging_logs_coordinator_epoch 
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.coordinator.job.status') = "start" and
(get_json_object(line, '$.coordinator.job.context') like "%$OrgId1%" or
get_json_object(line, '$.coordinator.job.context') like "%$OrgId2%")
SORT BY date_time ASC;

SELECT count(*) as total_number_of_jobs
FROM staging_logs_coordinator_epoch
WHERE
get_json_object(line, '$.level') = "EVENT" and
get_json_object(line, '$.coordinator.job.status') = "start" and
(get_json_object(line, '$.coordinator.job.context') like "%$OrgId1%" or
get_json_object(line, '$.coordinator.job.context') like "%$OrgId2%");
EOF

mail -s "Job/Org Priorities Test Report for Orgs $OrgId1 & $OrgId2 - $datestamp" -r ishekhtman@apixio.com ishekhtman@apixio.com,ishekhtman@apixio.com < $filename
#mail -s "Job/Org Priorities Test Report for Orgs $OrgId1 & $OrgId2 - $datestamp" -r ishekhtman@apixio.com ishekhtman@apixio.com,eng@apixio.com < $filename

rm $filename
