#
# Short Python script to demonstrate connecting to Hive
# Run: python2.6 new_hive_test.py
#============================= AUTHOR and EDIT HISTORY ====================================================
# Author: Igor Shekhtman
# Date: 08/08/2014 - Initial version of the script written and tested
#
# Updated by: Austin Rogers
# Date: 08/19/2014 - 
# 1.) Added baseline success and failure functions.  
# 2.) Corrected Hive queries to take into account provisions for DAYSBACK falling into previous month
# 3.) Adjusted new data representation for DAYSBACK falling into previous month
#
# Updated by: Igor Shekhtman
# Date: 08/20/2014 - Converted all references including Hive queries from Jobs to Docs - Igor
#
#==========================================================================================================
#============================= JSON TEMPLATE ==============================================================
#==========================================================================================================
#{
#    "charttitle": "Events per Org",
#    "charttype": "line",
#    "dotColor": "black",
#    "dotSize": "4",
#    "updateInterval": "5",
#    "legendtitle": {
#        "1": "Legend"
#    },
#    "legenddata": {
#        "1": "Events",
#        "2": "other Events"
#       
#    },
#    "legendcolors": {
#        "1": "red",
#        "2": "lime"
#        
#    },
#    "xaxistitle": "Number of Orgs",
#	"baselinedata": {
#		"1": [
#            "3872",
#            "2871",
#            "9307",
#            "1754",
#            "2986",
#            "7304",
#			"4923"
#        ],
#		"2": [
#			"2823",
#			"3278",
#			"6251",
#			"9476",
#			"8362",
#			"8372",
#			"2371"
#			]
#		},
#    "xaxisdata": {
#        "1": [
#            "Sun",
#            "Mon",
#            "Tue",
#            "Wed",
#            "Thur",
#            "Fri",
#			"Sat"
#        ]
#    },
#    "yaxistitle": "Number of Events",
#    "yaxisdata": {
#        "1": [
#            "9910",
#            "1200",
#            "2135",
#            "1134",
#            "7353",
#            "5012",
#			"8376"
#        ],
#        "2": [
#            "1111",
#            "1234",
#            "3038",
#            "9821",
#            "104",
#            "1937",
#			"2615"
#        ]
#        
#        
#    }
#}
#
#===========================================================================================
#

import pyhs2
import os
import json
from time import gmtime, strftime, localtime
from datetime import date, timedelta as td
import calendar
import time

DAYSBACK = 7
ST_DAY = str(int(strftime("%d", gmtime()))-DAYSBACK) # Starting day
EN_DAY = strftime("%d", gmtime()) # Ending day or today
MONTH = strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR = strftime("%Y", gmtime())
DATERANGE = ""
CURDAY = int(strftime("%d", gmtime()))
CURMONTH = int(strftime("%m", gmtime()))
DAY = strftime("%d", gmtime())
CURYEAR = strftime("%Y", gmtime())
START_DATE = None
END_DATE = None
START_DATE_BASE = None
END_DATE_BASE = None

#LOG_TYPE = "24"
LOG_TYPE = "epoch"

#Values can be "Staging" or "Production"
#ENVIRONMENT = "Production" 
ENVIRONMENT = "Staging"



def identifyReportDayandMonth():
#======== obtain day and month for previous from current day and month ==========================================================
	global DAYSBACK, DATERANGE, CURDAY, CURMONTH, DAY, MONTH, YEAR, CURYEAR, END_DATE, START_DATE, END_DATE_BASE, START_DATE_BASE
	global ST_DAY, ST_MONTH, ST_MONTHS,ST_YEAR, EN_DAY, EN_MONTH, EN_MONTHS, EN_YEAR
	
	MONTH_FMN=calendar.month_name[int(CURMONTH)]
	
	END_DATE = date(int(CURYEAR), int(CURMONTH), int(CURDAY))
	START_DATE = END_DATE - td(days = DAYSBACK)
	END_DATE_BASE = END_DATE - td(days =7)
	START_DATE_BASE = START_DATE - td(days =7)
	
	EN_DAY = END_DATE.day
	EN_MONTH = END_DATE.month
	EN_MONTHS = MONTH_FMN
	EN_YEAR = END_DATE.year
	
	print ("Day and month values before %s day(s) back adjustment ...") % (DAYSBACK)
	print ("DAY: %s, MONTH: %s, YEAR: %s, SPELLED MONTH: %s\n") % (CURDAY, CURMONTH, CURYEAR, EN_MONTHS)
	
	
	MONTH = CURMONTH
	MONTH_FMN=calendar.month_name[int(MONTH)]
	ST_DAY = START_DATE.day
	ST_MONTH = START_DATE.month
	ST_MONTHS = calendar.month_name[int(ST_MONTH)]
	ST_YEAR = START_DATE.year
	
	print ("Day and month values after %s day(s) back adjustment ...") % (DAYSBACK)
	print ("DAY: %s, MONTH: %s, YEAR: %s, SPELLED MONTH: %s\n") % (START_DATE.day, START_DATE.month, START_DATE.year, ST_MONTHS)
	#time.sleep(45)

