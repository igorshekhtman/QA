#!/bin/bash
# author: lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
    echo "
Arguments:  1={"staging","production"}
            2=orgId
            3=inputFolderPath(will submit one job per file in this folder)
            4=optionalParameters(quoted together)
        "
    exit
fi

. /usr/lib/apx-coordinator/bin/setcp

echo "Submitting event submission from load APO jobs on $1 for org $2 from input file $3"

#batchtime=$(date +'%m%d%y%H%M%S') changing this to unix time
batchtime=$(date +%s)

if [ "$1" = "staging" ]
then

#$JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $2 -b $2_eventSubmission_$batchtime -p 7 -g eventGeneration -l $3 -i /user/apxqueue/loadAPOInput_$batchtime $4

#echo "Batch ID: $2_eventSubmission_$batchtime"
echo "staging not implemented"


elif [ "$1" = "production" ]
then

    for file in $3/*
    do
        $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $2 -b $2_eventSubmission_$batchtime -p 7 -g eventGeneration -l $file -i /user/apxqueue/loadAPOInput_$batchtime $4
    done

    echo "
        Batch ID: $2_eventSubmission_$batchtime
    "

else
    echo "[WARN] $1 environment not recognized"
fi
