package com.apixio.qa.hive.query;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONObject;

import com.apixio.qa.hive.cache.CacheManager;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;

public class RecentErrorsProcessor extends QueryProcessor
{
    public RecentErrorsProcessor()
    {
        super();
    }
    
    private class ErrorDetails
    {
        String errorMessage;
        int errorCount;
        String time;
    }
    
    @Override
    protected JSONObject createJSONObject(Object resultsCollection, String orgId)
        throws Exception
    {
        @SuppressWarnings("unchecked")
        Map<String, List<ErrorDetails>> errorDetailsMap = (Map<String, List<ErrorDetails>>)resultsCollection;
        
        JSONObject obj = super.createJSONObject(resultsCollection, orgId);
        
        Iterator<String> it = errorDetailsMap.keySet().iterator();
        while (it.hasNext())
        {
            String typeOfError = it.next();
            JSONArray errorArray = new JSONArray();
            String trackDay = null;
            int countResults = 0;
            
            for (ErrorDetails e : errorDetailsMap.get(typeOfError))
            {
                //Add only first 2 days (recent) ones...
                String day = e.time.substring(0, e.time.indexOf("T"));
                if (countResults < 2)
                {
                    if (trackDay == null || !trackDay.equals(day))
                        countResults ++;
                    
                    JSONObject errObj = new JSONObject();
                    errObj.put("time", e.time);
                    errObj.put("count", e.errorCount);
                    errObj.put("msg", e.errorMessage);
                    errorArray.put(errObj);
                    
                    trackDay = day;
                }
                else break;
            }
            
            obj.put(typeOfError, errorArray);
        }
        
        return obj;
    }
    
    /*public static void main(String[] args)
    {
        Map<String, Map<String, List<ErrorDetails>>> orgToErrorDetailsMap = new HashMap<String, Map<String,List<ErrorDetails>>>();
        List<JSONObject> results = new ArrayList<JSONObject>();
        
        try
        {
            JSONObject ob1 = new JSONObject();
            ob1.put("org_id", "100"); 
            ob1.put("last_occured_time", "2014-06-09T00:11:90.009Z");
            ob1.put("error_count", "20");
            ob1.put("error_message", "Error message 1");
            ob1.put("status", "error");
            JSONObject ob2 = new JSONObject();
            ob2.put("org_id", "100"); 
            ob2.put("last_occured_time", "2014-06-10T01:11:90.009Z");
            ob2.put("error_count", "8");
            ob2.put("error_message", "Error message 2");
            ob2.put("status", "error");
            JSONObject ob4 = new JSONObject();
            ob4.put("org_id", "100"); 
            ob4.put("last_occured_time", "2014-06-11T01:11:90.009Z");
            ob4.put("error_count", "8");
            ob4.put("error_message", "Error message 2");
            ob4.put("status", "error");
            JSONObject ob3 = new JSONObject();
            ob3.put("org_id", "101"); 
            ob3.put("last_occured_time", "2014-05-09T01:11:90.009Z");
            ob3.put("error_count", "7");
            ob3.put("error_message", "Error message 3");
            ob3.put("status", "error");
            
            results.add(ob2);
            results.add(ob1);
            results.add(ob3);
            results.add(ob4);
            
            RecentErrorsProcessor p = new RecentErrorsProcessor();
            p.getErrorsObject(results, "parser_error_count", orgToErrorDetailsMap);
            
            JSONObject ob5 = new JSONObject();
            ob5.put("org_id", "100"); 
            ob5.put("last_occured_time", "2014-04-11T01:11:90.009Z");
            ob5.put("error_count", "8");
            ob5.put("error_message", "Error message 2");
            ob5.put("status", "error");
            JSONObject ob6 = new JSONObject();
            ob6.put("org_id", "101"); 
            ob6.put("last_occured_time", "2014-03-10T01:11:90.009Z");
            ob6.put("error_count", "7");
            ob6.put("error_message", "Error message 3");
            ob6.put("status", "error");
            JSONObject ob7 = new JSONObject();
            ob7.put("org_id", "200"); 
            ob7.put("last_occured_time", "2014-03-10T01:11:90.009Z");
            ob7.put("error_count", "7");
            ob7.put("error_message", "Error message 3");
            ob7.put("status", "error");
            JSONObject ob8 = new JSONObject();
            ob8.put("org_id", "200"); 
            ob8.put("last_occured_time", "2014-03-11T01:11:90.009Z");
            ob8.put("error_count", "7");
            ob8.put("error_message", "Error message 3");
            ob8.put("status", "error");
            JSONObject ob9 = new JSONObject();
            ob9.put("org_id", "200"); 
            ob9.put("last_occured_time", "2014-03-12T01:11:90.009Z");
            ob9.put("error_count", "7");
            ob9.put("error_message", "Error message 3");
            ob9.put("status", "error");
            JSONObject ob10 = new JSONObject();
            ob10.put("org_id", "200"); 
            ob10.put("last_occured_time", "2014-03-12T11:09:90.009Z");
            ob10.put("error_count", "7");
            ob10.put("error_message", "Error message 3");
            ob10.put("status", "error");
            
            results.add(ob5);
            results.add(ob6);
            results.add(ob7);
            results.add(ob8);
            results.add(ob9);
            results.add(ob10);
            
            p.getErrorsObject(results, "persist_error_count", orgToErrorDetailsMap);
            
            Iterator<String> it = orgToErrorDetailsMap.keySet().iterator();
            
            while (it.hasNext())
            {
                Map<String, List<ErrorDetails>> errorDetailsMap = orgToErrorDetailsMap.get(it.next());
                
                Iterator<String> itErrors = errorDetailsMap.keySet().iterator();
                
                while (itErrors.hasNext())
                {
                    List<ErrorDetails> errorDetailsList = errorDetailsMap.get(itErrors.next());
                    p.orderErrorsByTime(errorDetailsList);
                }
            }
            
            it = orgToErrorDetailsMap.keySet().iterator();
            while (it.hasNext())
            {
                String org = it.next(); 
                Map<String, List<ErrorDetails>> errorDetailsMap = orgToErrorDetailsMap.get(org);
                
                Iterator<String> itErrors = errorDetailsMap.keySet().iterator();
                
                while (itErrors.hasNext())
                {
                    List<ErrorDetails> errorDetailsList = errorDetailsMap.get(itErrors.next());
                    for (ErrorDetails e : errorDetailsList)
                    {
                        System.out.println("time:"+e.time+" for org:"+org);
                    }
                }
            }
            
            JSONObject resultObj = new JSONObject();
            JSONArray resultArray = new JSONArray();
            List<Long> sortedList = p.getSortedKeys(orgToErrorDetailsMap.keySet().iterator());
            for (Long orgId : sortedList)
            {
                String key = orgId.toString();
                JSONObject obj = p.createJSONObject(orgToErrorDetailsMap.get(key), key);
                resultArray.put(obj);
            }
            resultObj.put("results", resultArray);
            System.out.println(resultObj.toString());
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }*/
    
