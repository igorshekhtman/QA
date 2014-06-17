package com.apixio.qa.reporting.conf;

import com.yammer.dropwizard.config.Configuration;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.NotEmpty;

public class ApplicationConfiguration extends Configuration
{
    @NotEmpty
    @JsonProperty
    private String outputDir;
    
    @JsonProperty
    private String manifestDir;
        
    public String getOutputDir()
    {
        return outputDir;
    }
    
    public String getManifestDir()
    {
        return manifestDir;
    }
}