package com.apixio.qa.hive;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.json.JSONException;
import org.json.JSONObject;

public class QueryHive
{
    private static String driverName = "org.apache.hive.jdbc.HiveDriver";
    private static Logger log = Logger.getLogger(QueryHive.class);
    
    public static void main(String[] args)
    {
        try
        {
            createReport();
            // createScopedReport(1);
            // //String query =
            // "select status, count(distinct upload_doc_id) as num_docs FROM temp_partition_docreceiver_seqfile_document where org_id = '10000286' group by status";
            // String query =
            // "select document_status, count(distinct seqfile_doc_id) as num_docs, count(distinct seqfile_file) as num_seq_file FROM temp_partition_docreceiver_seqfile_document "
            // +
            // "where org_id = '10000286' and day=4 and month=2 group by document_status";
            //
            // String result = queryHive(query);
            // System.out.println(result);
            // JSONArray json = new JSONArray(result);
            // for (int i = 0; i < json.length(); i++) {
            // JSONObject object = (JSONObject) json.get(i);
            // String status = object.get("document_status").toString();
            // String num_docs = object.getString("num_docs");
            // String num_seq_file = object.getString("num_seq_file");
            // System.out.println(status + ": num_docs=" + num_docs +
            // ", num_seq_file=" + num_seq_file);
            // }
            // //log.info(rawQuery("production", "docreceiver", "12/18/2013",
            // "12/19/2013", "EVENT", "", "", "", "", "100"));
        }
        catch (Exception ex)
        {
            System.out.println(ex.toString());
        }
    }

    private static String getDateRangeTable(String startDate, String endDate, String tableName)
    {
        String dateRange = "";
        if (!StringUtils.isBlank(endDate) && endDate.length() == 10)
        {
            String endMonth = endDate.substring(0, 2);
            String endDay = endDate.substring(3, 5);
            dateRange = "((" + tableName + ".month < " + endMonth + ") OR (" + tableName + ".month = " + endMonth + " AND " + tableName + ".day <= " + endDay + "))";
        }

        if (!StringUtils.isBlank(startDate) && startDate.length() == 10)
        {
            String startMonth = startDate.substring(0, 2);
            String startDay = startDate.substring(3, 5);
            String beginClause = "((" + tableName + ".month > " + startMonth + ") OR (" + tableName + ".month = " + startMonth + " AND " + tableName + ".day >= " + startDay + "))";
            if (StringUtils.isBlank(dateRange))
                dateRange = beginClause;
            else
                dateRange += " AND " + beginClause;
        }

        return dateRange;
    }

    private static Date addDays(Date date, int days)
    {
        Calendar cal = Calendar.getInstance();
        cal.setTime(date);
        cal.add(Calendar.DATE, days); // minus number would decrement the days
        return cal.getTime();
    }

