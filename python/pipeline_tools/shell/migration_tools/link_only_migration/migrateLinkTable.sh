#!/bin/bash
# author: lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
    echo "
Arguments:  1=orgId
        "
    exit
fi
. /usr/lib/apx-coordinator/bin/setcp
$JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/linkRepair$1 -g linkMigration -a dev -l $1_uuids -b $1_linkRepair linkCFMigrationOrg=$1 
