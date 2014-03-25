package com.apixio.qa.hive.resource;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import org.json.JSONArray;
import org.json.JSONObject;

import com.yammer.metrics.annotation.Timed;

@Path("/graphite")
@Produces(MediaType.APPLICATION_JSON)
public class GraphiteResource {
    
    @GET
    @Path("/speed")
    @Timed
    public String getGraphiteSpeed(@QueryParam("environment") String environment, @QueryParam("from") String from, @QueryParam("sample") String sample)
    {
        try
        {
        	Integer sampleMinutes = Integer.valueOf(sample);
        	float scale = 1 / Float.valueOf(sampleMinutes * 60);
        	String url = "http://dashboard.apixio.com/render?from=" + from + "&until=-0hour&target=scale(summarize(" + environment + ".docreceiver.upload.document.bytes,%22" + sampleMinutes + "min%22),%22" + scale + "%22)&format=json";
        	 
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
    @Path("/speed")
    @Timed
    public String getDocumentCount(@QueryParam("environment") String environment, @QueryParam("from") String from, @QueryParam("sample") String sample)
    {
        try
        {
        	String url = "";// "http://dashboard.apixio.com/render?from=" + from + "&until=-0hour&target=scale(summarize(" + environment + ".docreceiver.upload.document.bytes,%22" + sampleMinutes + "min%22),%22" + scale + "%22)&format=json";
        	 
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
}
