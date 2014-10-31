package com.apixio.qa.api.dataorchestratorclient;

import com.apixio.model.EitherStringOrNumber;
import com.apixio.model.patient.Patient;
import com.apixio.model.utility.ApixioDateDeserialzer;
import com.apixio.model.utility.ApixioDateSerializer;
import com.apixio.model.utility.EitherStringOrNumberDeserializer;
import com.apixio.model.utility.EitherStringOrNumberSerializer;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.joda.time.DateTime;

import java.io.IOException;

public class CustomPatientJSONParser {

	private static ObjectMapper objectMapper = new ObjectMapper();

	public CustomPatientJSONParser() 
	{
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
        
        objectMapper.setSerializationInclusion(Include.NON_NULL);
        objectMapper.setSerializationInclusion(Include.NON_EMPTY);
        objectMapper.configure(SerializationFeature.WRITE_EMPTY_JSON_ARRAYS, false);
        objectMapper.configure(SerializationFeature.WRITE_NULL_MAP_VALUES, false);
        objectMapper.configure(JsonParser.Feature.ALLOW_NON_NUMERIC_NUMBERS, true);
	}

	/**
	 * Parse the patient data from a string
	 * @param jsonString	the json string containing the data
	 * @return	a patient object
	 * @throws java.io.IOException
	 * @throws com.fasterxml.jackson.databind.JsonMappingException
	 * @throws com.fasterxml.jackson.core.JsonParseException
	 */
	public Patient parsePatientData(String jsonString) throws JsonParseException, JsonMappingException, IOException  
	{
		//Patient p = g.fromJson(jsonString, Patient.class);
		Patient p = objectMapper.readValue(jsonString, Patient.class);
		//Populate Maps
		p.populateMaps();

		return p;
	}

	public String toJSON(Patient p) throws JsonProcessingException  
	{
		return objectMapper.writeValueAsString(p);
	}
}