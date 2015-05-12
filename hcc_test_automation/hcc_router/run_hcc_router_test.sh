#!/bin/sh
#
# Copyright 2015 Apixio
#
# Author: Igor Shekhtman
# Email:  ishekhtman@apixio.com
# Date:   05/12/2015
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
mkdir -p /usr/lib/apx-reporting/assets/reports/staging/hccrouterregression/$year/$month
# backup folder
mkdir -p /mnt/reports/staging/hccrouterregression/$year/$month
echo "Completed creating new folders..."


# ----- ./Configuration.sh stash
ssh -i ~/secrets/staging_new_hcc.pem root@hcc-opprouter-stg.apixio.com 'cd /root/Reset; pwd; sh Configurations.sh stash'


# exit 0


# This command will pull the configuration of the sorting hat and copy it to a subfolder called “normal.”  This configuration will be used to restore the hat to its “normal” configuration after a round of tests.  (The files that are copied there are the outbound rules, the default data sets and the configuration yml.)
#
# To set the sorting hat to test mode, type:

# ----- ./Configuration.sh test
ssh -i ~/secrets/staging_new_hcc.pem root@hcc-opprouter-stg.apixio.com 'cd /root/Reset; pwd; sh Configurations.sh test'


# This command will stop the service, copy the test versions of configuration files to standard locations, inject a standard SQL file to the staging hat’s MySQL server, and restart the sorting hat.  The SQL file in the folder will create a database called “Router_Test” and populate it from scratch.  The sorting hat server configuration will be switched to point at this database so that the main Router database won’t be contaminated with test data all the time.  Multiple invocations of this command will reset the sorting hat database to a pristine test state each time.



tests_folder="/mnt/hcc_test_automation/hcc_router/"

# Execute Test(s)

if [ "$specific_test" = "all" ];
	then
		nosetests --with-xunit --xunit-file=/usr/lib/apx-reporting/assets/reports/staging/hccrouterregression/$year/$month/$day.xml --where=$tests_folder	--all-modules
	else
		nosetests --with-xunit --xunit-file=/usr/lib/apx-reporting/assets/reports/staging/hccrouterregression/$year/$month/$day.xml --tests=/mnt/hcc_test_automation/hcc_router/$specific_test.py	
fi;	


# When testing is complete, one may type:

# ------ ./Configuration.sh normal
#ssh -i ~/secrets/staging_new_hcc.pem root@hcc-opprouter-stg.apixio.com "cd Reset; sh Configuration.sh normal"
ssh -i ~/secrets/staging_new_hcc.pem root@hcc-opprouter-stg.apixio.com 'cd /root/Reset; pwd; sh Configurations.sh normal'

# This command will stop the service, copy the normal versions of configuration files to standard locations and restart the service.  This will reset the sorting hat to the configuration just after the last stash command.  Note that it is a good idea to perform a stash before any testing in order pick up any changes to injected outbound rules.





xsltproc style.xsl /usr/lib/apx-reporting/assets/reports/staging/hccrouterregression/$year/$month/$day.xml > /usr/lib/apx-reporting/assets/reports/staging/hccrouterregression/$year/$month/$day.html

# backup to archive folder
cp -avr /usr/lib/apx-reporting/assets/reports/staging/hccrouterregression/$year/$month/$day.* /mnt/reports/staging/hccrouterregression/$year/$month/

# Check if the report line item already exists in txt file or not
# Append if does not, skip if does
directory="/usr/lib/apx-reporting/assets/"
file="hcc_hccrouterregression_reports_staging.txt"
lineitem="reports/staging/hccrouterregression/$year/$month/$day.html"
#echo directory=$directory
#echo file=$file
#echo item=$lineitem

cd $directory  
if grep -q "$lineitem" "$file";
then
echo "Report entry already exists, skipping write ..."
else
echo "Appending new report entry line to the $File ..."
echo -n -e "HCC Regression Staging Report - "$(date +"%B %d, %Y")"\treports/staging/hccrouterregression/$year/$month/$day.html\n" >> /usr/lib/apx-reporting/assets/hcc_hccrouterregression_reports_staging.txt
fi

echo "Nose Test Completed..."
