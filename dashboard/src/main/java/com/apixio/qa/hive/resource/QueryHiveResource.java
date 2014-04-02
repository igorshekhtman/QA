package com.apixio.qa.hive.resource;

import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.MultivaluedMap;
import javax.ws.rs.core.UriInfo;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.json.JSONObject;

import com.apixio.qa.hive.QueryHive;
import com.apixio.qa.hive.SummaryQueryUtilities;
import com.apixio.qa.hive.manager.DocumentCountManager;
import com.apixio.qa.hive.query.QueryConfig;
import com.apixio.qa.hive.query.QueryHandler;
import com.apixio.qa.hive.query.QueryManager;
import com.apixio.qa.hive.query.generated.Queries;
import com.apixio.qa.hive.query.generated.Queries.Group;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery.Param;
import com.apixio.qa.hive.query.generated.Queries.Query;
import com.google.common.base.Optional;
import com.yammer.metrics.annotation.Timed;

@Path("/hive")
@Produces(MediaType.APPLICATION_JSON)
public class QueryHiveResource
{
    private final String hiveAddress;
    private final String outputDir;
    private final AtomicLong counter;
    private DocumentCountManager dcm;
    private QueryHandler queryManager;

    public QueryHiveResource(String hiveAddress, String updateInterval, String outputDir)
    {
        this.hiveAddress = hiveAddress;
        this.outputDir = outputDir;
        this.counter = new AtomicLong();
        this.dcm = new DocumentCountManager(hiveAddress,updateInterval);
        queryManager = new QueryHandler(hiveAddress);
    }

    @GET
    @Path("/query")
    @Timed
    public String query(@QueryParam("query") String query)
    {
        try
        {
    		return QueryHive.queryHive(hiveAddress,query);
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    @GET
    @Path("/document_count/{environment}")
    @Timed
    public String documentCount(@PathParam("environment") String environment)
    {
        try
        {
            return dcm.getDocumentCount(environment);
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    @GET
    @Path("/json/{environment}/component/{component}")
    @Timed
    public String rawQuery(@PathParam("environment") String environment, @PathParam("component") String component, @QueryParam("startdate") Optional<String> startDate,
            @QueryParam("enddate") Optional<String> endDate, @QueryParam("level") Optional<String> level, @QueryParam("conditiononeobject") Optional<String> conditionOneObject,
            @QueryParam("conditiononevalue") Optional<String> conditionOneValue, @QueryParam("conditiontwoobject") Optional<String> conditionTwoObject,
            @QueryParam("conditiontwovalue") Optional<String> conditionTwoValue, @QueryParam("limit") Optional<String> limit)
    {
        try
        {
    		return QueryHive.rawQuery(hiveAddress,environment, component, startDate.or(""), endDate.or(""), level.or(""), conditionOneObject.or(""), conditionOneValue.or(""), conditionTwoObject.or(""), conditionTwoValue.or(""), limit.or(""));
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    @GET
    @Path("/json/{environment}/queue")
    @Timed
    public String coordinatorQueue(@PathParam("environment") String environment, @QueryParam("startdate") String startDate, @QueryParam("enddate") String endDate)
    {
        try
        {
    		return QueryHive.getQueueStats(hiveAddress,environment, startDate, endDate);
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }
    
    @GET
    @Path("/json/{environment}/stats")
    @Timed
    public String coordinatorStats(@PathParam("environment") String environment, @QueryParam("startdate") String startDate, @QueryParam("enddate") String endDate, @QueryParam("filterStat") Optional<String> filterStat)
    {
        try
        {
    		return 	SummaryQueryUtilities.getCoordinatorStats(hiveAddress, filterStat.or(""), startDate, endDate).toString();
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    @GET
    @Path("/json/{environment}/failed")
    @Timed
    public String coordinatorStatus(@PathParam("environment") String environment, @QueryParam("startdate") String startDate, @QueryParam("enddate") String endDate,
            @QueryParam("status") Optional<String> status)
    {
        try
        {
    		return QueryHive.getJobStats(hiveAddress,environment, startDate, endDate, status.or(""));
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }
    
    @GET
    @Path("/json/{environment}/group/{groupName}")
    @Timed
    public String runGroup(@PathParam("environment") String environment, @PathParam("groupName") String groupName)
    {
        try
        {
            Group groupToRun = QueryConfig.getQueryGroupByName(groupName);
            QueryHandler qm = new QueryHandler(hiveAddress);
            
            List<RunQuery> rQs = groupToRun.getRunQuery();
            
            if (rQs != null)
            {
                for (RunQuery rQ : rQs)
                {
                	String fileName = outputDir + rQ.getName();
                    List<JSONObject> results = qm.runQuery(rQ);
                    
                    IOUtils.write(StringUtils.join(results, "\n"), new FileOutputStream(fileName));
                }
            }
            return null;
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }
    
    @GET
    @Path("/query/{environment}/{queryName}")
    @Timed
    public String runQuery(@PathParam("environment") String environment, @PathParam("queryName") String queryName, @Context UriInfo uriInfo)
    {
        try
        {
            if (queryName != null)
            {
                QueryHandler qh = new QueryHandler(hiveAddress);
                List<JSONObject> results = qh.runQuery(queryName, uriInfo.getQueryParameters());
                if (results == null)
                    return "Error while trying to execute the query "+queryName+". Please make sure that query exists in queries.xml file";
                return results.toString();
            }
            return null;
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
            return ex.toString();
        }
    }
    
    @GET
    @Path("/json/{environment}/ui/group/{groupName}")
    @Timed
    public String runGroupUI(@PathParam("environment") String environment, @PathParam("groupName") String groupName)
    {
        try
        {
            QueryManager qm = new QueryManager(hiveAddress, outputDir);
            
            return qm.processQueryGroup(groupName).toString();
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
            return ex.toString();
        }
    }
}