def initializeGlobalArrays():
	global DOCS_SUCCEEDED, DOCS_FAILED, B_DOCS_SUCCEEDED, B_DOCS_FAILED
	DOCS_SUCCEEDED=[0 for i in range(DAYSBACK+1)]
	for i in range(DAYSBACK+1):
		DOCS_SUCCEEDED[i] = 0
	DOCS_FAILED=[0 for i in range(DAYSBACK+1)]
	for i in range(DAYSBACK+1):
		DOCS_FAILED[i] = 0
	B_DOCS_SUCCEEDED=[0 for i in range(DAYSBACK+1)]
	for i in range(DAYSBACK+1):
		B_DOCS_SUCCEEDED[i] = 0
	B_DOCS_FAILED=[0 for i in range(DAYSBACK+1)]
	for i in range(DAYSBACK+1):
		B_DOCS_FAILED[i] = 0	

def calcXAxis():
	#global START_DATE, END_DATE
	dateList = []
	#d1 = date(int(ST_YEAR),int(ST_MONTH),int(ST_DAY))
	#d2 = date(int(EN_YEAR),int(EN_MONTH),int(EN_DAY))
	
	delta = END_DATE - START_DATE

	
	#use +1 to include today's date
	#for i in range(delta.days):
	for i in range(delta.days + 1):
		dateList.append(str(START_DATE + td(days=i))[5:])
	#print dateList
	return (dateList)
	#time.sleep(45)

			
	
def connectToHive():
	print ("Connecting to Hive ...\n")
	global cur, conn
 	conn = pyhs2.connect(host='10.196.47.205', \
		port=10000, authMechanism="PLAIN", \
		user='hive', password='', \
		database='default')
	cur = conn.cursor()
	print ("Connection to Hive established ...\n")

def setHiveParameters():
	print ("Assigning Hive parameters ...\n")
	cur.execute("""set hive.exec.dynamic.partition=true""")
	cur.execute("""set hive.exec.dynamic.partition.mode=nonstrict""")
	cur.execute("""set mapred.reduce.tasks=16""")
	cur.execute("""set mapred.job.queue.name=default""")
	#cur.execute("""set mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	print ("Hive parameters assigned ...\n")	

def selectLogFile(environment, component):
	global LOG_TYPE
	if component == "indexer":
		logfilename="indexer_manifest_epoch"
	elif component == "docreceiver":
		logfilename=environment.lower()+"_logs_docreceiver_"+LOG_TYPE
	elif component == "coordinator":
		logfilename=environment.lower()+"_logs_coordinator_"+LOG_TYPE
	elif component == "parser":	
		logfilename=environment.lower()+"_logs_parserjob_"+LOG_TYPE
	elif component == "ocr":	
		logfilename=environment.lower()+"_logs_ocrjob_"+LOG_TYPE
	elif component == "persist":	
		logfilename=environment.lower()+"_logs_persistjob_"+LOG_TYPE
	elif component == "event":	
		logfilename=environment.lower()+"_logs_eventJob_"+LOG_TYPE
	return (logfilename)

