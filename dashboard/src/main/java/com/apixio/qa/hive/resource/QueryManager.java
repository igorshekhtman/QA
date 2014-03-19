package com.apixio.qa.hive.resource;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import org.json.JSONException;
import org.json.JSONObject;

import com.apixio.qa.hive.resource.generated.Queries.Group;
import com.apixio.qa.hive.resource.generated.Queries.Group.RunQuery;

public class QueryManager
{
    private QueryHandler queryHandler;
    
    public QueryManager()
    {
        queryHandler = new QueryHandler();
    }
    
    public JSONObject processQueryGroup(String groupName)
    {
        Group groupToRun = QueryConfig.getQueryGroupByName(groupName);
        
        List<RunQuery> rQs = groupToRun.getRunQuery();
        
        return null;
    }
    
    private JSONObject processCompletenessGroup(List<RunQuery> runQueries) throws SQLException, JSONException
    {
        if (runQueries != null)
        {
            JSONObject resultObj = new JSONObject();
            
            for (RunQuery rQ : runQueries)
            {
                List<JSONObject> results = queryHandler.runQuery(rQ);
                
                //TODO save the results in cache...
                if (rQ.getName().equalsIgnoreCase("parse_count"))
                {
                    List<JSONObject> erroredParsers = new ArrayList<JSONObject>();
                    List<JSONObject> successParsers = new ArrayList<JSONObject>();
                    
                    List<JSONObject> taggedToOCR = new ArrayList<JSONObject>();
                    List<JSONObject> taggedToPersist = new ArrayList<JSONObject>();
                    
                    for (JSONObject jObj : results)
                    {
                        String status = (String)jObj.get("status");
                        if (status.equalsIgnoreCase("error"))
                            erroredParsers.add(jObj);
                        else
                            erroredParsers.add(jObj);
                        
                        if (jObj.get("sent_to_ocr") != null && ((String)jObj.get("sent_to_ocr")).equalsIgnoreCase("success"))
                        {
                            //taggedToOCR.
                        }
                    }
                    
                    resultObj.put("error_parsers", erroredParsers);
                    resultObj.put("success_parsers", successParsers);
                }
                //else if (rQ.getName())
            }
        }
        return null;
    }
    
}
