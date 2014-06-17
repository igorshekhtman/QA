#!/bin/sh
#
# lschneider

#  Usage:
#   staging default
#   staging optimal
#   staging recoveryJobs
#   staging miscJobs
#
#   recoveryJobs
#   miscJobs
#
#   20
#   44
#   100
#   200
#
#   list (default)
#
#   alloc activityName=slots,borrowable
#   limit activityName=min,max
#
#  Activity Sets:
#   main pipeline jobs (dependent on cluster size):
#   {trace, ocr, persist, parser, dataCheckAndRecovery}
#   recovery jobs:
#   {rerunPersistReducer, patientUUIDCheckAndRecovery, recoverDocumentUUIDLink, recoverPatientUUIDLink, docUUIDLinkCheckAndRecovery, patientUUIDLinkCheckAndRecovery}
#   miscellaneous Jobs:
#   {linkMigration, qaLinkMigration, afsDownload, generate-patient-manifest, qa-fromSeqfile[*staging only], qa-fromManifest}

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
    echo "
========= Usage =========
    staging default
    staging optimal
    staging recoveryJobs
    staging miscJobs

    recoveryJobs
    miscJobs

    20
    44
    100
    200

    list (default)

    alloc activityName=slots,borrowable
    limit activityName=min,max

====== Activity Sets ======
    main pipeline jobs (dependent on cluster size):
{trace, ocr, persist, parser, dataCheckAndRecovery}

    recovery jobs:
{rerunPersistReducer, patientUUIDCheckAndRecovery, recoverDocumentUUIDLink, recoverPatientUUIDLink, docUUIDLinkCheckAndRecovery, patientUUIDLinkCheckAndRecovery}

    miscellaneous Jobs:
{linkMigration, qaLinkMigration, afsDownload, generate-patient-manifest, qa-fromSeqfile[*staging only], qa-fromManifest}

    "
    exit
fi

. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "staging" ]
then
    if [ "$2" = "default" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=2,2 ocr=2,2 persist=2,2 parser=2,2 dataCheckAndRecovery=2,2"
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "trace=0,2 ocr=0,2 persist=0,2 parser=0,2 dataCheckAndRecovery=0,2"
    elif [ "$2" = "optimal" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=1,1 ocr=9,9 persist=2,2 parser=2,2 dataCheckAndRecovery=1,1"
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "trace=0,1 ocr=0,2 persist=0,2 parser=0,2 dataCheckAndRecovery=0,1"
    elif [ "$2" = "recoveryJobs" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "rerunPersistReducer=1,0 patientUUIDCheckAndRecovery=1,0 recoverDocumentUUIDLink=1,0 recoverPatientUUIDLink=1,0 docUUIDLinkCheckAndRecovery=1,0 patientUUIDLinkCheckAndRecovery=1,0"
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "rerunPersistReducer=0,1 patientUUIDCheckAndRecovery=0,1 recoverDocumentUUIDLink=0,1 recoverPatientUUIDLink=0,1 docUUIDLinkCheckAndRecovery=0,1 patientUUIDLinkCheckAndRecovery=0,1"
    elif [ "$2" = "miscJobs" ]
    then
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "linkMigration=2,0 qaLinkMigration=2,0 afsDownload=2,0 generate-patient-manifest=2,0 qa-fromSeqfile=2,0 qa-fromManifest=2,0"
        java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "generate-patient-manifest=0,5 qa-fromSeqfile=0,2"
    fi

elif [ "$1" = "recoveryJobs" ]
then
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "rerunPersistReducer=5,0 patientUUIDCheckAndRecovery=5,0 recoverDocumentUUIDLink=1,0 recoverPatientUUIDLink=1,0 docUUIDLinkCheckAndRecovery=1,0 patientUUIDLinkCheckAndRecovery=1,0"
elif [ "$1" = "miscJobs" ]
then
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "linkMigration=5,0 qaLinkMigration=5,0 afsDownload=5,0 generate-patient-manifest=5,0 qa-fromManifest=5,0"

elif [ "$1" = "44" ]
then # overcommit ocr by 8, total borrowable = 44
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=4,4 ocr=30,22 persist=6,6 parser=6,6 dataCheckAndRecovery=6,6"
elif [ "$1" = "20" ]
then # overcommit ocr by 5, total borrowable = 20
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=2,2 ocr=15,10 persist=3,3 parser=3,3 dataCheckAndRecovery=2,2"
elif [ "$1" = "100" ]
then # total borrowable = 45, persist will max at 50, trace and dataCaR will max at 45
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=10,10 ocr=50,10 persist=15,10 parser=15,5 dataCheckAndRecovery=10,10"
elif [ "$1" = "200" ]
then # total borrowable = 35, persist will max at 55, trace and dataCaR will max at 45
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=20,10 ocr=100,0 persist=30,10 parser=30,5 dataCheckAndRecovery=20,10"

elif [ "$1" = "alloc" ]
then
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "$2"
elif [ "$1" = "limit" ]
then
    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-limit "$2"
fi

java com.apixio.coordinator.cmdline.ActivityConfigTool --list



