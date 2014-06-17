#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId
"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/testLinkMigration -g linkMigration -l cf$1/docKeys -b $1_docLinkMigration linkCFMigrationOrg=$1

java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/testLinkMigration -g linkMigration -l cf$1/patKeys -b $1_patLinkMigration linkCFMigrationOrg=$1