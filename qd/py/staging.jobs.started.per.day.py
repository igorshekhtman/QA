# short Python script to demonstrate connecting to Hive
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
#       "baselinedata": {
#               "1": [
#            "3872",
#            "2871",
#            "9307",
#            "1754",
#            "2986",
#            "7304",
#                       "4923"
#        ],
#               "2": [
#                       "2823",
#                       "3278",
#                       "6251",
#                       "9476",
#                       "8362",
#                       "8372",
#                       "2371"
#                       ]
#               },
#    "xaxisdata": {
#        "1": [
#            "Sun",
#            "Mon",
#            "Tue",
#            "Wed",
#            "Thur",
#            "Fri",
#                       "Sat"
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
#                       "8376"
#        ],
#        "2": [
#            "1111",
#            "1234",
#            "3038",
#            "9821",
#            "104",
#            "1937",
#                       "2615"
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
CURDAY = int(strftime("%d", gmtime()))
CURMONTH = int(strftime("%m", gmtime()))
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
        global DAYSBACK,  CURDAY, CURMONTH, CURYEAR, END_DATE, START_DATE, END_DATE_BASE, START_DATE_BASE

        END_DATE = date(int(CURYEAR), int(CURMONTH), int(CURDAY))
        START_DATE = END_DATE - td(days = DAYSBACK)
        END_DATE_BASE = END_DATE - td(days =7)
        START_DATE_BASE = START_DATE - td(days =7)

        EN_MONTHS = calendar.month_name[int(END_DATE.month)]
        print ("Day and month values before %s day(s) back adjustment ...") % (DAYSBACK)
        print ("DAY: %s, MONTH: %s, YEAR: %s, SPELLED MONTH: %s\n") % (CURDAY, CURMONTH, CURYEAR, EN_MONTHS)

        ST_MONTHS = calendar.month_name[int(START_DATE.month)]
        print ("Day and month values after %s day(s) back adjustment ...") % (DAYSBACK)
        print ("DAY: %s, MONTH: %s, YEAR: %s, SPELLED MONTH: %s\n") % (START_DATE.day, START_DATE.month, START_DATE.year, ST_MONTHS)


def initializeGlobalArrays():
        global JOBS_SUCCEEDED, JOBS_FAILED, B_JOBS_SUCCEEDED, B_JOBS_FAILED
        JOBS_SUCCEEDED=[0 for i in range(DAYSBACK)]
        for i in range(DAYSBACK):
                JOBS_SUCCEEDED[i] = 0
        JOBS_FAILED=[0 for i in range(DAYSBACK)]
        for i in range(DAYSBACK):
                JOBS_FAILED[i] = 0
        B_JOBS_SUCCEEDED=[0 for i in range(DAYSBACK)]
        for i in range(DAYSBACK):
                B_JOBS_SUCCEEDED[i] = 0
        B_JOBS_FAILED=[0 for i in range(DAYSBACK)]
        for i in range(DAYSBACK):
                B_JOBS_FAILED[i] = 0


def calcXAxis():
        dateList = []
        delta = END_DATE - START_DATE
        #use +1 to include today's date
        for i in range(delta.days):
        #for i in range(delta.days + 1):
                dateList.append(str(START_DATE + td(days=(i+1)))[5:])
        return (dateList)


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
        output_array = []
        output_array=[0 for i in range(DAYSBACK)]
        for i in range( DAYSBACK):
                if notBase:
                        tempD = START_DATE + td(days = (i+1))
                        output_array[i] = [0, str(tempD.year), str(tempD.month), str(tempD.day )]
                else:
                        tempD2 = START_DATE_BASE + td(days = (i+1))
                        output_array[i] = [0, str(tempD2.year), str(tempD2.month), str(tempD2.day )]
        for i in range(DAYSBACK):
                for j in input_array:
                        tempD3 = date(int(output_array[i][1]), int(output_array[i][2]), int(output_array[i][3]))
                        if date(int(j[1]),int(j[2]),int(j[3])) == tempD3:
                                output_array[i][0] = j[0]
        return (output_array)


