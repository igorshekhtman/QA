#!/bin/sh
#
#  lschneider

#  Usage:
#   activity default
#   activity activityType=priority
#   activity (list)
#
#   org orgId=priority
#   org (list) (default)

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
    echo "
======== Usage ========
    activity default
    activity activityType=priority
    activity (list)

    org orgId=priority
    org (list) (default)
    "
    exit
fi


. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "activity" ]
then
    if [ "$2" = "default" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-priority "trace=5 ocr=5 persist=5 parser=5 generate-patient-manifest=5 qa-fromSeqfile=5 dataCheckAndRecovery=5 rerunPersistReducer=5 patientUUIDCheckAndRecovery=5"
    else # single activity
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-priority "$2"
    fi

    java com.apixio.coordinator.cmdline.ActivityConfigTool --list

elif [ "$1" = "org" ]
then
    # single org
    java com.apixio.coordinator.cmdline.OrgConfigTool --set "$2"

    java com.apixio.coordinator.cmdline.OrgConfigTool --listall
else
    java com.apixio.coordinator.cmdline.OrgConfigTool --listall
fi