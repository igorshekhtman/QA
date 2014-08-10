package com.apixio.qa.hive.resource;

import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

/**
 * Build a table one cell at a time.
 * Graphite requires this. Forch Graphite requests don't return much data.
 * Generate json and csv format output.
 * 
 * @author lance
 *
 */

public class RowKeyedTable {
    // field->time->value
    private final Map<String,Map<String,String>> table = new java.util.HashMap<>();
    // maintain insertion orders
    private final Set<String> timeset = new LinkedHashSet<>();
    private final Set<String> fieldset = new LinkedHashSet<>();

    public void setCell(String name, String time, String value) {
        Map<String, String> field = table.get(name);
        if (field == null) {
            field = new java.util.HashMap<String, String>();
            fieldset.add(name);
            table.put(name, field);
        }
        // ISO8601-ize
        timeset.add(time);
        field.put(time, value);
    }

    public StringBuilder getJson(String fields, String jsonp, boolean filter) {
        StringBuilder json = new StringBuilder();
        if (jsonp != null)
            json.append(jsonp + "(");
        if (fields != null) {
            String[] fieldNames = fields.split("[,]");
            if (fieldNames.length != table.keySet().size() + 1)
                throw new IllegalArgumentException("Wrong number of fields in header: " + fieldNames.length + 
                                ", should be: " + (table.keySet().size() + 1));
            json.append("[[\"");
            for(String name: fieldNames) {
                json.append(name);
                json.append("\",\"");
            }
            json.setLength(json.length() - 2);
        } else {
            json.append("[[\"time\"");
            for(String name: fieldset) {
                json.append(",\"");
                json.append(name);
                json.append("\"");
            }
        }
        json.append("]");
        for(String time: timeset) {
            boolean isnull = filter;
            for(String field: fieldset) {
                if (filter && table.get(field).get(time) != null)
                    isnull = false;
            }
            if (isnull)
                continue;
            json.append(",[\"");
            json.append(time);
            json.append("\"");
            for(String field: fieldset) {
                String value = table.get(field).get(time);
                json.append(",");
                if (value != null) {
                    json.append("\"");
                    json.append(value.toString());
                    json.append("\"");
                } else {
                    json.append("null");
                }
            }
            json.append(']');
        }
        json.append(']');

        if (jsonp != null)
            json.append(")");
        String responseText = json.toString();
        System.out.println(responseText);
        return json;
    }

    public StringBuilder getCsv(String fields, boolean doHeader, boolean filter) {
        StringBuilder csv = new StringBuilder();
        if (fields != null) {
            String fieldNames[] = fields.split("[,]");
            if (fieldNames.length != table.keySet().size() + 1)
                throw new IllegalArgumentException("Wrong number of fields in header: " + fieldNames.length + 
                                ", should be: " + (table.keySet().size() + 1));
            for(String name: fieldNames) {
                csv.append(name);
                csv.append(",");
            }
            csv.setLength(csv.length() - 1);
        } else if (doHeader) {
            csv.append("time");
            for(String name: fieldset) {
                csv.append(",");
                csv.append(name);
            }
        }
        csv.append("\n");
        for(String time: timeset) {
            boolean isnull = filter;
            for(String field: fieldset) {
                if (filter && table.get(field).get(time) != null)
                    isnull = false;
            }
            if (isnull)
                continue;
            csv.append(time);
            for(String field: fieldset) {
                String value = table.get(field).get(time);
                csv.append(",");
                if (value != null) {
                    csv.append(value.replace(",", "\\,"));
                }                 
            }
            csv.append('\n');
        }
        return csv;
    }

}
