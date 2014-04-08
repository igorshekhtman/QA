function constructChartJson(data) {
   var jsonStr = "";
   var sentToOcr = data.sent_to_ocr;
   var sentToPersist = data.sent_to_persist;
   var persisted = data.persist_success_count;
   var persistVerified = data.verified_count;
   var ocr = data.ocr_success_count;
   var uploadRange = data.upload_count;
   var ocrRange = data.sent_to_ocr;
   
   if (sentToOcr == undefined)
	   sentToOcr = 0;
   if (sentToPersist == undefined)
	   sentToPersist = 0;
   if (persisted == undefined)
	   persisted = 0;
   if (persistVerified == undefined)
	   persistVerified = 0;
   if (ocr == undefined)
	   ocr = 0;
   if (uploadRange == undefined)
	   uploadRange = 0;
   if (ocrRange == undefined)
	   ocrRange = 0;
   
   jsonStr = [{"title":data.org_name,"subtitle":data.org_id,"measures":[persistVerified,persisted,ocr,sentToOcr+sentToPersist],"ranges":[uploadRange,sentToOcr],"markers":[uploadRange]}];
   
   return jsonStr;
}  
           
function processErrors(errors) {
   if (errors != undefined) {
	   var errorDetails = new Object();
	   var errorArr = new Array();
	   var i = 0;
	   var total = 0;
	   $.each(errors, function(key, value){
           errorArr[i] = {"error_msg":key,"count":value};
           total = total + value;
           i ++;
        });
	   
	   errorDetails.errorGroup = errorArr;
	   errorDetails.total = total;
	   
	   return errorDetails;
   }
   else {
	   return {};
   }
}
           
function processPendingDocuments(data) {
   var pendingObj = new Object();
   var drqArray = new Array();
   var i = 0;
   var total = 0;
   if (data.docreceiver_queue_count != undefined){
	   $.each(data.docreceiver_queue_count, function(key, value){
           drqArray[i] = {"seqfile":key,"doc_count":value.doc_count, "since":value.last_updated};
           if (value.doc_count != undefined)
               total = total + value.doc_count;
           i ++;
       });
       pendingObj.total = total;
       pendingObj.pendingGroup = drqArray;
       pendingObj.totalSeqFiles = i;
   }
   
   return pendingObj;
}
           
function calculateMissingDocuments(data, errorDetails) {
   var missingDocs = new Object();
   var sentToOcr = data.sent_to_ocr;
   var sentToPersist = data.sent_to_persist;
   var persisted = data.persist_success_count;
   var ocr = data.ocr_success_count;
   var uploaded = data.upload_count;
   var pendingParsers = data.pending_parsers;
   var pendingPersists = data.pending_persists;
   var pendingOcrs = data.pending_ocrs;
   var errorParsers = errorDetails.parser_errors.total;
   var errorPersists = errorDetails.persist_errors.total;
   var errorOcrs = errorDetails.ocr_errors.total;
   var failedParsers = data.failed_parsers;
   var failedPersists = data.failed_persists;
   var failedOcrs = data.failed_ocrs;
   
   missingDocs.documentsAbandoned = processAbandonedDocuments(data);
   
   if (sentToOcr == undefined)
       sentToOcr = 0;
   if (sentToPersist == undefined)
       sentToPersist = 0;
   if (persisted == undefined)
       persisted = 0;
   if (ocr == undefined)
       ocr = 0;
   if (uploaded == undefined)
	   uploaded = 0;
   if (pendingParsers == undefined)
	   pendingParsers = 0;
   if (pendingPersists == undefined)
	   pendingPersists = 0;
   if (pendingOcrs == undefined)
	   pendingOcrs = 0;
   if (failedParsers == undefined)
	   failedParsers = 0;
   if (failedOcrs == undefined)
	   failedOcrs = 0;
   if (failedPersists == undefined)
	   failedPersists = 0;
   if (errorParsers == undefined)
	   errorParsers = 0;
   if (errorOcrs == undefined)
	   errorOcrs = 0;
   if (errorPersists == undefined)
	   errorPersists = 0;
   
   missingDocs.missingParser = uploaded - (sentToOcr + sentToPersist + pendingParsers + failedParsers + errorParsers);
   missingDocs.missingOCR = sentToOcr - (ocr + pendingOcrs + failedOcrs + errorOcrs);
   missingDocs.missingPersist = (sentToPersist + ocr) - (persisted + failedPersists + errorPersists + pendingPersists);
   
   missingDocs.totalDocs = missingDocs.missingParser + missingDocs.missingOCR + missingDocs.missingPersist;
   
   return missingDocs;
}