    private static void createScopedReport(int daysBack) throws JSONException, SQLException, FileNotFoundException, IOException
    {
        Date today = new Date();

        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy");
        String dateRange = getDateRangeTable(sdf.format(addDays(today, -1)), sdf.format(addDays(today, -1 * (daysBack))), "s");
        JSONObject obj = new JSONObject();
        String uploadQuery = "select org_id, status, if(message like '/mnt%','No space left on device',message) as message, count(distinct upload_doc_id) as docs_uploaded, max(time) as last_upload_time "
                + "from temp_partition_docreceiver_upload_document s where " + dateRange + " group by org_id, status, if(message like '/mnt%','No space left on device',message)";
        obj.put("upload", queryHiveJson(uploadQuery));

        String seqfileQuery = "select s.org_id, u.status, s.document_status, count(distinct seqfile_doc_id) as num_files, count(distinct seqfile_file) num_seq_files, max(s.time) as last_upload_time "
                + "from temp_partition_docreceiver_seqfile_document s left outer join temp_partition_docreceiver_upload_document u on s.seqfile_doc_id = u.upload_doc_id and s.org_id = u.org_id "
                + "where u.upload_doc_id is not null and " + dateRange + " group by s.org_id, u.status, s.document_status";
        obj.put("seqfile", queryHiveJson(seqfileQuery));

        String abandonedSeqFileQuery = "select s.org_id, s.seqfile_file, count(s.seqfile_doc_id) as num_docs, max(s.time) as last_written_to from temp_partition_docreceiver_seqfile_document s left outer join "
                + "temp_partition_coordinator_hdfsmove c on c.move_from = s.seqfile_directory where c.move_from is null and s.document_status = 'success' and s.seqfile_file is not null "
                + "and "
                + dateRange + " group by s.org_id, s.seqfile_file";

        obj.put("abandonedSeqFile", queryHiveJson(abandonedSeqFileQuery));

        String jobDetailsQuery = "select c.org_id as org_id, c.job_type as job_type, c.status as status, count(distinct c.job_id) as num_jobs,  max(c.time) as last_update_time from temp_partition_coordinator_job c "
                + "inner join (select job_id, max(time) as time from temp_partition_coordinator_job s where "
                + dateRange
                + " group by job_id) m on m.job_id = c.job_id and c.time = m.time group by c.org_id, c.job_type, c.status";

        obj.put("jobDetails", queryHiveJson(jobDetailsQuery));

        String parserDetailsQuery = "select p.org_id, p.status, p.error_message, count(distinct p.doc_id) as total_num, sum(if(p.ocr_tag_status = 'success',1,0)) as ocr_num, sum(if(p.persist_tag_status = 'success',1,0)) as persist_num, max(p.time) as last_parse_time from "
                + "temp_partition_parser_tag p join (select input_dir from temp_partition_coordinator_job s where job_type='parser' and status='success' and "
                + dateRange
                + ") c  on "
                + "regexp_replace(regexp_replace(p.input_seqfile_path, 'hdfs://ip-10-199-6-149.us-west-1.compute.internal:8020', ''), concat('/',p.input_seqfile_name), '') = c.input_dir "
                + "where p.status is not null group by p.org_id, p.status, p.error_message";

        obj.put("parserDetails", queryHiveJson(parserDetailsQuery));

        String ocrDetailsQuery = "select p.org_id, p.status, p.error_message, count(distinct p.doc_id) as total_num, max(p.time) as last_parse_time from temp_partition_ocr p join (select input_dir from temp_partition_coordinator_job s where "
                + "job_type='ocr' and status='success' and "
                + dateRange
                + ") c  on "
                + "regexp_replace(regexp_replace(p.input_seqfile_path, 'hdfs://ip-10-199-6-149.us-west-1.compute.internal:8020', ''), concat('/',p.input_seqfil_name), '') = c.input_dir "
                + "where p.status is not null group by p.org_id, p.status, p.error_message";

        obj.put("ocrDetails", queryHiveJson(ocrDetailsQuery));

        String persistDetailsQuery = "select p.org_id, p.status, p.error_message, count(distinct p.doc_id) as total_num, max(p.time) as last_parse_time from temp_partition_persist_mapper p join (select input_dir from temp_partition_coordinator_job s where "
                + "job_type='persist' and status='success' and "
                + dateRange
                + ") c  on "
                + "regexp_replace(regexp_replace(p.input_seqfile_path, 'hdfs://ip-10-199-6-149.us-west-1.compute.internal:8020', ''), concat('/',p.input_seqfile_name), '') = c.input_dir "
                + "where p.status is not null group by p.org_id, p.status, p.error_message";

        obj.put("persistDetails", queryHiveJson(persistDetailsQuery));

        IOUtils.write(obj.toString(), new FileOutputStream("C:\\eclipse_new\\workspace\\hive-query-web-trunk\\src\\main\\resources\\assets\\report_" + daysBack + ".json"));
    }

