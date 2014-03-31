package com.apixio.qa.api.client;

import java.io.IOException;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.ISODateTimeFormat;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.util.ISO8601DateFormat;

public class CustomDateSerializer extends com.fasterxml.jackson.databind.JsonSerializer<DateTime> {
	@Override
	public void serialize(DateTime value, JsonGenerator jgen,
			SerializerProvider provider) throws IOException,
			JsonProcessingException 
	{
		String stringFormat = value.toString();
		Date date = new Date(value.getMillis());
		String dateString = date.toString();
		//String convertedDate = df.format(dateValue);
		jgen.writeString(dateString);
	}

}
