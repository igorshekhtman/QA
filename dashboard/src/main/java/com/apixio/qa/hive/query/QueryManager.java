package com.apixio.qa.hive.query;

import java.util.List;
import java.util.Properties;

import javax.ws.rs.core.MultivaluedMap;

import org.json.JSONObject;

import com.apixio.qa.hive.manager.DocManifestManager;
import com.apixio.qa.hive.query.generated.Queries.Group;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;

public class QueryManager
{
    private QueryHandler queryHandler;
    private String outputDir;
    private String manifestDir;
    private Properties orgProperties;

    public static void main(String[] args) throws Exception
    {
        String hiveAddress = "jdbc:hive2://184.169.209.24:10000";
        String outputDir = "C:/workspace_3/QA/dashboard/assets/reports/json/";
        QueryManager qm = new QueryManager(hiveAddress, outputDir, null);
        qm.processQueryGroup("production", "completeness");
    }

    public QueryManager(String hiveAddress, String outputDir, String manifestDir)
    {
        this.outputDir = outputDir;
        this.manifestDir = manifestDir;
        if (this.manifestDir == null)
            this.manifestDir = outputDir;
        
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
    
    public List<JSONObject> processQuery(String environment, String queryName, MultivaluedMap<String, String> queryParams) throws Exception
    {
        List<JSONObject> results = queryHandler.runQuery(environment, queryName, queryParams);
        
        if (results != null)
        {
            if (queryName.equalsIgnoreCase("docs_in_drq"))
            {
                //Generate manifest for these docs
                DocManifestManager dmm = new DocManifestManager(environment, manifestDir);
                dmm.createDocManifestForRecovery(results, true);
            }
            return results;
        }
        return null;
    }
    
    public List<JSONObject> processQueryByTableName(String tableName, String queryName, MultivaluedMap<String, String> queryParams) throws Exception
    {
        List<JSONObject> results = queryHandler.runQuery(tableName, queryName, queryParams);
        
        return results;
    }
    
    public String processManifestQuery(String environment, String queryName, MultivaluedMap<String, String> queryParams) throws Exception
    {
        List<JSONObject> results = queryHandler.runQuery(environment, queryName, queryParams);
        
        if (results != null)
        {
            if (queryName.equalsIgnoreCase("manifest_recovery"))
            {
                //Generate manifest for these docs
                DocManifestManager dmm = new DocManifestManager(environment, manifestDir);
                return dmm.createDocManifestForRecovery(results, false);
            }
        }
        return null;
    }
    
    public JSONObject processQueryGroup(String environment, String groupName) throws Exception
    {
        Group groupToRun = QueryConfig.getQueryGroupByName(groupName);

        List<RunQuery> rQs = groupToRun.getRunQuery();

        JSONObject processedGroup = null;
        QueryProcessor processor = null;
        if (groupToRun.getName().equalsIgnoreCase("completeness"))
        {
            processor = new OrgCompletenessProcessor();
        }
        else if (groupToRun.getName().equalsIgnoreCase("recentErrors"))
        {
            processor = new RecentErrorsProcessor();
        }
        else if (groupToRun.getName().equalsIgnoreCase("failedJobs"))
        {
            processor = new FailedJobsProcessor();
        }
        
        if (processor != null)
            processedGroup = processor.processQuery(queryHandler, outputDir, environment, rQs);
        //TODO else just run the group and return results.. 
        return processedGroup;
    }
}
