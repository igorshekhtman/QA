#!/bin/sh
#
# Copyright 2015 Apixio
#
# Author: Igor Shekhtman
# Date:   03/12/2015
#
#

echo "Starting Nose Test..."

epoch_date1=$(date +%s)
epoch_date2=${epoch_date1:0:6}

year=$(date +%Y)
month=$(date +%m)
day=$(date +%d)
echo year=$year month=$month day=$day

#echo $1

if [ -z "$1" ]
  then
    echo "No specific test selected, terminating ..."
    exit 1
  else
  	specific_test=$1
    echo "Running $test_number test(s) ..." 
fi

#exit 0



echo "Creating folders if do not already exist..."
# work folder
mkdir -p /usr/lib/apx-reporting/assets/reports/staging/hccregression/$year/$month
# backup folder
mkdir -p /mnt/reports/staging/hccregression/$year/$month
echo "Completed creating new folders..."

tests_folder="/mnt/hcc_test_automation/hcc_front_end/"


if [ "$specific_test" = "all" ];
	then
		nosetests --with-xunit --xunit-file=/usr/lib/apx-reporting/assets/reports/staging/hccregression/$year/$month/$day.xml --where=$tests_folder	--all-modules
	else
		nosetests --with-xunit --xunit-file=/usr/lib/apx-reporting/assets/reports/staging/hccregression/$year/$month/$day.xml --tests=/mnt/hcc_test_automation/hcc_front_end/$specific_test.py	
fi;	

xsltproc style.xsl /usr/lib/apx-reporting/assets/reports/staging/hccregression/$year/$month/$day.xml > /usr/lib/apx-reporting/assets/reports/staging/hccregression/$year/$month/$day.html

# backup to archive folder
cp -avr /usr/lib/apx-reporting/assets/reports/staging/hccregression/$year/$month/$day.* /mnt/reports/staging/hccregression/$year/$month/

# Check if the report line item already exists in txt file or not
# Append if does not, skip if does
directory="/usr/lib/apx-reporting/assets/"
file="hcc_regression_reports_staging.txt"
lineitem="reports/staging/hccregression/$year/$month/$day.html"
#echo directory=$directory
#echo file=$file
#echo item=$lineitem

cd $directory  
if grep -q "$lineitem" "$file";
then
echo "Report entry already exists, skipping write ..."
else
echo "Appending new report entry line to the $File ..."
echo -n -e "HCC Regression Staging Report - "$(date +"%B %d, %Y")"\treports/staging/hccregression/$year/$month/$day.html\n" >> /usr/lib/apx-reporting/assets/hcc_regression_reports_staging.txt
fi

echo "Nose Test Completed..."
