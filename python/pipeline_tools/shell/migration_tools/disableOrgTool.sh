#!/bin/sh
#
# lschneider

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]
then
echo "
======== Usage ========
enable <orgId>
enable all
enable lowPriority
enable highPriority

disable <orgId>
disable all
disable lowPriority
disable highPriority

initialize

list (default)
"
exit
fi

. /usr/lib/apx-coordinator/bin/setcp

ALL="10000230 10000232 10000235 10000236 10000237 10000250 10000253 10000259 10000262 10000263 10000264 10000265 10000270 10000278 10000283 10000284 10000285 10000286 10000287 10000288"
LOWPRI="10000230 10000235 10000236 10000237 10000253 10000259 10000264 10000265 10000270 10000278 10000283 10000284 10000285 10000286 10000287 10000288"
HIGHPRI="10000232 10000250 10000262 10000263"

if [ "$1" = "enable" ]
then
    if [ "$2" = "all" ]
    then
        for org in $ALL
        do
            $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --enable $org
        done
    elif [ "$2" = "lowPriority" ]
    then
        for org in $LOWPRI
        do
            $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --enable $org
        done
    elif [ "$2" = "highPriority" ]
    then
        for org in $HIGHPRI
        do
            $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --enable $org
        done
    else
        $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --enable "$2"
    fi
elif [ "$1" = "disable" ]
then
    if [ "$2" = "all" ]
    then
        for org in $ALL
        do
            $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --disable $org
        done
    elif [ "$2" = "lowPriority" ]
    then
        for org in $LOWPRI
        do
            $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --disable $org
        done
    elif [ "$2" = "highPriority" ]
    then
        for org in $HIGHPRI
        do
            $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --disable $org
        done
    else
        $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --disable "$2"
    fi
elif [ "$1" = "initialize" ]
then
    $JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --set "10000230=5 10000232=5 10000235=5 10000236=5 10000237=5 10000250=5 10000253=5 10000259=5 10000262=5 10000263=5 10000264=5 10000265=5 10000270=5 10000278=5 10000283=7 10000284=7 10000285=5 10000286=7 10000287=5 10000288=5"
fi

$JAVAEXEC com.apixio.coordinator.cmdline.OrgConfigTool --listall
