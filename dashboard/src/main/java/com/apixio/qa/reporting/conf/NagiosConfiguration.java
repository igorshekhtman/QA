package com.apixio.qa.reporting.conf;

import com.yammer.dropwizard.config.Configuration;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.NotEmpty;

public class NagiosConfiguration extends Configuration
{
    @NotEmpty
    @JsonProperty
    private String url;

	@NotEmpty
    @JsonProperty
    private String username;
    
    @NotEmpty
    @JsonProperty
    private String password;
        
    public String getUrl()
    {
        return url;
    }

    public String getUsername() {
		return username;
    }

	public String getPassword() {
		return password;
	}
}