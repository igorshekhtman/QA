package com.apixio.qa.hive.cache;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.json.JSONObject;

public class CacheManager
{
    private String outputDir;
    
    public CacheManager(String environment, String outputDir)
    {
        this.outputDir = outputDir;
        
        if (environment != null && environment.equalsIgnoreCase("staging"))
            this.outputDir = outputDir + "/" + environment.toLowerCase();
    }
    
    public List<JSONObject> fetchResults(String fileName) throws Exception
    {
        File jsonFile = new File(outputDir + "/" +fileName);

        List<JSONObject> results = null;
        
        if (jsonFile.exists())
        {
            Scanner scanner = new Scanner(jsonFile);
            results = new ArrayList<JSONObject>();
            while (scanner.hasNextLine())
            {
                results.add(new JSONObject(scanner.nextLine()));
            }
            scanner.close();
        }
        
        return results;
    }
    
    public void writeResults(List<JSONObject> results, String fileName) throws Exception
    {
        IOUtils.write(StringUtils.join(results, "\n"), new FileOutputStream(new File(outputDir + "/" +fileName)));
    }
}
