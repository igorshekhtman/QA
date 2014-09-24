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
# Date: 09/02/2014
# 4.) Added all-in-one functionality to allow easy addition of new charts.

#==========================================================================================================
#============================= JSON TEMPLATE ==============================================================
#==========================================================================================================
#{
    # "legenddata": {
        # "1": "Succeeded Jobs",
        # "2": "Failed Jobs"
    # },
    # "legendcolors": {
        # "1": "lime",
        # "2": "red"
    # },
    # "xaxisdata": {
        # "1": [
            # "08-27",
            # "08-28",
            # "08-29",
            # "08-30",
            # "08-31",
            # "09-01",
            # "09-02"
        # ]
    # },
    # "updateInterval": "5",
    # "yaxistitle": "# of Jobs",
    # "baselinedata": {
        # "1": [
            # 285,
            # 255,
            # 14,
            # 14,
            # 14,
            # 14,
            # 28
        # ],
        # "2": [
            # 0,
            # 0,
            # 0,
            # 0,
            # 0,
            # 0,
            # 0
        # ]
    # },
    # "dotColor": "black",
    # "yaxisdata": {
        # "1": [
            # 224,
            # 224,
            # 28,
            # 60,
            # 14,
            # 14,
            # 0
        # ],
        # "2": [
            # 0,
            # 0,
            # 0,
            # 2,
            # 0,
            # 0,
            # 0
        # ]
    # },
    # "xaxistitle": "7 Days",
    # "charttitle": "staging.jobs.succeeded.or.failed.per.day",
    # "legendtitle": {
        # "1": "Legend"
    # },
    # "charttype": "line",
    # "dotSize": "4"
# }
#
#===========================================================================================
#

import pyhs2
import os
import json
from json import JSONEncoder
from time import gmtime, strftime, localtime
from datetime import date, timedelta as td
import calendar
import time

CURDAY = int(strftime("%d", gmtime()))
CURMONTH = int(strftime("%m", gmtime()))
CURYEAR = strftime("%Y", gmtime())

START_DATE = None
END_DATE = None
START_DATE_BASE = None
END_DATE_BASE = None

ENVIRONMENT = ""
CATEGORY = ""
TYPES = []
QUERY = []
DAYSBACK = 7
DATA = {}
DATA_LOC = ""
Y_AXIS_LABEL = ""
CHART_TYPE = ""


def setGlobals(env, cat, types, days, query, dataloc, yaxis, charttype):
        global DAYSBACK, CATEGORY, ENVIRONMENT, QUERY, TYPES, DATA_LOC, Y_AXIS_LABEL, CHART_TYPE
        DAYSBACK = int(days)
        CATEGORY = cat
        TYPES = types
        DATA_LOC = dataloc
        ENVIRONMENT = env
        QUERY = query
	Y_AXIS_LABEL = yaxis
	CHART_TYPE = charttype

		
def identifyReportDayandMonth():
#======== obtain day and month for previous from current day and month ==========================================================
        global  CURDAY, CURMONTH, CURYEAR, END_DATE, START_DATE, END_DATE_BASE, START_DATE_BASE

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
        global DATA
        for j in range(len(TYPES)):
                DATA[TYPES[j]] = [0 for i in range(DAYSBACK)]
        for k in range(len(TYPES)):
                DATA["B_" + TYPES[k]] = [0 for i in range(DAYSBACK)]
        print DATA


def calcXAxis():
        dateList = []
        delta = END_DATE - START_DATE

        for i in range(delta.days):
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
        #cur.execute("""set mapred.job.queue.name=default""")
        cur.execute("""set mapred.job.queue.name=hive""")
        cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
        print ("Hive parameters assigned ...\n")


def selectLogFile(environment, component):
		
		logfilename = CATEGORY
		if environment == "staging":
			logfilename = logfilename + "_staging"
		print logfilename
		return (logfilename)
		

def adjustArray(input_array, notBase):
        output_array = []
        output_array=[0 for i in range(DAYSBACK)]
        for i in range(1,DAYSBACK+1):
                if notBase:
                        tempD = START_DATE + td(days = (i))
                        output_array[i-1] = [0, str(tempD.year), str(tempD.month), str(tempD.day )]
                else:
                        tempD2 = START_DATE_BASE + td(days = (i))
                        output_array[i-1] = [0, str(tempD2.year), str(tempD2.month), str(tempD2.day )]
        for i in range(DAYSBACK):
                for j in input_array:
                        tempD3 = date(int(output_array[i][1]), int(output_array[i][2]), int(output_array[i][3]))
                        if date(int(j[1]),int(j[2]),int(j[3])) == tempD3:
                                output_array[i][0] = j[0]
        return (output_array)

		
