package com.apixio.qa.reporting.conf;

import com.yammer.dropwizard.config.Configuration;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.NotEmpty;

public class ApiConfiguration extends Configuration
{
    @NotEmpty
    @JsonProperty
    private String url;
    @NotEmpty
    @JsonProperty
    private String authUrl;
    @NotEmpty
    @JsonProperty
    private String tokenUrl;
    @NotEmpty
    @JsonProperty
    private String dataUrl;

    public String getAuthUrl() {
        return authUrl;
    }

    public String getTokenUrl() {
        return tokenUrl;
    }

    public String getDataUrl() {
        return dataUrl;
    }
        
    public String getUrl()
    {
        return url;
    }
}