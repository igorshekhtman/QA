#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId 2={"staging","production"} 3=hdfsErrorFilePath
"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

if [ "$2" = "staging" ]
then

echo "
Resubmitting apoLoader error file: $3
"

java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i $3 -g apoMigration -b $1_apoMigration_reload orgId=$1 newHosts=10.199.22.32,10.196.81.90,10.198.2.83,10.196.100.53,10.197.91.36,10.199.52.19

elif [ "$2" = "production" ]
then

echo "needs hostnames"
#java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys -b $1_apoMigration orgId=$1 newHosts=?

fi

