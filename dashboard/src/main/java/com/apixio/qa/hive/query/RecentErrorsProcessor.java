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
