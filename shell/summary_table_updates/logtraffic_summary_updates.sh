#! /bin/sh

#=========================================== Assigning default variable values =====================================

export TZ=America/Los_Angeles

daysBack=1
daysBack=$1
dateRange="";

if [ -z $1 ]; then
	echo ">>> Days back not provided, assigning value of 1"
	echo ">>> "
	daysBack=1
fi
curDay=$(date +%d);
curMonth=$(date +%m);
scurDay=$(date +%d);
scurMonth=$(date +%m);
scurYear=$(date +%Y);

echo "Current day: $curDay"
echo "Current month: $curMonth"
echo " "

#============ adjust day and month of the report =================================================================

#============ Overwrite day,month and dateRange values ======
#============================================================

day=$scurDay
month=$scurMonth
year=$scurYear
dateRange="(month=$curMonth and day=$curDay and year=$year)"

echo "Updating partitioned log traffic summary table with date range: $dateRange"
echo " "

envs="production staging"
appNames="persistJob json2trace parserJob coordinator ocrJob docreceiver careopt dataCheckAndRecover dataorchestrator useraccount bundler eventJob"

for env in $envs
do

environment="_"$env
if [ "$env" = "production" ] 
then
  environment=""
fi

# TODO: drop partition, then add to instead of 'override'- throws data away - Lance

for t in $appNames
do

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver  >> update_summary.log   << EOF
set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
set mapred.reduce.tasks=16;
set mapred.job.queue.name=hive;
set hive.exec.max.dynamic.partitions.pernode = 1000;
-- compress all data 
set mapred.output.compress=true;
set hive.exec.compress.output=true;
set mapred.output.compression.codec=org.apache.hadoop.io.compress.GzipCodec;
set io.compression.codecs=org.apache.hadoop.io.compress.GzipCodec;
SET mapred.output.compression.type=BLOCK;

insert overwrite table summary_logstraffic${environment} partition (app_name, month, day, year)
select 
count(*) as total,
sum(if(discarded is not null, discarded, 0)) as discarded,
count(if(line like "%INFO%", "true", null)) as infos,
count(if(line like "%EVENT%", "true", null)) as events,
count(if(line like "%WARN%", "true", null)) as warnings,
count(if(line like '%ERROR%', "true", null)) as errors,
"${t}" as app_name, month, day, year
from
(select month, day, line, year,
cast(regexp_extract(line, "Discarded (.*) messages due to full event buffer including.*", 1) as int) as discarded
from
${env}_logs_${t}_epoch
where $dateRange
) sub group by month,day,year;

EOF

done
done

chmod 777 update_summary.log
