function expandOrCollapse(element) {
	console.log(element);
	console.log($(element).siblings(".expandableContent"));
	$(element).siblings(".expandableContent").slideToggle(500);
}

function loadChart() {
	$("#chartSpan").load("chart_new.html");
}

function refreshRecentErrors() {
	
	var _selected = $("#envDropdown").val();
	var jobNames = ["parserJob", "ocrJob", "persistJob", "json2trace", "dataCheckAndRecover"];
	
	for (var i = 0 ; i < jobNames.length; i ++) {
		
		var tableName = _selected+"_logs_"+jobNames[i]+"_epoch";
		
		var url = "/hive/table/query/"+tableName+"/recent_errors?month=06&day=10,09&year=2014";
		
		$.get(url).done(function( values ) {
			var contentHtml = "<ul>";
			
			$.each(values.results, function(n, data) {
				contentHtml = contentHtml + "<li>";
				
				var orgDiv = "<div id='div_"+data.org_id+"' class='notice'>\
							  Org Name (Org Id) : {{org_name}} ({{org_id}})\
							  <p><a onclick='expandOrCollapse(this)'>Upload Errors</a><br/>\
							  <div class='expandableContent' style='display: none'><ul>{{#upload_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/upload_count}}</ul></div></p>\
							  <p><a onclick='expandOrCollapse(this)'>Parser Errors</a>\
							  <ul class='expandableContent' style='display: none'>{{#parser_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/parser_error_count}}</ul></p>\
							  <p><a onclick='expandOrCollapse(this)'>OCR Errors</a>\
							  <ul class='expandableContent' style='display: none'>{{#ocr_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/ocr_error_count}}</ul></p>\
				              <p><a onclick='expandOrCollapse(this)'>Persist Errors</a>\
				              <ul class='expandableContent' style='display: none'>{{#persist_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/persist_error_count}}</ul></p>\
							  <p><a onclick='expandOrCollapse(this)'>Persist Reducer Errors</a>\
	            			  <ul class='expandableContent' style='display: none'>{{#persistReducer_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/persistReducer_error_count}}</ul></p>\
							  </div>";
				
				contentHtml = contentHtml + Mustache.render(orgDiv, data);
				contentHtml = contentHtml + "</li>";
			});
			
			contentHtml = contentHtml + "</ul>";
			
			$("#errorsDiv").html(contentHtml);
		});
	}
}

function loadRecentErrors() {
	
	var _selected = $("#envDropdown").val();
	var url = "/hive/json/"+_selected+"/ui/group/recentErrors";
	
	$.get(url).done(function( values ) {
		var contentHtml = "<ul>";
		
		$.each(values.results, function(n, data) {
			contentHtml = contentHtml + "<li>";
			
			var orgDiv = "<div id='div_"+data.org_id+"' class='notice'>\
						  Org Name (Org Id) : {{org_name}} ({{org_id}})\
						  <p><a onclick='expandOrCollapse(this)'>Upload Errors</a><br/>\
						  <div class='expandableContent' style='display: none'><ul>{{#upload_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/upload_count}}</ul></div></p>\
						  <p><a onclick='expandOrCollapse(this)'>Parser Errors</a>\
						  <ul class='expandableContent' style='display: none'>{{#parser_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/parser_error_count}}</ul></p>\
						  <p><a onclick='expandOrCollapse(this)'>OCR Errors</a>\
						  <ul class='expandableContent' style='display: none'>{{#ocr_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/ocr_error_count}}</ul></p>\
			              <p><a onclick='expandOrCollapse(this)'>Persist Errors</a>\
			              <ul class='expandableContent' style='display: none'>{{#persist_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/persist_error_count}}</ul></p>\
						  <p><a onclick='expandOrCollapse(this)'>Persist Reducer Errors</a>\
            			  <ul class='expandableContent' style='display: none'>{{#persistReducer_error_count}}<li type=square>Error message:<i>{{msg}}</i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/persistReducer_error_count}}</ul></p>\
						  </div>";
			
			contentHtml = contentHtml + Mustache.render(orgDiv, data);
			contentHtml = contentHtml + "</li>";
		});
		
		contentHtml = contentHtml + "</ul>";
		
		$("#errorsDiv").html(contentHtml);
	});
}

function loadRecentFailedJobs() {
	$("#failedJobsSpan").load("chart_new.html");
}