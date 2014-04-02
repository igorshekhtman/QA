package com.apixio.qa.hive.query;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;
import java.util.Scanner;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.json.JSONArray;
import org.json.JSONObject;

import com.apixio.qa.hive.query.generated.Queries.Group;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;

public class QueryManager
{
    private QueryHandler queryHandler;
    private String outputDir;
    private Properties orgProperties;

    public static void main(String[] args) throws Exception
    {
        String hiveAddress = "jdbc:hive2://184.169.209.24:10000";
        String outputDir = "C:/workspace_3/QA/dashboard/assets/reports/json/";
        QueryManager qm = new QueryManager(hiveAddress, outputDir);
        qm.processQueryGroup("completeness");
    }

    public QueryManager(String hiveAddress, String outputDir)
    {
        this.outputDir = outputDir;
        queryHandler = new QueryHandler(hiveAddress);
        
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
    
    public JSONObject processQueryGroup(String groupName) throws Exception
    {
        Group groupToRun = QueryConfig.getQueryGroupByName(groupName);

        List<RunQuery> rQs = groupToRun.getRunQuery();

        JSONObject processedGroup = null;
        if (groupToRun.getName().equalsIgnoreCase("completeness"))
        {
            processedGroup = processCompletenessGroup(rQs);
            System.out.println(processedGroup.toString());
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
                    results = queryHandler.runQuery(rQ);
                    IOUtils.write(StringUtils.join(results, "\n"), new FileOutputStream(jsonFile));
                }

                getOrgObject(results, rQ.getName(), orgDetails);
            }

            Iterator it = orgDetails.keys();
            JSONArray orgs = new JSONArray();
            while (it.hasNext())
            {
                String key = it.next().toString();
                
                orgs.put(orgDetails.get(key));
            }
            resultObj.put("orgs", orgs);
        }
        return resultObj;
    }
    
    private void getOrgObject(List<JSONObject> results, String typeOfResults, JSONObject orgDetails) throws Exception
    {
        for (JSONObject result : results)
        {
            String orgId = result.getString("org_id");
            
            if (orgId != null && !orgId.equalsIgnoreCase("__HIVE_DEFAULT_PARTITION__"))
            {
                String status = "NotKnown";
                String errorMsg = "NotKnown";
                
                if (result.has("error_message"))
                    errorMsg = result.getString("error_message");
                
                Integer doc_count = 0;
                if (result.has("doc_count"))
                    doc_count = result.getInt("doc_count");
                
                JSONObject orgObject = null;
                
                if (orgDetails.has(orgId))
                {
                    orgObject = orgDetails.getJSONObject(orgId);
                }
                else
                {
                    orgObject = new JSONObject();
                    orgObject.put("org_id", orgId);
                    orgObject.put("org_name", orgProperties.getProperty(orgId, ""));
                }
                
                if (result.has("status"))
                {
                    status = result.getString("status");
                }
                else
                {
                    fillPendingDocsData(orgObject, result, typeOfResults, doc_count);
                }
                
                if (status.equals("success"))
                {
                    fillSucceededData(orgObject, result, typeOfResults, doc_count);
                }
                else if (status.equals("error"))
                {
                    fillErroredData(orgObject, result, typeOfResults, errorMsg, doc_count);
                }
                
                orgDetails.put(orgId, orgObject);
            }
        }
    }
    
    private void fillPendingDocsData(JSONObject orgObject, JSONObject result, String typeOfResults, int doc_count) throws Exception
    {
        if (typeOfResults.equalsIgnoreCase("docs_queue"))
        {
            if (result.has("activity") && result.get("activity").toString().equalsIgnoreCase("parser"))
                orgObject.put("pending_parsers", doc_count);
            else if (result.has("activity") && result.get("activity").toString().equalsIgnoreCase("persist"))
                orgObject.put("pending_persists", result.get("sent_to_persist_count"));
            else if (result.has("activity") && result.get("activity").toString().equalsIgnoreCase("ocr"))
                orgObject.put("pending_ocrs", result.get("sent_to_ocr_count"));
        }
        else if (typeOfResults.equalsIgnoreCase("docs_in_failedjobs"))
        {
            if (result.has("activity") && result.get("activity").toString().equalsIgnoreCase("parser"))
                orgObject.put("failed_parsers", doc_count);
            else if (result.has("activity") && result.get("activity").toString().equalsIgnoreCase("persist"))
                orgObject.put("failed_persists", result.get("sent_to_persist_count"));
            else if (result.has("activity") && result.get("activity").toString().equalsIgnoreCase("ocr"))
                orgObject.put("failed_ocrs", result.get("sent_to_ocr_count"));
        }
        else if (typeOfResults.equalsIgnoreCase("docs_in_drq_count"))
        {
            JSONObject seqFileObject = new JSONObject();
            if (result.has("seqfile_file"))
            {
                String seqFileName = result.get("seqfile_file").toString();
                JSONObject seqFileDetails = new JSONObject();
                if (orgObject.has("docreceiver_queue_count"))
                {
                    seqFileObject = (JSONObject)orgObject.get("docreceiver_queue_count");
                }
                if (seqFileObject.has(seqFileName))
                {
                    seqFileDetails = (JSONObject)seqFileObject.get(seqFileName);
                }
                
                seqFileDetails.put("doc_count", seqFileDetails.has("doc_count")?
                        (((Integer)seqFileDetails.get("doc_count"))+doc_count):doc_count);
                seqFileDetails.put("last_updated", (result.has("updated_time")?result.get("updated_time"):""));
                seqFileObject.put(seqFileName, seqFileDetails);
            }
            
            orgObject.put("docreceiver_queue_count", seqFileObject);
        }
        else if (typeOfResults.equalsIgnoreCase("docs_abandoned_coordinator_count"))
        {
            JSONObject seqFileObject = new JSONObject();
            if (result.has("seqfile_file"))
            {
                String seqFileName = result.get("seqfile_file").toString();
                JSONObject seqFileDetails = new JSONObject();
                if (orgObject.has("docs_abandoned_count"))
                {
                    seqFileObject = (JSONObject)orgObject.get("docs_abandoned_count");
                }
                if (seqFileObject.has(seqFileName))
                {
                    seqFileDetails = (JSONObject)seqFileObject.get(seqFileName);
                }
                
                seqFileDetails.put("doc_count", seqFileDetails.has("doc_count")?
                        (((Integer)seqFileDetails.get("doc_count"))+doc_count):doc_count);
                seqFileDetails.put("posted_time", (result.has("posted_time")?result.get("posted_time"):""));
                seqFileObject.put(seqFileName, seqFileDetails);
            }
            
            orgObject.put("docs_abandoned_count", seqFileObject);
        }
        else orgObject.put(typeOfResults, doc_count);
    }
    
    private void fillSucceededData(JSONObject orgObject, JSONObject result, String typeOfResults, int doc_count) throws Exception
    {
        if (typeOfResults.equalsIgnoreCase("parse_success_count"))
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
        else orgObject.put(typeOfResults, doc_count);
    }
    
    private void fillErroredData(JSONObject orgObject, JSONObject result, String typeOfResults, String errorMsg, int doc_count) throws Exception
    {
        JSONObject errorObject = new JSONObject();
        
        if (typeOfResults.equalsIgnoreCase("parse_error_count"))
        {
            if (orgObject.has("parse_errors"))
            {
                errorObject = (JSONObject)orgObject.get("parse_errors");
            }
            errorObject.put(errorMsg, errorObject.has(errorMsg)?
                    (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
            
            orgObject.put("parse_errors", errorObject);
        }
        else if (typeOfResults.equalsIgnoreCase("persist_error_count"))
        {
            if (orgObject.has("persist_errors"))
            {
                errorObject = (JSONObject)orgObject.get("persist_errors");
            }
            errorObject.put(errorMsg, errorObject.has(errorMsg)?
                    (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
            
            orgObject.put("persist_errors", errorObject);
        }
        else if (typeOfResults.equalsIgnoreCase("ocr_error_count"))
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
        else if (typeOfResults.equalsIgnoreCase("upload_count"))
        {
            if (orgObject.has("upload_errors"))
            {
                errorObject = (JSONObject)orgObject.get("upload_errors");
            }
            errorObject.put(errorMsg, errorObject.has(errorMsg)?
                    (((Integer)errorObject.get(errorMsg))+doc_count):doc_count);
            
            orgObject.put("upload_errors", errorObject);
        }
    }
}
