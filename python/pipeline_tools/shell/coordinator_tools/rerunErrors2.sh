#!/bin/bash
# author: nkrishna

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=logFileName 2=activity 3=orgId 4=date(format:yyyy-mm-dd)(optional)
"
exit
fi

hdfsPath="/user/apxqueue/queue-location-14/jobs-with-errors"
i=0

activity=$2
if [ -z "$4" ]
then
scanPath="$hdfsPath/$3/*/$activity"
else
scanPath="$hdfsPath/$3/$4/$activity"
echo "Date given:"$4
fi

. /usr/lib/apx-coordinator/bin/setcp

hadoop fs -ls $scanPath | awk '{print $8}' | \
( while read x
do
echo "Scanning folder:"$x
IFS='\/' read -a dirArr <<< "${x}"
orgId=${dirArr[5]}

if [ $(hadoop fs -ls "$x" | wc -l) -gt 0 ]; then
echo "Submitting the $x folder for org:$orgId, operation:$activity..." >> $1
$JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $orgId -b "$orgId"_errorsBatch -i $x -g $activity -a dev
fi
done
)