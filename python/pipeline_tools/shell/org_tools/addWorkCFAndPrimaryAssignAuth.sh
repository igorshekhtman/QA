#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId 2=primaryAssignAuthority 3={"staging","production"} 
"
exit
fi

if [ "$3" = "staging" ]
then

    java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.CreateColumnFamilies --hosts 10.199.22.32 --workAreaColumnFamily work$1 --orgId $1 --output createdCF.out
    java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --set --name WORK_DATASRC_KEY --value work$1 --orgId $1
    java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --set --name PRIMARY_ASSIGN_AUTHORITY_KEY --value "$2" --orgId $1

    echo "Listing org properties for org $1."
java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --list all --orgId $1


elif [ "$3" = "production" ]
then
    echo "NOT SETUP FOR PRODUCTION"

fi