def adjustArray(input_array, notBase):
	global DAYSBACK, ST_DAY

	output_array = []
	output_array=[0 for i in range(DAYSBACK)]
	for i in range(DAYSBACK):
		
		if notBase:
			tempD = START_DATE + td(days = (i))
			output_array[i] = [0, str(tempD.year), str(tempD.month), str(tempD.day )]
		else:
			tempD2 = START_DATE_BASE + td(days = (i))
			output_array[i] = [0, str(tempD2.year), str(tempD2.month), str(tempD2.day )]
	for i in range(DAYSBACK):
		for j in input_array:
			tempD3 = date(int(output_array[i][1]), int(output_array[i][2]), int(output_array[i][3]))
			if date(int(j[1]),int(j[2]),int(j[3])) == tempD3:
				#output_array[i] = [j[0], j[1], j[2], j[3]]	 
				output_array[i][0] = j[0]
	return (output_array)

	
def runBaseDocFailed(environment):
	global B_DOCS_FAILED
	LOGFILE = selectLogFile(environment,"event")
	
	#baseDateStart2 = date(int(ST_YEAR),int(ST_MONTH),int(ST_DAY))
	#baseDateEnd2 = date(int(EN_YEAR),int(EN_MONTH),int(EN_DAY))
	
	#baseDateStart2 = START_DATE - td(days =7)
	#baseDateEnd2 = END_DATE - td(days = 7)
	
	print ("Running %s Hive Query to extract failed jobs baseline data, please wait ...\n") % (environment)

			
	cur.execute("""SELECT COUNT(DISTINCT get_json_object(line, '$.documentUUID')) as total_docs, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		and \
		get_json_object(line, '$.level') ='EVENT' and \
		get_json_object(line, '$.status') = 'error' \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day), (END_DATE_BASE.year * 10000 + END_DATE_BASE.month * 100 + END_DATE_BASE.day)))
	
	print (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day)
	print ("Ended running %s Hive Query to extract baseline failed docs ...\n")	 % (environment)
	result = cur.fetch()
	
	#print "OLD:"
	#print result
	new_result = adjustArray(result, False)
	#print "NEW:"
	#print new_result
	#time.sleep(45)	
	
	
	print ("Failed:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))	
	#print new_result
		B_DOCS_FAILED[ind] = int(i[0])
		ind = ind + 1
	
	
def runBaseDocSucceeded(environment):
	global B_DOCS_SUCCEEDED
	LOGFILE = selectLogFile(environment,"event")
	#baseDateStart = date(int(ST_YEAR),int(ST_MONTH),int(ST_DAY))
	#baseDateEnd = date(int(EN_YEAR),int(EN_MONTH),int(EN_DAY))
	
	#baseDateStart = START_DATE - td(days =7)
	#baseDateEnd = END_DATE - td(days = 7)
	print ("Running %s Hive Query to extract successful docs baseline data, please wait ...\n") % (environment)
		

	
	cur.execute("""SELECT COUNT(DISTINCT get_json_object(line, '$.documentUUID')) as total_docs, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		and \
		get_json_object(line, '$.level') ='EVENT' and \
		get_json_object(line, '$.status') = 'success' \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day), (END_DATE_BASE.year * 10000 + END_DATE_BASE.month * 100 + END_DATE_BASE.day)))
	
	
	print ("Ended running %s Hive Query to extract baseline successful docs ...\n")	 % (environment)
			
	#for ind in range (0,0):
	result = cur.fetch()
	new_result = adjustArray(result, False)
	#time.sleep(45)	
	#print result
	print ("Success:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
		#print i
		#print cur.fetch()
		B_DOCS_SUCCEEDED[ind] = int(i[0])
		ind = ind + 1	
	
	
	
def runDocSucceeded(environment):
	global DOCS_SUCCEEDED
	LOGFILE = selectLogFile(environment,"event")
		
	print ("Running %s Hive Query to extract successful docs, please wait ...\n") % (environment)
		
		
	cur.execute("""SELECT COUNT(DISTINCT get_json_object(line, '$.documentUUID')) as total_docs, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		and \
		get_json_object(line, '$.level') ='EVENT' and \
		get_json_object(line, '$.status') = 'success' \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE.year * 10000 + START_DATE.month * 100 + START_DATE.day), (END_DATE.year * 10000 + END_DATE.month * 100 + END_DATE.day)))
	
	print ("Ended running %s Hive Query to extract successful docs ...\n")	 % (environment)
			
	#for ind in range (0,0):
	result = cur.fetch()
	#time.sleep(45)	
	#print result
	print ("Success:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	new_result = adjustArray(result, True)
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
		#print i
		#print cur.fetch()
		DOCS_SUCCEEDED[ind] = int(i[0])
		ind = ind + 1	

def runDocFailed(environment):
	global DOCS_FAILED
	LOGFILE = selectLogFile(environment,"event")
	
	print ("Running %s Hive Query to extract failed docs, please wait ...\n") % (environment)
	
	
	
	cur.execute("""SELECT COUNT(DISTINCT get_json_object(line, '$.documentUUID')) as total_docs, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		and \
		get_json_object(line, '$.level') ='EVENT' and \
		get_json_object(line, '$.status') = 'error' \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE.year * 10000 + START_DATE.month * 100 + START_DATE.day), (END_DATE.year * 10000 + END_DATE.month * 100 + END_DATE.day)))
	
	
	print ("Ended running %s Hive Query to extract failed docs ...\n")	 % (environment)
	result = cur.fetch()
	
	#print "OLD:"
	#print result
	new_result = adjustArray(result, True)
	#print "NEW:"
	#print new_result
	#time.sleep(45)	
	
	
	print ("Failed:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))	
	#print new_result
		DOCS_FAILED[ind] = int(i[0])
		ind = ind + 1
	
def runQueries(environment):
	global ST_DAY, EN_DAY, MONTH, YEAR, DOCS_SUCCEEDED, ORGID, DAYSOFMONTH, DOCS_FAILED, B_DOCS_FAILED, B_DOCS_SUCCEEDED
	global ST_DAY, ST_MONTH, ST_MONTHS,ST_YEAR, EN_DAY, EN_MONTH, EN_MONTHS, EN_YEAR
	
	runDocSucceeded(environment)
	runDocFailed(environment)	
	runBaseDocSucceeded(environment)
	runBaseDocFailed(environment)
	#time.sleep(45)	

	
def closeHiveConnection():
	print ("\nClosing Hive connection ...\n")
	global cur, conn
	cur.close()
	conn.close()
	print ("Completed closing Hive connection ...\n")

	
def appendData():
	global DATA, ORGID, ENVIRONMENT, MONTH_FMN#, DOCS_FAILED, DOCS_SUCCEEDED, B_DOCS_FAILED, B_DOCS_SUCCEEDED
	global ST_DAY, ST_MONTH, ST_MONTHS,ST_YEAR, EN_DAY, EN_MONTH, EN_MONTHS, EN_YEAR
	
	JSON_DATA_FILENAME ="/var/www/html/json/"+ENVIRONMENT.lower()+".successful.docs.through.event.extraction.json" 
	print ("Start writing json data ...\n")

	new_json_data = { \
		"charttitle": ""+ENVIRONMENT.lower()+".successful.docs.through.event.extraction", \
		"charttype": "line", \
		"dotColor": "black", \
		"dotSize": "4", \
		"updateInterval": "5", \
		"legendtitle": {"1": "Legend"}, \
		"legenddata": { "1": "Succeeded Docs", "2": "Failed Docs" }, \
		"legendcolors": { "1": "lime", "2": "red" }, \
		"xaxistitle": str(DAYSBACK+1)+" Days", \
		"baselinedata": { \
		"1": B_DOCS_SUCCEEDED, \
		"2": B_DOCS_FAILED}, \
		"xaxisdata": { \
		"1": calcXAxis()}, \
		"yaxistitle": "# of Docs",
		"yaxisdata": { \
		"1": DOCS_SUCCEEDED, \
        "2": DOCS_FAILED} \
		}	
	
	
	with open(JSON_DATA_FILENAME) as f:
		json_data = json.load(f)
	
	json_data.update(new_json_data)
	with open(JSON_DATA_FILENAME, 'w') as f:
		json.dump(json_data, f)	
	print ("End writing json data ...\n")	

#================ START OF MAIN BODY ======================

identifyReportDayandMonth()

initializeGlobalArrays()

connectToHive()

setHiveParameters()

runQueries(ENVIRONMENT)

closeHiveConnection()

appendData()

#================ END OF MAIN BODY ========================