function processAbandonedDocuments(data) {
   var abObj = new Object();
   var abArray = new Array();
   var i = 0;
   var total = 0;
   if (data.docs_abandoned_count != undefined) {
	   $.each(data.docs_abandoned_count, function(key, value) {
		   abArray[i] = {"seqfile":key,"doc_count":value.doc_count, "since":value.posted_time};
           if (value.doc_count != undefined)
               total = total + value.doc_count;
           i ++;
       });
	   abObj.total = total;
	   abObj.abGroup = abArray;
	   abObj.totalSeqFiles = i;
   }
   
   return abObj;
}

function scrollToOrg() {
	var _selected = $("#orgDropdown").val();
	var scrollPos = "#tbl_"+_selected;
	if (_selected == '')
		scrollPos = "#orgDetails";
	
	$('html, body').animate({
		
		scrollTop: $(scrollPos).offset().top
		
	}, 1000);
	//$.scrollTo('#tbl_'+_selected);
}

function resetOptionsOfOrgs() {
	var orgDropdownEle = $("#orgDropdown");
	
	orgDropdownEle.empty();
	orgDropdownEle.append( new Option('Select Org', '', true, true) );
}

function addOptionToOrgs(text, val) {
	$("#orgDropdown").append( new Option(text, val) );
}

