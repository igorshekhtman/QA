#
# Short Python script to demonstrate connecting to Hive
# Run: python2.6 new_hive_test.py
#===========================================================================================
#============================= JSON TEMPLATE ===============================================
#===========================================================================================
#
#{
#    "charttitle": "Events per Org",
#    "charttype": "line",
#    "dotColor": "black",
#    "dotSize": "4",
#    "updateInterval": "5",
#    "legendtitle": {
#        "1": "Events per Org"
#    },
#    "legenddata": {
#        "1": "Events"
#    },
#    "legendcolors": {
#        "1": "red"
#    },
#    "xaxistitle": "Number of Orgs",
#    "xaxisdata": {
#        "1": [
#            "0",
#            "1",
#            "2",
#            "3",
#            "4",
#            "5"
#        ]
#    },
#    "yaxistitle": "Number of Events",
#    "yaxisdata": {
#        "1": [
#            "0",
#            "1",
#            "2",
#            "3",
#            "4",
#            "5"
#        ]
#    }
#}
#
#===========================================================================================
#

import pyhs2
import os
import json
from time import gmtime, strftime, localtime

#ST_DAY = strftime("%d", gmtime()) # Starting day of the month
ST_DAY = "1" # Starting day of the month
EN_DAY = strftime("%d", gmtime()) # Ending day of the month
MONTH = strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR = strftime("%Y", gmtime())
#LOG_TYPE = "24"
LOG_TYPE = "epoch"

#Values can be "Staging" or "Production"
ENVIRONMENT = "Production" 
#ENVIRONMENT = "Staging"
# DATA[] = 0
# DATA = 0
DATA=[0 for i in range(31)]
for i in range(31):
	DATA[i] = 0
ORGID=[0 for i in range(31)]
for i in range(31):
	ORGID[i] = 0
DAYSOFMONTH=[0 for i in range(31)]
for i in range(31):
	DAYSOFMONTH[i] = i+1

print ("ST_DAY: "+ST_DAY)
print ("EN_DAY: "+EN_DAY)
print ("MONTH: "+MONTH)
print ("YEAR: "+YEAR)


def connectToHive():
	print ("Connecing to Hive ...\n")
	global cur, conn
 	conn = pyhs2.connect(host='10.196.47.205', \
		port=10000, authMechanism="PLAIN", \
		user='hive', password='', \
		database='default')
	cur = conn.cursor()
	print ("Connection to Hive established ...\n")

def setHiveParameters():
	print ("Assigning Hive paramaters ...\n")
	cur.execute("""set hive.exec.dynamic.partition=true""")
	cur.execute("""set hive.exec.dynamic.partition.mode=nonstrict""")
	cur.execute("""set mapred.reduce.tasks=16""")
	cur.execute("""set mapred.job.queue.name=default""")
	#cur.execute("""set mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	print ("Hive paramaters assigned ...\n")	

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
	elif component == "bundler":
		logfilename=environment.lower()+"_logs_bundler_"+LOG_TYPE
	return (logfilename)

	
def runQueries(environment):
	global ST_DAY, EN_DAY, MONTH, YEAR, DATA, ORGID, DAYSOFMONTH
	#if environment == "Staging":
	#	LOGFILE = "staging_logs_eventJob_epoch" 
	#else:
	#	LOGFILE = "production_logs_eventJob_epoch"
	
	LOGFILE = selectLogFile(environment,"event")
		
	print ("Running %s Hive Query, please wait ...\n") % (environment)
	
	
	cur.execute("""SELECT COUNT(DISTINCT get_json_object(line, '$.documentUUID')) as total_docs, \
		day \
		FROM %s \
		WHERE \
		day>=%s and \
		day<=%s and \
		month=%s and \
		year=%s and \
		get_json_object(line, '$.level') ='EVENT' and \
		get_json_object(line, '$.status') = 'success' \
		GROUP BY day ORDER BY day ASC""" % (LOGFILE, ST_DAY, EN_DAY, MONTH, YEAR))	
	
	print ("Ended running %s Hive Query ...\n")	 % (environment)
			
	print ("Docs:\t\t\tDofM:")
	ind = 0
	for i in cur.fetch():
		print (str(i[0])+"\t\t\t"+str(i[1]))
		DATA[ind] = int(i[0])
		DAYSOFMONTH[ind] = int(i[1])
		ind = ind + 1


	
def closeHiveConnection():
	print ("\nClosing Hive connection ...\n")
	global cur, conn
	cur.close()
	conn.close()
	print ("Completed closing Hive connection ...\n")

	
def appendData():
	global DATA, ORGID, ENVIRONMENT, MONTH_FMN
	DATA_FILENAME ="/var/www/html/json/"+ENVIRONMENT.lower()+".successful.docs.through.event.extraction.json" 
	print ("Start writing json data ...\n")

	new_data = {\
		"xaxisdata": {"1": DAYSOFMONTH}, \
		"yaxisdata": {"1": DATA}, \
		"charttitle": ""+ENVIRONMENT.lower()+".successful.docs.through.event.extraction", \
		"yaxistitle": "Docs", \
		"xaxistitle": "Day of the Month" , \
		"legendtitle": {"1": "Docs per Day - "+MONTH_FMN}, \
		"legenddata": {"1": "Docs"}, \
		"legendcolors": {"1": "#00FF00"} \
		}
	
	with open(DATA_FILENAME) as f:
		data = json.load(f)
	
	data.update(new_data)
	with open(DATA_FILENAME, 'w') as f:
		json.dump(data, f)	
	print ("End writing json data ...\n")	

#================ START OF MAIN BODY ======================

connectToHive()

setHiveParameters()

runQueries(ENVIRONMENT)

closeHiveConnection()

appendData()

#================ END OF MAIN BODY ========================
