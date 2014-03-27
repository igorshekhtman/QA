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
fi

java com.apixio.coordinator.cmdline.ResubmitJob --list