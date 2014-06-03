#!/bin/sh
#
#lschneider

# apixio-datasource jar AND lib must be in the same folder as this script
#
# args: 1=cassandraIP, 2=columnFamily, 3=keysPerFile(for unlimited file size use 0)

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1={"staging","production"}, 2=orgId, 3=keysPerFile(for unlimited file size use 0)
"
exit
fi

mkdir docs_$2

if [ "$1" = "staging" ]
then
echo "
Getting partial patient keys for org $2 from $1:
"
java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.ListKeys -c cf$2 -a 10.222.101.109 -n $3 -o docs_$2/docUUIDs -k documentUUID

echo "
Getting document UUID keys for org $2 from new $1:
"
java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.ListKeys -c cf$2 -a 10.199.22.32 -n $3 -o docs_$2/migratedDocUUIDs -k documentUUID

echo "
Checking differences between document UUIDs in old and new cassandra:
"

diff -r docs_$2/docUUIDs docs_$2/migratedDocUUIDs

echo "DONE."

elif [ "$1" = "production" ]
then
echo "need production cassandra IP"
#java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.ListKeys -c cf$2 -a productionCassandra -n $3 -o cf$2_partKeys -k partialPatientKey

fi
