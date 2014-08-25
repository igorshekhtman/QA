#==========================Instructions to add Queries for New Charts=====================#

### 1: add queries to dict QUERIES with a key of your choosing and a value of an array containing the queries you wish to add. See Below for example.
### 2: add a call of executeMethods to executeScripts with the proper variables to fit your desired graph.



import dynamicPython as script

QUERIES = {}

### 1: EX: QUERIES["newchart"] = ["""new query 1""","""new query 2"""]

QUERIES["stagingparser"] = ["""SELECT COUNT(DISTINCT get_json_object(line, '$.documentuuid')) as documents_parsed, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                get_json_object(line, '$.level') ='EVENT' and \
                get_json_object(line, '$.status') = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""","""SELECT COUNT(DISTINCT get_json_object(line, '$.documentuuid')) as documents_parsed, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                get_json_object(line, '$.level') ='EVENT' and \
                get_json_object(line, '$.status') = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["stagingcoordinator"] = ["""SELECT COUNT(DISTINCT(get_json_object(line, '$.job.jobID'))) as count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                get_json_object(line, '$.job.status') = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""","""SELECT COUNT(DISTINCT(get_json_object(line, '$.job.jobID'))) as count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                get_json_object(line, '$.job.status') = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]

				
def executeScripts():

	### 2: EX: script.executeMethods("environment", "chart category(ex: parser, OCR, coordinator, etc.)", ["attribute measured 1","attribute measured 2"], DaysBack, QUERIES["newchart"], "filename to save to (w/o environment or filetype extension)")
	### NOTE: the attribute array and queries array must match up in indexes
	
	print "Generating JSON files for all charts"
	script.executeMethods("staging", "parser", ["docsSUCCESS","docsFAIL"], 7, QUERIES["stagingparser"], "docs.parsed.per.day")
	script.executeMethods("staging", "coordinator", ["jobsSUCCESS","jobsFAIL"], 7, QUERIES["stagingcoordinator"], "jobs.succeeded.per.day")
	

executeScripts()
