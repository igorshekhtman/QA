package com.apixio.qa.hive;

import java.sql.SQLException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class SummaryQueryManager {

	Map<String,SummaryQuery> summaryQueries;
	
	public static void main(String[] args) throws SQLException, JSONException {

		//System.out.println(cleanedStatsArray.toString());
	}
	
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
		docreceiverArchive.setQuery("select get_json_object(line, '$.datestamp') as time, get_json_object(line, '$.archive.afs.docid') as doc_id, get_json_object(line, '$.archive.afs.batchid') as batch_id, cast(get_json_object(line, '$.archive.afs.bytes') as int) as file_size, get_json_object(line, '$.archive.afs.status') as status, cast(get_json_object(line, '$.archive.afs.millis') as int) as archive_time, get_json_object(line, '$.message') as error_message, substr(get_json_object(line, '$.datestamp'),0,4) as year, month, day, get_json_object(line, '$.archive.afs.orgid') as org_id from production_logs_docreceiver_epoch where get_json_object(line, '$.archive') is not null");
		docreceiverArchive.setCreateStatement("create table summary_docreceiver_archive  (time string, doc_id string, batch_id string, file_size int, status string, archive_time int, error_message string) partitioned by (year string, month string, day string, org_id string)");
		
		summaryQueries.put(docreceiverArchive.getTableName(), docreceiverArchive);
		
		SummaryQuery coordinatorStats = new SummaryQuery();
		coordinatorStats.setDescription("Coordinator Stats");
		coordinatorStats.setTableName("summary_coordinator_stats");
		coordinatorStats.setQuery("select get_json_object(line, '$.datestamp') as time, get_json_object(line, '$.coordinator.stats') as stats_json, substr(get_json_object(line, '$.datestamp'),0,4) as year, month, day from production_logs_coordinator_epoch where get_json_object(line, '$.coordinator.stats.parser.queuedCount') is not null");
		coordinatorStats.setCreateStatement("create table summary_coordinator_stats (time string, stats_json string) partitioned by (year STRING, month STRING, day STRING)");
		
		summaryQueries.put(coordinatorStats.getTableName(), coordinatorStats);
		
		SummaryQuery coordinatorStatsStaging = new SummaryQuery();
		coordinatorStats.setDescription("Coordinator Stats - Staging");
		coordinatorStats.setTableName("summary_coordinator_stats_staging");
		coordinatorStats.setQuery("select get_json_object(line, '$.datestamp') as time, get_json_object(line, '$.coordinator.stats') as stats_json, substr(get_json_object(line, '$.datestamp'),0,4) as year, month, day from staging_logs_coordinator_epoch where get_json_object(line, '$.coordinator.stats.parser.queuedCount') is not null");
		coordinatorStats.setCreateStatement("create table summary_coordinator_stats_staging (time string, stats_json string) partitioned by (year STRING, month STRING, day STRING)");
		
		summaryQueries.put(coordinatorStatsStaging.getTableName(), coordinatorStatsStaging);
	}

}
