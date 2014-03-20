package com.apixio.qa.hive.resource;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.json.JSONException;
import org.json.JSONObject;

import com.apixio.qa.hive.resource.generated.Queries.Group;
import com.apixio.qa.hive.resource.generated.Queries.Group.RunQuery;

public class QueryManager
{
    private QueryHandler queryHandler;
    private String hiveAddress;
    private String outputDir;
    
    public static void main(String[] args) throws SQLException, JSONException, FileNotFoundException, IOException, ClassNotFoundException {
    	String hiveAddress = "jdbc:hive2://184.169.209.24:10000";
    	String outputDir = "C:\\alarocca_git\\QA\\dashboard\\assets\\reports\\json\\";
    	QueryManager qm = new QueryManager(hiveAddress, outputDir);
    	qm.processQueryGroup("completeness");
    }
    
    public QueryManager(String hiveAddress, String outputDir)
    {
    	this.hiveAddress = hiveAddress;
    	this.outputDir = outputDir;
        queryHandler = new QueryHandler();
    }
    
    public JSONObject processQueryGroup(String groupName) throws SQLException, JSONException, FileNotFoundException, IOException, ClassNotFoundException
    {
        Group groupToRun = QueryConfig.getQueryGroupByName(groupName);
        
        List<RunQuery> rQs = groupToRun.getRunQuery();
        
        JSONObject processedGroup = null;
        if (groupName.equalsIgnoreCase("completeness")) {
        	processedGroup = processCompletenessGroup(rQs);
        }
        return processedGroup;
    }
    
    private JSONObject processCompletenessGroup(List<RunQuery> runQueries) throws SQLException, JSONException, FileNotFoundException, IOException, ClassNotFoundException
    {
        JSONObject resultObj = null;
        if (runQueries != null)
        {
            resultObj =  new JSONObject();
            JSONObject orgDetails = new JSONObject();
            resultObj.put("orgDetails", orgDetails);
            for (RunQuery rQ : runQueries)
            {
            	List<JSONObject> results = null;
            	File jsonFile = new File(outputDir + rQ.getName());
            	
            	if (jsonFile.exists()) { 
            		Scanner scanner = new Scanner(jsonFile);
            		results = new ArrayList<JSONObject>();
            		while (scanner.hasNextLine()) {
            			results.add(new JSONObject(scanner.nextLine()));
            		}
            		scanner.close();
            	} else {
	            	results = queryHandler.runQuery(hiveAddress, rQ);
                    IOUtils.write(StringUtils.join(results, "\n"), new FileOutputStream(jsonFile));
            	}
            	
                //TODO save the results in cache...
            	if (rQ.getName().equalsIgnoreCase("archivedToS3_count"))
            	{
            	}
            	else if (rQ.getName().equalsIgnoreCase("parse_count"))
                {
                    for (JSONObject result : results)
                    {
                    	String org_id = result.getString("org_id");
                    	String status = result.getString("status");
                    	String doc_count = result.getString("doc_count");
                    	if (status.equals("success")) {
                    		JSONObject orgObject = null;
                    		if (orgDetails.has(org_id)) {
                    			orgObject = orgDetails.getJSONObject(org_id);
                    		} else {
                    			orgObject = new JSONObject();
                    			orgDetails.put(org_id, orgObject);
                    			orgObject.put("org_id", org_id);
                    		}
                    		if (result.has("sent_to_persist")) {
                    			orgObject.put("sent_to_persist", doc_count);
                    		} else if (result.has("sent_to_ocr")) {
                    			orgObject.put("sent_to_ocr", doc_count);                    			
                    		}
                    	}
                    }
                }
            }
        }
        System.out.println(resultObj);
        return null;
    }
    
}
