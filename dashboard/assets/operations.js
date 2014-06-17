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
	
	var _selected = $("#envDropdownForErrors").val();
	var url = "/hive/json/"+_selected+"/ui/group/recentErrors";
	
	$.get(url).done(function( values ) {
		var contentHtml = "<ul>";
		
		$.each(values.results, function(n, data) {
			contentHtml = contentHtml + "<li>";
			
			var orgDiv = "<div id='div_"+data.org_id+"' class='redBox'>\
						  Org Name (Org Id) : {{org_name}} ({{org_id}})\
						  <br/>\
						  <a>Upload Errors</a><br/>\
						  <div class='expandableContent'><ul class='squareList'>{{#upload_count}}<li type=square>Error message:<i><font color='#FA5858'>{{msg}}</font></i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/upload_count}}</ul></div>\
						  <br/>\
						  <a>Parser Errors</a>\
						  <div class='expandableContent'><ul class='squareList'>{{#parser_error_count}}<li type=square>Error message:<i><font color='#FA5858'>{{msg}}</font></i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/parser_error_count}}</ul></div>\
						  <br/>\
						  <a>OCR Errors</a>\
						  <div class='expandableContent'><ul class='squareList'>{{#ocr_error_count}}<li type=square>Error message:<i><font color='#FA5858'>{{msg}}</font></i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/ocr_error_count}}</ul></div>\
			              <br/>\
			              <a>Persist Errors</a>\
			              <div class='expandableContent'><ul class='squareList'>{{#persist_error_count}}<li type=square>Error message:<i><font color='#FA5858'>{{msg}}</font></i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/persist_error_count}}</ul></div>\
						  <br/>\
						  <a>Persist Reducer Errors</a>\
            			  <div class='expandableContent'><ul class='squareList'>{{#persistReducer_error_count}}<li type=square>Error message:<i><font color='#FA5858'>{{msg}}</font></i>, happened <b>{{count}}</b> time(s), last seen on: {{time}}</li>{{/persistReducer_error_count}}</ul></div>\
						  </div>";
			
			contentHtml = contentHtml + Mustache.render(orgDiv, data);
			contentHtml = contentHtml + "</li>";
		});
		
		contentHtml = contentHtml + "</ul>";
		
		$("#errorsDiv").html(contentHtml);
	});
}

function loadFailedJobs() {
	var _selected = $("#envDropdownForFailed").val();
    	var url = "/hive/json/"+_selected+"/ui/group/failedJobs";

    	$.get(url).done(function( values ) {
    		var contentHtml = "<ul>";

    		$.each(values.results, function(n, data) {
    			contentHtml = contentHtml + "<li>";

    			var orgDiv = "<div id='div_"+data.org_id+"' class='redBox'>\
    						  Org Name (Org Id) : {{org_name}} ({{org_id}})\
    						  <br/>\
    						  <a>Failed Parser Jobs</a><br/>\
    						  <div class='expandableContent'><ul class='squareList'>{{#parser}}<li type=square>Hadoop JobId:<i><font color='#FA5858'>{{hadoop_job_id}}</font></i>, JobId:<i><font color='#FA5858'>{{job_id}}</font></i>, BatchId:<i><font color='#FA5858'>{{batch_id}}</font></i>, failed on: {{time}}</li>{{/parser}}</ul></div>\
    						  <br/>\
    						  <a>Failed OCR Jobs</a><br/>\
                              <div class='expandableContent'><ul class='squareList'>{{#ocr}}<li type=square>Hadoop JobId:<i><font color='#FA5858'>{{hadoop_job_id}}</font></i>, JobId:<i><font color='#FA5858'>{{job_id}}</font></i>, BatchId:<i><font color='#FA5858'>{{batch_id}}</font></i>, failed on: {{time}}</li>{{/ocr}}</ul></div>\
                              <br/>\
                              <a>Failed Persist Jobs</a><br/>\
                              <div class='expandableContent'><ul class='squareList'>{{#persist}}<li type=square>Hadoop JobId:<i><font color='#FA5858'>{{hadoop_job_id}}</font></i>, JobId:<i><font color='#FA5858'>{{job_id}}</font></i>, BatchId:<i><font color='#FA5858'>{{batch_id}}</font></i>, failed on: {{time}}</li>{{/persist}}</ul></div>\
                              <br/>\
                              <a>Failed Trace Jobs</a><br/>\
                              <div class='expandableContent'><ul class='squareList'>{{#trace}}<li type=square>Hadoop JobId:<i><font color='#FA5858'>{{hadoop_job_id}}</font></i>, JobId:<i><font color='#FA5858'>{{job_id}}</font></i>, BatchId:<i><font color='#FA5858'>{{batch_id}}</font></i>, failed on: {{time}}</li>{{/trace}}</ul></div>\
                              <br/>\
                              <a>Failed RerunPersistReducer Jobs</a><br/>\
                              <div class='expandableContent'><ul class='squareList'>{{#rerunPersistReducer}}<li type=square>Hadoop JobId:<i><font color='#FA5858'>{{hadoop_job_id}}</font></i>, JobId:<i><font color='#FA5858'>{{job_id}}</font></i>, BatchId:<i><font color='#FA5858'>{{batch_id}}</font></i>, failed on: {{time}}</li>{{/rerunPersistReducer}}</ul></div>\
                              ";

    			contentHtml = contentHtml + Mustache.render(orgDiv, data);
    			contentHtml = contentHtml + "</li>";
    		});

    		contentHtml = contentHtml + "</ul>";

    		$("#failedJobsSpan").html(contentHtml);
    	});
}