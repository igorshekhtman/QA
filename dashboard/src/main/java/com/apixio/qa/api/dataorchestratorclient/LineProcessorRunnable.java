package com.apixio.qa.api.dataorchestratorclient;

import com.apixio.model.patient.*;
import com.apixio.model.patient.event.Event;
import com.apixio.model.utility.PatientJSONParser;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;

import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.UUID;


public class LineProcessorRunnable implements Runnable{

    DataOrchestratorClient apiClient;
	String patientUUID;
	String documentUUID;
	String[] fields;
	String delimiter;
	OutputStream output;
	String reportMode;
	public LineProcessorRunnable(DataOrchestratorClient apiClient, String line, String delimiter, int patientIdIndex, int documentIdIndex, String reportMode, OutputStream output) {
		// TODO: take lines[], patientIndex, documentIndex and delimiter. output additional fields at end
		// Also, if document not found for patient, go ahead and make second API call to get specific document
		
		this.apiClient = apiClient;
		this.delimiter = delimiter;
		this.fields = line.split(delimiter, -1);
		this.patientUUID = fields[patientIdIndex];
    	UUID uuid = UUID.fromString(patientUUID);
		this.documentUUID = fields[documentIdIndex];
		this.reportMode = reportMode;
		this.output = output;
	}
	
	public void run() {
		try {
			long start = System.currentTimeMillis();
			//CustomPatientJSONParser pj = new CustomPatientJSONParser();
			PatientJSONParser pj = new PatientJSONParser();
			String patientString = apiClient.getPatientApo(patientUUID);
			Patient patient = pj.parsePatientData(patientString);
			String reportOutput = getReportOutput(patient);
			String outputLine = StringUtils.join(fields, delimiter) + delimiter + reportOutput;
            outputLine += "\n";
			IOUtils.write(outputLine, output);	
			System.out.println(System.currentTimeMillis() + "\tGot report fields \"" + reportOutput + "\" in:\t" + (System.currentTimeMillis() - start));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}	
	}

    private String getReportOutput(Patient patient) throws Exception {
		String reportOutput = "";
		if (reportMode.equals("scripps")) {
			reportOutput = getScrippsReport(patient);
		} else if (reportMode.equals("rmc")) {
			reportOutput = getRmcReport(patient);
		}else if (reportMode.equals("hcpnv")) {
			reportOutput = getHcpnvReport(patient);
		}
		return reportOutput;
	}

	private String getHcpnvReport(Patient patient) {
		String hicNo = "";
		for (ExternalID id : patient.getExternalIDs()) {
			if (id.getAssignAuthority().equals("HICN1")) {
				hicNo = id.getId();
			}
		}
		String reportOutput = hicNo;
		System.out.println("got additional data: " + reportOutput);
		return reportOutput;
	}

