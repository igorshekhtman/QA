#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId 2={"staging","production"} 3=newColumnFamilyName 4=primaryAssignAuthority 5=numFilesPerSubmit(optional)
"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

echo "
Submitting migration to new patient column family for org $1 on $2:
    > new work table (column family & org property): work$1
    > new patient column family: $3
    > using primary assign authority: $4
    > using new link table: tmp1
"

if [ "$2" = "staging" ]
then

    java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.CreateColumnFamilies --hosts 10.199.22.32 --columnFamily $3 --workAreaColumnFamily work$1 --orgId $1 --output createdCF.log
    java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --set --name WORK_DATASRC_KEY --value work$1 --orgId $1

    $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/PMMigrationInput -g apoMigration -a dev -l $1_partKeys -b $1_PMMigrationTest orgId=$1 newPatientCF=$3 primaryAssignAuthority="$4" newLinkCF=apx_cfLink_new

elif [ "$2" = "production" ]
then

    java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.CreateColumnFamilies --hosts 10.174.97.35 --columnFamily $3 --workAreaColumnFamily work$1 --orgId $1 --output createdCF.log
    java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518140788360689940544V01x1iehnaJs6qqoIWNMVa6sog== --set --name WORK_DATASRC_KEY --value work$1 --orgId $1

    if [ -z "$5" ]
    then
        java com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/PMMigrationInput -g apoMigration -l $1_partKeys -b $1_PMMigration orgId=$1 newPatientCF=$3 primaryAssignAuthority="$4" newLinkCF=apx_cfLink_new
    else

        count=0
        filenumber=0
        for file in $1_partKeys/*
        do
            if [ "$count" = "0" ]
            then
                filenumber=$((filenumber+1))
                mkdir $1_partKeys/sub-$filenumber
            fi

            count=$((count+1))
            mv $file $1_partKeys/sub-$filenumber

            if [ "$count" = "$5" ]
            then
                count=0

                echo "[SUBMISSION] count: $filenumber..."
                java com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/PMMigrationInput -g apoMigration -l $1_partKeys/sub-$filenumber -b $1_PMMigration orgId=$1 newPatientCF=$3 primaryAssignAuthority="$4" newLinkCF=apx_cfLink_new
            fi
        done
        if [ "$count" != "0" ]
        then
            echo "[SUBMISSION] count: $filenumber..."
            java com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/PMMigrationInput -g apoMigration -l $1_partKeys/sub-$filenumber -b $1_PMMigration orgId=$1 newPatientCF=$3 primaryAssignAuthority="$4" newLinkCF=apx_cfLink_new
        fi
    fi
fi
