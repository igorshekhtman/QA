#==========================Instructions to add Queries for New Charts=====================#

### 1: add list of queries to DICT QUERIES with a key of your choosing and a value of a LIST containing the queries you wish to add. See Below for example.
### 2: add a call of executeMethods to executeScripts with the proper variables to fit your desired graph.

#=========================================================================================#


import dynamicPython as script

QUERIES = {}
### 1: EX: QUERIES["newchart"] = ["""new query 1""","""new query 2"""]

QUERIES["docsuploaded"] = ["""SELECT COUNT(DISTINCT doc_id) as documents_uploaded, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""", """SELECT COUNT(DISTINCT doc_id) as documents_uploaded, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["docsarchived"] = ["""SELECT COUNT(DISTINCT doc_id) as documents_archived, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""", """SELECT COUNT(DISTINCT doc_id) as documents_archived, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["docsaddseq"] = ["""SELECT SUM(num_docs) as documents_added_to_seq_file, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""", """SELECT SUM(num_docs) as documents_added_to_seq_file, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]			
QUERIES["parser"] = ["""SELECT COUNT(DISTINCT doc_id) as documents_parsed, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""","""SELECT COUNT(DISTINCT doc_id) as documents_parsed, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]			
QUERIES["coordinatorrequest"] = ["""SELECT COUNT(DISTINCT job_id) as count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["coordinatorstart"] = ["""SELECT COUNT(DISTINCT job_id) as count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["coordinatorfinish"] = ["""SELECT COUNT(DISTINCT job_id) as count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""","""SELECT COUNT(DISTINCT job_id) as count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]		
QUERIES["ocr"] = ["""SELECT COUNT(DISTINCT doc_id) as documents_ocred, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""","""SELECT COUNT(DISTINCT doc_id) as documents_ocred, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]			
QUERIES["persistmap"] = ["""SELECT COUNT(DISTINCT doc_id) as  Persist_mapper_count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""", """SELECT COUNT(DISTINCT doc_id) as  Persist_mapper_count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["persistred"] = ["""SELECT COUNT(*) as  Persist_reducer_count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""" , """SELECT COUNT(*) as  Persist_reducer_count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]		
QUERIES["eventmap"] = ["""SELECT SUM(num_of_events_extracted) as Total_Mapper_Events_Count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""", """SELECT COUNT(*) as Total_Mapper_Events_Count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]	
QUERIES["eventred"] = ["""SELECT SUM(event_batch_count) as Total_Reducer_Events_Count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                event_batch_count is not null and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC""", """SELECT SUM(event_batch_count) as Total_Reducer_Events_Count, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]							

#need summary tables, not ready to implement
QUERIES["successeventextract"] = ["""SELECT COUNT(DISTINCT doc_id) as total_docs, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'success' \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
QUERIES["erroreventextract"] = ["""SELECT COUNT(*) as total_errors, \
                year, month, day \
                FROM %s \
                WHERE year*10000+month*100+day >= %s and year*10000+month*100+day <= %s \
                and \
                status = 'error' or status = 'apoError') \
                GROUP BY year, month, day ORDER BY year, month, day ASC"""]
			

#DO NOT DELETE comment used for updating queries.#

#==========================Instructions to add a new call of executeMethods=====================#
	### 2: EX: script.executeMethods(var1, var2, var3, var4, var5, var6, var7, var8)
	# var1 = STRING representing environment for this chart. (e.g. "staging" or "production")
	# var2 = STRING representing the log file to run the Hive Query from (w/o environment). (e.g. "summary_docreceiver_upload" or "summary_docreceiver_archive")
	# var3 = LIST representing the attributes to be displayed by the graph. These values are used as Legend Labels. (e.g. ["Successful Docs", "Failed Docs"])
	# var4 = INT representing how many days are to be displayed by the graph. (7 is typically used)
	# var5 = DICT entry in the QUERIES DICT representing the Hive Queries to be executed. Requires that the queries have been added to the DICT QUERIES above. (e.g. QUERIES["docsuploaded"] or QUERIES["docsarchived"])
	# var6 = STRING representing filename to save to (w/o environment or filetype extension). (e.g. "docs.uploaded.per.day" or "docs.archived.per.day")
	# var7 = STRING representing the label of the y axis. (e.g. "docs" or "jobs")
	# var8 = STRING representing the type of chart to be displayed. (Must be either "bar" or "line")
	### NOTE: var3 values must be in the same order as the queries in var5. 
		# i.e. if var3 = ["Successful Docs", "Failed Docs"], then the first query in the QUERIES dict entry must be the query to find successful docs, and the second must be the query to find failed docs.
#===============================================================================================#
	
#DOC RECEIVER
#script.executeMethods("production", "summary_docreceiver_upload", ["Successful Docs", "Failed Docs"], 7, QUERIES["docsuploaded"], "docs.uploaded.per.day", "docs" )
#script.executeMethods("production", "summary_docreceiver_archive", ["Successful Docs", "Failed, Docs"], 7, QUERIES["docsarchived"], "docs.archived.per.day", "docs")
#script.executeMethods("production", "summary_docreceiver_seqfile_post", ["Successful Docs", "Failed Docs"], 7, QUERIES["docsaddseq"], "docs.added.to.seq.file.per.day", "docs")
script.executeMethods("staging", "summary_docreceiver_upload", ["Successful Docs", "Failed Docs"], 7, QUERIES["docsuploaded"], "docs.uploaded.per.day", "docs", "bar" )
#script.executeMethods("staging", "summary_docreceiver_archive", ["Successful Docs", "Failed, Docs"], 7, QUERIES["docsarchived"], "docs.archived.per.day", "docs")
#script.executeMethods("staging", "summary_docreceiver_seqfile_post", ["Successful Docs", "Failed Docs"], 7, QUERIES["docsaddseq"], "docs.added.to.seq.file.per.day", "docs")
	
#COORDINATOR
#script.executeMethods("production", "summary_coordinator_jobrequest", ["Successful Job Requests"], 7, QUERIES["coordinatorrequest"], "jobs.requested.per.day", "jobs")
#script.executeMethods("production", "summary_coordinator_jobstart", ["Successful Job Starts"], 7, QUERIES["coordinatorstart"], "jobs.started.per.day", "jobs")
#script.executeMethods("production", "summary_coordinator_jobfinish", ["Successful Jobs","Failed Jobs"], 7, QUERIES["coordinatorfinish"], "jobs.succeeded.per.day", "jobs")
#script.executeMethods("staging", "summary_coordinator_jobrequest", ["Successful Job Requests"], 7, QUERIES["coordinatorrequest"], "jobs.requested.per.day", "jobs")
#script.executeMethods("staging", "summary_coordinator_jobstart", ["Successful Job Starts"], 7, QUERIES["coordinatorstart"], "jobs.started.per.day", "jobs")
#script.executeMethods("staging", "summary_coordinator_jobfinish", ["Successful Jobs","Failed Jobs"], 7, QUERIES["coordinatorfinish"], "jobs.succeeded.per.day", "jobs")
	
#PARSER
#script.executeMethods("production", "summary_parser", ["Successful Docs","Failed Docs"], 7, QUERIES["parser"], "docs.parsed.per.day", "docs")
#script.executeMethods("staging", "summary_parser", ["Successful Docs","Failed Docs"], 7, QUERIES["parser"], "docs.parsed.per.day", "docs")
	
#OCR
#script.executeMethods("production", "summary_ocr", ["Successful Docs","Failed Docs"], 7, QUERIES["ocr"], "docs.ocred.per.day", "docs")
#script.executeMethods("staging", "summary_ocr", ["Successful Docs","Failed Docs"], 7, QUERIES["ocr"], "docs.ocred.per.day", "docs")
	
#PERSIST MAPPER
#script.executeMethods("production", "summary_persist_mapper", ["Successful Docs","Failed Docs"], 7, QUERIES["persistmap"], "docs.persist.mapped.per.day", "docs")
#script.executeMethods("staging", "summary_persist_mapper", ["Successful Docs","Failed Docs"], 7, QUERIES["persistmap"], "docs.persist.mapped.per.day", "docs")
	
#PERSIST REDUCER
#script.executeMethods("production", "summary_persist_reducer", ["Successful Docs","Failed Docs"], 7, QUERIES["persistred"], "docs.persist.reduced.per.day", "docs")
#script.executeMethods("staging", "summary_persist_reducer", ["Successful Docs","Failed Docs"], 7, QUERIES["persistred"], "docs.persist.reduced.per.day", "docs")

#EVENT MAPPER	
#script.executeMethods("production", "summary_event_mapper", ["Successful Events","Failed Events"], 7, QUERIES["eventmap"], "events.mapped.per.day", "events")
#script.executeMethods("staging", "summary_event_mapper", ["Successful Events","Failed Events"], 7, QUERIES["eventmap"], "events.mapped.per.day", "events")
	
#EVENT REDUCER
#script.executeMethods("production", "summary_event_reducer", ["Successful Events","Failed Events"], 7, QUERIES["eventred"], "events.reduced.per.day", "events")
#script.executeMethods("staging", "summary_event_reducer", ["Successful Events","Failed Events"], 7, QUERIES["eventred"], "events.reduced.per.day", "events")
	
#BUNDLER
# script.executeMethods("production", "bundler", ["Successful Events","Failed Events"], 7, QUERIES["eventsafterbundle"], "patient.events.after.bundling", "events")
# script.executeMethods("production", "bundler", ["Successful Opps","Failed Opps"], 7, QUERIES["oppsafterbundle"], "opportunities.after.bundling", "opportunities")
# script.executeMethods("staging", "bundler", ["Successful Events","Failed Events"], 7, QUERIES["eventsafterbundle"], "patient.events.after.bundling", "events")
# script.executeMethods("staging", "bundler", ["Successful Opps","Failed Opps"], 7, QUERIES["oppsafterbundle"], "opportunities.after.bundling", "opportunities")
	
#EVENT EXTRACTOR
# script.executeMethods("production", "event", ["Successful Docs"], 7, QUERIES["successeventextract"], "successful.docs.through.event.extraction", "docs")
# script.executeMethods("production", "event", ["errors"], 7, QUERIES["erroreventextract"], "errors.after.event.extraction", "errors")
# script.executeMethods("staging", "event", ["Successful Docs"], 7, QUERIES["successeventextract"], "successful.docs.through.event.extraction", "docs")
# script.executeMethods("staging", "event", ["errors"], 7, QUERIES["erroreventextract"], "errors.after.event.extraction", "errors")


#DO NOT DELETE comment used for updating method calls.#