def runBaseJobFailed(environment):
	global B_JOBS_FAILED
	#LOGFILE = selectLogFile(environment,"coordinator")
	LOGFILE = "summary_coordinator_jobstart_staging"
	print ("Running %s Hive Query to extract failed jobs baseline data, please wait ...\n") % (environment)

	cur.execute("""SELECT COUNT(DISTINCT job_id) as count, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day), (END_DATE_BASE.year * 10000 + END_DATE_BASE.month * 100 + END_DATE_BASE.day)))

	print (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day)
	print ("Ended running %s Hive Query to extract baseline failed jobs ...\n")      % (environment)
	result = cur.fetch()
	new_result = adjustArray(result, False)
	print ("Failed:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
		B_JOBS_FAILED[ind] = int(i[0])
		ind = ind + 1


def runBaseJobSucceeded(environment):
	global B_JOBS_SUCCEEDED
	#LOGFILE = selectLogFile(environment,"coordinator")
	LOGFILE = "summary_coordinator_jobstart_staging"
	print ("Running %s Hive Query to extract successful jobs baseline data, please wait ...\n") % (environment)

	cur.execute("""SELECT COUNT(DISTINCT job_id) as count, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day), (END_DATE_BASE.year * 10000 + END_DATE_BASE.month * 100 + END_DATE_BASE.day)))

	print ("Ended running %s Hive Query to extract baseline successful jobs ...\n")  % (environment)
	result = cur.fetch()
	new_result = adjustArray(result, False)
	print ("Success:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
		B_JOBS_SUCCEEDED[ind] = int(i[0])
		ind = ind + 1


def runJobSucceeded(environment):
	global JOBS_SUCCEEDED
	#LOGFILE = selectLogFile(environment,"coordinator")
	LOGFILE = "summary_coordinator_jobstart_staging"
	print ("Running %s Hive Query to extract successful jobs, please wait ...\n") % (environment)

	cur.execute("""SELECT COUNT(DISTINCT job_id) as count, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE.year * 10000 + START_DATE.month * 100 + START_DATE.day), (END_DATE.year * 10000 + END_DATE.month * 100 + END_DATE.day)))

	print ("Ended running %s Hive Query to extract successful jobs ...\n")   % (environment)
	result = cur.fetch()
	print ("Success:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	new_result = adjustArray(result, True)
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
		JOBS_SUCCEEDED[ind] = int(i[0])
		ind = ind + 1


def runJobFailed(environment):
	global JOBS_FAILED
	#LOGFILE = selectLogFile(environment,"coordinator")
	LOGFILE = "summary_coordinator_jobstart_staging"
	print ("Running %s Hive Query to extract failed jobs, please wait ...\n") % (environment)

	cur.execute("""SELECT COUNT(DISTINCT job_id) as count, \
		year, month, day \
		FROM %s \
		WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
		GROUP BY year, month, day ORDER BY year, month, day ASC""" % (LOGFILE, (START_DATE.year * 10000 + START_DATE.month * 100 + START_DATE.day), (END_DATE.year * 10000 + END_DATE.month * 100 + END_DATE.day)))

	print ("Ended running %s Hive Query to extract failed jobs ...\n")       % (environment)
	result = cur.fetch()
	new_result = adjustArray(result, True)
	print ("Failed:\tYear:\t\tMonth:\t\tDay:")
	ind = 0
	for i in new_result:
		print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
		JOBS_FAILED[ind] = int(i[0])
		ind = ind + 1


def runQueries(environment):

        runJobSucceeded(environment)
        runJobFailed(environment)
        runBaseJobSucceeded(environment)
        runBaseJobFailed(environment)


def closeHiveConnection():
        print ("\nClosing Hive connection ...\n")
        global cur, conn
        cur.close()
        conn.close()
        print ("Completed closing Hive connection ...\n")


def appendData():
        JSON_DATA_FILENAME ="/var/www/html/json/"+ENVIRONMENT.lower()+".jobs.started.per.day.json"
        print ("Start writing json data ...\n")

        new_json_data = { \
                "charttitle": ""+ENVIRONMENT.lower()+".jobs.started.per.day", \
                "charttype": "line", \
                "dotColor": "black", \
                "dotSize": "4", \
                "updateInterval": "5", \
                "legendtitle": {"1": "Legend"}, \
                "legenddata": { "1": "Succeeded Jobs", "2": "Failed Jobs" }, \
                "legendcolors": { "1": "lime", "2": "red" }, \
                "xaxistitle": str(DAYSBACK)+" Days", \
                "baselinedata": { \
                "1": B_JOBS_SUCCEEDED, \
                "2": B_JOBS_FAILED}, \
                "xaxisdata": { \
                "1": calcXAxis()}, \
                "yaxistitle": "# of Jobs",
                "yaxisdata": { \
                "1": JOBS_SUCCEEDED, \
        "2": JOBS_FAILED} \
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
