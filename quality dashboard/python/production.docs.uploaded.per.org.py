#
# Short Python script to demonstrate connecting to Hive
# Run: python2.6 new_hive_test.py
#===========================================================================================
#============================= JSON TEMPLATE ===============================================
#===========================================================================================
#
# "charttitle": "Events per Org",
#    "charttype": "line",
#    "dotColor":"black",
#    "dotSize": "3",    
#    "updateInterval": "5",
#    "legendtitle": [
#        "1": "Events per Org"
#    ],
#    "legenddata": [
#        "1": "Events"
#    ],
#    "legendcolors": [
#        "1": "red"
#    ],
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
#
#===========================================================================================
#

import pyhs2
import os
import json

ST_DAY = "20" # Starting day of the month
EN_DAY = "30" # Ending day of the month
MONTH = "7"
YEAR = "2014"
#Values can be "Staging" or "Production"
ENVIRONMENT = "Production" 
#ENVIRONMENT = "Staging"
# DATA[] = 0
# DATA = 0
DATA1=[0 for i in range(10)]
DATA2=[0 for i in range(10)]
DATA3=[0 for i in range(10)]

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
	
def runQueries(environment):
	global ST_DAY, EN_DAY, MONTH, YEAR, DATA
	if environment == "Staging":
		LOGFILE = "staging_logs_eventJob_epoch" 
	else:
		LOGFILE = "production_logs_eventJob_epoch"
		
	print ("Running %s Hive Query, please wait ...\n") % (environment)
	cur.execute("""SELECT COUNT(line) as total_events, get_json_object(line, '$.orgId') as orgid \
		FROM %s \
		WHERE \
		day>=%s and day<=%s and month=%s and year=%s and \
		get_json_object(line, '$.status') = 'success' \
		GROUP BY get_json_object(line, '$.status'), get_json_object(line, '$.orgId')""" % (LOGFILE, ST_DAY, EN_DAY, MONTH, YEAR))
	print ("Ended running %s Hive Query ...\n")	 % (environment)
			
	print ("Events:\t\tOrgID:")
	ind = 0
	#DATA = DATA + "["
	for i in cur.fetch():
		print (str(i[0])+"\t\t"+str(i[1]))
		DATA1[ind] = int(i[0])
		DATA2[ind] = int(i[0]) + 500
		DATA3[ind] = int(i[0]) + 1000
		ind = ind + 1
	#DATA = DATA[:-2] + "]"
	#DATA = DATA[:-2]

	
def closeHiveConnection():
	print ("\nClosing Hive connection ...\n")
	global cur, conn
	cur.close()
	conn.close()
	print ("Completed closing Hive connection ...\n")

	
def appendData():
	global DATA
	DATA_FILENAME ="/var/www/html/production.docs.uploaded.per.org.json" 
	print ("Start writing json data ...\n")

	new_data = {"yaxisdata": {\
		"1": DATA1, \
		"2": DATA2, \
		"3": DATA3}, \
		"charttitle": "production.docs.uploaded.per.org", \
		"yaxistitle": "documents"}
	
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
