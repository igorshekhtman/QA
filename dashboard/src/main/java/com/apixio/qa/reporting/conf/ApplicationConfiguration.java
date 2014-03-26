package com.apixio.qa.reporting.conf;

import com.yammer.dropwizard.config.Configuration;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.NotEmpty;

public class ApplicationConfiguration extends Configuration
{
    @NotEmpty
    @JsonProperty
    private String outputDir;
        
    public String getOutputDir()
    {
        return outputDir;
    }
}