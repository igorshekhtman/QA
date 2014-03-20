package com.apixio.qa.hive.resource;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.json.JSONObject;

import com.apixio.qa.hive.resource.generated.Queries.Group;
import com.apixio.qa.hive.resource.generated.Queries.Group.RunQuery;

public class QueryManager
{
    private QueryHandler queryHandler;
    private String hiveAddress;
    private String outputDir;

    public static void main(String[] args) throws Exception
    {
        String hiveAddress = "jdbc:hive2://184.169.209.24:10000";
        String outputDir = "C:/Users/nkrishna/Documents/apixio/docs/hive/";
        QueryManager qm = new QueryManager(hiveAddress, outputDir);
        qm.processQueryGroup("completeness");
    }

    public QueryManager(String hiveAddress, String outputDir)
    {
        this.hiveAddress = hiveAddress;
        this.outputDir = outputDir;
        queryHandler = new QueryHandler();
    }

    public JSONObject processQueryGroup(String groupName) throws Exception
    {
        Group groupToRun = QueryConfig.getQueryGroupByName(groupName);

        List<RunQuery> rQs = groupToRun.getRunQuery();

        JSONObject processedGroup = null;
        if (groupToRun.getName().equalsIgnoreCase("completeness"))
        {
            processedGroup = processCompletenessGroup(rQs);
        }
        //TODO else just run the group and return results.. 
        return processedGroup;
    }

    private JSONObject processCompletenessGroup(List<RunQuery> runQueries) throws Exception
    {
        JSONObject resultObj = null;
        if (runQueries != null)
        {
            resultObj = new JSONObject();
            JSONObject orgDetails = new JSONObject();

            for (RunQuery rQ : runQueries)
            {
                List<JSONObject> results = null;
                File jsonFile = new File(outputDir + rQ.getName());

                if (jsonFile.exists())
                {
                    Scanner scanner = new Scanner(jsonFile);
                    results = new ArrayList<JSONObject>();
                    while (scanner.hasNextLine())
                    {
                        results.add(new JSONObject(scanner.nextLine()));
                    }
                    scanner.close();
                }
                else
                {
                    results = queryHandler.runQuery(hiveAddress, rQ);
                    IOUtils.write(StringUtils.join(results, "\n"), new FileOutputStream(jsonFile));
                }

                getOrgObject(results, rQ.getName(), orgDetails);
            }

            resultObj.put("orgDetails", orgDetails);
        }
        System.out.println(resultObj);
        return resultObj;
    }

    private void getOrgObject(List<JSONObject> results, String typeOfResults, JSONObject orgDetails) throws Exception
    {
        for (JSONObject result : results)
        {
            String org_id = result.getString("org_id");
            String status = "NotKnown";
            String errorMsg = "NotKnown";
            
            if (result.has("error_message"))
                errorMsg = result.getString("error_message");
            
            Integer doc_count = result.getInt("doc_count");
            
            JSONObject orgObject = null;
            
            if (orgDetails.has(org_id))
            {
                orgObject = orgDetails.getJSONObject(org_id);
            }
            else
            {
                orgObject = new JSONObject();
            }
            
            if (result.has("status"))
                status = result.getString("status");
            
            if (status.equals("success"))
            {
                if (typeOfResults.equalsIgnoreCase("parse_count"))
                {
                    if (result.has("sent_to_persist"))
                    {
                        orgObject.put("sent_to_persist", doc_count);
                    }
                    else if (result.has("sent_to_ocr"))
                    {
                        orgObject.put("sent_to_ocr", doc_count);
                    }
                }
                else if (typeOfResults.equalsIgnoreCase("persist_count"))
                {
                    orgObject.put("persist_success", doc_count);
                }
                else if (typeOfResults.equalsIgnoreCase("ocr_count"))
                {
                    orgObject.put("ocr_success", doc_count);
                }
                else if (typeOfResults.equalsIgnoreCase("verified_count"))
                {
                    orgObject.put("persist_verified", doc_count);
                }
                else if (typeOfResults.equalsIgnoreCase("archivedToS3_count"))
                {
                    orgObject.put("archive_success", doc_count);
                }
            }
            else if (status.equals("error"))
            {
                JSONObject errorObject = new JSONObject();
                
                if (typeOfResults.equalsIgnoreCase("parse_count"))
                {
                    if (orgObject.has("parse_errors"))
                    {
                        errorObject = (JSONObject)orgObject.get("parse_errors");
                    }
                    errorObject.put(errorMsg, errorObject.has(errorMsg)?
                            (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
                    
                    orgObject.put("parse_errors", errorObject);
                }
                else if (typeOfResults.equalsIgnoreCase("persist_count"))
                {
                    if (orgObject.has("persist_errors"))
                    {
                        errorObject = (JSONObject)orgObject.get("persist_errors");
                    }
                    errorObject.put(errorMsg, errorObject.has(errorMsg)?
                            (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
                    
                    orgObject.put("persist_errors", errorObject);
                }
                else if (typeOfResults.equalsIgnoreCase("ocr_count"))
                {
                    if (orgObject.has("ocr_errors"))
                    {
                        errorObject = (JSONObject)orgObject.get("ocr_errors");
                    }
                    errorObject.put(errorMsg, errorObject.has(errorMsg)?
                            (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
                    
                    orgObject.put("ocr_errors", errorObject);
                }
                else if (typeOfResults.equalsIgnoreCase("archivedToS3_count"))
                {
                    if (orgObject.has("archive_errors"))
                    {
                        errorObject = (JSONObject)orgObject.get("archive_errors");
                    }
                    errorObject.put(errorMsg, errorObject.has(errorMsg)?
                            (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
                    
                    orgObject.put("archive_errors", errorObject);
                }
            }
            
            orgDetails.put(org_id, orgObject);
        }
    }
}
