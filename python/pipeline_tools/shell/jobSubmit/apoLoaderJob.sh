#!/bin/bash
# author: lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
    echo "
Arguments: 1={"staging","production"}
           2={"event","summary","manifest"}
           3=orgId
           4=inputFilePath
           5=extraParameter(optional)
    "
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

echo "Submitting a(n) $2 from load APO job on $1 for org $3 from input file $4"

#batchtime=$(date +'%m%d%y%H%M%S') changing this to unix time
batchtime=$(date +%s)

if [ "$1" = "staging" ]
then

    if [ "$2" = "event" ] || [ "$2" = "summary" ] || [ "$2" = "manifest" ]
    then
        $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $3 -b $3_$2Submission_$batchtime -p 7 -a dev -g $2Generation -l $4 -i /user/apxqueue/loadAPOInput_$batchtime $5
        echo "Batch ID: $3_$2Submission_$batchtime"
    else
        echo "[WARN] $2 loader job not recognized"
    fi

elif [ "$1" = "production" ]
then

    if [ "$2" = "event" ] || [ "$2" = "manifest" ] # summary objects not available on prod yet
    then
        $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $3 -b $3_$2Submission_$batchtime -p 7 -g $2Generation -l $4 -i /user/apxqueue/loadAPOInput_$batchtime $5
        echo "Batch ID: $3_$2Submission_$batchtime"
    else
        echo "[WARN] $2 loader job not available"
    fi

else
    echo "[WARN] $1 environment not recognized"
fi