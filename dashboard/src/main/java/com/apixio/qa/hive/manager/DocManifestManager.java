package com.apixio.qa.hive.manager;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.util.List;

import org.apache.commons.io.FileUtils;
import org.json.JSONObject;

import com.apixio.qa.hive.cache.CacheManager;

public class DocManifestManager
{
    public static String DOCMAN_RECOVERY_FILEPREFIX = "docman_recovery_";
    private CacheManager cache;
    private String outputDir;
    private FileOutputStream fileOut;
    private PrintStream      printOut;
    
    public DocManifestManager(String environment, String manifestDir)
    {
        cache = new CacheManager(environment, manifestDir);
        this.outputDir = manifestDir;
        
        if (environment != null && environment.equalsIgnoreCase("staging"))
            this.outputDir = manifestDir + "/" + environment.toLowerCase();
    }
    
    public String createDocManifestForRecovery(List<JSONObject> data, boolean makeFile) throws Exception
    {
        String resultManifest = "";
        String fieldSeparator = "\t";
        if (data != null)
        {
            String fileName = null;
            for (JSONObject row : data)
            {
                if (row.has("org_id") && row.has("doc_id"))
                {
                    String orgId = (String)row.get("org_id");
                    String seqFileName = null;
                    if (row.has("seqfile_file"))
                    {
                        seqFileName = (String)row.get("seqfile_file");
                    }
                    String currFileName = orgId + (seqFileName != null ?("_" + seqFileName):"");
                    
                    if (makeFile && !currFileName.equals(fileName))
                    {
                        fileName = currFileName;
                        File file = new File(outputDir+ "/"+ DOCMAN_RECOVERY_FILEPREFIX+currFileName);
                        
                        if (file.exists())
                            FileUtils.forceDelete(file);
                        
                        newListFile(outputDir+ "/"+ DOCMAN_RECOVERY_FILEPREFIX+currFileName);
                    }
                    resultManifest += row.get("doc_id") + fieldSeparator + orgId;
                    
                    if (makeFile)
                        printOut.println(resultManifest);
                    
                    resultManifest += "\n";
                }
            }
        }
        return resultManifest;
    }
    
    private void newListFile(String filePath) throws IOException
    {
        if (printOut != null && fileOut != null)
        {
            printOut.close();
            fileOut.close();
        }
            
        fileOut = new FileOutputStream(filePath, true);
        printOut = new PrintStream(fileOut);
    }
}