    private void orderErrorsByTime(List<ErrorDetails> errorDetailsList)
    {
        Collections.sort(errorDetailsList, new Comparator<ErrorDetails>()
        {
            public int compare(ErrorDetails o1, ErrorDetails o2)
            {
                return o2.time.compareTo(o1.time);
            }
        });
    }
    
    @Override
    public JSONObject processQuery(QueryHandler queryHandler, String outputDir, String environment, List<RunQuery> runQueries) throws Exception
    {
        JSONObject resultObj = null;
        CacheManager cache = new CacheManager(environment, outputDir);
        
        if (runQueries != null)
        {
            resultObj = new JSONObject();
            Map<String, Map<String, List<ErrorDetails>>> orgToErrorDetailsMap = new HashMap<String, Map<String,List<ErrorDetails>>>();
            
            for (RunQuery rQ : runQueries)
            {
                //Fetch data from cache...
                List<JSONObject> results = cache.fetchResults(rQ.getName());

                if (results == null)
                {
                    results = queryHandler.runQuery(environment, rQ);
                    cache.writeResults(results, rQ.getName());
                }
                //Just collect all types of errors
                collectResults(results, rQ.getName(), orgToErrorDetailsMap); 
            }
            
            Iterator<String> it = orgToErrorDetailsMap.keySet().iterator();
            //Order each type of errors in descending order of time
            while (it.hasNext())
            {
                Map<String, List<ErrorDetails>> errorDetailsMap = orgToErrorDetailsMap.get(it.next());
                
                Iterator<String> itErrors = orgToErrorDetailsMap.keySet().iterator();
                
                while (itErrors.hasNext())
                {
                    List<ErrorDetails> errorDetailsList = errorDetailsMap.get(itErrors.next());
                    if (errorDetailsList != null)
                        orderErrorsByTime(errorDetailsList);
                }
            }
            
            JSONArray resultArray = new JSONArray();
            //Order the results by orgId
            List<Long> sortedList = getSortedLongKeys(orgToErrorDetailsMap.keySet().iterator());
            for (Long orgId : sortedList)
            {
                String key = orgId.toString();
                //Create JSONObject
                JSONObject obj = createJSONObject(orgToErrorDetailsMap.get(key), key);
                resultArray.put(obj);
            }
            resultObj.put("results", resultArray);
        }
        return resultObj;
    }

    @Override
    protected void collectResults(List<JSONObject> results, String typeOfResults, Object resultsCollection) throws Exception
    {
        @SuppressWarnings("unchecked")
        Map<String, Map<String, List<ErrorDetails>>> orgToErrorDetailsMap = (Map<String, Map<String, List<ErrorDetails>>>)resultsCollection;
        
        for (JSONObject result : results)
        {
            String orgId = result.getString("org_id");
            if (orgId != null && !orgId.equalsIgnoreCase("__HIVE_DEFAULT_PARTITION__")
                    && result.has("status") && result.getString("status").equals("error"))
            {
                Map<String, List<ErrorDetails>> errorDetails = orgToErrorDetailsMap.get(orgId);
                if (errorDetails == null)
                    errorDetails = new HashMap<String, List<ErrorDetails>>();
                
                List<ErrorDetails> errorDetailsList = errorDetails.get(typeOfResults);
                if (errorDetailsList == null)
                    errorDetailsList = new ArrayList<ErrorDetails>();
                
                ErrorDetails errorDetail = new ErrorDetails();
                //System.out.println(typeOfResults+":"+result.toString());
                if (result.has("error_message"))
                    errorDetail.errorMessage = result.getString("error_message");
                else errorDetail.errorMessage = "NotKnown";
                
                errorDetail.time = result.getString("last_occured_time");
                
                if (result.has("error_count"))
                    errorDetail.errorCount = result.getInt("error_count");
                else if (result.has("doc_count"))
                    errorDetail.errorCount = result.getInt("doc_count"); 
                
                errorDetailsList.add(errorDetail);
                errorDetails.put(typeOfResults, errorDetailsList);
                
                orgToErrorDetailsMap.put(orgId, errorDetails);
            }
        }
    }
}
