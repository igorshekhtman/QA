package com.apixio.qa.hive.conf;

import com.yammer.dropwizard.config.Configuration;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.NotEmpty;

public class QueryHiveConfiguration extends Configuration
{
    @NotEmpty
    @JsonProperty
    private String hiveAddress;

    public String getHiveAddress()
    {
        return hiveAddress;
    }

    @NotEmpty
    @JsonProperty
    private String updateInterval;

    public String getUpdateInterval()
    {
        return updateInterval;
    }
}