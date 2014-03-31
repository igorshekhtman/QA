package com.apixio.qa.api.client;

import java.io.InputStreamReader;
import java.util.ArrayList;

import org.apache.commons.io.IOUtils;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONObject;

import com.apixio.model.patient.Patient;
import com.apixio.model.utility.PatientJSONParser;

public class ApiClient {
	
	private String url;
	public ApiClient(String url) {
		this.url = url;
	}

	public JSONObject getUserToken(String username, String password) throws Exception {
		//System.out.println("getting user token with username " + username + " and password " + password);
		ArrayList<BasicNameValuePair> nameValuePairs = new ArrayList<BasicNameValuePair>();
		nameValuePairs.add(new BasicNameValuePair("username", username));
		nameValuePairs.add(new BasicNameValuePair("password", password));
		String authUrl = "/auth/token/";
		if (!url.endsWith("v1"))
			authUrl = "/v1" + authUrl;
		String tokenJson = getPostResult(authUrl, nameValuePairs);
		JSONObject token = new JSONObject(tokenJson);
		return token;
	}

	public Patient getPatientByUUID(String token, String userId, String patientUUID) throws Exception {
		Patient patient = null;
		String tokenJson = "";
		try {			
			ArrayList<BasicNameValuePair> nameValuePairs = new ArrayList<BasicNameValuePair>();
			nameValuePairs.add(new BasicNameValuePair("user_id", userId));
			nameValuePairs.add(new BasicNameValuePair("token", token));
			nameValuePairs.add(new BasicNameValuePair("apixio_id", patientUUID));		
			String patientUrl = "/patient/detail/";
			if (!url.endsWith("v1"))
				patientUrl = "/v1" + patientUrl;
			tokenJson = getPostResult(patientUrl, nameValuePairs);
			CustomPatientJSONParser parser = new CustomPatientJSONParser();
			
			patient = parser.parsePatientData(tokenJson.trim());
		} catch (Exception ex) {
			System.out.println("bad json, last 10 characters: " + tokenJson.substring(tokenJson.length() - 10));
			throw ex;
		}
		return patient;
	}
	private String getPostResult(String service, ArrayList<BasicNameValuePair> nameValuePairs) throws Exception {
		try {
			String fullUrl = url + service;
			//System.out.println("calling: " + fullUrl);
			HttpClient httpClient = new DefaultHttpClient();
			httpClient.getParams().setParameter("http.socket.timeout", 990000);
			httpClient.getParams().setParameter("http.connection.timeout", 990000);
			HttpPost httppost = new HttpPost(fullUrl);
			httppost.setEntity(new UrlEncodedFormEntity(nameValuePairs));
			HttpResponse response = httpClient.execute(httppost);
			InputStreamReader isr = new InputStreamReader(response.getEntity().getContent());
			return IOUtils.toString(isr);
		} catch (Exception e) {
			e.printStackTrace();
			//throw e;
		}
		return null;
	}

}
