package com.apixio.qa.api.client;

import java.io.IOException;
import java.text.ParseException;

import org.apache.commons.lang.time.DateUtils;
import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.DateTimeParser;
import org.joda.time.format.ISODateTimeFormat;

import com.apixio.model.utility.StringDeserializer;
import com.fasterxml.jackson.databind.JsonDeserializer;

public class ApixioDateDeserialzer extends JsonDeserializer<DateTime> 
	implements StringDeserializer<DateTime> {
	
	
	@Override
	public DateTime getNullValue() { return null; }


	@Override
	public DateTime deserialize(com.fasterxml.jackson.core.JsonParser jp,
			com.fasterxml.jackson.databind.DeserializationContext ctxt)
			throws IOException,
			com.fasterxml.jackson.core.JsonProcessingException 
			{
		if(jp == null)
			return null;
		
		String date = jp.getText();
		return fromString(date);
	}


	public DateTime fromString(String arg0) {
		DateTime parsedDate = new DateTime(Long.valueOf(arg0));
		return parsedDate;
	}
}
