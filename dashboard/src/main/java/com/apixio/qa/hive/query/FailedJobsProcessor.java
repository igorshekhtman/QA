package com.apixio.qa.hive.query;

import com.apixio.qa.hive.cache.CacheManager;
import com.apixio.qa.hive.query.generated.Queries;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.*;

/**
 * Created by nkrishna on 6/11/14.
 */
public class FailedJobsProcessor
{
    private Properties orgProperties;

    public FailedJobsProcessor()
    {
        try
        {
            orgProperties = new Properties();
            orgProperties.load(Thread.currentThread().getContextClassLoader().getResourceAsStream("prod_orgid_names.properties"));
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }

    private class FailedJobsDetails
    {
        String time;
        String hadoopJobId;
        String internalJobId;
        String batchId;
    }

    public JSONObject processFailedJobs(QueryHandler queryHandler, String outputDir, String environment, List<Queries.Group.RunQuery> runQueries) throws Exception
    {
        JSONObject resultObj = null;
        CacheManager cache = new CacheManager(environment, outputDir);

        if (runQueries != null)
        {
            resultObj = new JSONObject();
            Map<String, Map<String, List<FailedJobsDetails>>> orgToFailedJobsMap = new HashMap<String, Map<String,List<FailedJobsDetails>>>();

            for (Queries.Group.RunQuery rQ : runQueries)
            {
                //Fetch data from cache...
                List<JSONObject> results = cache.fetchResults(rQ.getName());

                if (results == null)
                {
                    results = queryHandler.runQuery(environment, rQ);
                    cache.writeResults(results, rQ.getName());
                }
                //Just collect all types of errors
                getFailedJobsObject(results, rQ.getName(), orgToFailedJobsMap);
            }

            Iterator<String> it = orgToFailedJobsMap.keySet().iterator();
            //Order each type of errors in descending order of time
            while (it.hasNext())
            {
                Map<String, List<FailedJobsDetails>> errorDetailsMap = orgToFailedJobsMap.get(it.next());

                Iterator<String> itErrors = orgToFailedJobsMap.keySet().iterator();

                while (itErrors.hasNext())
                {
                    List<FailedJobsDetails> errorDetailsList = errorDetailsMap.get(itErrors.next());
                    if (errorDetailsList != null)
                        orderErrorsByTime(errorDetailsList);
                }
            }

            JSONArray resultArray = new JSONArray();
            //Order the results by orgId
            List<String> sortedList = getSortedKeys(orgToFailedJobsMap.keySet().iterator());
            for (String orgId : sortedList)
            {
                String key = orgId.toString();
                //Create JSONObject
                JSONObject obj = createJSONObject(orgToFailedJobsMap.get(key), key);
                resultArray.put(obj);
            }
            resultObj.put("results", resultArray);
        }
        return resultObj;
    }

    private void getFailedJobsObject(List<JSONObject> results, String typeOfResults, Map<String, Map<String, List<FailedJobsDetails>>> orgToFailedJobsMap)
            throws Exception
    {
        for (JSONObject result : results)
        {
            String orgId = result.getString("org_id");
            if (orgId != null && !orgId.equalsIgnoreCase("__HIVE_DEFAULT_PARTITION__")
                    && result.has("status") && result.getString("status").equals("error"))
            {
                String activityName = result.getString("activity");
                Map<String, List<FailedJobsDetails>> failedDetails = orgToFailedJobsMap.get(orgId);
                if (failedDetails == null)
                    failedDetails = new HashMap<String, List<FailedJobsDetails>>();

                List<FailedJobsDetails> errorDetailsList = failedDetails.get(activityName);
                if (errorDetailsList == null)
                    errorDetailsList = new ArrayList<FailedJobsDetails>();

                FailedJobsDetails errorDetail = new FailedJobsDetails();
                //System.out.println(typeOfResults+":"+result.toString());

                errorDetail.time = result.getString("failed_time");
                errorDetail.hadoopJobId = result.getString("hadoop_job_id");
                errorDetail.internalJobId = result.getString("job_id");
                if (result.has("batch_id"))
                    errorDetail.batchId = result.getString("batch_id");

                errorDetailsList.add(errorDetail);
                failedDetails.put(activityName, errorDetailsList);

                orgToFailedJobsMap.put(orgId, failedDetails);
            }
        }
    }

    private List<String> getSortedKeys(Iterator<String> keyIterator)
    {
        if (keyIterator != null && keyIterator.hasNext())
        {
            List<String> orgIds = new ArrayList<String>();
            while (keyIterator.hasNext())
            {
                String key = keyIterator.next();
                if (!key.trim().equalsIgnoreCase("null"))
                {
                    orgIds.add(key);
                }
            }

            Collections.sort(orgIds, new Comparator<String>()
            {
                public int compare(String o1, String o2)
                {
                    return o1.compareTo(o2);
                }
            });

            return orgIds;
        }
        return null;
    }

    private JSONObject createJSONObject(Map<String, List<FailedJobsDetails>> errorDetailsMap, String orgId)
            throws Exception
    {
        JSONObject obj = new JSONObject();

        obj.put("org_id", orgId);
        obj.put("org_name", orgProperties.getProperty(orgId, ""));

        Iterator<String> it = errorDetailsMap.keySet().iterator();
        while (it.hasNext())
        {
            String activity = it.next();
            JSONArray errorArray = new JSONArray();
            String trackDay = null;
            int countResults = 0;

            for (FailedJobsDetails e : errorDetailsMap.get(activity))
            {
                //Add only first 2 days (recent) ones...
                String day = e.time.substring(0, e.time.indexOf("T"));
                if (countResults < 100)
                {
                    if (trackDay == null || !trackDay.equals(day))
                        countResults ++;

                    JSONObject errObj = new JSONObject();
                    errObj.put("time", e.time);
                    errObj.put("hadoop_job_id", e.hadoopJobId);
                    errObj.put("batch_id", e.batchId);
                    errObj.put("job_id", e.internalJobId);
                    errorArray.put(errObj);

                    trackDay = day;
                }
                else break;
            }

            obj.put(activity, errorArray);
        }

        return obj;
    }

    private void orderErrorsByTime(List<FailedJobsDetails> errorDetailsList)
    {
        Collections.sort(errorDetailsList, new Comparator<FailedJobsDetails>()
        {
            public int compare(FailedJobsDetails o1, FailedJobsDetails o2)
            {
                return o2.time.compareTo(o1.time);
            }
        });
    }
}
