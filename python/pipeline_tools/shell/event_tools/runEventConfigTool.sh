#!/bin/sh
#
#nkrishna

# apixio-datasource jar AND lib, extractor.properties, apixio-security.properties must be in the same folder as this script

echo "
redisHost, hdfsDir, prefix, propertyName arguments are provided in this script.
Please edit script to change the values of the above arguments
"
# hadoop access:
_h=/etc/hadoop

# note that hadoop has a copy of log4j.properties so when we set up logging
# we have to change the order here to pick up our copy first:
cp=$(echo              \
  $_h/hadoop-core*.jar \
  $_h                  \
  $_h/conf             \
  | sed 's/ /:/g')

CLASSPATH=$cp
export CLASSPATH

java -cp apixio-datasource-`version`.jar:lib/*:$CLASSPATH com.apixio.dao.cmdline.EventConfigTool --redisHost localhost --hdfsDir /user/apxqueue/events --prefix Staging --propertyName apxEventsProperties $@

# staging is now different jar&classpath than prod
# java -cp apixio-dao-2.0.0-SNAPSHOT.jar:lib/*:$CLASSPATH com.apixio.dao.cmdline.eventtool.EventConfigTool --redisHost redis-stg.apixio.com --hdfsDir /user/apxqueue/events --prefix Staging --propertyName scienceProperties $@
