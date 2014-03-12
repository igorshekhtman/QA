package apixio.hive.resource;

import java.util.concurrent.atomic.AtomicLong;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import apixio.hive.DocumentCountManager;
import apixio.hive.QueryHive;

import com.google.common.base.Optional;
import com.yammer.metrics.annotation.Timed;

@Path("/hive")
@Produces(MediaType.APPLICATION_JSON)
public class QueryHiveResource {
    private final String hiveAddress;
    private final AtomicLong counter;
    private DocumentCountManager dcm;
    public QueryHiveResource(String hiveAddress, String updateInterval) {
        this.hiveAddress = hiveAddress;
        this.counter = new AtomicLong();
        this.dcm = new DocumentCountManager(updateInterval);
    }

    @GET
    @Path("/query")
    @Timed
    public String query(@QueryParam("query") String query) {
        try
        {
    		return QueryHive.queryHive(query);
        }
        catch (Exception ex) {
        	return ex.toString();
        }
    }

    @GET
    @Path("/document_count/{environment}")
    @Timed
    public String documentCount(@PathParam("environment") String environment) {
        try
        {
    		return dcm.getDocumentCount(environment);
        }
        catch (Exception ex) {
        	return ex.toString();
        }
    }

    @GET
    @Path("/json/{environment}/{component}")
    @Timed
    public String rawQuery(@PathParam("environment") String environment,
    					   @PathParam("component") String component,
    					   @QueryParam("startdate") Optional<String> startDate,
    					   @QueryParam("enddate") Optional<String> endDate,
    					   @QueryParam("level") Optional<String> level,
    					   @QueryParam("conditiononeobject") Optional<String> conditionOneObject,
    					   @QueryParam("conditiononevalue") Optional<String> conditionOneValue,
    					   @QueryParam("conditiontwoobject") Optional<String> conditionTwoObject,
    					   @QueryParam("conditiontwovalue") Optional<String> conditionTwoValue,
    					   @QueryParam("limit") Optional<String> limit) {
        try
        {
    		return QueryHive.rawQuery(environment, component, startDate.or(""), endDate.or(""), level.or(""), conditionOneObject.or(""), conditionOneValue.or(""), conditionTwoObject.or(""), conditionTwoValue.or(""), limit.or(""));
        }
        catch (Exception ex) {
        	return ex.toString();
        }
    }
    
    @GET
    @Path("/json/{environment}/queue")
    @Timed
    public String coordinatorQueue(@PathParam("environment") String environment,
    					   @QueryParam("startdate") String startDate,
    					   @QueryParam("enddate") String endDate) {
        try
        {
    		return QueryHive.getQueueStats(environment, startDate, endDate);
        }
        catch (Exception ex) {
        	return ex.toString();
        }
    }
    
    @GET
    @Path("/json/{environment}/failed")
    @Timed
    public String coordinatorStatus(@PathParam("environment") String environment,
    					   @QueryParam("startdate") String startDate,
    					   @QueryParam("enddate") String endDate,
    					   @QueryParam("status") Optional<String> status) {
        try
        {
    		return QueryHive.getJobStats(environment, startDate, endDate, status.or(""));
        }
        catch (Exception ex) {
        	return ex.toString();
        }
    }
}
