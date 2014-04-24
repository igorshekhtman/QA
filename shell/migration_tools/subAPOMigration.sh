#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId 2={"staging","production"}
"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

echo "
Submitting APO Migration for org $1 on $2:
"

if [ "$2" = "staging" ]
then

java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.CreateColumnFamilies -a 10.199.22.32 -c cf$1 -g $1 -t trace$1 -o createdCF.out

java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys -b $1_apoMigration orgId=$1 newHosts=10.199.22.32,10.196.81.90,10.198.2.83,10.196.100.53,10.197.91.36,10.199.52.19

elif [ "$2" = "production" ]
then

echo "[FAILURE] needs new cassandra hostnames!"
#java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.CreateColumnFamilies -a ONENEWHOSTNAME -c cf$1 -g $1 -t trace$1 -o createdCF.out

#java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys -b $1_apoMigration orgId=$1 newHosts=?

fi
