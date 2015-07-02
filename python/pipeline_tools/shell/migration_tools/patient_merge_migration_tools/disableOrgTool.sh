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

ALL="10000232 10000235 10000236 10000237 10000253 10000259 10000262 10000263 10000278 10000279 10000281 10000282 10000283 10000284 10000285 10000286 10000288 10000289 10000290 10000291 10000292 10000293 10000294 10000295 10000296 10000297 10000298 10000299 10000300 10000301 10000302 10000303 10000304 10000305 10000306 10000307 10000308 10000309 10000310 10000311 10000312 10000313 10000314 10000315 10000316 10000317 10000318 10000319 10000320"
LOWPRI=""
HIGHPRI=""

if [ "$1" = "enable" ]
then
    if [ "$2" = "all" ]
    then
        for org in $ALL
        do
            java com.apixio.coordinator.cmdline.OrgConfigTool --enable $org
        done
    elif [ "$2" = "lowPriority" ]
    then
        for org in $LOWPRI
        do
            java com.apixio.coordinator.cmdline.OrgConfigTool --enable $org
        done
    elif [ "$2" = "highPriority" ]
    then
        for org in $HIGHPRI
        do
            java com.apixio.coordinator.cmdline.OrgConfigTool --enable $org
        done
    else
        java com.apixio.coordinator.cmdline.OrgConfigTool --enable "$2"
    fi
elif [ "$1" = "disable" ]
then
    if [ "$2" = "all" ]
    then
        for org in $ALL
        do
            java com.apixio.coordinator.cmdline.OrgConfigTool --disable $org
        done
    elif [ "$2" = "lowPriority" ]
    then
        for org in $LOWPRI
        do
            java com.apixio.coordinator.cmdline.OrgConfigTool --disable $org
        done
    elif [ "$2" = "highPriority" ]
    then
        for org in $HIGHPRI
        do
            java com.apixio.coordinator.cmdline.OrgConfigTool --disable $org
        done
    else
        java com.apixio.coordinator.cmdline.OrgConfigTool --disable "$2"
    fi
elif [ "$1" = "initialize" ]
then
    java com.apixio.coordinator.cmdline.OrgConfigTool --set "10000232=5 10000235=5 10000236=5 10000237=5 10000253=5 10000259=5 10000262=5 10000263=5 10000278=7 10000279=8 10000281=5 10000282=5 10000283=7 10000284=7 10000285=5 10000286=7 10000288=5 10000289=5 10000290=7 10000291=5 10000292=5 10000293=5 10000294=9 10000295=9 10000296=9 10000297=9 10000298=9 10000299=9 10000300=9 10000301=5 10000302=5 10000303=5 10000304=5 10000305=5 10000306=5 10000307=5 10000308=5 10000309=5 10000310=5 10000311=5 10000312=5 10000313=5 10000314=5 10000315=5 10000316=5 10000317=5 10000318=9 10000319=5 10000320=5"
fi

java com.apixio.coordinator.cmdline.OrgConfigTool --listall
