#!/bin/bash
# author: lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
    echo "
Arguments: 1={"staging","production"}
           2=orgId
           3=inputFilePath
    "
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

echo "Submitting an AFS recover job on $1 for org $2 from input file $3"

batchtime=$(date +'%m%d%y%H%M%S')

if [ "$1" = "staging" ]
then

    $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $2 -b $2_recovery_$batchtime -p 7 -a release -g recoverDocuments -l $3 -i /user/apxqueue/afsRecoverInput_$batchtime
    echo "Batch ID: $2_recover_$batchtime"

elif [ "$1" = "production" ]
then

    $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $2 -b $2_recovery_$batchtime -p 7 -g recoverDocuments -l $3 -i /user/apxqueue/afsRecoverInput_$batchtime
    echo "Batch ID: $2_recover_$batchtime"

else
echo "[WARN] $1 environment not recognized"
fi
