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

echo "
Getting partial patient keys for org $2 from $1:
"

if [ "$1" = "staging" ]
then

java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.ListKeys -c cf$2 -a 10.222.101.109 -n $3 -o cf$2_partKeys -k partialPatientKey

elif [ "$1" = "production" ]
then

echo "[FAILURE] need production cassandra IP!"
#java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.ListKeys -c cf$2 -a productionCassandra -n $3 -o cf$2_partKeys -k partialPatientKey

fi
