import pyhs2
import sys

# args
if len(sys.argv) < 2:
	print "Run with python version 2.6"
	print "Requires arg: <orgId>"
	sys.exit()
	
orgId = sys.argv[1]
	
print "\n\nCreating document external ID manifest for Org ID: " + orgId
	
## strings
fileLine = "%s\t%s\t%s\n" #external_id	doc_source	assign_authority
query = "select external_id, doc_source, assign_authority from summary_doc_manifest_staging where org_id = '%s'" % orgId
fileName = orgId + "-manifest"

## hive connection
conn = pyhs2.connect(host='10.196.47.205',
                     port=10000,
                     authMechanism="PLAIN",
                     user='hive',
                     password='',
                     database='default')
cur = conn.cursor()

count = 0

print "Executing query: " + query
cur.execute(query)

print "Building query results..."
out = open(fileName, "w")
for row in cur.fetch():
	out.write(fileLine%(row[0], row[1], row[2]))
	count+=1
	if count%100000 == 0:
		print "...wrote " + str(count) + " entries so far."
out.close()

print "Wrote " + str(count) + " entries into the file: " + fileName
print "\n"