function loadData() {
	
	var _selected = $("#envDropdown").val();
	
	resetOptionsOfOrgs();
	//------------Fetching data script---------------
	var url = "/hive/json/"+_selected+"/ui/group/completeness";
	
	//------------Bullet chart script-----------------------
	var margin = {top: 5, right: 40, bottom: 20, left: 120},
	width = 960 - margin.left - margin.right,
	height = 50 - margin.top - margin.bottom;

	var chart = d3.bullet()
	    .width(width)
	    .height(height);

	 $.get(url).done(function( values ) {
		 
		 var orgHtml = "<ul>";
		 var alternate = 0;
		 
		 $.each(values.orgs, function(n, data) {
			 
			 //add org data to dropdown.
			 addOptionToOrgs(data.org_name+'('+data.org_id+')', data.org_id);
			 
			 orgHtml = orgHtml + "<li class='alternate s"+alternate+"'>";
			 
			 var successDiv = "\
	             <table id='tbl_"+data.org_id+"' class='success'> \
	             <tr><th>Org Name (Org Id)</th><th>Successful archives</th><th>Successful Uploads to Pipeline</th><th>Sent To OCR</th><th>Sent To Persist</th><th>OCRed</th><th>Persisted</th><th>Verified Persistence</th></tr>\
	             <tr>\
	             <td>{{org_name}} ({{org_id}})</td>\
	             <td>{{archivedToS3_count}}</td>\
	             <td>{{upload_count}}</td>\
	             <td>{{sent_to_ocr}}</td>\
	             <td>{{sent_to_persist}}</td>\
	             <td>{{ocr_success_count}}</td>\
	             <td>{{persist_success_count}}</td>\
	             <td>{{verified_count}}</td>\
	             </tr>\
	             </table>\
	             ";

	             orgHtml = orgHtml + Mustache.render(successDiv, data);
	             
	             var chartId = 'chart'+n;
	             orgHtml = orgHtml + "<div id='"+chartId+"'></div><br/>";
	             
	         var pendingObj = processPendingDocuments(data);
	         pendingObj.org_name = data.org_name;
	         pendingObj.org_id = data.org_id;
	         pendingObj.pending_parsers = data.pending_parsers;
	         pendingObj.pending_ocrs = data.pending_ocrs;
	         pendingObj.pending_persists = data.pending_persists;
	         
	         var pendingDiv = "<table class='notice'> \
	    	     <tr><th>Org Name (Org Id)</th><th>Documents in docreceiver's queue</th><th>Pending Parser documents</th><th>Pending Persist documents</th><th>Pending OCR documents</th>\
	    	     <tr><td>{{org_name}}({{org_id}})</td>\
	    	     <td>Total:<b>{{total}}</b> (No. of Seq files: <b>{{totalSeqFiles}}</b>)<br/><b>Details:</b><br/>{{#pendingGroup}}<i>{{seqfile}}</i>: <b>{{doc_count}}</b> Since: {{since}}<br/>{{/pendingGroup}}</td>\
	    	     <td>{{pending_parsers}}</td>\
	             <td>{{pending_ocrs}}</td>\
	             <td>{{pending_persists}}</td></tr>\
	    	     ";       
	             
	             orgHtml = orgHtml + Mustache.render(pendingDiv, pendingObj);
	             
	             var errorObj = new Object();
	             
	             errorObj.org_name = data.org_name;
	             errorObj.org_id = data.org_id;
	             errorObj.upload_errors = processErrors(data.upload_errors);
	             errorObj.archive_errors = processErrors(data.archive_errors);
	             errorObj.parser_errors = processErrors(data.parse_errors);
	             errorObj.persist_errors = processErrors(data.persist_errors);
	             errorObj.ocr_errors = processErrors(data.ocr_errors);
	             errorObj.failed_parsers = data.failed_parsers;
	             errorObj.failed_ocrs = data.failed_ocrs;
	             errorObj.failed_persists = data.failed_persists;
	             
	             var errorDiv = "<table class='error'>\
	                             <tr><th>Org Name (Org Id)</th><th>Archive Error Documents</th><th>Upload Error Documents</th><th>Parser Error Documents</th><th>OCR Error Documents</th><th>Persist Error Documents</th><th>Failed Parser Documents</th><th>Failed OCR Documents</th><th>Failed Persist Documents</th></tr>\
	                             <tr><td>{{org_name}} ({{org_id}})</td><td>Total:<b>{{archive_errors.total}}</b><br/>{{#archive_errors.errorGroup}}<i>{{error_msg}}:</i> <b>{{count}}</b><br/>{{/archive_errors.errorGroup}}</td>\
	                             <td>Total:<b>{{upload_errors.total}}</b><br/><b>Details:</b><br/>{{#upload_errors.errorGroup}}<i>{{error_msg}}:</i> <b>{{count}}</b><br/>{{/upload_errors.errorGroup}}</td>\
	                             <td>Total:<b>{{parser_errors.total}}</b><br/><b>Details:</b><br/>{{#parser_errors.errorGroup}}<i>{{error_msg}}:</i> <b>{{count}}</b><br/>{{/parser_errors.errorGroup}}</td>\
	                             <td>Total:<b>{{ocr_errors.total}}</b><br/><b>Details:</b><br/>{{#ocr_errors.errorGroup}}<i>{{error_msg}}:</i> <b>{{count}}</b><br/>{{/ocr_errors.errorGroup}}</td>\
	                             <td>Total:<b>{{persist_errors.total}}</b><br/><b>Details:</b><br/>{{#persist_errors.errorGroup}}<i>{{error_msg}}:</i> <b>{{count}}</b><br/>{{/persist_errors.errorGroup}}</td>\
	                             <td class='notice'>{{failed_parsers}}</td><td class='notice'>{{failed_ocrs}}</td><td class='notice'>{{failed_persists}}</td></tr>\
	                             </table>";
	                             
	             orgHtml = orgHtml + Mustache.render(errorDiv, errorObj);
	             
	             var missingDocsData = calculateMissingDocuments(data, errorObj);
	             missingDocsData.org_name = data.org_name;
	             missingDocsData.org_id = data.org_id;
	             missingDocsData.abandoned_docs = data.abandoned_docs;
	             
	             var missingDocsDiv = "<table class='fatal'>\
	            	                   <tr><th>Org Name (Org Id)</th><th>Documents abandoned</th><th>Documents not seen by parser</th><th>Documents seen by parser but missed by OCR job</th><th>Documents seen by parser but missed by Persist job</th><th>Total documents to be recovered</th></tr>\
	            	                   <tr><td>{{org_name}} ({{org_id}})</td><td>Total: <b>{{documentsAbandoned.total}}</b>(No. of Seq files: <b>{{documentsAbandoned.totalSeqFiles}}</b>)<br/><b>Details:</b><br/>{{#documentsAbandoned.abGroup}}<i>{{seqfile}}</i>: <b>{{doc_count}}</b> Posted On: {{since}}<br/>{{/documentsAbandoned.abGroup}}</td>\
	            	                   <td>{{missingParser}}</td><td>{{missingOCR}}</td><td>{{missingPersist}}</td><td class='notice'><b>{{totalDocs}}</b></td></tr>\
	            	                   ";
	             
	             orgHtml = orgHtml + Mustache.render(missingDocsDiv, missingDocsData);
	             
	             orgHtml = orgHtml + "</li>";
	             
	             if (alternate==0)
	            	 alternate = 1;
	             else
	            	 alternate = 0;
			}); 
		 
		 orgHtml = orgHtml + "</ul>";
		 
		 $("#orgDetails").html(orgHtml);
		 
		 $.each(values.orgs, function(n, data) {
			 
			 var constructedJson = constructChartJson(data);
			 var chartId = 'chart'+n;
			 
	         var svg = d3.select("#"+chartId).selectAll("svg")
	        .data(constructedJson)
	      .enter().append("svg")
	        .attr("class", "bullet")
	        .attr("width", width + margin.left + margin.right)
	        .attr("height", height + margin.top + margin.bottom)
	      .append("g")
	        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
	        .call(chart);

	       var title = svg.append("g")
	           .style("text-anchor", "end")
	           .attr("transform", "translate(-6," + height / 2 + ")");

	       title.append("text")
	           .attr("class", "title")
	           .text(function(d) { return d.title; });

	       title.append("text")
	           .attr("class", "subtitle")
	           .attr("dy", "1em")
	           .text(function(d) { return d.subtitle; }); 
		 });
	  }); 
}
