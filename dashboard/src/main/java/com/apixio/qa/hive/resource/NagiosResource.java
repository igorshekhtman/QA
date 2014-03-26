package com.apixio.qa.hive.resource;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Iterator;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import org.json.JSONArray;
import org.json.JSONObject;

import com.sun.jersey.core.util.Base64;
import com.yammer.metrics.annotation.Timed;

@Path("/nagios")
@Produces(MediaType.APPLICATION_JSON)
public class NagiosResource {

	private String url;
	private String username;
	private String password;

	public NagiosResource(String url, String username, String password) {
		this.url = url;
		this.username = username;
		this.password = password;
	}
	
    @GET
    @Path("/status")
    @Timed
    public String getNagiosStatus()
    {
        try
        {        	
    		//URL url = new URL(nagiosUrl);
    		HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection(); 
    		String encoded = new String(Base64.encode(username+":"+password)); 
    		connection.setRequestProperty("Authorization", "Basic "+encoded);
    		// optional default is GET
    		connection.setRequestMethod("GET");
     
    		//add request header
    		connection.setRequestProperty("User-Agent", "ReportServer");
     
    		int responseCode = connection.getResponseCode();
    		System.out.println("\nSending 'GET' request to URL : " + url);
    		System.out.println("Response Code : " + responseCode);
     
    		BufferedReader in = new BufferedReader(
    		        new InputStreamReader(connection.getInputStream()));
    		String inputLine;
    		StringBuffer response = new StringBuffer();
     
    		while ((inputLine = in.readLine()) != null) {
    			response.append(inputLine);
    		}
    		in.close();
    		   		
    		String responseText = response.toString();
    		System.out.println(responseText);
    		JSONObject obj = new JSONObject(responseText);
    		JSONObject simplified = new JSONObject();
    		JSONObject hosts =  obj.getJSONObject("hosts");
    		JSONObject services =  obj.getJSONObject("services");
    		Iterator hostKeys = hosts.keys();
    		while (hostKeys.hasNext()) {
    			String host = (String)hostKeys.next();
    			JSONObject host_values = hosts.getJSONObject(host);
    			JSONObject host_simplified = new JSONObject();
    			host_simplified.put("host_current_state", host_values.get("current_state"));
    			JSONObject service_values = services.getJSONObject(host);
    			Iterator serviceKeys = service_values.keys();
        		while (serviceKeys.hasNext()) {
        			String serviceName = (String) serviceKeys.next();
        			JSONObject serviceFields = service_values.getJSONObject(serviceName);
        			host_simplified.put(serviceName, serviceFields.get("current_state"));
        		}
    			simplified.put(host, host_simplified);
    		}
    		return simplified.toString();
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }
    @GET
    @Path("/alerts")
    @Timed
    public String getNagiosAlerts()
    {
        try
        {        	
    		//URL url = new URL(nagiosUrl);
    		HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection(); 
    		String encoded = new String(Base64.encode(username+":"+password)); 
    		connection.setRequestProperty("Authorization", "Basic "+encoded);
    		// optional default is GET
    		connection.setRequestMethod("GET");
     
    		//add request header
    		connection.setRequestProperty("User-Agent", "ReportServer");
     
    		int responseCode = connection.getResponseCode();
    		System.out.println("\nSending 'GET' request to URL : " + url);
    		System.out.println("Response Code : " + responseCode);
     
    		BufferedReader in = new BufferedReader(
    		        new InputStreamReader(connection.getInputStream()));
    		String inputLine;
    		StringBuffer response = new StringBuffer();
     
    		while ((inputLine = in.readLine()) != null) {
    			response.append(inputLine);
    		}
    		in.close();
    		   		
    		String responseText = response.toString();
    		System.out.println(responseText);
    		JSONObject obj = new JSONObject(responseText);
    		JSONObject simplified = new JSONObject();
    		JSONArray hostErrors = new JSONArray();
    		simplified.put("alerts", hostErrors);
    		JSONObject hosts =  obj.getJSONObject("hosts");
    		JSONObject services =  obj.getJSONObject("services");
    		Iterator hostKeys = hosts.keys();
    		while (hostKeys.hasNext()) {
    			String host = (String)hostKeys.next();
    			JSONObject host_values = hosts.getJSONObject(host);
    			JSONArray host_alerts = new JSONArray();
    			String host_state = (String) host_values.get("current_state");
    			if (!host_state.equals("0"))
    				host_alerts.put("Host is down");
    			JSONObject service_values = services.getJSONObject(host);
    			Iterator serviceKeys = service_values.keys();
        		while (serviceKeys.hasNext()) {
        			String serviceName = (String) serviceKeys.next();
        			JSONObject serviceFields = service_values.getJSONObject(serviceName);
        			String service_state = (String) serviceFields.get("current_state");
        			if (!service_state.equals("0")) {
        				host_alerts.put("Service: \"" + serviceName + "\" is down");
        			}
        		}
        		if (host_alerts.length() > 0) {
        			JSONObject hostData = new JSONObject();
        			hostData.put("hostname", host);
        			hostData.put("hostalerts", host_alerts);
        			hostErrors.put(hostData);
        		}
    		}
    		return simplified.toString();
        }
        catch (Exception ex)
        {
            return ex.toString();
        }
    }
}
