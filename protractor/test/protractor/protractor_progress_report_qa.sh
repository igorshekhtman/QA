#!/bin/sh
#
# Author:  Igor Shekhtman - 04-27-2015
#
# Purpose: To work in conjunction with Protractor tests, make calls to execute specific
#          tests and/or test suites, archive test results, backup test results and 
#          append new line to the test results .txt file if one does not already exist for
#          the ability to view test results through Apixio Reports Portal:
#          https://reports.apixio.com/html/progress_regression_reports_staging.html
#
#

echo "Protractor Progress Report Test Started ..." 

epoch_date1=$(date +%s)
epoch_date2=${epoch_date1:0:6}
day=$(date +%d)
month=$(date +%m)
monthname=$(date +%B) 
year=$(date +%Y)
report_line="PR Regression Staging Report - $monthname $day, $year\treports/staging/progressreport/$year/$month/$day.html\n"
part_report_line="reports/staging/progressreport/$year/$month/$day.html"
report_txt_folder="/usr/lib/apx-reporting/assets/"
report_txt_fname="progress_regression_reports_staging.txt"
report_folder="/usr/lib/apx-reporting/assets/reports/staging/progressreport/$year/$month"
backup_folder="/mnt/reports/staging/progressreport/$year/$month"
grep_string="$part_report_line $report_txt_folder$report_txt_fname"

#exit 0

# set DISPLAY
export DISPLAY=:1

# run specific set of Protractor Tests
protractor protractor.config.firefox.mocha.js

# backup archive tests folder
cp -avr $report_folder $backup_folder

# append new report line if one does not already exist
if grep $grep_string; then
   echo "report already exists, skipping append new line"
else
   echo "appending new line to $report_txt_fname"
   echo -n -e "$report_line" >> $report_txt_folder$report_txt_fname
fi

echo "Protractor Progress Report Test Completed..."
