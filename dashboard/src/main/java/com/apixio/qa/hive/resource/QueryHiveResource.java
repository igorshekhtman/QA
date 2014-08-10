package com.apixio.qa.hive.resource;

import java.io.FileOutputStream;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
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
import com.apixio.qa.hive.query.generated.Queries.Group;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;
import com.google.common.base.Optional;
import com.yammer.metrics.annotation.Timed;

@Path("/hive")
@Produces(MediaType.APPLICATION_JSON)
public class QueryHiveResource
{
    public static final String LIMIT = "100";
    private final String hiveAddress;
    private final String outputDir;
    private final String manifestDir;
    private final AtomicLong guard;
    private DocumentCountManager dcm;
    private QueryManager queryManager;

    public QueryHiveResource(String hiveAddress, String updateInterval, String outputDir, String manifestDir)
    {
        this.hiveAddress = hiveAddress;
        this.outputDir = outputDir;
        this.manifestDir = manifestDir;
        this.guard = new AtomicLong();
        this.dcm = new DocumentCountManager(hiveAddress,updateInterval);
        queryManager = new QueryManager(hiveAddress, outputDir, manifestDir);
    }

    @GET
    @Path("/query")
    @Timed
    public String query(@QueryParam("query") String query, @QueryParam("limit") String limit)
    {
        if (limit == null)
            limit = LIMIT;
        else if (limit.equals("-1"))
            limit = Long.toString(1000*1000*1000);
        // limit returns and mild sql injection attack prevention
        String wrapped = "select * from (" + query + ") X limit " + limit;
        try
        {
            System.out.println("wrapped query: " + wrapped);
            return QueryHive.queryHive(hiveAddress,wrapped);
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    /**
     * Do query and return in afterquery format
     * [["time","field1","field2"],["2014-etc.","1","2"],...]
     * 
     * Only allow one at a time. Afterquery editor is twitchy.
     * 
     * @param query
     * @param fields
     *  overrides field names from Hive
     * @param jsonp
     *  whether to wrap with jsonp string
     * @return
     */
    @GET
    @Path("/after")
    @Timed
    public String after(@QueryParam("query") String query, @QueryParam("fields") String fields, 
                    @QueryParam("jsonp") String jsonp, @QueryParam("limit") String limit)
    {
        synchronized(guard) {
            if (guard.get() > 0)
                return "only one hive query at a time, please";
            guard.incrementAndGet();
        }
        try
        {
            if (limit == null)
                limit = LIMIT;
            // limit returns and mild sql injection attack prevention
            String wrapped = "select * from (" + query + ") X limit " + limit;
            System.out.println("wrapped query: " + wrapped);
            System.out.println("fields: " + fields);
            StringBuilder sb = new StringBuilder();
            String[] fieldset = fields.split("[,]");
            if (jsonp != null) 
                sb.append(jsonp + "(");
            sb.append("[[");
            for(String field: fieldset) 
                sb.append("\"" + field + "\",");
            sb.setLength(sb.length() - 1);
            sb.append("],");
            List<JSONObject> result = QueryHive.queryHiveJson(hiveAddress,wrapped);
            for(JSONObject jsonob: result) {
                String time = null;
                sb.append("[");
                for(String field: fieldset) {
                    Object cell = JSONObject.quote(jsonob.get(field).toString());
                    sb.append(cell.toString() + ",");
                }
                sb.setLength(sb.length() - 1);
                sb.append("],");
            }
            sb.setLength(sb.length() - 1);
            sb.append("]");
            if (jsonp != null)
                sb.append(")");
            System.out.println("Return: " + sb.toString());
            guard.decrementAndGet();
            return sb.toString();
        }
        catch (Exception ex)
        {
            guard.decrementAndGet();
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
            return SummaryQueryUtilities.getCoordinatorStats(hiveAddress, environment, filterStat.or(""), startDate, endDate).toString();
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
    public String runGroup(@PathParam("environment") String environment, @PathParam("groupName") String groupName, @QueryParam("orgId") String orgId)
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

                    if (environment.equalsIgnoreCase("staging"))
                        fileName = outputDir + environment.toLowerCase() + "/" + rQ.getName();

                    List<JSONObject> results = qm.runQuery(environment, rQ);
                    System.out.println("Writing to file:"+fileName);
                    IOUtils.write(StringUtils.join(results, "\n"), new FileOutputStream(fileName));
                    return results.toString();
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
                List<JSONObject> results = queryManager.processQuery(environment, queryName, uriInfo.getQueryParameters());
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
    @Path("/table/query/{tableName}/{queryName}")
    @Timed
    public String runQueryOnTable(@PathParam("tableName") String tableName, @PathParam("queryName") String queryName, @Context UriInfo uriInfo)
    {
        try
        {
            if (queryName != null)
            {
                List<JSONObject> results = queryManager.processQueryByTableName(tableName, queryName, uriInfo.getQueryParameters());
                if (results == null)
                    return "Error while trying to execute the query "+queryName+". Please make sure that query exists in queries.xml file";
                System.out.println(results);
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
            QueryManager qm = new QueryManager(hiveAddress, outputDir, manifestDir);

            return qm.processQueryGroup(environment, groupName).toString();
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
            return ex.toString();
        }
    }

    @GET
    @Path("/manifest/{environment}/{queryName}")
    @Timed
    public String getManifestForRecovery(@PathParam("environment") String environment, @PathParam("queryName") String queryName, 
                    @Context UriInfo uriInfo)
    {
        try
        {
            QueryManager qm = new QueryManager(hiveAddress, outputDir, manifestDir);

            return qm.processManifestQuery(environment, queryName, uriInfo.getQueryParameters());
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
            return ex.toString();
        }
    }
}
