package com.apixio.qa.api.client;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;

import org.joda.time.DateTime;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.apixio.model.EitherStringOrNumber;
import com.apixio.model.patient.Document;
import com.apixio.model.patient.Patient;
import com.apixio.model.utility.ApixioDateDeserialzer;
import com.apixio.model.utility.ApixioDateSerializer;
import com.apixio.model.utility.EitherStringOrNumberDeserializer;
import com.apixio.model.utility.EitherStringOrNumberSerializer;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;

public class PatientUtils {
	
	private static ObjectMapper objectMapper = null;
	
	public static JSONObject getJsonObjectFromPatientObjectPart(Object object) 
	{
		if (object == null)
			return null;
		JSONObject json = null;
		if (objectMapper == null) {
			objectMapper = new ObjectMapper();
	        SimpleModule module1 = new SimpleModule("DateTimeDeserializerModule");
	        module1.addDeserializer(DateTime.class, new ApixioDateDeserialzer());
	        
	        objectMapper.registerModule(module1);
	        
	        SimpleModule module2 = new SimpleModule("EitherStringOrNumberDeserializerModule");
	        module2.addDeserializer(EitherStringOrNumber.class, new EitherStringOrNumberDeserializer());
	        
	        objectMapper.registerModule(module2);

	        SimpleModule module3 = new SimpleModule("DateTimeSerializerModule");
	        module3.addSerializer(DateTime.class, new ApixioDateSerializer());
	        
	        objectMapper.registerModule(module3);
	        
	        SimpleModule module4 = new SimpleModule("EitherStringOrNumberSerializerModule");
	        module4.addSerializer(EitherStringOrNumber.class, new EitherStringOrNumberSerializer());
	        
	        objectMapper.registerModule(module4);
		}
		String jsonString = "";
		try {
			jsonString = objectMapper.writeValueAsString(object);
			json = new JSONObject(jsonString);
		} catch (JsonProcessingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return json;
	}

	public static JSONObject getDocumentDetails(Patient patient, String documentUuid) throws JSONException {
		JSONObject documentDetails = null;
		
		for (Document document : patient.getDocuments()) {
			if (document.getInternalUUID().toString().equals(documentUuid)) {
				documentDetails = getDocumentDetails(patient, document);
			}		
		}
		
		return documentDetails;
	}

	public static JSONObject getDocumentDetails(Patient patient, Document document) throws JSONException {
		JSONObject documentDetails = new JSONObject();
		documentDetails.put("demographics", getJsonObjectFromPatientObjectPart(patient.getPrimaryDemographics()));
		documentDetails.put("document",getJsonObjectFromPatientObjectPart(document));				
		documentDetails.put("encounter", getJsonObjectFromPatientObjectPart(patient.getEncounterById(document.getSourceEncounter())));
		documentDetails.put("clinicalActor", getJsonObjectFromPatientObjectPart(patient.getClinicalActorById(document.getPrimaryClinicalActorId())));
		documentDetails.put("parsingDetails", getJsonObjectFromPatientObjectPart(patient.getParsingDetailById(document.getParsingDetailsId())));
		documentDetails.put("source", getJsonObjectFromPatientObjectPart(patient.getSourceById(document.getSourceId())));
		
		return documentDetails;
	}
	
	public static Map<String,String> getEncounterDetails(Patient patient, String documentUuid, List<String> paths) throws JSONException {
		Map<String, String> encounterDetails = new HashMap<String,String>();
		for (Document document : patient.getDocuments()) {
			if (document.getInternalUUID().toString().equals(documentUuid)) {
				JSONObject encounter = getJsonObjectFromPatientObjectPart(patient.getEncounterById(document.getSourceEncounter()));
				for (String path : paths) {
					String[] pathParts = path.split("/", -1);
					String pathValue = getJsonStringForPath(encounter, pathParts);
					encounterDetails.put(path, pathValue);
					for (int i = 0; i < pathParts.length; i++) {
						if (i + 1 < pathParts.length) {
							
						}
					}
				}
			}		
		}
		
		return encounterDetails;
	}

	private static String getJsonStringForPath(JSONObject object, String[] pathParts) throws JSONException {
		if (object == null)
			return null;
		if (pathParts.length == 1) {
			return object.getString(pathParts[0]);
		} else {
			JSONObject nextObject = null;
			try {
				nextObject = object.getJSONObject(pathParts[0]);
			} catch (Exception ex) {
				System.out.println("Not a valid json path: " + pathParts[0] + ": " + ex.toString());
			}
			return getJsonStringForPath(nextObject, Arrays.copyOfRange(pathParts, 1, pathParts.length));
		}
	}
	
	public static Map<String,String> getDocumentDetails(Patient patient, String documentUuid, Map<String,String> paths) throws JSONException {
		Map<String, String> encounterDetails = new HashMap<String,String>();
		for (Document document : patient.getDocuments()) {
			if (document.getInternalUUID().toString().equals(documentUuid)) {
				for (Entry<String, String> pathSet : paths.entrySet()) {
					String[] pathParts = pathSet.getValue().split("/", -1);
					String pathValue = getJsonStringForPath(patient, getJsonObjectFromPatientObjectPart(document), pathParts);
					encounterDetails.put(pathSet.getKey(), pathValue);
				}
			}		
		}
		
		return encounterDetails;
	}

	private static String getJsonStringForPath(Patient patient, JSONObject object, String[] pathParts) throws JSONException {
		if (pathParts.length == 1) {
			return object.getString(pathParts[0]);
		} else {
			String currentPathPart = pathParts[0];
			String[] remainingParts = Arrays.copyOfRange(pathParts, 1, pathParts.length);
			JSONObject nextObject = null;
			// @encounter[sourceEncounter]
			if (currentPathPart.startsWith("@encounter")) {
				String encounterPath = currentPathPart.substring(currentPathPart.indexOf("[") + 1, currentPathPart.indexOf("]"));
				nextObject = getJsonObjectFromPatientObjectPart(patient.getEncounterById(UUID.fromString(getJsonStringForPath(patient, object, encounterPath.split("\\|", -1)))));
			} else if (currentPathPart.startsWith("@clinicalActor")) {
				String clinicalActorPath = currentPathPart.substring(currentPathPart.indexOf("[") + 1, currentPathPart.indexOf("]"));
				nextObject = getJsonObjectFromPatientObjectPart(patient.getClinicalActorById(UUID.fromString(getJsonStringForPath(patient, object, clinicalActorPath.split("\\|", -1)))));
			} else if (currentPathPart.startsWith("@parsingDetails")) {
				String parsingDetailsPath = currentPathPart.substring(currentPathPart.indexOf("[") + 1, currentPathPart.indexOf("]"));
				nextObject = getJsonObjectFromPatientObjectPart(patient.getParsingDetailById(UUID.fromString(getJsonStringForPath(patient, object, parsingDetailsPath.split("\\|", -1)))));
			} else if (currentPathPart.startsWith("@source")) {
				String sourcePath = currentPathPart.substring(currentPathPart.indexOf("[") + 1, currentPathPart.indexOf("]"));
				nextObject = getJsonObjectFromPatientObjectPart(patient.getSourceById(UUID.fromString(getJsonStringForPath(patient, object, sourcePath.split("\\|", -1)))));
			} else if (currentPathPart.startsWith("@careSite")) {
				String careSitePath = currentPathPart.substring(currentPathPart.indexOf("[") + 1, currentPathPart.indexOf("]"));
				nextObject = getJsonObjectFromPatientObjectPart(patient.getCareSiteById(UUID.fromString(getJsonStringForPath(patient, object, careSitePath.split("\\|", -1)))));
			} else{
				Object newObject = object.get(pathParts[0]);
				if (newObject instanceof JSONArray) {
					nextObject = ((JSONArray) newObject).getJSONObject(0);
				} else {
					nextObject = object.getJSONObject(pathParts[0]);
				}
			}
			return getJsonStringForPath(nextObject, remainingParts);
		}
	}

	public static JSONObject getDocumentEncounterDetails(String patient_documents, String url, String requestToken, String requestUserId) throws Exception {
		JSONObject documentEncounterDetails = new JSONObject();
		Map<String, Set<String>> patientDocumentMap = new HashMap<String, Set<String>>();
		String[] patientDocumentList = patient_documents.split(";", -1);
		for (int i = 0; i < patientDocumentList.length; i++) {
			String[] patientDocumentParts = patientDocumentList[i].split("\\|", -1);
			if (patientDocumentParts.length != 2)
				continue;
			String patientUuid = patientDocumentParts[0];
			String documentUuid = patientDocumentParts[1];
			Set<String> documents = null;
			if (patientDocumentMap.containsKey(patientUuid)) {
				documents = patientDocumentMap.get(patientUuid);
			} else {
				documents = new HashSet<String>();
				patientDocumentMap.put(patientUuid, documents);
			}
			if (!documents.contains(documentUuid)) {
				documents.add(documentUuid);
			}
		}

    	ApiClient apiClient = new ApiClient(url);
		for (String patientUuid : patientDocumentMap.keySet()) {
			Patient patient = apiClient.getPatientByUUID(requestToken, requestUserId, patientUuid);		
			if (patient != null) {
				for (String documentUuid : patientDocumentMap.get(patientUuid)) {
					Map<String, String> complexPaths = new HashMap<String, String>();
					complexPaths.put("Encounter Start Date", "@encounter[sourceEncounter]/encounterStartDate");
					complexPaths.put("Encounter Original ID", "@encounter[sourceEncounter]/originalId/id");
					complexPaths.put("Encounter Display Name", "@encounter[sourceEncounter]/code/displayName");
					Map<String,String> complexDetails = PatientUtils.getDocumentDetails(patient, documentUuid, complexPaths);
					//documentEncounterDetails += patientUuid + "\t" + documentUuid + "\t" + StringUtils.join(complexDetails.values(),"\t") + "\n";
					documentEncounterDetails.put(patientUuid + "|" + documentUuid, complexDetails);
				}
			}
		}
		return documentEncounterDetails;
	}

	public static JSONObject getDocumentPathDetails(String patient_documents, String paths, String url, String requestToken, String requestUserId) throws Exception {
		JSONObject documentEncounterDetails = new JSONObject();
		Map<String, Set<String>> patientDocumentMap = new HashMap<String, Set<String>>();
		String[] patientDocumentList = patient_documents.split(";", -1);
		for (int i = 0; i < patientDocumentList.length; i++) {
			String[] patientDocumentParts = patientDocumentList[i].split("\\|", -1);
			if (patientDocumentParts.length != 2)
				continue;
			String patientUuid = patientDocumentParts[0];
			String documentUuid = patientDocumentParts[1];
			Set<String> documents = null;
			if (patientDocumentMap.containsKey(patientUuid)) {
				documents = patientDocumentMap.get(patientUuid);
			} else {
				documents = new HashSet<String>();
				patientDocumentMap.put(patientUuid, documents);
			}
			if (!documents.contains(documentUuid)) {
				documents.add(documentUuid);
			}
		}

		Map<String, String> complexPaths = new HashMap<String, String>();
		String[] pathPairs = paths.split(";", -1);
		for (int i = 0; i < pathPairs.length; i++) {
			String[] pathSet = pathPairs[i].split("\\|", -1);
			complexPaths.put(pathSet[0], pathSet[1]);
		}
		
    	ApiClient apiClient = new ApiClient(url);
		for (String patientUuid : patientDocumentMap.keySet()) {
			Patient patient = apiClient.getPatientByUUID(requestToken, requestUserId, patientUuid);		
			if (patient != null) {
				for (String documentUuid : patientDocumentMap.get(patientUuid)) {
					Map<String,String> complexDetails = PatientUtils.getDocumentDetails(patient, documentUuid, complexPaths);
					//documentEncounterDetails += patientUuid + "\t" + documentUuid + "\t" + StringUtils.join(complexDetails.values(),"\t") + "\n";
					documentEncounterDetails.put(patientUuid + "|" + documentUuid, complexDetails);
				}
			}
		}
		return documentEncounterDetails;
	}
}