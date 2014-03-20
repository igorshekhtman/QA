package com.apixio.qa.hive;

import java.util.HashMap;
import java.util.Map;

public class SummaryQueryManager {

	Map<String,SummaryQuery> summaryQueries;
	
	public SummaryQuery getSummaryQuery(String tableName) {
		if (summaryQueries.containsKey(tableName)) {
			return summaryQueries.get(tableName);
		} else {
			return null;
		}
	}
	
	public SummaryQueryManager() {
		summaryQueries = new HashMap<String,SummaryQuery>();
		
		SummaryQuery docreceiverArchive = new SummaryQuery();
		docreceiverArchive.setDescription("Documents Archived by Doc Receiver");
		docreceiverArchive.setTableName("summary_docreceiver_archive");
		docreceiverArchive.setQuery("select get_json_object(line, '$.datestamp') as time, get_json_object(line, '$.archive.afs.docid') as doc_id, get_json_object(line, '$.archive.afs.batchid') as batch_id, cast(get_json_object(line, '$.archive.afs.bytes') as int) as file_size, get_json_object(line, '$.archive.afs.status') as status, cast(get_json_object(line, '$.archive.afs.millis') as int) as archive_time, get_json_object(line, '$.message') as error_message, month, day, get_json_object(line, '$.archive.afs.orgid') as org_id from production_logs_docreceiver_epoch where get_json_object(line, '$.archive') is not null");
		docreceiverArchive.setCreateStatement("create table summary_docreceiver_archive  (time string, doc_id string, batch_id string, file_size int, status string, archive_time int, error_message string) partitioned by (month string, day string, org_id string)");
		
		summaryQueries.put(docreceiverArchive.getTableName(), docreceiverArchive);
	}

}
