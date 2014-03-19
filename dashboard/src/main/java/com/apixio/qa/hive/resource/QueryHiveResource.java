package com.apixio.qa.hive.resource;

import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import org.json.JSONObject;

import com.apixio.qa.hive.QueryHive;
import com.apixio.qa.hive.manager.DocumentCountManager;
import com.apixio.qa.hive.resource.generated.Queries.Group;
import com.apixio.qa.hive.resource.generated.Queries.Group.RunQuery;
import com.google.common.base.Optional;
import com.yammer.metrics.annotation.Timed;

@Path("/hive")
@Produces(MediaType.APPLICATION_JSON)
public class QueryHiveResource
{
    private final String hiveAddress;
    private final AtomicLong counter;
    private DocumentCountManager dcm;
    private QueryHandler queryManager;

    public QueryHiveResource(String hiveAddress, String updateInterval)
    {
        this.hiveAddress = hiveAddress;
        this.counter = new AtomicLong();
        this.dcm = new DocumentCountManager(hiveAddress,updateInterval);
        queryManager = new QueryHandler();
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
    @Path("/json/{environment}/{component}")
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
    @Path("/json/{environment}/{groupName}")
    @Timed
    public String runGroup(@PathParam("environment") String environment, @QueryParam("startdate") String startDate, @QueryParam("enddate") String endDate,
            @QueryParam("groupName") String groupName)
    {
        try
        {
            Group groupToRun = QueryConfig.getQueryGroupByName(groupName);
            QueryHandler qm = new QueryHandler();
            
            List<RunQuery> rQs = groupToRun.getRunQuery();
            
            if (rQs != null)
            {
                for (RunQuery rQ : rQs)
                {
                    List<JSONObject> results = qm.runQuery(rQ);
                    
                }
            }
            return null;
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }
}
