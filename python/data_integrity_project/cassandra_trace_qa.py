from cassandra.cluster import Cluster
import logging
import os
import json

ORGID = "382"

#"d12240a0-a67b-4fd6-969a-e17bcb3a022a"

os.system('clear')
log = logging.getLogger()
log.setLevel('INFO')


cluster = Cluster(['10.199.22.32', '10.196.81.90', '10.198.2.83', '10.196.100.53', '10.197.91.36', '10.199.52.19'], port=9042)
session = cluster.connect('apixio')
session_new = cluster.connect('apixio')

PROC_MAP = { \
	"docEntry":"DE", \
	"appendToSequenceFile":"ATSF", \
	"eventJob":"EJ", \
	"ocrJob":"OJ", \
	"parserJob":"PAJ", \
	"persistJob":"PEJ", \
	"submitToCoordinator":"STC", \
}

# Initialize all global counters to zero
for i in PROC_MAP:
	exec("%s = %d" % (PROC_MAP[i],0)) in globals()	

def countNumberOfOccurrences(proc_name):
	if proc_name in PROC_MAP:
		exec("%s = %s + %d" % (PROC_MAP[proc_name],PROC_MAP[proc_name],1)) in globals()


def checkForExistance (doc_uuid):
	results_new = session_new.execute("""SELECT * FROM trace"""+ORGID+""" where rowkey='"""+doc_uuid+"""';""")
	for row_new in results_new:
		data_new = json.loads(row_new.d)
		if row_new.col[:8] == "docentry":
			process_name = "docEntry"	
		else:
			process_name = str(data_new["processName"])
		countNumberOfOccurrences(process_name)
		#if process_name == "docEntry":	
		#	print str(row_new)
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
print "received from Doc-Receiver: " + str(counter)
print "\n"

for i in PROC_MAP:
	print str(i) +  ": " + str(eval(PROC_MAP[i]))

print "\n\n"



#checkForExistance("docuuid_d12240a0-a67b-4fd6-969a-e17bcb3a022a")


cluster.shutdown()
print "\nThe End ..."