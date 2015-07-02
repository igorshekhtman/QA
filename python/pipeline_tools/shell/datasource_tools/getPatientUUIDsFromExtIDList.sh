#!/bin/sh
#
#lschneider

# apixio-datasource jar AND lib AND apixio-security.properties must be in the same folder as this script

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Resources: apixio-datasource-*.jar (ONE version at a time please)
           lib
           apixio-security.properties

Arguments: 1={"staging","production"}, 2=orgId, 3=assignAuthority, 4=inputFile
"
exit
fi

echo "
Getting patient keys for org $2 from $1 using assignAuthority $3:

"

if [ "$1" = "staging" ]
then

java -cp apixio-datasource-*.jar com.apixio.dao.cmdline.ReadKey --hosts 10.199.22.32 --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --output $2-patientUUIDs-withExtIDs --input $4 --assignAuthority "$3" --orgId $2 --keyType externalID

elif [ "$1" = "production" ]
then

java -cp apixio-datasource-*.jar com.apixio.dao.cmdline.ReadKey --hosts 10.174.97.35 --mysqlHost 10.198.2.97 --mysqlUser apxDB --mysqlPwd 2518140788360689940544V01x1iehnaJs6qqoIWNMVa6sog== --output $2-patientUUIDs-withExtIDs --input $4 --assignAuthority "$3" --orgId $2 --keyType externalID

else

echo "Environment $1 not recognized."
exit

fi

echo "Output file with rows External ID, time stamp, and patient UUID tab separated: $2-patientUUIDs-withExtIDs"
awk -F'\t' '{print $3}' $2-patientUUIDs-withExtIDs >> $2-patientUUIDs
echo "Output file with just patient UUIDs: $2-patientUUIDs"
