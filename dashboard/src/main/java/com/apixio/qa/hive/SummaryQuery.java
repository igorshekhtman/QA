package com.apixio.qa.hive;

public class SummaryQuery {
	
	private String description;
	private String tableName;
	private String createStatement;
	private String query;

	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getTableName() {
		return tableName;
	}
	public void setTableName(String tableName) {
		this.tableName = tableName;
	}
	public String getCreateStatement() {
		return createStatement;
	}
	public void setCreateStatement(String createStatement) {
		this.createStatement = createStatement;
	}
	public String getQuery() {
		return query;
	}
	public void setQuery(String query) {
		this.query = query;
	}

}
