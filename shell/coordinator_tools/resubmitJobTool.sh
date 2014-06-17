#!/bin/sh
#
# lschneider

#  Usage:
#   job <jobId>
#   activity <activity>
#   type <type>
#   org <orgId>
#   all
#
#   ignore job <jobId>
#   ignore activity <activity>
#   ignore type <type>
#   ignore org <orgId>
#
#   list (default)
#
#  Note:
#   Only accepts one argument at a time.
#   types = {failed, orphaned, launcherror}

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
    echo "
======== Usage ========
    job <jobId>
    activity <activity>
    type <type>
    org <orgId>
    all

    ignore job <jobId>
    ignore activity <activity>
    ignore type <type>
    ignore org <orgId>

    list (default)
    "
    exit
fi

. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "job" ]
then
    java com.apixio.coordinator.cmdline.ResubmitJob --submit --job "$2"
elif [ "$1" = "activity" ]
then
    java com.apixio.coordinator.cmdline.ResubmitJob --submit --activity $2
elif [ "$1" = "type" ]
then
    java com.apixio.coordinator.cmdline.ResubmitJob --submit --type $2
elif [ "$1" = "org" ]
then
    java com.apixio.coordinator.cmdline.ResubmitJob --submit --org "$2"
elif [ "$1" = "all" ]
then
    java com.apixio.coordinator.cmdline.ResubmitJob --submit --all
elif [ "$1" = "ignore" ]
then
    if [ "$2" = "job" ]
    then
        java com.apixio.coordinator.cmdline.ResubmitJob --ignore --job "$3"
    elif [ "$2" = "activity" ]
    then
        java com.apixio.coordinator.cmdline.ResubmitJob --ignore --activity $3
    elif [ "$2" = "type" ]
    then
        java com.apixio.coordinator.cmdline.ResubmitJob --ignore --type $3
    elif [ "$2" = "org" ]
    then
        java com.apixio.coordinator.cmdline.ResubmitJob --ignore --org "$3"
    fi
fi

java com.apixio.coordinator.cmdline.ResubmitJob --list