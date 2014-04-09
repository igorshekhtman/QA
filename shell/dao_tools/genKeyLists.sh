#!/bin/sh
#
#lschneider

# apixio-datasource jar AND lib must be in the same folder as this script
#
# args: 1=cassandraIP, 2=columnFamily, 3=keysPerFile(for unlimited file size use 0)

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=cassandraIP, 2=columnFamily, 3=keysPerFile(for unlimited file size use 0)
"
exit
fi

mkdir $2

java -cp apixio-datasource-1.1.0.jar com.apixio.dao.cmdline.ListKeys -c $2 -a $1 -n $3 -o $2/patKeys -k patientUUID

java -cp apixio-datasource-1.1.0.jar com.apixio.dao.cmdline.ListKeys -c $2 -a $1 -n $3 -o $2/docKeys -k documentUUID

java -cp apixio-datasource-1.1.0.jar com.apixio.dao.cmdline.ListKeys -c $2 -a $1 -n $3 -o $2/partKeys -k partialPatientKey