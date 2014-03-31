package com.apixio.qa.reporting.service;

import com.apixio.qa.hive.resource.ApiResource;
import com.apixio.qa.hive.resource.GraphiteResource;
import com.apixio.qa.hive.resource.NagiosResource;
import com.apixio.qa.hive.resource.QueryHiveResource;
import com.apixio.qa.reporting.conf.ReportingServiceConfiguration;
import com.yammer.dropwizard.Service;
import com.yammer.dropwizard.assets.AssetsBundle;
import com.yammer.dropwizard.config.Bootstrap;
import com.yammer.dropwizard.config.Environment;

public class ReportingService extends Service<ReportingServiceConfiguration>
{
    public static void main(String[] args) throws Exception
    {
        new ReportingService().run(args);
    }

    @Override
    public void initialize(Bootstrap<ReportingServiceConfiguration> bootstrap)
    {
        bootstrap.setName("Query Hive");
        bootstrap.addBundle(new AssetsBundle("/assets", "/html"));
    }

    @Override
    public void run(ReportingServiceConfiguration configuration, Environment environment) throws Exception
    {
        final String hiveAddress = configuration.getHiveConfiguration().getUrl();
        final String updateInterval = "90";
        final String outputDir = configuration.getApplicationConfiguration().getOutputDir();
        environment.addResource(new QueryHiveResource(hiveAddress, updateInterval, outputDir));
        
        environment.addResource(new GraphiteResource(configuration.getGraphiteConfiguration()));
        
        final String nagiosUrl = configuration.getNagiosConfiguration().getUrl();
        final String nagiosUsername = configuration.getNagiosConfiguration().getUsername();
        final String nagiosPassword = configuration.getNagiosConfiguration().getPassword();
        environment.addResource(new NagiosResource(nagiosUrl, nagiosUsername, nagiosPassword));
        
        final String apiUrl = configuration.getApiConfiguration().getUrl();
        environment.addResource(new ApiResource(apiUrl));
    }
}
