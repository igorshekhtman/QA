#!/bin/sh
#
# Copyright 2011-2014 eBusiness Information, Groupe Excilys (www.ebusinessinformation.fr)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

echo "Protractor Progress Report Test Started ..." 

epoch_date1=$(date +%s)
epoch_date2=${epoch_date1:0:6}
day=$(date +%d)
month=$(date +%m) 
year=$(date +%Y)

#echo $day, $month, $year
#echo $epoch_date1
#echo $epoch_date2

#exit 0

# set DISPLAY
export DISPLAY=:1

# run Protractor Tests
protractor protractor.config.firefox.js

# this is where reports are stored
# '/usr/lib/apx-reporting/assets/reports/staging/progressreport/'+year+'/'+month+'/'
# this is reports backup folder
# '/mnt/reports/staging/progressreport/'+year+'/'+month+'/'


# backup archive folder
cp -avr /usr/lib/apx-reporting/assets/reports/staging/progressreport/$year/$month /mnt/reports/staging/progressreport/$year/$month



# original archive folder
#remove cp -avr /mnt/gatling_2_0_0_RC5/results/dataorchestratorsimulation-$epoch_date2* /usr/lib/apx-reporting/assets/reports/staging/do
#remove echo -n -e "DO Performance Report (staging) - "$(date +"%B %d, %Y")"\treports/staging/do/" >> /usr/lib/apx-reporting/assets/do_reports.txt
#remove temp=$(ls -d /mnt/gatling_2_0_0_RC5/results/dataorchestratorsimulation-$epoch_date2*/ | cut -f5 -d'/')
#remove echo -n "$temp" >> /usr/lib/apx-reporting/assets/do_reports.txt
#remove echo "/index.html" >> /usr/lib/apx-reporting/assets/do_reports.txt

echo "Protractor Progress Report Test Completed..."
