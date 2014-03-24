import pyhs2
import sys

# args
if len(sys.argv) < 2:
    print "Requires args: <orgId> <userName> (opt)<linesPerFile>"
    sys.exit()

orgId = sys.argv[1]
userName = sys.argv[2]
if len(sys.argv) > 2:
    fileSize = int(sys.argv[3])
else:
    fileSize = 100000

print "\nCreating input manifests..."
print "...for Org ID: " + orgId
print "...with User Name: " + userName
print "...and with " + str(fileSize) + " lines per file.\n"

# strings
line = """NULL\tNULL\t%s\t%%s\tNULL\t%s\tNULL\tNULL\tNULL"""%(userName, orgId)
#line = """DOC_ID\tSOURCESYSTEM\t%s\t%%s\tORGNAME\t%s\tBATCHID\tFILETYPE\tTIMESTAMP"""
select = """SELECT distinct doc_id FROM summary_docreceiver_upload WHERE org_id = '%s' and status = 'success' and month=%%s"""%orgId
fileName = """qaManifest-%s-"""%orgId

# hive connection
conn = pyhs2.connect(host='10.196.47.205',
                     port=10000,
                     authMechanism="PLAIN",
                     user='hive',
                     password='',
                     database='default')
cur = conn.cursor()

# make queries
queries = []
for month in range(1, 13):
    queries.append(select%month)


# run queries
fileCount = 0
result = []

for query in queries:
    print "Executing query: " + query
    cur.execute(query)
    
    print "Fetching results..."
    for row in cur.fetch():
        result.append(row[0])

    while len(result) > fileSize:
        out = open(fileName + str(fileCount), "w")
        fileCount = fileCount + 1
        print "..." + str(fileCount) + " manifest(s) created"
        for uuid in result[0:fileSize]:
            out.write(line%uuid + "\n")
        out.close()
        result = result[fileSize:]

while len(result) > 0:
    out = open(fileName + str(fileCount), "w")
    fileCount = fileCount + 1
    print "..." + str(fileCount) + " manifest(s) created"
    for uuid in result[0:fileSize]:
        out.write(line%uuid + "\n")
    out.close()
    result = result[fileSize:]

print "\n"