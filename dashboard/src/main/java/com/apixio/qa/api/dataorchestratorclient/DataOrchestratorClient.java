package com.apixio.qa.api.dataorchestratorclient;

public class DataOrchestratorClient extends AuthClient{

	String dataUrl = "";

	public DataOrchestratorClient(String username, String password, String authUrl, String tokenUrl, String dataUrl) {
        super(username, password, authUrl, tokenUrl);
		this.dataUrl = dataUrl;
	}

    public String getPatientApo(String patientUUID) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/patient/" + patientUUID + "/apo");
    }

    public byte[] getPatientApoBytes(String patientUUID) throws Exception {
        return getAuthenticatedGetBytes(dataUrl + "/patient/" + patientUUID + "/apo");
    }
    
    public String getDemographics(String patientUUID) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/patient/" + patientUUID + "/demographics");
    }
    public String getPatientEvents(String patientUUID, String orgId) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/patient/" + patientUUID + "/events/" + orgId);
    }
	public String getDemographicsSummary(String patientUUID) throws Exception {
		return getAuthenticatedGetString(dataUrl + "/patient/" + patientUUID + "/summary/demographic");
	}
	public String getPatientUUID(String externalId, String externalSource, String orgId) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/patient/external/" + externalId + "/" + externalSource + "/" + orgId);
	}
    public String getDocumentTraces(String documentUUID) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/document/" + documentUUID + "/traces");
    }
    public String getDocumentText(String documentUUID) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/document/" + documentUUID + "/text");
    }
    public String getDocumentMetadata(String documentUUID) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/document/" + documentUUID + "/metadata");
    }
    public String getDocumentApo(String documentUUID) throws Exception {
        return getAuthenticatedGetString(dataUrl + "/document/" + documentUUID + "/apo");
    }
    public byte[] getDocumentFile(String documentUUID) throws Exception {
        return getAuthenticatedGetBytes(dataUrl + "/document/" + documentUUID + "/file");
    }

}
