import pyhs2

LOGFILE = "staging_logs_eventJob_24" 
DAY = "1"
MONTH = "8"
YEAR = "2014"

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
	# cur.execute("""set mapred.job.queue.name=default""")
	cur.execute("""set mapred.job.queue.name=hive""")
	cur.execute("""set hive.exec.max.dynamic.partitions.pernode = 1000""")
	print ("Hive paramaters assigned ...\n")
	
	
def runQueries(environment):
	global LOGFILE, DAY, MONTH, YEAR
	if environment == "Staging":
		print ("Running Staging Hive Query, please wait ...\n")
		cur.execute("""SELECT COUNT(line) as total_events, get_json_object(line, '$.orgId') as orgid \
			FROM %s \
			WHERE \
			day=%s and month=%s and year=%s and \
			get_json_object(line, '$.status') = 'success' \
			GROUP BY get_json_object(line, '$.status'), get_json_object(line, '$.orgId')""" % (LOGFILE, DAY, MONTH, YEAR))
		print ("Ended running Staging Hive Query ...\n")	
	else:
		print ("Running Production Hive Query, please wait ...\n")
		cur.execute("""SELECT COUNT(line) as total_events, get_json_object(line, '$.orgId') as orgid \
			FROM %s \
			WHERE \
			day=%s and month=%s and year=%s and \
			get_json_object(line, '$.status') = 'success' \
			GROUP BY get_json_object(line, '$.status'), get_json_object(line, '$.orgId')""" % (LOGFILE, DAY, MONTH, YEAR))
		print ("Ended running Production Hive Query ...\n")		
	
	print ("Events:\t\tOrgID:")
	for i in cur.fetch():
		print (str(i[0])+"\t\t"+str(i[1]))

def closeHiveConnection():
	print ("\nClosing Hive connection ...\n")
	global cur, conn
	cur.close()
	conn.close()
	print ("Completed closing Hive connection ...\n")

#================ START OF MAIN BODY ======================

connectToHive()

setHiveParameters()

runQueries("Staging")

closeHiveConnection()

#================ END OF MAIN BODY ========================