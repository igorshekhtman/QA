#!/bin/sh
#
#lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1=orgId 2={"staging","production"} 3=numFilesPerSubmit(optional)
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
    java -cp apixio-datasource-1.1.3.jar com.apixio.dao.cmdline.CreateColumnFamilies -a 10.173.29.185,10.174.49.107,10.174.97.35 -c cf$1 -g $1 -t trace$1 -o createdCF.out

    if [ -z "$3" ]
    then
        java com.apixio.coordinator.SubmitWorkCmd -o $1 -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys -b $1_apoMigration orgId=$1 newHosts=10.173.29.185,10.174.49.107,10.174.97.35
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

            if [ "$count" = "$3" ]
            then
                count=0

                echo "[SUBMISSION] count: $filenumber..."
                java com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys/sub-$filenumber -b $1_apoMigration_$filenumber orgId=$1 newHosts=10.173.29.185,10.174.49.107,10.174.97.35
            fi
        done
        if [ "$count" != "0" ]
        then
            echo "[SUBMISSION] count: $filenumber..."
            java com.apixio.coordinator.SubmitWorkCmd -o $1_migration -p 8 -i /user/apxqueue/apoMigrationInput -g apoMigration -l cf$1_partKeys/sub-$filenumber -b $1_apoMigration_$filenumber orgId=$1 newHosts=10.173.29.185,10.174.49.107,10.174.97.35
        fi
    fi
fi
