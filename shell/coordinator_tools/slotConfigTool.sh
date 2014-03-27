#!/bin/sh
#
# lschneider

#  Usage:
#   staging default (or) 18 default
#   staging optimal (or) 18 optimal
#
#   custom
#
#   44
#
#   list (default)
#
#   alloc activity=slots,borrowable
#   limit activity=min,max
#
#  Note:
#   includes activities:
#   {trace, ocr, persist, parser, generate-patient-manifest, qa-fromSeqfile, dataCheckAndRecovery, rerunPersistReducer, patientUUIDCheckAndRecovery}

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
    echo "
======== Usage ========
    staging default (or) 18 default
    staging optimal (or) 18 optimal
    custom
    44

    list (default)

    alloc activity=slots,borrowable
    limit activity=min,max
    "
    exit
fi

. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "18" ] || [ "$1" = "staging" ]
then
    if [ "$2" = "default" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=2,2 ocr=2,2 persist=2,2 parser=2,2 generate-patient-manifest=2,2 qa-fromSeqfile=2,2 dataCheckAndRecovery=2,2 rerunPersistReducer=2,2 patientUUIDCheckAndRecovery=2,2"
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "trace=0,2 ocr=0,2 persist=0,2 parser=0,2 generate-patient-manifest=0,2 qa-fromSeqfile=0,2 dataCheckAndRecovery=0,2 rerunPersistReducer=0,2 patientUUIDCheckAndRecovery=0,2"
    elif [ "$2" = "optimal" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=1,1 ocr=9,9 persist=2,2 parser=2,2 generate-patient-manifest=0,0 qa-fromSeqfile=1,1 dataCheckAndRecovery=1,1 rerunPersistReducer=1,1 patientUUIDCheckAndRecovery=1,1"
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "trace=0,1 ocr=0,2 persist=0,2 parser=0,2 generate-patient-manifest=0,2 qa-fromSeqfile=0,1 dataCheckAndRecovery=0,1 rerunPersistReducer=0,1 patientUUIDCheckAndRecovery=0,1"
    elif [ "$2" = "custom" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc ""
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit ""
    fi
elif [ "$1" = "44" ]
then
    # overcommits by 10 (so map jobs aren't waiting for reducers to finish)
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=4,4 ocr=22,22 persist=6,6 parser=6,6 dataCheckAndRecovery=6,6 generate-patient-manifest=5,5 rerunPersistReducer=5,5 patientUUIDCheckAndRecovery=5,0"
elif [ "$1" = "alloc" ]
then
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "$2"
elif [ "$1" = "limit" ]
then
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "$2"
fi

java com.apixio.coordinator.cmdline.ActivityConfigTool --list