def mainQuery(environment,queryNum):
        global DATA
        LOGFILE = selectLogFile(environment,CATEGORY)
        print ("Running %s Hive Query to extract successful jobs, please wait ...\n") % (environment)

        cur.execute(QUERY[queryNum] % (LOGFILE, (START_DATE.year * 10000 + START_DATE.month * 100 + START_DATE.day), (END_DATE.year * 10000 + END_DATE.month * 100 + END_DATE.day)))

        print ("Ended running %s Hive Query to extract successful jobs ...\n")   % (environment)
        result = cur.fetch()
        print ("Query " + str(queryNum) +":\tYear:\t\tMonth:\t\tDay:")
        ind = 0
        new_result = adjustArray(result, True)
        for i in new_result:
           print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
           DATA[TYPES[queryNum]][ind] = int(i[0])
           ind = ind + 1


def baseQuery(environment,queryNum):
        global DATA
        LOGFILE = selectLogFile(environment,CATEGORY)
        print ("Running %s Hive Query to extract successful jobs, please wait ...\n") % (environment)
		
        cur.execute(QUERY[queryNum] % (LOGFILE, (START_DATE_BASE.year * 10000 + START_DATE_BASE.month * 100 + START_DATE_BASE.day), (END_DATE_BASE.year * 10000 + END_DATE_BASE.month * 100 + END_DATE_BASE.day)))

        print ("Ended running %s Hive Query to extract successful jobs ...\n")   % (environment)
        result = cur.fetch()
        print ("B_Query " + str(queryNum) + ":\tYear:\t\tMonth:\t\tDay:")
        ind = 0
        new_result = adjustArray(result, False)
        for i in new_result:
           print (str(i[0])+" \t\t "+str(i[1])+" \t\t "+str(i[2])+" \t\t "+str(i[3]))
           DATA["B_" + TYPES[queryNum]][ind] = int(i[0])
           ind = ind + 1


def runQueries(environment):
        for i in range(len(QUERY)):
                mainQuery(environment,i)
                baseQuery(environment,i) 


def closeHiveConnection():
        print ("\nClosing Hive connection ...\n")
        global cur, conn
        cur.close()
        conn.close()
        print ("Completed closing Hive connection ...\n")


def appendData():

        JSON_DATA_FILENAME ="/var/www/html/json/" + ENVIRONMENT.lower() + "." + DATA_LOC + ".json"
        print ("Start writing json data ...\n")

        yDataDict = {}
        for i in range(len(TYPES)):
                yDataDict[str(i+1)] = DATA[TYPES[i]]

        baseDataDict = {}
        for i in range(len(TYPES)):
                baseDataDict[str(i+1)] = DATA["B_" + TYPES[i]]

        legDataDict = {}
        for i in range(len(TYPES)):
                legDataDict[str(i+1)] = TYPES[i]

        legColorDict = {}
        colors = ["lime","red", "cyan", "yellow", "gray", "purple"]
        for i in range(len(TYPES)):
                legColorDict[str(i+1)] = colors[i]

        new_json_data = { \
                "charttitle": ""+ENVIRONMENT.lower()+ "." + DATA_LOC, \
                "charttype": CHART_TYPE, \
                "dotColor": "black", \
                "dotSize": "4", \
                "updateInterval": "5", \
                "legendtitle": {"1": "Legend"}, \
                "legenddata": legDataDict, \
                "legendcolors": legColorDict, \
                "xaxistitle": str(DAYSBACK)+" Days", \
                "baselinedata": baseDataDict, \
                "xaxisdata": { \
                "1": calcXAxis()}, \
                "yaxistitle": "# of " + Y_AXIS_LABEL,
                "yaxisdata": yDataDict \
                }
        f = open(JSON_DATA_FILENAME, 'w+')
        #json_data = json.load(f)

        #json_data.update(new_json_data)
        #with open(JSON_DATA_FILENAME, 'w') as f:
        json.dump(new_json_data, f)
        print ("End writing json data ...\n")

#================ START OF MAIN BODY ======================
def executeMethods(env, cat, types, days, query, dataloc, yaxis, charttype):
        setGlobals(env, cat, types, days, query, dataloc, yaxis, charttype)
        identifyReportDayandMonth()
        initializeGlobalArrays()
        connectToHive()
        setHiveParameters()
        runQueries(ENVIRONMENT)
        closeHiveConnection()
        appendData()

#================ END OF MAIN BODY ========================

