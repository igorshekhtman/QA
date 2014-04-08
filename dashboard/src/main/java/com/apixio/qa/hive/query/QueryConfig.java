package com.apixio.qa.hive.query;

import java.util.List;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.Unmarshaller;

import com.apixio.qa.hive.query.generated.Queries;
import com.apixio.qa.hive.query.generated.Queries.Group;
import com.apixio.qa.hive.query.generated.Queries.Group.RunQuery;
import com.apixio.qa.hive.query.generated.Queries.Query;

public class QueryConfig
{
    private Queries queries = null;
    
    private QueryConfig()
    {
        try
        {
            JAXBContext jaxbContext = JAXBContext.newInstance("com.apixio.qa.hive.query.generated");
            Unmarshaller unmarshaller = jaxbContext.createUnmarshaller();
            
            queries = (Queries)unmarshaller.unmarshal(Thread.currentThread().getContextClassLoader().getResourceAsStream("queries.xml"));
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }
    
    private static class SingletonHolder
    {
        public static final QueryConfig instance = new QueryConfig();
    }
    
    public static Queries getQueries()
    {
        return SingletonHolder.instance.queries;
    }
    //TODO may be I should create Maps for this to avoid looping..
    public static Group getQueryGroupByName(String name)
    {
        Queries queries = getQueries();
        
        List<Group> groups = queries.getGroup();
        
        if (groups != null)
        {
            for (Group group : groups)
            {
                if (group.getName().equalsIgnoreCase(name))
                    return group;
            }
        }
        return null;
    }
    
    public static List<RunQuery> getRunQueriesOfGroup(String groupName)
    {
        Group group = getQueryGroupByName(groupName);
        
        if (group != null)
            return group.getRunQuery();
        
        return null;
    }
    
    public static List<Query> getQueryList()
    {
        return getQueries().getQuery();
    }
    //TODO may be I should create Maps for this to avoid looping..
    public static Query getQuery(String queryName)
    {
        List<Query> queries = getQueryList();
        
        if (queries != null)
        {
            for (Query query : queries)
            {
                if (query.getName().equalsIgnoreCase(queryName))
                    return query;
            }
        }
        return null;
    }
}
