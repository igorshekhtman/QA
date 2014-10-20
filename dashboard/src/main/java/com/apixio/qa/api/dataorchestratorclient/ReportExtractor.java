package com.apixio.qa.api.dataorchestratorclient;

import com.apixio.model.patient.*;
import com.apixio.model.patient.event.Event;
import org.apache.commons.lang.StringUtils;

import java.util.List;
import java.util.UUID;

public class ReportExtractor {
	private String delimiter;
	public ReportExtractor(String delimiter) {
		this.delimiter = delimiter;
	}

	public String getHcpnvReport(Patient patient) {
		// TODO Auto-generated method stub
		return null;
	}

	public String getHpmgReport(Patient patient) {
		String documentOriginalId = "";

		for (Document doc : patient.getDocuments()) {
			documentOriginalId = doc.getOriginalId().getAssignAuthority();
		}
		String reportOutput = documentOriginalId;
		System.out.println("got additional data: " + reportOutput);
		return reportOutput;
	}

	public String getRmcReport(Patient patient, String documentUUID) throws Exception {

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
//		if (document == null)
//			document = getDocumentFromDocumentApo();
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

	public String getScrippsReport(Patient patient, String documentUUID) {

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

    public String getCambiaReport(Patient patient) {
        String firstName = patient.getPrimaryDemographics().getName().getGivenNames().get(0);
        String lastName = patient.getPrimaryDemographics().getName().getFamilyNames().get(0);
        String reportOutput = firstName + "\t" + lastName;
        System.out.println("got additional data: " + reportOutput);
        return reportOutput;
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
}
