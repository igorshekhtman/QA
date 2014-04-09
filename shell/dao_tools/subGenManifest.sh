#!/bin/sh
#
# lschneider

# apixio-datasource jar AND lib must be in the same folder as this script
# must run from apxqueue
#
# args: 1=cassandraIP, 2=columnFamily, 3=keysPerFile(for unlimited file size use 0), 4=orgId

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=cassandraIP, 2=columnFamily, 3=keysPerFile(for unlimited file size use 0), 4=orgId
"
exit
fi


java -cp apixio-datasource-1.1.0.jar com.apixio.dao.cmdline.ListKeys -a $1 -c $2 -o $2keys -k partialPatientKey -n $3

. /usr/lib/apx-coordinator/bin/setcp

java com.apixio.coordinator.SubmitWorkCmd -o $4 -p 8 -i /user/apxqueue/genManifest_$2 -g patientmanifest -l $2keys manifestColumnFamily=$2 manifestOrgId=$4