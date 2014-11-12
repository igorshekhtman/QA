from cassandra.cluster import Cluster
import logging
import os
import json

ORGID = "381"


os.system('clear')
log = logging.getLogger()
log.setLevel('INFO')


cluster = Cluster(['10.199.22.32', '10.196.81.90', '10.198.2.83', '10.196.100.53', '10.197.91.36', '10.199.52.19'], port=9042)
session = cluster.connect('apixio')
session_new = cluster.connect('apixio')
DE = ATSF = EJ = OJ = PAJ = PEJ = STC = 0

def countNumberOfOccurrences(proc_name):
	global DE, ATSF, EJ, OJ, PAJ, PEJ, STC
	if proc_name == "docEntry":
		DE = DE + 1
	elif  proc_name == "appendToSequenceFile":
		ATSF = ATSF + 1
	elif  proc_name == "eventJob":
		EJ = EJ + 1
	elif  proc_name == "ocrJob":
		OJ = OJ + 1
	elif  proc_name == "parserJob":
		PAJ = PAJ + 1
	elif  proc_name == "persistJob":
		PEJ = PEJ + 1
	elif  proc_name == "submitToCoordinator":
		STC = STC + 1

def checkForExistance (doc_uuid):
	results_new = session_new.execute("""SELECT * FROM trace"""+ORGID+""" where rowkey='"""+doc_uuid+"""';""")
	for row_new in results_new:
		data_new = json.loads(row_new.d)
		if row_new.col[:8] == "docentry":
			process_name = "docEntry"	
		else:
			process_name = str(data_new["processName"])
		countNumberOfOccurrences(process_name)	
		
		#print "\n" + str(data_new["documentUUID"]) + "\t" + process_name	


#trace as you can guess contains document trace objects
print "\n\n"
print "OrgID: "+ORGID
print "Cassandra Table Name: trace"+ORGID

results = session.execute("""SELECT COUNT(*) as count FROM trace"""+ORGID+""";""")
for row in results:
	print str(row.count)
	
counter = 0	
results = session.execute("""SELECT DISTINCT rowkey as rowkey FROM trace"""+ORGID+""";""")
for row in results:
	if str(row.rowkey)[:7] == "docuuid":
		print str(row.rowkey)
		counter = counter + 1
		checkForExistance(str(row.rowkey))
		print "\n================"
		print str(counter)
		print "================\n"

print "\n\n\n"
print "Total number of documents received from Doc-Receiver: " + str(counter)
print "Total number of documents docEntry: " + str(DE)
print "Total number of documents appendToSequenceFile: " + str(ATSF)
print "Total number of documents eventJob: " + str(EJ)
print "Total number of documents ocrJob: " + str(OJ)
print "Total number of documents parserJob: " + str(PAJ)
print "Total number of documents persistJob: " + str(PEJ)
print "Total number of documents submitToCoordinator: " + str(STC)
print "\n\n"



#checkForExistance("docuuid_c02101c0-9dde-4c1d-9cc0-2673971414dd")


cluster.shutdown()
print "\nThe End ..."