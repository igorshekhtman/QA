#!/bin/sh
#
# lschneider

#  Usage:
#   enable <activity>
#   enable org <orgId>
#   enable all
#
#   disable <activity>
#   disable org <orgId>
#   disable all
#
#   list (default)
#   list org
#
#  Note:
#   all = {trace, ocr, persist, parser, generate-patient-manifest, qa-fromSeqfile, dataCheckAndRecovery, rerunPersistReducer, patientUUIDCheckAndRecovery}

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
    echo "
======== Usage ========
    enable <activity>
    enable org <orgId>
    enable all

    disable <activity>
    disable org <orgId>
    disable all

    list (default)
    list org
    "
    exit
fi


. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "enable" ]
then
    if [ "$2" = "all" ]
    then
        $JAVAEXEC com.apixio.coordinator.cmdline.ActivityConfigTool --enable "trace ocr persist parser generate-patient-manifest qa-fromSeqfile dataCheckAndRecovery rerunPersistReducer patientUUIDCheckAndRecovery"
    elif [ "$2" = "org" ]
    then
        $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --enable "$3"
    else
        $JAVAEXEC com.apixio.coordinator.cmdline.ActivityConfigTool --enable "$2"
    fi
elif [ "$1" = "disable" ]
then
    if [ "$2" = "all" ]
    then
        $JAVAEXEC com.apixio.coordinator.cmdline.ActivityConfigTool --disable "trace ocr persist parser generate-patient-manifest qa-fromSeqfile dataCheckAndRecovery rerunPersistReducer patientUUIDCheckAndRecovery"
    elif [ "$2" = "org" ]
    then
        $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --disable "$3"
    else
        $JAVAEXEC com.apixio.coordinator.cmdline.ActivityConfigTool --disable "$2"
    fi
fi

if [ "$2" = "org" ]
then
    $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --listall
else
    $JAVAEXEC com.apixio.coordinator.cmdline.ActivityConfigTool --list
fi