	private String getRmcReport(Patient patient) throws Exception {

		String encounterOriginalId = "not found";
		String encounterDate = "not found";
		String providerOriginalId = "not found";
		String providerOtherId = "notfound";
		String providerFirstName = "not found";
		String providerLastName = "not found";
		String docProviderOriginalId = "not found";
		String docProviderOtherId = "notfound";
		String docProviderFirstName = "not found";
		String docProviderLastName = "not found";
		Document document = null;
		for (Document currDocument : patient.getDocuments()) {
			if (currDocument.getInternalUUID().toString().toLowerCase().equals(documentUUID.toLowerCase())) {
				document = currDocument;
			}
		}
		if (document == null)
			document = getDocumentFromDocumentApo();
		if (document != null) {
			UUID encounterUUID = document.getSourceEncounter();
			Encounter documentEncounter = patient.getEncounterById(encounterUUID);
			ExternalID encounterId = documentEncounter.getOriginalId();
			if (encounterId != null) {
				encounterOriginalId = encounterId.getId();
			}
			if (documentEncounter.getEncounterStartDate() != null) {
				encounterDate = documentEncounter.getEncounterStartDate().toString();
			}
			ClinicalActor provider = patient.getClinicalActorById(documentEncounter.getPrimaryClinicalActorId());
			if (provider != null) {
				providerOriginalId = provider.getOriginalId().getId();
				providerOtherId = getOtherIds(provider.getAlternateIds());
				providerFirstName = StringUtils.join(provider.getActorGivenName().getGivenNames(), " ");
				providerLastName = StringUtils.join(provider.getActorGivenName().getFamilyNames(), " ");
				//providerDisplayName = provider.getActorGivenName().getMetaTag("displayName");
			}
			ClinicalActor docProvider = patient.getClinicalActorById(document.getPrimaryClinicalActorId());
			if (docProvider != null) {
				if (docProvider.getOriginalId() != null)
					docProviderOriginalId = docProvider.getOriginalId().getId();
				docProviderOtherId = getOtherIds(docProvider.getAlternateIds());
				if (docProvider.getActorGivenName() != null) {
					docProviderFirstName = StringUtils.join(docProvider.getActorGivenName().getGivenNames(), " ");
					docProviderLastName = StringUtils.join(docProvider.getActorGivenName().getFamilyNames(), " ");
				}
				//providerDisplayName = provider.getActorGivenName().getMetaTag("displayName");
			}
		}
		//System.out.println("sourceVisitId: " + encounterOriginalId + ", encounterDate: " + encounterDate + ", providerOriginalId: " + providerOriginalId);
		String reportOutput = encounterOriginalId + delimiter + encounterDate + delimiter + providerOriginalId + delimiter + providerOtherId + delimiter + providerFirstName + delimiter + providerLastName + 
				delimiter + docProviderOriginalId + delimiter + docProviderOtherId + delimiter + docProviderFirstName + delimiter + docProviderLastName;
		System.out.println("got additional data: " + reportOutput);
		return reportOutput;
	}
	
	private Document getDocumentFromDocumentApo() throws Exception {
		Document documentFromApo = null;
		CustomPatientJSONParser pj = new CustomPatientJSONParser();
		String patientDocument = apiClient.getDocumentApo(documentUUID);
		Patient patient = pj.parsePatientData(patientDocument);
		for (Document document : patient.getDocuments()) {
			documentFromApo = document;
		}
		return documentFromApo;
	}

	private String getOtherIds(List<ExternalID> otherOriginalIds) {
		String otherIds = "";
		if (otherOriginalIds != null) {
			for (ExternalID id : otherOriginalIds) {
				otherIds += id.getId() + "^" + id.getAssignAuthority() + ";";
			}
		}
		return otherIds;
	}

	private String getScrippsReport(Patient patient) {

		String sourceVisitId = "not found";
		String documentOriginalId = "not found";
		for (Document document : patient.getDocuments()) {
			if (document.getInternalUUID().toString().toLowerCase().equals(documentUUID.toLowerCase())) {
				documentOriginalId = document.getOriginalId().getAssignAuthority();
				UUID encounterUUID = document.getSourceEncounter();
				Encounter documentEncounter = patient.getEncounterById(encounterUUID);
				ExternalID encounterId = documentEncounter.getOriginalId();
				sourceVisitId = encounterId.getAssignAuthority();
			}
		}
		String fscName = "not found";
		String fscNumber = "not found";
		for (Event event : patient.getClinicalEvents()) {
			for (String metadataKey : event.getMetadata().keySet()) {
				if (metadataKey.equals("FSC_Name")) {
					fscName = event.getMetaTag(metadataKey);
				}
				if (metadataKey.equals("FSC_NO")) {
					fscNumber = event.getMetaTag(metadataKey);
				}
			}
		}
		System.out.println("sourceVisitId: " + sourceVisitId + ", fscName: " + fscName + ", fscNumber: " + fscNumber + ", documentOriginalId: " + documentOriginalId);
		String reportOutput = sourceVisitId + "\t" + fscName + "\t" + fscNumber + "\t" + documentOriginalId;
		return reportOutput;
	}

	private String getDOB(Object dob) {
        String dobString = dob.toString();
        try {
            Date date = new Date(1000*Long.valueOf(dob.toString()));
            SimpleDateFormat formatter = new SimpleDateFormat("MM/dd/yyyy");
            dobString = formatter.format(date);
            System.out.println("got data: " + dobString);
        } catch (Exception ex) {
            System.out.println("Couldn't parse DOB: " + dob);
        }
        return dobString;
    }

}
