package com.apixio.qa.hive.manager;

import java.util.Calendar;
import java.util.HashMap;
import java.util.Map;
import java.util.TimeZone;
import java.util.Timer;
import java.util.TimerTask;

import org.apache.log4j.Logger;
import org.json.JSONObject;

import com.apixio.qa.hive.QueryHive;

public class DocumentCountManager
{
    private static String driverName = "org.apache.hive.jdbc.HiveDriver";
    private static Logger log = Logger.getLogger(DocumentCountManager.class);
    private Map<String, Integer> oldCount = new HashMap<String, Integer>();
    private Map<String, String> currentCount = new HashMap<String, String>();
    private Timer timer = null;
    private Integer seconds = 60;
    private String hiveAddress;

    public static void main(String[] args)
    {
        DocumentCountManager dcm = new DocumentCountManager("jdbc:hive2://184.169.209.24:10000", "60");
        log.info(dcm.getDocumentCount("staging"));
    }

    public DocumentCountManager(String hiveAddress, String updateInterval)
    {
        this.hiveAddress = hiveAddress;
        try
        {
            seconds = Integer.valueOf(updateInterval);
            log.info("Set update interval to: " + seconds.toString());
        }
        catch (Exception ex)
        {
            log.info("Error setting seconds: " + ex.toString());
        }
    }

    public String getDocumentCount(String environment)
    {
        String documentCount = "0";
        if (!oldCount.containsKey(environment))
        {
            loadEnvironment(environment);
        }
        if (currentCount.containsKey(environment))
        {
            documentCount = currentCount.get(environment);
        }
        return documentCount;
    }

    private void loadEnvironment(String environment)
    {
        // query hive and get base number
        try
        {
            String sql = "select count(distinct upload_doc_id) as prevcount from  temp_partition_docreceiver_upload_document";
            // String response =
            JSONObject prevcount = QueryHive.queryHiveJsonFirstResult(hiveAddress, "select count(distinct upload_doc_id) as prevCount from  temp_partition_docreceiver_upload_document");
            Integer count = prevcount.getInt("prevcount");
            System.out.println("got count: " + count);
            oldCount.put(environment, count);
            log.info("Got old count " + count.toString() + " for environment " + environment);
            setupTimer();
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
        }
        // set up a timer to query for updated values
    }

    private void setupTimer()
    {
        if (timer == null)
        {
            timer = new Timer();
            timer.schedule(new UpdateTask(), 0, seconds * 1000);
        }
    }

    class UpdateTask extends TimerTask
    {
        public void run()
        {
            for (String environment : oldCount.keySet())
            {
                updateEnvironment(environment);
            }
        }

        private void updateEnvironment(String environment)
        {
            try
            {
                Calendar localCalendar = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
                int month = localCalendar.get(Calendar.MONTH) + 1;
                int day = localCalendar.get(Calendar.DAY_OF_MONTH);
                String sql = "select count(DISTINCT get_json_object(line, '$.upload.document.docid')) as count from " + environment
                        + "_logs_docreceiver_epoch WHERE get_json_object(line, '$.level') = 'EVENT' and get_json_object(line, '$.upload.document.status') = 'success' and (day = " + day
                        + " and month = " + month + ")";
                System.out.println("running sql: " + sql);
                JSONObject newCount = QueryHive.queryHiveJsonFirstResult(hiveAddress, sql);
                Integer newNumber = newCount.getInt("count");
                log.info("Got new count " + newNumber.toString() + " for environment " + environment);
                currentCount.put(environment, String.valueOf(oldCount.get(environment) + newNumber));
            }
            catch (Exception ex)
            {
                ex.printStackTrace();
            }
        }
    }
}