    private static void createReport() throws JSONException, SQLException, FileNotFoundException, IOException
    {
        JSONObject obj = new JSONObject();
        String uploadQuery = "select org_id, status, if(message like '/mnt%','No space left on device',message) as message, count(distinct upload_doc_id) as docs_uploaded, max(time) as last_upload_time "
                + "from temp_partition_docreceiver_upload_document group by org_id, status, if(message like '/mnt%','No space left on device',message)";
        obj.put("upload", queryHiveJson(uploadQuery));

        /*String seqfileQuery = "select s.org_id, u.status, s.document_status, count(distinct seqfile_doc_id) as num_files, count(distinct seqfile_file) num_seq_files, max(s.time) as last_upload_time "
                + "from temp_partition_docreceiver_seqfile_document s left outer join temp_partition_docreceiver_upload_document u on s.seqfile_doc_id = u.upload_doc_id and s.org_id = u.org_id "
                + "where u.upload_doc_id is not null group by s.org_id, u.status, s.document_status";
        obj.put("seqfile", queryHiveJson(seqfileQuery));

        String abandonedSeqFileQuery = "select s.org_id, s.seqfile_file, count(s.seqfile_doc_id) as num_docs, max(s.time) as last_written_to from temp_partition_docreceiver_seqfile_document s left outer join "
                + "temp_partition_coordinator_hdfsmove c on c.move_from = s.seqfile_directory where c.move_from is null and s.document_status = 'success' and s.seqfile_file is not null group by s.org_id, s.seqfile_file";

        obj.put("abandonedSeqFile", queryHiveJson(abandonedSeqFileQuery));

        String jobDetailsQuery = "select c.org_id as org_id, c.job_type as job_type, c.status as status, count(distinct c.job_id) as num_jobs,  max(c.time) as last_update_time from temp_partition_coordinator_job c "
                + "inner join (select job_id, max(time) as time from temp_partition_coordinator_job group by job_id) m on m.job_id = c.job_id and c.time = m.time group by c.org_id, c.job_type, c.status";

        obj.put("jobDetails", queryHiveJson(jobDetailsQuery));

        String parserDetailsQuery = "select p.org_id, p.status, p.error_message, count(distinct p.doc_id) as total_num, sum(if(p.ocr_tag_status = 'success',1,0)) as ocr_num, sum(if(p.persist_tag_status = 'success',1,0)) as persist_num, max(p.time) as last_parse_time from "
                + "temp_partition_parser_tag p join (select input_dir from temp_partition_coordinator_job where job_type='parser' and status='success') c  on "
                + "regexp_replace(regexp_replace(p.input_seqfile_path, 'hdfs://ip-10-199-6-149.us-west-1.compute.internal:8020', ''), concat('/',p.input_seqfile_name), '') = c.input_dir "
                + "where p.status is not null group by p.org_id, p.status, p.error_message";

        obj.put("parserDetails", queryHiveJson(parserDetailsQuery));

        String ocrDetailsQuery = "select p.org_id, p.status, p.error_message, count(distinct p.doc_id) as total_num, max(p.time) as last_parse_time from temp_partition_ocr p join (select input_dir from temp_partition_coordinator_job where "
                + "job_type='ocr' and status='success') c  on "
                + "regexp_replace(regexp_replace(p.input_seqfile_path, 'hdfs://ip-10-199-6-149.us-west-1.compute.internal:8020', ''), concat('/',p.input_seqfil_name), '') = c.input_dir "
                + "where p.status is not null group by p.org_id, p.status, p.error_message";

        obj.put("ocrDetails", queryHiveJson(ocrDetailsQuery));

        String persistDetailsQuery = "select p.org_id, p.status, p.error_message, count(distinct p.doc_id) as total_num, max(p.time) as last_parse_time from temp_partition_persist_mapper p join (select input_dir from temp_partition_coordinator_job where "
                + "job_type='persist' and status='success') c  on "
                + "regexp_replace(regexp_replace(p.input_seqfile_path, 'hdfs://ip-10-199-6-149.us-west-1.compute.internal:8020', ''), concat('/',p.input_seqfile_name), '') = c.input_dir "
                + "where p.status is not null group by p.org_id, p.status, p.error_message";

        obj.put("persistDetails", queryHiveJson(persistDetailsQuery));*/

        IOUtils.write(obj.toString(), new FileOutputStream("reports.json"));
    }

