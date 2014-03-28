package com.apixio.qa.hive.resource;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import org.apache.commons.lang3.StringUtils;
import org.json.JSONObject;

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
    @Path("/document/details")
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
			} catch (Exception e) {
				e.printStackTrace();
			}
    	}
    	
    	return documentDetails.toString();
    }
}
