#!/bin/sh
#
#  lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
echo "
========= Usage =========
40
60
100

"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

if [ "$1" = "40" ]
then

    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=1,0 ocr=20,0 persist=1,0 parser=1,0 dataCheckAndRecovery=1,0 loadAPO=20,0 migrateAPO=20,0 qaMigrateAPO=20,0"

elif [ "$1" = "60" ]
then

    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=0,0 ocr=20,10 persist=0,0 parser=0,0 dataCheckAndRecovery=0,0 loadAPO=20,10 migrateAPO=10,0 qaMigrateAPO=10,0"

elif [ "$1" = "100" ]
then

    java com.apixio.coordinator.cmdline.ActivityConfigTool --set-slot-alloc "trace=0,0 ocr=40,10 persist=0,0 parser=0,0 dataCheckAndRecovery=0,0 loadAPO=30,0 migrateAPO=15,0 qaMigrateAPO=15,0"

fi

java com.apixio.coordinator.cmdline.ActivityConfigTool --list