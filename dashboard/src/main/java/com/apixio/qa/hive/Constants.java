package com.apixio.qa.hive;

public class Constants
{
    public static enum COMPONENTS
    {
        COORDINATOR 
        {
            public String getTableName()
            {
                return "coordinator";
            }
        }, 
        DOCRECEIVER
        {
            public String getTableName()
            {
                return "docreceiver";
            }
        }, 
        OCR
        {
            public String getTableName()
            {
                return "ocrjob";
            }
        }, 
        PARSER
        {
            public String getTableName()
            {
                return "parserjob";
            }
        }, 
        PERSIST
        {
            public String getTableName()
            {
                return "persistjob";
            }
        },
        TRACE
        {
            public String getTableName()
            {
                return "json2trace";
            }
        };
        
        public abstract String getTableName();
    }
}
