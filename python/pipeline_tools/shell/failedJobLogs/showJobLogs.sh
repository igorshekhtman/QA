#!/bin/bash

hosts="10.196.89.152 10.198.10.241 10.198.10.249 10.196.47.205 10.196.50.151 10.198.10.216 10.197.58.250 10.196.80.54 10.197.17.172"
jobid=$1

mkdir $jobid

for h in $hosts; do
    mkdir $jobid/$h
    echo "Copying files from:$h:/var/log/hadoop/mapred/userlogs/$jobid/"
    scp -i /home/share/keys/staging.pem -r root@$h:/var/log/hadoop/mapred/userlogs/$jobid/attempt_*/ $jobid/$h/
done

#grep "org.apache.hadoop.mapred.Child: Error running child" /mnt/home/apxqueue/$jobid/*/*/syslog
