#!/bin/sh
#
# lschneider

#  Usage:
#   running
#   launching
#   stats
#
#   queued (default)

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
    echo "
======== Usage ========
    running
    launching
    stats

    queued (default)
        "
    exit
fi

. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "running" ]
then
    $JAVAEXEC com.apixio.coordinator.cmdline.JobsInfo --running
elif [ "$1" = "launching" ]
then
    $JAVAEXEC com.apixio.coordinator.cmdline.JobsInfo --launching
elif [ "$1" = "stats" ]
then
    $JAVAEXEC com.apixio.coordinator.cmdline.JobsInfo --stats
else
# default to 'queued' from all activities found in pipeline.xml workflow
    $JAVAEXEC com.apixio.coordinator.cmdline.JobsInfo --queued --workflow /etc/apx-coordinator/pipeline.xml
fi