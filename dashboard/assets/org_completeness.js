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