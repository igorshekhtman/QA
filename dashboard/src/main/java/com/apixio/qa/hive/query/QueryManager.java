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
        //qm.processQueryGroup("completeness");
        
        Group groupToRun = QueryConfig.getQueryGroupByName("completeness");
        List<RunQuery> rQs = groupToRun.getRunQuery();

        IOUtils.write(qm.processChartDetails(rQs), new FileOutputStream(outputDir+"orgcompletenesschart.json"));
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
    
    public String processQueryGroupChart(String groupName) throws Exception
    {
        Group groupToRun = QueryConfig.getQueryGroupByName(groupName);

        List<RunQuery> rQs = groupToRun.getRunQuery();

        if (groupToRun.getName().equalsIgnoreCase("completeness"))
        {
            return processChartDetails(rQs);
        }
        //TODO else just run the group and return results.. 
        return null;
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
    
    private String processChartDetails(List<RunQuery> runQueries) throws Exception
    {
        if (runQueries != null)
        {
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

                getChartDataForOrgs(results, rQ.getName(), orgDetails);
            }
            
            Iterator it = orgDetails.keys();
            List<JSONObject> resultObjs = new ArrayList<JSONObject>();
            while (it.hasNext())
            {
                resultObjs.add((JSONObject)orgDetails.get(it.next().toString()));
            }
            
            return resultObjs.toString();
        }
        return null;
    }

    private JSONObject processCompletenessGroup(List<RunQuery> runQueries) throws Exception
    {
        JSONObject resultObj = null;
        if (runQueries != null)
        {
            resultObj = new JSONObject();
            JSONObject orgDetails = new JSONObject();
            JSONObject chartOrgDetails = new JSONObject();

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
                getChartDataForOrgs(results, rQ.getName(), chartOrgDetails);
            }

            Iterator addChartIt = orgDetails.keys();
            while (addChartIt.hasNext())
            {
                String key = addChartIt.next().toString();
                
                List<JSONObject> chartDetail = new ArrayList<JSONObject>();
                chartDetail.add((JSONObject)chartOrgDetails.get(key));
                
                JSONObject chart = (JSONObject)orgDetails.get(key);
                chart.put("chart", chartDetail);
                
                orgDetails.put(key, chart);
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
                    status = result.getString("status");
                else
                    orgObject.put("persist_verified", doc_count);
                
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
                    else
                    {
                        orgObject.put(typeOfResults, doc_count);
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
                
                orgDetails.put(orgId, orgObject);
            }
        }
    }
    
    private JSONObject getChartDataForOrgs(List<JSONObject> results, String typeOfResults, JSONObject orgChartDetails) throws Exception
    {
        for (JSONObject result : results)
        {
            String orgId = result.getString("org_id");
            String status = "NotKnown";
            Integer doc_count = 0;
            
            if (result.has("doc_count"))
                doc_count = result.getInt("doc_count");
            
            if (orgId != null && !orgId.equalsIgnoreCase("__HIVE_DEFAULT_PARTITION__"))
            {
                JSONObject orgObject = null;
                List<Integer> rangeList = null;
                List<Integer> measureList = null;
                List<Integer> markerList = null;
                
                if (orgChartDetails.has(orgId))
                {
                    orgObject = orgChartDetails.getJSONObject(orgId);
                    rangeList = convertJsonArrayToList(orgObject.getJSONArray("ranges"));
                    measureList = convertJsonArrayToList(orgObject.getJSONArray("measures"));
                    markerList = convertJsonArrayToList(orgObject.getJSONArray("markers"));
                }
                else
                {
                    orgObject = new JSONObject();
                    orgObject.put("subtitle", orgId);
                    orgObject.put("title", orgProperties.getProperty(orgId, ""));
                    
                    rangeList = new ArrayList<Integer>();
                    rangeList.add(0, 0);
                    
                    orgObject.put("ranges", rangeList);
                    
                    measureList = new ArrayList<Integer>();
                    measureList.add(0, 0);
                    measureList.add(1, 0);
                    measureList.add(2, 0);
                    measureList.add(3, 0);
                    
                    orgObject.put("measures", measureList);
                    
                    markerList = new ArrayList<Integer>();
                    markerList.add(0, 0);
                    
                    orgObject.put("markers", markerList);
                }
                
                if (result.has("status"))
                    status = result.getString("status");
                else
                {
                    replaceDataInList(measureList, doc_count, 3);
                }
                
                if (status.equals("success"))
                {
                    if (typeOfResults.equalsIgnoreCase("parse_count"))
                    {
                        replaceDataInList(measureList, doc_count, 0);
                    }
                    else if (typeOfResults.equalsIgnoreCase("upload_count"))
                    {
                        replaceDataInList(rangeList, doc_count, 0);
                        replaceDataInList(markerList, doc_count, 0);
                    }
                    else if (typeOfResults.equalsIgnoreCase("ocr_count"))
                    {
                        replaceDataInList(measureList, doc_count, 2);
                    }
                    else if (typeOfResults.equalsIgnoreCase("persist_count"))
                    {
                        replaceDataInList(measureList, doc_count, 1);
                    }
                }
                
                orgObject.put("ranges", rangeList);
                orgObject.put("measures", measureList);
                orgObject.put("markers", markerList);
                
                orgChartDetails.put(orgId, orgObject);
            }
        }
        
        return orgChartDetails;
    }
    
    private List<Integer> convertJsonArrayToList(JSONArray jsonArray) throws Exception
    {
        List<Integer> list = new ArrayList<Integer>();
        
        for (int i=0; i<jsonArray.length(); i++) 
        {
            list.add( (Integer)jsonArray.getInt(i) );
        }
        return list;
    }
    
    private List<Integer> replaceDataInList(List<Integer> listToModify, Integer data, int index)
    {
        Integer oldData = listToModify.get(index);
        
        listToModify.remove(index);
        listToModify.add(index, oldData+data);
        
        return listToModify;
    }
}
