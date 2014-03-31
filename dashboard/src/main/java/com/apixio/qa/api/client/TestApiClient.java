package com.apixio.qa.api.client;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;
import org.json.JSONObject;

import com.apixio.model.patient.Patient;

public class TestApiClient {

	public static void main(String[] args) {
		String url = "https://localprodapi.apixio.com/API";
		String token = null;
		String username = "rmc_hcc@apixio.com";
		String password = "8p1rmc19..";
		String patient_uuid = "00018d04-3fce-4178-bd07-8aeb1ab6402c";
		String document_uuid = "fd199416-6a40-414f-9470-72547d153c7c";
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
				Patient patient = apiClient.getPatientByUUID(requestToken, requestUserId, patient_uuid);
				
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
				Map<String,String> complexDetails = PatientUtils.getDocumentDetails(patient, document_uuid, complexPaths);
				System.out.println(complexDetails);
			} catch (Exception e) {
				e.printStackTrace();
			}
    	}
	}
}
