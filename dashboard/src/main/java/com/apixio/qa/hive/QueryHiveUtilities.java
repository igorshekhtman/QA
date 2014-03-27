package com.apixio.qa.hive;

import org.apache.commons.lang.StringUtils;

public class QueryHiveUtilities {

    public static String addtoWhereClause(String whereClause, String clause)
    {
        if (!StringUtils.isBlank(clause))
        {
            if (StringUtils.isBlank(whereClause))
                whereClause = " WHERE (" + clause + ")";
            else
                whereClause += " AND (" + clause + ")";
        }
        return whereClause;
    }

    public static String getDateRange(String startDate, String endDate)
    {
        String dateRange = "";
        if (!StringUtils.isBlank(endDate) && endDate.length() == 10)
        {
            String endMonth = endDate.substring(0, 2);
            String endDay = endDate.substring(3, 5);
            dateRange = "((month < " + endMonth + ") OR (month = " + endMonth + " AND day <= " + endDay + "))";
        }

        if (!StringUtils.isBlank(startDate) && startDate.length() == 10)
        {
            String startMonth = startDate.substring(0, 2);
            String startDay = startDate.substring(3, 5);
            String beginClause = "((month > " + startMonth + ") OR (month = " + startMonth + " AND day >= " + startDay + "))";
            if (StringUtils.isBlank(dateRange))
                dateRange = beginClause;
            else
                dateRange += " AND " + beginClause;
        }

        return dateRange;
    }  


    public static String getDateRangeTable(String startDate, String endDate, String tableName)
    {
        String dateRange = "";
        if (!StringUtils.isBlank(endDate) && endDate.length() == 10)
        {
            String endMonth = endDate.substring(0, 2);
            String endDay = endDate.substring(3, 5);
            dateRange = "((" + tableName + ".month < " + endMonth + ") OR (" + tableName + ".month = " + endMonth + " AND " + tableName + ".day <= " + endDay + "))";
        }

        if (!StringUtils.isBlank(startDate) && startDate.length() == 10)
        {
            String startMonth = startDate.substring(0, 2);
            String startDay = startDate.substring(3, 5);
            String beginClause = "((" + tableName + ".month > " + startMonth + ") OR (" + tableName + ".month = " + startMonth + " AND " + tableName + ".day >= " + startDay + "))";
            if (StringUtils.isBlank(dateRange))
                dateRange = beginClause;
            else
                dateRange += " AND " + beginClause;
        }

        return dateRange;
    }

    public static String getLimitClause(String limit)
    {
        String limitClause = "";
        if (!StringUtils.isBlank(limit))
            limitClause = " limit " + limit;
        return limitClause;
    }
}
