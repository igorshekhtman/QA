package com.apixio.qa.api.dataorchestratorclient;

import com.apixio.model.utility.StringDeserializer;
import com.fasterxml.jackson.databind.JsonDeserializer;
import org.joda.time.DateTime;

import java.io.IOException;

public class OLDApixioDateDeserialzer extends JsonDeserializer<DateTime>
	implements StringDeserializer<DateTime> {
	
	
	@Override
	public DateTime getNullValue() { return null; }


	@Override
	public DateTime deserialize(com.fasterxml.jackson.core.JsonParser jp,
			com.fasterxml.jackson.databind.DeserializationContext ctxt)
			throws IOException,
			com.fasterxml.jackson.core.JsonProcessingException 
			{
		try {
		if(jp == null)
			return null;
		
		String date = jp.getText();
		return fromString(date);

		} catch (Exception ex) {
			System.out.println("Exception parsing date: " + ex.toString());
			return null;
		}
	}


	public DateTime fromString(String arg0) {
		DateTime parsedDate = new DateTime(1000 * Long.valueOf(arg0));
		System.out.println(parsedDate.toString());
		return parsedDate;
	}
}
