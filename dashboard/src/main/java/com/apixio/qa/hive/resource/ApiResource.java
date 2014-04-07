package com.apixio.qa.hive.resource;

import javax.ws.rs.Consumes;
import javax.ws.rs.FormParam;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import org.apache.commons.lang3.StringUtils;
import org.json.JSONObject;

import com.apixio.model.patient.Document;
import com.apixio.model.patient.Patient;
import com.apixio.qa.api.client.ApiClient;
import com.apixio.qa.api.client.PatientUtils;
import com.google.common.base.Optional;
import com.yammer.metrics.annotation.Timed;

@Path("/api")
@Produces(MediaType.APPLICATION_JSON)
public class ApiResource {

	private String url;

	public ApiResource(String url) {
		this.url = url;
	}
	
    @GET
    @Path("/document/detail")
    @Timed
    public String getDocumentDetails(@QueryParam("token") Optional<String> token, @QueryParam("user_id") Optional<String> user_id, @QueryParam("username") Optional<String> username, @QueryParam("password") Optional<String> password, @QueryParam("patient_uuid") String patient_uuid, @QueryParam("document_uuid") String document_uuid)
    {
    	ApiClient apiClient = new ApiClient(url);
    	JSONObject documentDetails = null;
    	String requestToken = "";
    	String requestUserId = "";
    	if (StringUtils.isBlank(token.orNull())) {
    		try {
				JSONObject tokenObject = apiClient.getUserToken(username.or(""), password.or(""));
				requestToken = tokenObject.getString("token");
				requestUserId = tokenObject.getString("user_id");
			} catch (Exception e) {
				e.printStackTrace();
			}
    	} else {
			requestToken = token.orNull();
	    	requestUserId = user_id.orNull();
    	}
    	
    	if (!StringUtils.isBlank(requestToken) && !StringUtils.isBlank(requestUserId)) {
    		try {
				Patient patient = apiClient.getPatientByUUID(requestToken, requestUserId, patient_uuid);
				documentDetails = PatientUtils.getDocumentDetails(patient, document_uuid);
				
				if (documentDetails == null) {
					Patient patientDocument = apiClient.getPatientDocumentByUUID(requestToken, requestUserId, patient_uuid, document_uuid);
					for (Document document : patientDocument.getDocuments()) {
						documentDetails = PatientUtils.getDocumentDetails(patient, document);
					}
				}
			} catch (Exception e) {
				e.printStackTrace();
			}
    	}
    	
    	return documentDetails.toString();
    }
	
    @POST
    @Path("/document/details/encounter")
    @Timed
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public String getDocumentEncounterDetails(@FormParam("username") String username, @FormParam("password") String password, @FormParam("patient_documents") String patient_documents)
    {
    	long start = System.currentTimeMillis();
    	System.out.println("Starting request for document encounter details: " + start);
    	ApiClient apiClient = new ApiClient(url);
    	JSONObject documentEncounterDetails = null;
    	String requestToken = "";
    	String requestUserId = "";
    	//if (StringUtils.isBlank(token.orNull())) {
    		try {
				JSONObject tokenObject = apiClient.getUserToken(username, password);
				requestToken = tokenObject.getString("token");
				requestUserId = tokenObject.getString("user_id");
			} catch (Exception e) {
				e.printStackTrace();
			}
    	//} else {
		//	requestToken = token.orNull();
	    //	requestUserId = user_id.orNull();
    	//}
    	
    	if (!StringUtils.isBlank(requestToken) && !StringUtils.isBlank(requestUserId)) {
    		try {
				documentEncounterDetails = PatientUtils.getDocumentEncounterDetails(patient_documents, url, requestToken, requestUserId);
			} catch (Exception e) {
				e.printStackTrace();
			}
    	}
    	
    	long end = System.currentTimeMillis();
    	System.out.println("Completed document encounter details request: " + ((end - start) / 1000) + " seconds");
    	System.out.println("Payload returned to client: " + documentEncounterDetails.toString());
    	return documentEncounterDetails.toString();
    }
    
    @POST
    @Path("/document/details/paths")
    @Timed
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public String getDocumentPathDetails(@FormParam("username") String username, @FormParam("password") String password, @FormParam("patient_documents") String patient_documents, @FormParam("document_paths") String document_paths, @FormParam("patient_paths") String patient_paths)
    {
    	long start = System.currentTimeMillis();
    	System.out.println("Starting request for document encounter details: " + start);
    	ApiClient apiClient = new ApiClient(url);
    	JSONObject documentEncounterDetails = null;
    	String requestToken = "";
    	String requestUserId = "";
    	//if (StringUtils.isBlank(token.orNull())) {
    		try {
				JSONObject tokenObject = apiClient.getUserToken(username, password);
				requestToken = tokenObject.getString("token");
				requestUserId = tokenObject.getString("user_id");
			} catch (Exception e) {
				e.printStackTrace();
			}
    	//} else {
		//	requestToken = token.orNull();
	    //	requestUserId = user_id.orNull();
    	//}
    	
    	if (!StringUtils.isBlank(requestToken) && !StringUtils.isBlank(requestUserId)) {
    		try {
				documentEncounterDetails = PatientUtils.getPatientPathDetails(patient_documents, document_paths, patient_paths, url, requestToken, requestUserId);
			} catch (Exception e) {
				e.printStackTrace();
			}
    	}
    	
    	long end = System.currentTimeMillis();
    	System.out.println("Completed document encounter details request: " + ((end - start) / 1000) + " seconds");
    	System.out.println("Payload returned to client: " + documentEncounterDetails.toString());
    	return documentEncounterDetails.toString();
    }
}
