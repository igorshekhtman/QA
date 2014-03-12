package apixio.hive.service;

import apixio.hive.conf.QueryHiveConfiguration;
import apixio.hive.resource.QueryHiveResource;

import com.yammer.dropwizard.Service;
import com.yammer.dropwizard.assets.AssetsBundle;
import com.yammer.dropwizard.config.Bootstrap;
import com.yammer.dropwizard.config.Environment;

public class QueryHiveService extends Service<QueryHiveConfiguration> {
    public static void main(String[] args) throws Exception {
        new QueryHiveService().run(args);
    }

	@Override
	public void initialize(Bootstrap<QueryHiveConfiguration> bootstrap) {
	    bootstrap.setName("Query Hive");
	    bootstrap.addBundle(new AssetsBundle("/assets", "/html"));
	}

	@Override
	public void run(QueryHiveConfiguration configuration, Environment environment) throws Exception {

	    final String hiveAddress = configuration.getHiveAddress();
	    final String updateInterval = configuration.getUpdateInterval();
	    environment.addResource(new QueryHiveResource(hiveAddress, updateInterval));
	}

}
