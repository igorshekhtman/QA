package com.apixio.qa.hive.query;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import javax.ws.rs.core.MultivaluedMap;

import org.apache.log4j.Logger;
import org.json.JSONException;
import org.json.JSONObject;

import com.apixio.qa.hive.query.generated.Queries.Group;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery.Param;
import com.apixio.qa.hive.query.generated.Queries.Query;

public class QueryHandler
{
    private static String driverName = "org.apache.hive.jdbc.HiveDriver";
    private static Logger log = Logger.getLogger(QueryHandler.class);
    private String hiveAddress;
    
    public QueryHandler(String hiveAddress)
    {
        this.hiveAddress = hiveAddress;
    }

    public List<JSONObject> runQuery(String environment, RunQuery queryToRun) throws SQLException, JSONException
    {
        Query query = QueryConfig.getQuery(queryToRun.getName());
        
        String queryText = query.getText(environment);
        
        return queryHive(queryToRun.getParam(), queryText);
    }
    
    public List<JSONObject> runQuery(String environment, String queryName, MultivaluedMap<String,String> queryParams) throws SQLException, JSONException
    {
        Query query = QueryConfig.getQuery(queryName);
        
        if (query != null)
        {
            String queryText = query.getText(environment);
            
            String modifiedQuery = QueryHiveUtilities.addUserParamsToWhereClause(queryText, queryParams);
            
            return queryHive(new ArrayList<Param>(), modifiedQuery);
        }
        return null;
    }
    
    public static void main(String[] args)
    {
        String hiveAddress = "jdbc:hive2://184.169.209.24:10000";
        Group groupToRun = QueryConfig.getQueryGroupByName("completeness");
        QueryHandler qh = new QueryHandler(hiveAddress);
        
        List<RunQuery> rQs = groupToRun.getRunQuery();
        
        if (rQs != null)
        {
            for (RunQuery rQ : rQs)
            {
                try
                {
                    System.out.println(qh.runQuery("production", rQ).toString());
                }
                catch (SQLException e)
                {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
                catch (JSONException e)
                {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
        }
    }
    
    private List<JSONObject> queryHive(List<Param> parameters, String sql) throws SQLException, JSONException
    {
        try
        {
            Class.forName(driverName);
            Connection connection = DriverManager.getConnection(hiveAddress, "hive", "");

            try
            {
                connection.createStatement().execute("set mapred.job.queue.name=default");
                PreparedStatement prepStatement = connection.prepareStatement(sql);

                try
                {
                    log.info("Running: " + sql);
                    
                    for (Param param : parameters)
                    {
                        prepStatement.setString(param.getIndex().intValue(), param.getVal());
                    }
                    
                    ResultSet resultSet = prepStatement.executeQuery();

                    try
                    {
                        return getJsonObjects(resultSet);
                    }
                    finally
                    {
                        resultSet.close();
                    }
                }
                finally
                {
                    prepStatement.close();
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
            return null;
        }
    }
    
    private List<JSONObject> getJsonObjects(ResultSet rs) throws SQLException, JSONException
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
