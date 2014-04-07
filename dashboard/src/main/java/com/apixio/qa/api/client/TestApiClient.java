package com.apixio.qa.api.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;
import org.json.JSONObject;

import com.apixio.model.patient.Patient;

public class TestApiClient {

	public static void main(String[] args) {
		
		String url = "https://localstagingapi.apixio.com/TESTAPI";
		String token = null;
		String username = "apxdemot0232";// "rmc_hcc@apixio.com";
		username = "apxdemot0227";
		String password = "Hadoop.4522"; //"8p1rmc19..";
		String patient_uuid = "97c15739-fdee-4e74-b2e7-26b012ca319f"; //"00018d04-3fce-4178-bd07-8aeb1ab6402c";
		patient_uuid = "019481b9-512b-4858-83d3-106e2384afd5"; 
		String document_uuid = "86b0531c-be89-41d8-8fab-bdce6844f431"; //"fd199416-6a40-414f-9470-72547d153c7c";
		document_uuid = "4d62e63d-fec0-4b04-9838-64aee47b1bc5";
		ApiClient apiClient = new ApiClient(url);
    	String requestToken = "";
    	String requestUserId = "";
    	if (StringUtils.isBlank(token)) {
    		try {
				JSONObject tokenObject = apiClient.getUserToken(username, password);
				requestToken = tokenObject.getString("token");
				requestUserId = tokenObject.getString("user_id");
			} catch (Exception e) {
				e.printStackTrace();
			}
    	} else {
			//requestToken = token;
	    	//requestUserId = user_id;
    	}
    	
    	if (!StringUtils.isBlank(requestToken) && !StringUtils.isBlank(requestUserId)) {
    		try {
				Patient patient = apiClient.getPatientDocumentByUUID(requestToken, requestUserId, patient_uuid, document_uuid);

				Patient patient2 = apiClient.getPatientByUUID(requestToken, requestUserId, patient_uuid);
				
//				List<String> paths = new ArrayList<String>();
//				paths.add("encounterStartDate");
//				paths.add("originalId/id");
//				paths.add("code/displayName");
//				Map<String,String> encounterDetails = PatientUtils.getEncounterDetails(patient, document_uuid, paths);
//				System.out.println(encounterDetails);
				
				
				List<String> complexPaths = new ArrayList<String>();
				complexPaths.add("@encounter[sourceEncounter]/encounterStartDate");
				complexPaths.add("@encounter[sourceEncounter]/originalId/id");
				complexPaths.add("@encounter[sourceEncounter]/code/displayName");
				complexPaths.add("@source[documentContents|sourceId]/organization/name");
				//Map<String,String> complexDetails = PatientUtils.getDocumentDetails(patient, document_uuid, complexPaths);
				//System.out.println(complexDetails);
			} catch (Exception e) {
				e.printStackTrace();
			}
    	}
	}
}
