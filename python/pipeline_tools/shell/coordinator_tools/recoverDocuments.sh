#!/bin/sh
#
# nkrishna

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
    echo "
Arguments: 1=orgId
    "
    exit
fi

. /usr/lib/apx-coordinator/bin/setcp

url="https://10.170.181.208:443/hive/manifest/staging/recovery_manifest"
params="?org_id=%27$1%27"

filename=recover_$1

echo "Doc UUIDs getting recovered will be stored in this file: $filename"
curl --insecure -o $filename $url$params
$JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/afsRecoverInput -g recoverDocuments -a dev -l $filename -b $1_afsRecovery
