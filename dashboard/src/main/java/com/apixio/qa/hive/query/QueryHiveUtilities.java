package com.apixio.qa.hive.query;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.regex.Pattern;

import javax.ws.rs.core.MultivaluedMap;

import org.apache.commons.lang.StringUtils;

public class QueryHiveUtilities 
{
    public static String addUserParamsToWhereClause(String queryStr, MultivaluedMap<String,String> conditions)
    {
        String uParamsPlaceHolder = "{userParams}";
        if (queryStr != null && queryStr.indexOf(uParamsPlaceHolder) != -1)
        {
            String addedParams = "";
            if (conditions != null)
            {
                Iterator<String> keySet = conditions.keySet().iterator();
                int index = 0;
                while (keySet.hasNext())
                {
                    if (index > 0)
                        addedParams += " and ";
                    
                    String key = keySet.next();
                    index ++;
                    
                    List<String> values = conditions.get(key);
                    
                    List<String> processedList = new ArrayList<String>();
                    for (String value : values)
                    {
                        processedList.addAll(Arrays.asList(value.split(",")));
                    }
                    
                    if (processedList.size() == 1)
                    {
                        //Only one value. So do "equals" query.
                        addedParams += key + " = '" + processedList.get(0) + "'";
                    }
                    else if (processedList.size() > 1)
                    {
                        //More than one value. So do "in" query.
                        addedParams += key + " in (";
                        for (int i = 0; i < processedList.size(); i++)
                        {
                            if (i != 0)
                                addedParams += ",";
                            addedParams += "'"+processedList.get(i)+"'";
                        }
                        addedParams += ")";
                    }
                }
            }
            
            return queryStr.replaceAll(Pattern.quote(uParamsPlaceHolder), addedParams);
        }
        return queryStr;
    }
    
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
