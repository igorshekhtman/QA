package com.apixio.qa.hive.query;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;

import org.json.JSONObject;

import com.apixio.qa.hive.query.generated.Queries;

public abstract class QueryProcessor
{
    protected Properties orgProperties;

    public QueryProcessor()
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
    
    public abstract JSONObject processQuery(QueryHandler queryHandler, String outputDir, String environment, List<Queries.Group.RunQuery> runQueries) 
            throws Exception;
    
    
    protected abstract void collectResults(List<JSONObject> results, String typeOfResults, Object resultsCollection)
            throws Exception;
    
    protected List<String> getSortedKeys(Iterator<String> keyIterator)
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
    
    protected List<Long> getSortedLongKeys(Iterator<String> keyIterator)
    {
        if (keyIterator != null && keyIterator.hasNext())
        {
            List<Long> orgIds = new ArrayList<Long>();
            while (keyIterator.hasNext())
            {
                String key = keyIterator.next();
                if (!key.trim().equalsIgnoreCase("null"))
                    orgIds.add(Long.parseLong(key));
            }
            
            Collections.sort(orgIds, new Comparator<Long>()
            {
                public int compare(Long o1, Long o2)
                {
                    return o1.compareTo(o2);
                }
            });
            
            return orgIds;
        }
        return null;
    }
    
    protected JSONObject createJSONObject(Object resultsCollection, String orgId) throws Exception
    {
        JSONObject obj = new JSONObject();

        obj.put("org_id", orgId);
        obj.put("org_name", orgProperties.getProperty(orgId, ""));
        
        return obj;
    }
}
