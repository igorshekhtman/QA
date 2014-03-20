package com.apixio.qa.hive;

public class SummaryQueryUtilities {


	public static String summaryQuery(String hiveAddress, String environment, String component, String startDate, String endDate, String limit) {
//		String tableName = component;
//		if (environment.equals("staging")) {
//			tableName += "_staging";
//		}
//
//        String whereClause = "";
//        whereClause = QueryHiveUtilities.addtoWhereClause(whereClause, QueryHiveUtilities.getDateRange(startDate, endDate));
//
//        String limitClause = QueryHiveUtilities.getLimitClause(limit);
//        String sql = "select * FROM " + tableName + whereClause + limitClause;
        return "";//getLineJson(hiveAddress, sql);
	}

}
