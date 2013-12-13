#! /bin/sh

# Get statistics on files of different types from HIVE

export TZ=America/Los_Angeles

timestamp=$(date +'%s')

datestamp=$(date +'%m/%d/%y %r')

totalnumberofdocuments=0


# timestamp=$(date +'%s')
# datestamp=$(date +'%F-%H%M%S')

#batchId=testbatch100113
batchId=testbatch100313
filename=qc_tool_$timestamp.txt

/usr/bin/hive --service beeline -u jdbc:hive2://10.196.47.205:10000 -n hive -d org.apache.hive.jdbc.HiveDriver >> $filename << EOF
select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "DOCX";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "RTF";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "PDF";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "DOC";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "TIF";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "TIFF";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "HED";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "APO";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "JPG";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "JPEG";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "BMP";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "PNG";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "TXT";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "CCR";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
get_json_object(line, '$.file.type') = "CCD";

select count(*) from staging_logs_parserjob_epoch where get_json_object(line, '$.jobname') like 'Igor-Lance-1org-MMG-2%' and 
get_json_object(line, '$.file.bytes') > 0 and 
(get_json_object(line, '$.file.type') = "DOCX" or 
get_json_object(line, '$.file.type') = "RTF" or 
get_json_object(line, '$.file.type') = "PDF" or 
get_json_object(line, '$.file.type') = "DOC" or 
get_json_object(line, '$.file.type') = "TIF" or
get_json_object(line, '$.file.type') = "TIFF" or
get_json_object(line, '$.file.type') = "HED" or
get_json_object(line, '$.file.type') = "APO" or
get_json_object(line, '$.file.type') = "JPG" or
get_json_object(line, '$.file.type') = "JPEG" or
get_json_object(line, '$.file.type') = "BMP" or
get_json_object(line, '$.file.type') = "PNG" or
get_json_object(line, '$.file.type') = "TXT" or
get_json_object(line, '$.file.type') = "CCR" or
get_json_object(line, '$.file.type') = "CCD");
EOF

mail -s "Pipeline QA Report On: $datestamp for Batch ID: $batchId" -r donotreply@apixio.com ishekhtman@apixio.com < $filename
rm $filename
