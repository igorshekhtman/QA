#!/bin/sh
#
#lschneider

# apixio-datasource jar AND lib AND apixio-security.properties must be in the same folder as this script

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]
then
echo "
Arguments: 1={"staging","production"}, 2=orgId, 3=keysPerFile(for unlimited file size use 0)
"
exit
fi

echo "
Getting partial patient keys for org $2 from $1:
"

if [ "$1" = "staging" ]
then

java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.ListKeys --orgId $2 --hosts 10.199.22.32 --numKeysPerFile $3 --output $2_partKeys --keyFilter partialPatientKey --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518151802496110413072V01xHZ27yWvIJnuc3WFLQfexFA==
#java -cp apixio-datasource-primaryExternalId.jar com.apixio.dao.cmdline.ListKeys --orgId $2 --hosts 10.199.22.32 --numKeysPerFile $3 --output $2_partKeys --keyFilter partialPatientKey --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd dVyGpwY3

elif [ "$1" = "production" ]
then

java -cp apixio-datasource-1.7.1.jar com.apixio.dao.cmdline.ListKeys --orgId $2 --hosts 10.174.97.35 --numKeysPerFile $3 --output $2_partKeys --keyFilter partialPatientKey --mysqlHost mysql.stg1.apixio.net --mysqlUser apxDB --mysqlPwd 2518140788360689940544V01x1iehnaJs6qqoIWNMVa6sog==

fi
