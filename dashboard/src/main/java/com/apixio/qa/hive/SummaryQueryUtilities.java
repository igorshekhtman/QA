package com.apixio.qa.hive;

import java.sql.SQLException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Iterator;
import java.util.List;

import org.apache.commons.lang.StringUtils;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.joda.time.Days;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.apixio.qa.hive.query.QueryHiveUtilities;

public class SummaryQueryUtilities {

	private static SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy");
	public static List<JSONObject> summaryQuery(SummaryQuery summaryQuery, String hiveAddress, String startDate, String endDate, boolean useSample) throws Exception, ParseException {
		String sql = "";
		
		int days = Math.abs(Days.daysBetween(new DateTime(sdf.parse(endDate)), new DateTime(sdf.parse(startDate))).getDays()) + 1;
		int percent = 100;
		if (days > 0) {
			percent = (int)(100 / days);
		}
		String sampleQuery = "";
		if (useSample)
			sampleQuery = " TABLESAMPLE(" + percent + " PERCENT) s ";
		if (DateTime.now(DateTimeZone.UTC).toString("MM/dd/yyyy").equals(endDate)) {
			System.out.println("includes today");
			
			// if the start date is also today, just do a basic summary query
			if (DateTime.now(DateTimeZone.UTC).toString("MM/dd/yyyy").equals(startDate)) {
				sql = summaryQuery.getQuery() + " and " + QueryHiveUtilities.getDateRange(startDate, endDate);
			} 
			// else, we need to union the two
			else {
				String epochPart = summaryQuery.getQuery() + " and " + QueryHiveUtilities.getDateRange(endDate, endDate);
				String summaryEnd = DateTime.now(DateTimeZone.UTC).minusDays(1).toString("MM/dd/yyyy");
				String summaryPart = "select * from " + summaryQuery.getTableName() + sampleQuery + " where " + QueryHiveUtilities.getDateRange(startDate, summaryEnd);
				
				sql = "select * from (" + epochPart + " UNION ALL " + summaryPart + ") combined"; 
			}
		} else {
			sql = "select * from " + summaryQuery.getTableName() + sampleQuery + " where " + QueryHiveUtilities.getDateRange(startDate, endDate);
		}
		QueryHiveUtilities.getDateRange(startDate, endDate);
		return QueryHive.queryHiveJson(hiveAddress, sql);
	}
	
	public static JSONArray getCoordinatorStats(String hiveAddress, String environment, String statFilter, String startDate, String endDate) throws Exception, ParseException {
		JSONArray cleanedStatsArray = new JSONArray();
		SummaryQueryManager manager = new SummaryQueryManager();
		String tableName = "summary_coordinator_stats";
		if (environment.equalsIgnoreCase("staging"))
			tableName += "_staging";
		List<JSONObject> output = SummaryQueryUtilities.summaryQuery(manager.getSummaryQuery("summary_coordinator_stats"), hiveAddress, startDate, endDate, true);
		for (JSONObject outputLine : output) {
			JSONObject cleanedStatsLine = new JSONObject();
			cleanedStatsLine.put("time", outputLine.get("time"));
			String statsString = outputLine.getString("stats_json");
			JSONObject statsLine = new JSONObject(statsString);
			Iterator statsIterator = statsLine.keys();
			while (statsIterator.hasNext()) {
				String activity = statsIterator.next().toString();
				if (activity.equals("running")) {
					cleanedStatsLine.put("running", statsLine.getString(activity));
				} else if (activity.equals("toLaunch")) {
					cleanedStatsLine.put("toLaunch", statsLine.getString(activity));
					
				} else {
					JSONObject activityStats = statsLine.getJSONObject(activity);
					Iterator activityStatsIterator = activityStats.keys();
					while (activityStatsIterator.hasNext()) {
						String statName = activityStatsIterator.next().toString();
						String statValue = activityStats.getString(statName);
						
						if (StringUtils.isEmpty(statFilter) || statFilter.equals(statName)) {
							JSONObject statMap = null;
							if (cleanedStatsLine.isNull(statName)) {
								statMap = new JSONObject();
								cleanedStatsLine.put(statName, statMap);
							} else {
								statMap = cleanedStatsLine.getJSONObject(statName);
							}
							statMap.put(activity, statValue);
						}
					}
				}
			}
			cleanedStatsArray.put(cleanedStatsLine);
		}
		return cleanedStatsArray;
	}

}
