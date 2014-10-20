package com.apixio.qa.hive.resource;

import com.apixio.model.patient.Document;
import com.apixio.model.patient.Patient;
import com.apixio.model.utility.PatientJSONParser;
import com.apixio.qa.api.client.CustomPatientJSONParser;
import com.apixio.qa.api.client.PatientUtils;
import com.apixio.qa.api.dataorchestratorclient.DataOrchestratorClient;
import com.google.common.base.Optional;
import com.yammer.metrics.annotation.Timed;
import org.apache.commons.lang3.StringUtils;
import org.json.JSONObject;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;

@Path("/dataorchestrator")
@Produces(MediaType.APPLICATION_JSON)
public class DataOrchestratorResource {

	private String authUrl;
    private String tokenUrl;
    private String dataUrl;

	public DataOrchestratorResource(String authUrl, String tokenUrl, String dataUrl) {
		this.authUrl = authUrl;
        this.tokenUrl = tokenUrl;
        this.dataUrl = dataUrl;
	}
	
    @GET
    @Path("/document/detail")
    @Timed
    public String getDocumentDetails(@QueryParam("token") Optional<String> token, @QueryParam("user_id") Optional<String> user_id, @QueryParam("username") Optional<String> username, @QueryParam("password") Optional<String> password, @QueryParam("patient_uuid") String patient_uuid, @QueryParam("document_uuid") String document_uuid)
    {
    	DataOrchestratorClient dataOrchestratorClient = new DataOrchestratorClient(username.get(),password.get(),authUrl, tokenUrl, dataUrl);
    	JSONObject documentDetails = null;
    	try {
            CustomPatientJSONParser pj = new CustomPatientJSONParser();
            Patient patient = pj.parsePatientData(dataOrchestratorClient.getPatientApo(patient_uuid));
            documentDetails = PatientUtils.getDocumentDetails(patient, document_uuid);

            if (documentDetails == null) {
                Patient patientDocument = pj.parsePatientData(dataOrchestratorClient.getDocumentApo(document_uuid));
                for (Document document : patientDocument.getDocuments()) {
                    documentDetails = PatientUtils.getDocumentDetails(patient, document);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
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
        DataOrchestratorClient dataOrchestratorClient = new DataOrchestratorClient(username,password,authUrl, tokenUrl, dataUrl);
        JSONObject documentEncounterDetails = null;
    	try {
            documentEncounterDetails = PatientUtils.getDocumentEncounterDetails(patient_documents, dataOrchestratorClient);
        } catch (Exception e) {
            e.printStackTrace();
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
        DataOrchestratorClient dataOrchestratorClient = new DataOrchestratorClient(username,password,authUrl, tokenUrl, dataUrl);
        JSONObject documentEncounterDetails = null;
    	try {
            documentEncounterDetails = PatientUtils.getPatientPathDetails(patient_documents, document_paths, patient_paths, dataOrchestratorClient);
        } catch (Exception e) {
            e.printStackTrace();
        }
    	long end = System.currentTimeMillis();
    	System.out.println("Completed document encounter details request: " + ((end - start) / 1000) + " seconds");
    	System.out.println("Payload returned to client: " + documentEncounterDetails.toString());
    	return documentEncounterDetails.toString();
    }
}
