#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
======== Usage ========
<orgId> set <name> <value>
<orgId> migrate <newPatientCF> <primaryAssignAuthority>
<orgId> (list)

PATIENT_DATASRC_KEY;
DOCUMENT_DATASRC_KEY; 
TRACE_DATASRC_KEY;
SUMMARY_DATASRC_KEY; 
EVENT_DATASRC_KEY;             
WORK_DATASRC_KEY;
PRIMARY_ASSIGN_AUTHORITY_KEY
"
exit
fi

if [ "$2" = "set" ]
then

echo "Setting $3 to $4 for org $1."
java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --orgId $1 --set --name $3 --value "$4"

elif [ "$2" = "migrate" ]
then

echo "Setting PATIENT_DATASRC_KEY to $3 for org $1."
java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --orgId $1 --set --name PATIENT_DATASRC_KEY --value $3

echo "Setting PRIMARY_ASSIGN_AUTHORITY_KEY to $4 for org $1."
java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --orgId $1 --set --name PRIMARY_ASSIGN_AUTHORITY_KEY --value "$4"

fi

echo "Listing org properties for org $1."
java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --list all --orgId $1