    public static String rawQuery(String environment, String component, String startDate, String endDate, String level, String conditionOneObject, String conditionOneValue, String conditionTwoObject,
            String conditionTwoValue, String limit) throws SQLException, JSONException
    {

        String tableName = environment + "_logs_" + (Constants.COMPONENTS.valueOf(component.toUpperCase())).getTableName() + "_epoch";

        String whereClause = "";
        whereClause = addtoWhereClause(whereClause, getDateRange(startDate, endDate));
        whereClause = addtoWhereClause(whereClause, getLevel(level));
        whereClause = addtoWhereClause(whereClause, getCondition(conditionOneObject, conditionOneValue));
        whereClause = addtoWhereClause(whereClause, getCondition(conditionTwoObject, conditionTwoValue));

        String limitClause = getLimitClause(limit);
        String sql = "select line FROM " + tableName + whereClause + limitClause;
        return getLineJson(sql);
    }

    public static String getQueueStats(String environment, String startDate, String endDate) throws SQLException, JSONException
    {
        String sql = "select time, cast(parserQueue as int) as parserQueue, cast(ocrQueue as int) as ocrQueue, cast(traceQueue as int) as traceQueue, cast(persistQueue as int) as persistQueue " +
        // "from " + environment +
        // "_logs_coordinator_epoch TABLESAMPLE(1 PERCENT) s " +
                "from temp_partition_coordinator_stats " + "where " + getDateRange(startDate, endDate) + " order by time asc ";
        return queryHive(sql);
    }

    public static String getJobStats(String environment, String startDate, String endDate, String status) throws SQLException, JSONException
    {
        String sql = "select get_json_object(line, '$.datestamp') as time, " + "get_json_object(line, '$.coordinator.job.jobType') as jobType, " + "get_json_object(line, '$.coordinator.job.jobID'), "
                + "get_json_object(line, '$.coordinator.job.status') from " + environment + "_logs_coordinator_epoch " + "where " + getDateRange(startDate, endDate) + " order by time asc ";
        return queryHive(sql);
    }

    private static String getLimitClause(String limit)
    {
        String limitClause = "";
        if (!StringUtils.isBlank(limit))
            limitClause = " limit " + limit;
        return limitClause;
    }

    private static String getCondition(String conditionObject, String conditionValue)
    {
        String conditionClause = "";
        if (!StringUtils.isEmpty(conditionObject) && !StringUtils.isEmpty(conditionValue))
            conditionClause = "get_json_object(line, '$." + conditionObject + "') = \"" + conditionValue + "\"";
        return conditionClause;
    }

    private static String getLevel(String level)
    {
        String levelClause = "";
        if (!StringUtils.isBlank(level))
            levelClause = "get_json_object(line, '$.level') = \"" + level.toUpperCase() + "\"";
        return levelClause;
    }

    private static String addtoWhereClause(String whereClause, String clause)
    {
        if (!StringUtils.isBlank(clause))
        {
            if (StringUtils.isBlank(whereClause))
                whereClause = " WHERE (" + clause + ")";
            else
                whereClause += " AND (" + clause + ")";
        }
        return whereClause;
    }

    private static String getDateRange(String startDate, String endDate)
    {
        String dateRange = "";
        if (!StringUtils.isBlank(endDate) && endDate.length() == 10)
        {
            String endMonth = endDate.substring(0, 2);
            String endDay = endDate.substring(3, 5);
            dateRange = "((month < " + endMonth + ") OR (month = " + endMonth + " AND day <= " + endDay + "))";
        }

        if (!StringUtils.isBlank(startDate) && startDate.length() == 10)
        {
            String startMonth = startDate.substring(0, 2);
            String startDay = startDate.substring(3, 5);
            String beginClause = "((month > " + startMonth + ") OR (month = " + startMonth + " AND day >= " + startDay + "))";
            if (StringUtils.isBlank(dateRange))
                dateRange = beginClause;
            else
                dateRange += " AND " + beginClause;
        }

        return dateRange;
    }
   
    /**
     * @param args
     * @throws SQLException
     * @throws JSONException
     */
    public static String queryHive(String sql) throws SQLException, JSONException
    {
        String queryResult = "";
        try
        {
            Class.forName(driverName);
            Connection connection = DriverManager.getConnection("jdbc:hive2://184.169.209.24:10000", "hive", "");

            try
            {
                Statement statement = connection.createStatement();

                try
                {
                    log.info("Running: " + sql);
                    ResultSet resultSet = statement.executeQuery(sql);

                    try
                    {
                        queryResult = getJson(resultSet).toString();
                    }
                    finally
                    {
                        resultSet.close();
                    }
                }
                finally
                {
                    statement.close();
                }
            }
            finally
            {
                connection.close();
            }
        }
        catch (Exception ex)
        {

        }
        return queryResult;
    }

