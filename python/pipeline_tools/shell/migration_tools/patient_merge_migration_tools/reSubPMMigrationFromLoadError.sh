#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId 2={"staging","production"} 3=hdfsErrorFilePath 4=primaryAssignAuthority 5=newPatientCF
"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

echo "
Resubmitting apoLoader error file: $3
"

if [ "$2" = "staging" ]
then

$JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i $3 -g apoMigration -a dev -b $1_PMMigrationTest_reload orgId=$1 newPatientCF=$5 primaryAssignAuthority="$4" newLinkCF=apx_cfLink_new

elif [ "$2" = "production" ]
then

java com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i $3 -g apoMigration -b $1_PMMigration_reload orgId=$1 newPatientCF=$5 primaryAssignAuthority="$4" newLinkCF=apx_cfLink_new

fi

