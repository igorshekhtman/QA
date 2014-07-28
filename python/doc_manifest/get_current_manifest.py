import pyhs2
import sys
import datetime
i = datetime.datetime.now()

# args
if len(sys.argv) < 2:
        print "Run with python version 2.6"
        print "Requires arg: <orgId>"
        sys.exit()

orgId = sys.argv[1]

print "\n\nCreating document external ID manifest for Org ID: " + orgId

## strings
fileLine = "%s\t%s\t%s\n" #external_id  doc_source assign_authority
query = """select * from (select external_id, doc_source, assign_authority from summary_doc_manifest where org_id = '%s'
		UNION ALL select get_json_object(line, '$.document.id') as external_id, get_json_object(line, '$.document.source') as doc_source,
		get_json_object(line, '$.document.assignAuthority') as assign_authority from production_logs_datacheckandrecover_epoch
		where get_json_object(line, '$.docManifest') is not null and get_json_object(line, '$.orgId') = '%s'
		and day=%s and month=%s and year=2014) joined_table""" %(orgId, orgId, i.day, i.month)  
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
        if count%1000000 == 0:
                print "...wrote " + str(count) + " entries so far."
out.close()

print "...wrote " + str(count) + " entries into the file: " + fileName
print "\n"