    /**
     * @param args
     * @throws SQLException
     * @throws JSONException
     */
    public static Object queryHiveJson(String sql) throws SQLException, JSONException
    {
        Object queryResult = "";
        try
        {
            Class.forName(driverName);
            Connection connection = DriverManager.getConnection("jdbc:hive2://184.169.209.24:10000", "hive", "");

            try
            {
                Statement statement = connection.createStatement();

                try
                {
                    log.info("Running: " + sql);
                    ResultSet resultSet = statement.executeQuery(sql);

                    try
                    {
                        queryResult = getJson(resultSet);
                    }
                    finally
                    {
                        resultSet.close();
                    }
                }
                finally
                {
                    statement.close();
                }
            }
            finally
            {
                connection.close();
            }
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
        }
        return queryResult;
    }

    private static String getLineJson(String sql)
    {
        String queryResult = "";
        try
        {
            Class.forName(driverName);
            Connection connection = DriverManager.getConnection("jdbc:hive2://184.169.209.24:10000", "hive", "");

            try
            {
                Statement statement = connection.createStatement();

                try
                {
                    log.info("Running: " + sql);
                    ResultSet resultSet = statement.executeQuery(sql);

                    try
                    {
                        Set<JSONObject> results = new HashSet<JSONObject>();
                        while (resultSet.next())
                        {
                            results.add(new JSONObject(resultSet.getString(1)));
                        }
                        queryResult = results.toString();
                    }
                    finally
                    {
                        resultSet.close();
                    }
                }
                finally
                {
                    statement.close();
                }
            }
            finally
            {
                connection.close();
            }
        }
        catch (Exception ex)
        {

        }
        return queryResult;
    }

    private static Object getJson(ResultSet rs) throws SQLException, JSONException
    {
        List<JSONObject> objSet = new ArrayList<JSONObject>();

        ResultSetMetaData rsmd = rs.getMetaData();
        while (rs.next())
        {
            JSONObject obj = new JSONObject();
            int numColumns = rsmd.getColumnCount();

            for (int i = 1; i < numColumns + 1; i++)
            {
                String column_name = rsmd.getColumnName(i);

                switch (rsmd.getColumnType(i))
                {
                    case java.sql.Types.ARRAY:
                        obj.put(column_name, rs.getArray(column_name));
                        break;
                    case java.sql.Types.BIGINT:
                        obj.put(column_name, rs.getInt(column_name));
                        break;
                    case java.sql.Types.BOOLEAN:
                        obj.put(column_name, rs.getBoolean(column_name));
                        break;
                    case java.sql.Types.BLOB:
                        obj.put(column_name, rs.getBlob(column_name));
                        break;
                    case java.sql.Types.DOUBLE:
                        obj.put(column_name, rs.getDouble(column_name));
                        break;
                    case java.sql.Types.FLOAT:
                        obj.put(column_name, rs.getFloat(column_name));
                        break;
                    case java.sql.Types.INTEGER:
                        obj.put(column_name, rs.getInt(column_name));
                        break;
                    case java.sql.Types.NVARCHAR:
                        obj.put(column_name, rs.getNString(column_name));
                        break;
                    case java.sql.Types.VARCHAR:
                        obj.put(column_name, rs.getString(column_name));
                        break;
                    case java.sql.Types.TINYINT:
                        obj.put(column_name, rs.getInt(column_name));
                        break;
                    case java.sql.Types.SMALLINT:
                        obj.put(column_name, rs.getInt(column_name));
                        break;
                    case java.sql.Types.DATE:
                        obj.put(column_name, rs.getDate(column_name));
                        break;
                    case java.sql.Types.TIMESTAMP:
                        obj.put(column_name, rs.getTimestamp(column_name));
                        break;
                    default:
                        obj.put(column_name, rs.getObject(column_name));
                        break;
                }
            }
            objSet.add(obj);
        }
        return objSet;
    }

}
