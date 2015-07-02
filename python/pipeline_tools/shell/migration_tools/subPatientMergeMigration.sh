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

    java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.CreateColumnFamilies --hosts 10.199.22.32 --columnFamily $3 --workAreaColumnFamily work$1 --orgId $1 --output createdCF.out
    java -cp apixio-datasource-primaryExternalId-SNAPSHOT.jar com.apixio.dao.cmdline.OrgPropertiesTool --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA== --set --name WORK_DATASRC_KEY --value work$1 --orgId $1

    $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/PMMigrationInput -g apoMigration -a dev -l $1_partKeys -b $1_PMMigrationTest orgId=$1 newPatientCF=$3 primaryAssignAuthority="$4" newLinkCF=tmp1

elif [ "$2" = "production" ]
then
    java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.CreateColumnFamilies -a 10.173.29.185,10.174.49.107,10.174.97.35 -c cf$1 -g $1 -t trace$1 -o createdCF.out

    if [ -z "$5" ]
    then
        $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys -b $1_apoMigration orgId=$1 newHosts=10.173.29.185,10.174.49.107,10.174.97.35
    else

        count=0
        filenumber=0
        for file in cf$1_partKeys/*
        do
            if [ "$count" = "0" ]
            then
                filenumber=$((filenumber+1))
                mkdir cf$1_partKeys/sub-$filenumber
            fi

            count=$((count+1))
            mv $file cf$1_partKeys/sub-$filenumber

            if [ "$count" = "$5" ]
            then
                count=0

                echo "[SUBMISSION] count: $filenumber..."
                $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys/sub-$filenumber -b $1_apoMigration_$filenumber orgId=$1 newHosts=10.173.29.185,10.174.49.107,10.174.97.35
            fi
        done
        if [ "$count" != "0" ]
        then
            echo "[SUBMISSION] count: $filenumber..."
            $JAVAEXEC com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys/sub-$filenumber -b $1_apoMigration_$filenumber orgId=$1 newHosts=10.173.29.185,10.174.49.107,10.174.97.35
        fi
    fi
fi
