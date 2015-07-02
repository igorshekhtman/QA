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

Arguments: 1={"staging","production"}, 2=orgId
"
exit
fi

echo "
Getting document to patient UUID mapping for org $2 from $1:

"

if [ "$1" = "staging" ]
then

java -cp apixio-datasource-*.jar com.apixio.dao.cmdline.ListKeys --orgId $2 --hosts 10.199.22.32 --numKeysPerFile 0 --output $2_docUUIDKeys --keyFilter documentUUID --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA==

java -cp apixio-datasource-*.jar com.apixio.dao.cmdline.ReadKey --hosts 10.199.22.32 --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --output $2readDocKeys --input $2_docUUIDKeys/* --orgId $2 --keyType documentUUID

elif [ "$1" = "production" ]
then

java -cp apixio-datasource-*.jar com.apixio.dao.cmdline.ListKeys --orgId $2 --hosts 10.174.97.35 --numKeysPerFile 0 --output $2_docUUIDKeys --keyFilter documentUUID --mysqlHost 10.198.2.97 --mysqlUser apxDB --mysqlPwd 2518140788360689940544V01x1iehnaJs6qqoIWNMVa6sog==

java -cp apixio-datasource-*.jar com.apixio.dao.cmdline.ReadKey --hosts 10.174.97.35 --mysqlHost 10.198.2.97 --mysqlUser apxDB --mysqlPwd 2518140788360689940544V01x1iehnaJs6qqoIWNMVa6sog== --output $2readDocKeys --input $2_docUUIDKeys/* --orgId $2 --keyType documentUUID

fi

awk -F'\t' '{print $1, "\t", $2}' $2readDocKeys >> $2docKeyToPatientUUID
echo "Output file mapping document UUID reverse keys to their patient UUIDs: $2docKeyToPatientUUID"
rm $2readDocKeys
rm -r $2_docUUIDKeys