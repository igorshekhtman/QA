package com.apixio.qa.reporting.conf;

import javax.validation.constraints.NotNull;

import com.yammer.dropwizard.config.Configuration;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.NotEmpty;

public class ReportingServiceConfiguration extends Configuration
{
	@NotNull
    @JsonProperty
    private HiveConfiguration hiveConfiguration;
    
    @NotNull
    @JsonProperty
    private GraphiteConfiguration graphiteConfiguration;
    
    @NotNull
    @JsonProperty
    private NagiosConfiguration nagiosConfiguration;

	@NotNull
    @JsonProperty
    private ApplicationConfiguration applicationConfiguration;
	
	@NotNull
    @JsonProperty
    private ApiConfiguration apiConfiguration;

	public HiveConfiguration getHiveConfiguration() {
		return hiveConfiguration;
	}

	public void setHiveConfiguration(HiveConfiguration hiveConfiguration) {
		this.hiveConfiguration = hiveConfiguration;
	}

	public GraphiteConfiguration getGraphiteConfiguration() {
		return graphiteConfiguration;
	}

	public void setGraphiteConfiguration(GraphiteConfiguration graphiteConfiguration) {
		this.graphiteConfiguration = graphiteConfiguration;
	}

	public NagiosConfiguration getNagiosConfiguration() {
		return nagiosConfiguration;
	}

	public void setNagiosConfiguration(NagiosConfiguration nagiosConfiguration) {
		this.nagiosConfiguration = nagiosConfiguration;
	}
    
    public ApplicationConfiguration getApplicationConfiguration() {
		return applicationConfiguration;
	}

	public void setApplicationConfiguration(
			ApplicationConfiguration applicationConfiguration) {
		this.applicationConfiguration = applicationConfiguration;
	}
    
	public ApiConfiguration getApiConfiguration() {
		return apiConfiguration;
	}

	public void setApiConfiguration(ApiConfiguration apiConfiguration) {
		this.apiConfiguration = apiConfiguration;
	}
}