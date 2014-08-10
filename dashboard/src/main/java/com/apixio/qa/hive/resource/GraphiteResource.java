package com.apixio.qa.hive.resource;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import org.json.JSONArray;

import com.apixio.qa.reporting.conf.GraphiteConfiguration;
import com.yammer.metrics.annotation.Timed;

@Path("/graphite")
@Produces(MediaType.APPLICATION_JSON)
public class GraphiteResource {

    private GraphiteConfiguration graphiteConfig;
    public GraphiteResource(GraphiteConfiguration graphiteConfig) {
        this.graphiteConfig = graphiteConfig;
    }

    @GET
    @Path("/speed")
    @Timed
    public String getGraphiteSpeed(@QueryParam("callback") String callback,
                    @QueryParam("environment") String environment, @QueryParam("from") String from, @QueryParam("sample") String sample)
    {
        try
        {
            Integer sampleMinutes = Integer.valueOf(sample);
            float scale = 1 / Float.valueOf(sampleMinutes * 60);
            String speedUrl = graphiteConfig.getUrl() + "?from=" + from + "&until=-0hour&target=scale(summarize(" + environment + ".docreceiver.upload.document.serialize.bytes,%22" + sampleMinutes + "min%22),%22" + scale + "%22)&format=json";

            URL obj = new URL(speedUrl);
            HttpURLConnection con = (HttpURLConnection) obj.openConnection();

            // optional default is GET
            con.setRequestMethod("GET");

            //add request header
            con.setRequestProperty("User-Agent", "ReportServer");

            int responseCode = con.getResponseCode();
            System.out.println("\nSending 'GET' request to URL : " + speedUrl);
            System.out.println("Response Code : " + responseCode);

            BufferedReader in = new BufferedReader(
                            new InputStreamReader(con.getInputStream()));
            String inputLine;
            StringBuffer response = new StringBuffer();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            String responseText = response.toString();
            System.out.println(responseText);
            JSONArray data = new JSONArray(responseText);
            JSONArray datapoints = data.getJSONObject(0).getJSONArray("datapoints");
            String speed = "0";
            for (int i = 0; i < datapoints.length(); i++) {
                JSONArray datapoint = datapoints.getJSONArray(i);
                if (!datapoint.get(0).toString().equals("null")) {
                    Float value = new Float(datapoint.get(0).toString());
                    Float speedValue = value / (1024*1024);
                    speed = speedValue.toString();
                }
            }
            return speed;
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    @GET
    @Path("/document_count")
    @Timed
    public String getDocumentCount(@QueryParam("environment") String environment, @QueryParam("range") String range)
    {
        try
        {
            String url = graphiteConfig.getUrl() + "?from=-" + range + "&target=summarize(" + environment + ".docreceiver.seqfile.file.document.count,\"" + range + "\",\"sum\",true)&format=json";

            URL obj = new URL(url);
            HttpURLConnection con = (HttpURLConnection) obj.openConnection();

            // optional default is GET
            con.setRequestMethod("GET");

            //add request header
            con.setRequestProperty("User-Agent", "ReportServer");

            int responseCode = con.getResponseCode();
            System.out.println("\nSending 'GET' request to URL : " + url);
            System.out.println("Response Code : " + responseCode);

            BufferedReader in = new BufferedReader(
                            new InputStreamReader(con.getInputStream()));
            String inputLine;
            StringBuffer response = new StringBuffer();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            String responseText = response.toString();
            System.out.println(responseText);
            JSONArray data = new JSONArray(responseText);
            JSONArray datapoints = data.getJSONObject(0).getJSONArray("datapoints");
            String documentCount = "0";
            for (int i = 0; i < datapoints.length(); i++) {
                JSONArray datapoint = datapoints.getJSONArray(i);
                if (!datapoint.get(0).toString().equals("null")) {
                    Double docs = (Double)datapoint.get(0);
                    documentCount = String.format("%.0f", docs);
                    System.out.println("Got Document Count: " + documentCount);
                }
            }
            return documentCount;
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }

    /**
     * Return Graphite data in 2-dimensional jsonp format suitable for afterquery.
     * Simple two-level vector where first row is field names
     */
    @GET
    @Path("/after")
    @Timed
    public String getGraphiteRaw(@QueryParam("jsonp") String jsonp,
                    @QueryParam("target") String target,
                    @QueryParam("from") String from,
                    @QueryParam("fields") String fields,
                    @QueryParam("format") String format)
                                    throws Exception {
        try
        {
            String speedUrl = graphiteConfig.getUrl() + "?from=" + from + "&until=-0hour&target=" + target + "&tz=UTC&format=csv";

            URL obj = new URL(speedUrl);
            HttpURLConnection con = (HttpURLConnection) obj.openConnection();

            // optional default is GET
            con.setRequestMethod("GET");

            //add request header
            con.setRequestProperty("User-Agent", "ReportServer");

            int responseCode = con.getResponseCode();
            System.out.println("\nSending 'GET' request to URL : " + speedUrl);
            System.out.println("Response Code : " + responseCode);
            RowKeyedTable table = new RowKeyedTable();

            BufferedReader in = new BufferedReader(
                            new InputStreamReader(con.getInputStream()));

            // metric.name,2014-07-24 19:51:00,0.00017465314557475427
            // deconstruct into table of field, timestamp, value
            // value can be null, when line = name,timestamp,
            String inputLine;
            while ((inputLine = in.readLine()) != null) {
                System.out.println(inputLine);
                String parts[] = inputLine.split("[,]");
                String time = parts[1].replace(' ', 'T') + ".000Z";
                table.setCell(parts[0], time, parts.length == 3 ? parts[2] : null);
            }
            in.close();
            if (format == null || format.equals("json")) {
                return table.getJson(fields, jsonp, true).toString();
            } else if (format.equals("csv")) {
                return table.getCsv(fields, true, true).toString();
            } else {
                throw new IllegalArgumentException("Param 'format' needs to be 'json' or 'csv': " + format);
            }
        } catch (Exception ex) {
            throw ex;
        }

    }

}
