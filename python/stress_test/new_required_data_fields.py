# Accept Opportunity (original, old from Alex B time)   
    
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "accept", \
    		"comment": "Comment by the stressTest", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"flag_for_review": "true", \
    		"icd9[code_system_name]": opportunity.get("suggested_codes")[0].get("code_system_name"), \
    		"icd9[code]": opportunity.get("suggested_codes")[0].get("code"), \
    		"icd9[display_name]": opportunity.get("suggested_codes")[0].get("display_name")+" stressTest", \
    		"icd9[code_system]": opportunity.get("suggested_codes")[0].get("code_system"), \
    		"icd9[code_system_version]": opportunity.get("suggested_codes")[0].get("code_system_version"), \
    		"provider[name]": "The stressTest M.D.", \
    		"provider[id]": "1992754832", \
    		"provider[type]": "Hospital Outpatient Setting", \
    		"payment_year": str(opportunity.get("payment_year")), \
    		"orig_date_of_service": scorable.get("date_of_service"), \
    		"page": "2015", \
    		"opportunity_hash": opportunity.get("hash"), \
    		"rule_hash": opportunity.get("rule_hash"), \
    		"get_id": str(opportunity.get("get_id")), \
    		"patient_uuid": opportunity.get("patient_uuid"), \
    		"patient_org_id": str(scorable.get("patient_org_id")), \
    		"hcc[code]": str(opportunity.get("hcc")), \
    		"hcc[model_run]": opportunity.get("model_run"), \
    		"hcc[model_year]": str(opportunity.get("model_year")), \
    		"hcc[description]": opportunity.get("hcc_description")+" grinder", \
    		"hcc[label_set_version]": opportunity.get("label_set_version"), \
    		"hcc[mapping_version]": str(opportunity.get("model_year")) + " " + opportunity.get("model_run"), \
    		"hcc[code_system]": str(opportunity.get("model_year")) + "PYFinal", \
    		"finding_id": str(finding_id), \
    		"document_uuid": scorable.get("document_uuid"), \
    		"list_position": str(doc_no_current), \
    		"list_length": str(doc_no_max), \
    		"document_date": scorable.get("date_of_service"), \
    		"predicted_code[code_system_name]": "The stressTest", \
    		"predicted_code[code]": "The stressTest", \
    		"predicted_code[display_name]": "The stressTest", \
    		"predicted_code[code_system]": "The stressTest", \
    		"predicted_code[code_system_version]": "The stressTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
    		
    		
#===========================================================================================================================================================    		
    
    opportunity = { \
    		"model_year": "2013", "hash": "93C13D261670AC5E", \
    		"scorables": \
    		[ \
    		{ \
    		"mimeType": "application/pdf", "document_title": "Clinical Data Notes - 6-17-2014-83713408.pdf", "code": \
    		{ \
    		"code_system_name": "N/A", "code": "V12_96", "display_name": "stroke", "code_system": "APXCAT", "code_system_version": "2.0" \
    		},  \
    		"end": 1402963200000, "source_type": "document", "conditionSet": "Ischemic or Unspecified Stroke", "patient_org_id": "407", \
    		"patient_id": "dfb6d1da-4775-4a6b-9827-e0c66722d49b", "start": 1402963200000, "document_uuid": "83938d30-3872-475e-ad94-8402b7ffba1f", \
    		"elements": \
    		[ \
    		{ \
    		"event.sourceType": "NARRATIVE", "evidence.appliedDateExtraction": "false", "event.totalPages": "1.0000", \
    		"evidence.hasMention": "YES", "evidence.junkiness": "0.8247", "index": "1.0000", "event.bucketName": "dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10", \
    		"title": "Clinical Data Notes - 6-17-2014-83713408.pdf", "snippet": "stroke", "evidence.extractionType": "ocrText", "event.editType": "ACTIVE", \
    		"evidence.snippet": "stroke", "evidence.predictionConfidence": "1.0000", "evidence.title": "Clinical Data Notes - 6-17-2014-83713408.pdf", \
    		"condition": "Ischemic or Unspecified Stroke", "event.$batchId": "407_eventSubmission_031215015433", "evidence.f2fConfidence": "0.9903", \
    		"evidence.mentions": "stroke", "evidence.patternsFile": "negation_triggers_20140211.txt", "event.bucketType": "dictionary.v0.1", \
    		"fact": "APXCAT-V12_96", "evidence.face2face": "true" \
    		}, \
    		{ \
    		"event.sourceType": "NARRATIVE", "evidence.appliedDateExtraction": "false", \
    		"event.totalPages": "1.0000", "evidence.hasMention": "YES", "evidence.junkiness": "0.8247", "index": "1.0000", \
    		"event.bucketName": "dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10", "title": "Clinical Data Notes - 6-17-2014-83713408.pdf", \
    		"snippet": "stroke", "evidence.extractionType": "ocrText", "event.editType": "ACTIVE", "evidence.snippet": "stroke", \
    		"evidence.predictionConfidence": "1.0000", "evidence.title": "Clinical Data Notes - 6-17-2014-83713408.pdf", "condition": "Ischemic or Unspecified Stroke", \
    		"event.$batchId": "407_eventSubmission_031215004944", "evidence.f2fConfidence": "0.9903", "evidence.mentions": "stroke", \
    		"evidence.patternsFile": "negation_triggers_20140211.txt", "event.bucketType": "dictionary.v0.1", "fact": "APXCAT-V12_96", \
    		"evidence.face2face": "true"}], "source_id": "83938d30-3872-475e-ad94-8402b7ffba1f", "date_of_service": "06/17/2014", "id": 8224863, "page": "1" \
    		} \
    		], \
    		"hcc_description": "Ischemic or Unspecified Stroke", \
    		"payment_year": "2015", \
    		"patient_id": "dfb6d1da-4775-4a6b-9827-e0c66722d49b", \
    		"project": "CP_c0810d74-bae7-466e-a200-51175a38ddd9", \
    		"hcc": "96", \
    		"get_id": "5c62ec89-f717-45d2-ab34-3ff11a4203ec", \
    		"label_set_version": "V12", \
    		"suggested_codes": \
    		[ \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", \
    		"code": "433.01", "display_name": "Occlusion and stenosis of basilar artery with cerebral infarction", \
    		"code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "433.11", "display_name": "Occlusion and stenosis of carotid artery with cerebral infarction", \
    		"code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "433.21", \
    		"display_name": "Occlusion and stenosis of vertebral artery with cerebral infarction", "code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", \
    		"code": "433.31", \
    		"display_name": "Occlusion and stenosis of multiple and bilateral precerebral arteries with cerebral infarction", \
    		"code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "433.81", \
    		"display_name": "Occlusion and stenosis of other specified precerebral artery with cerebral infarction", "code_system": "2.16.840.1.113883.6.103", \
    		"code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "433.91", \
    		"display_name": "Occlusion and stenosis of unspecified precerebral artery with cerebral infarction", "code_system": "2.16.840.1.113883.6.103", \
    		"code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "434.01", "display_name": "Cerebral thrombosis with cerebral infarction", \
    		"code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "434.11", \
    		"display_name": "Cerebral embolism with cerebral infarction", "code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "434.91", "display_name": "Cerebral artery occlusion unspecified with cerebral infarction", \
    		"code_system": "2.16.840.1.113883.6.103", "code_system_version": "0.1" \
    		}, \
    		{ \
    		"code_system_name": "2.16.840.1.113883.6.103", "code": "436", "display_name": null, \
    		"code_system": "2.16.840.1.113883.6.103", "code_system_version": "9" \
    		} \
    		], \
    		"rule_hash": "33735625423A8A6D", \
    		"patient": \
    		{ \
    		"first_name": "DONNA", \
    		"last_name": "SCHOPPER", \
    		"middle_name": "", \
    		"dob": "11/27/1939", \
    		"gender": "FEMALE", \
    		"org_id": 407 \
    		}, \
    		"patient_uuid": "dfb6d1da-4775-4a6b-9827-e0c66722d49b", \
    		"model_run": "Final" \
    		}
    		
 #===========================================================================================================================================================    		

    scorable = { \
    		"mimeType": "application/pdf", "document_title": "Clinical Data Notes - 6-17-2014-83713408.pdf", "code": \
    		{ \
    		"code_system_name": "N/A", "code": "V12_96", "display_name": "stroke", "code_system": "APXCAT", "code_system_version": "2.0" \
    		}, \
    		"end": 1402963200000, "source_type": "document", "conditionSet": "Ischemic or Unspecified Stroke", "patient_org_id": "407", \
    		"patient_id": "dfb6d1da-4775-4a6b-9827-e0c66722d49b", "start": 1402963200000, "document_uuid": "83938d30-3872-475e-ad94-8402b7ffba1f", \
    		"elements": \
    		[{ \
    		"event.sourceType": "NARRATIVE", "evidence.appliedDateExtraction": "false", "event.totalPages": "1.0000", \
    		"evidence.hasMention": "YES", "evidence.junkiness": "0.8247", "index": "1.0000", \
    		"event.bucketName": "dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10", \
    		"title": "Clinical Data Notes - 6-17-2014-83713408.pdf", \
    		"snippet": "stroke", "evidence.extractionType": "ocrText", \
    		"event.editType": "ACTIVE", "evidence.snippet": "stroke", \
    		"evidence.predictionConfidence": "1.0000", "evidence.title": "Clinical Data Notes - 6-17-2014-83713408.pdf", \
    		"condition": "Ischemic or Unspecified Stroke", "event.$batchId": "407_eventSubmission_031215015433", \
    		"evidence.f2fConfidence": "0.9903", "evidence.mentions": "stroke", \
    		"evidence.patternsFile": "negation_triggers_20140211.txt", "event.bucketType": "dictionary.v0.1", "fact": "APXCAT-V12_96", \
    		"evidence.face2face": "true"}, \
    		{ \
    		"event.sourceType": "NARRATIVE", "evidence.appliedDateExtraction": "false", "event.totalPages": "1.0000", \
    		"evidence.hasMention": "YES", "evidence.junkiness": "0.8247", "index": "1.0000", "event.bucketName": "dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10", \
    		"title": "Clinical Data Notes - 6-17-2014-83713408.pdf", "snippet": "stroke", "evidence.extractionType": "ocrText", \
    		"event.editType": "ACTIVE", "evidence.snippet": "stroke", "evidence.predictionConfidence": "1.0000", \
    		"evidence.title": "Clinical Data Notes - 6-17-2014-83713408.pdf", "condition": "Ischemic or Unspecified Stroke", \
    		"event.$batchId": "407_eventSubmission_031215004944", "evidence.f2fConfidence": "0.9903", "evidence.mentions": "stroke", \
    		"evidence.patternsFile": "negation_triggers_20140211.txt", "event.bucketType": "dictionary.v0.1", "fact": "APXCAT-V12_96", \
    		"evidence.face2face": "true" \
    		}], \
    		"source_id": "83938d30-3872-475e-ad94-8402b7ffba1f", \
    		"date_of_service": "06/17/2014", \
    		"id": 8224863, \
    		"page": "1" \
    		}

  #============================================================== NEW ACCEPT ==========================================================================================       
    		
 
    DATA = 	{ \   		
			"opportunity": \
			{ \
			"model_year": opportunity.get("model_year"), \
			"hash": opportunity.get("hash"), \
			"scorables": \
			[ \
			{ \
			"mimeType": scorable.get("mimeType"), \
			"document_title": scorable.get("document_title"), \
			"code": \
			{ \
			"code_system_name": scorable.get("code_system_name"), \
			"code": scorable.get("code"), \
			"display_name": scorable.get("display_name"), \
			"code_system": scorable.get("code_system"), \
			"code_system_version": scorable.get("code_system_version") \
			}, \
			"end": scorable.get("end"), \
			"start": scorable.get("start"), \
			"conditionSet": scorable.get("conditionSet"), \
			"patient_org_id": scorable.get("patient_org_id"), \
			"patient_id": scorable.get("patient_id"), \
			"source_type": scorable.get("source_type"), \
			"document_uuid": scorable.get("document_uuid"), \
			"elements": scorable.get("elements"), \
			"source_id": scorable.get("source_id"), \
			"date_of_service": scorable.get("date_of_service"), \
			"id": scorable.get("id"), \
			"page": scorable.get("page"), \
			"list_position": str(doc_no_current) \
			} \
			], \
			"hcc_description": opportunity.get("hcc_description"), \
			"payment_year": opportunity.get("payment_year"), \
			"patient_id": opportunity.get("patient_id"), \
			"project": opportunity.get("project"), \
			"hcc": opportunity.get("hcc"), \
			"get_id": opportunity.get("get_id"), \
			"label_set_version": opportunity.get("label_set_version"), \
			"suggested_codes": opportunity.get("suggested_codes"), \
			"rule_hash": opportunity.get("rule_hash"), \
			"patient": opportunity.get("patient"), \
			"patient_uuid": opportunity.get("patient_uuid"), \
			"model_run": opportunity.get("model_run") \
			}, \
			"annotations": \
			[ \
			{ \
			"flaggedForReview": True, \
			"changed": True, \
			"result": "accept", \
			"encounterType": "Hospital Inpatient Setting: Other Diagnosis", \
			"icd": \
			{ \
			"code_system_name": opportunity.get("suggested_codes")[0].get("code_system_name"), \
			"code": opportunity.get("suggested_codes")[0].get("code"), \
			"display_name": opportunity.get("suggested_codes")[0].get("display_name"), \
			"code_system": opportunity.get("suggested_codes")[0].get("code_system"), \
			"code_system_version": opportunity.get("suggested_codes")[0].get("code_system_version") \
			}, \
			"provider": "Dr. Grinder", \
			"dateOfService": scorable.get("date_of_service"), \
			"page": scorable.get("page"), \
			"comment":"Grinder Flag for Review" \
			}]}	
			
			
#============================================================== OLD REJECT ==========================================================================================	 			
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "reject", \
    		"reject_reason": "Additional documentation needed to Accept the document for this HCC", \
    		"comment": "Comment by The stressTest", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"flag_for_review": "true", \
    		"payment_year": str(opportunity.get("payment_year")), \
    		"orig_date_of_service": scorable.get("date_of_service"), \
    		"opportunity_hash": opportunity.get("hash"), \
    		"rule_hash": opportunity.get("rule_hash"), \
    		"get_id": str(opportunity.get("get_id")), \
    		"patient_uuid": opportunity.get("patient_uuid"), \
    		"patient_org_id": str(scorable.get("patient_org_id")), \
    		"hcc[code]": str(opportunity.get("hcc")), \
    		"hcc[model_run]": opportunity.get("model_run"), \
    		"hcc[model_year]": str(opportunity.get("model_year")), \
    		"hcc[description]": opportunity.get("hcc_description"), \
    		"hcc[label_set_version]": opportunity.get("label_set_version"), \
    		"hcc[mapping_version]": str(opportunity.get("model_year")) + " " + opportunity.get("model_run"), \
    		"hcc[code_system]": str(opportunity.get("model_year")) + "PYFinal", \
    		"finding_id": str(finding_id), \
    		"document_uuid":  scorable.get("document_uuid"), \
    		"list_position": str(doc_no_current), \
    		"list_length": str(doc_no_max), \
    		"document_date": scorable.get("date_of_service"), \
    		"snippets": str(scorable.get("snippets")), \
    		"predicted_code[code_system_name]": "The stressTest", \
    		"predicted_code[code]": "The stressTest", \
    		"predicted_code[display_name]": "The stressTest", \
    		"predicted_code[code_system]": "The stressTest", \
    		"predicted_code[code_system_version]": "The stressTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}	
    		
#========================================================= ACTUAL REJECT FROM BROWSER ===================================================================================

{"opportunity":{"model_year":"2013","hash":"5F4E796F1D0EABB1","scorables":[{"mimeType":"application/pdf","document_title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf","code":{"code_system_name":"N/A","code":"V12_7","display_name":"metastatic disease","code_system":"APXCAT","code_system_version":"2.0"},"end":1394582400000,"start":1394582400000,"conditionSet":"Metastatic Cancer and Acute Leukemia","patient_org_id":"407","patient_id":"069c8315-630d-467f-bff0-023692eac02a","source_type":"document","document_uuid":"7400d7d4-c62d-4c41-aae8-07f2c62b418c","elements":[{"event.sourceType":"NARRATIVE","evidence.appliedDateExtraction":"false","event.bucketType":"dictionary.v0.1","evidence.hasMention":"YES","evidence.junkiness":"0.8735","index":"4.0000","event.bucketName":"dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10","title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf","snippet":"metastatic disease","evidence.extractionType":"ocrText","event.editType":"ACTIVE","evidence.snippet":"metastatic disease","evidence.predictionConfidence":"1.0000","evidence.title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf","condition":"Metastatic Cancer and Acute Leukemia","event.$batchId":"407_eventSubmission_031215015448","evidence.f2fConfidence":"0.9831","evidence.mentions":"metastatic disease","evidence.patternsFile":"negation_triggers_20140211.txt","event.totalPages":"5.0000","fact":"APXCAT-V12_7","evidence.face2face":"true"},{"event.sourceType":"NARRATIVE","evidence.appliedDateExtraction":"false","event.bucketType":"dictionary.v0.1","evidence.hasMention":"YES","evidence.junkiness":"0.8735","index":"4.0000","event.bucketName":"dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10","title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf","snippet":"metastatic disease","evidence.extractionType":"ocrText","event.editType":"ACTIVE","evidence.snippet":"metastatic disease","evidence.predictionConfidence":"1.0000","evidence.title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf","condition":"Metastatic Cancer and Acute Leukemia","event.$batchId":"407_eventSubmission_031115224051","evidence.f2fConfidence":"0.9831","evidence.mentions":"metastatic disease","evidence.patternsFile":"negation_triggers_20140211.txt","event.totalPages":"5.0000","fact":"APXCAT-V12_7","evidence.face2face":"true"}],"source_id":"7400d7d4-c62d-4c41-aae8-07f2c62b418c","date_of_service":"03/12/2014","id":8319631,"page":"4","list_position":0}],"hcc_description":"Metastatic Cancer and Acute Leukemia","payment_year":"2015","patient_id":"069c8315-630d-467f-bff0-023692eac02a","project":"CP_c0810d74-bae7-466e-a200-51175a38ddd9","hcc":"7","get_id":"62414a4b-6b3c-495e-a45c-32c28a92dc15","label_set_version":"V12","suggested_codes":[{"code_system_name":"2.16.840.1.113883.6.103","code":"196.0","display_name":"Secondary and unspecified malignant neoplasm of lymph nodes of head face and neck","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.1","display_name":"Secondary and unspecified malignant neoplasm of intrathoracic lymph nodes","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.2","display_name":"Secondary and unspecified malignant neoplasm of intra-abdominal lymph nodes","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.3","display_name":"Secondary and unspecified malignant neoplasm of lymph nodes of axilla and upper limb","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.5","display_name":"Secondary and unspecified malignant neoplasm of lymph nodes of inguinal region and lower limb","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.6","display_name":"Secondary and unspecified malignant neoplasm of intrapelvic lymph nodes","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.8","display_name":"Secondary and unspecified malignant neoplasm of lymph nodes of multiple sites","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"196.9","display_name":"Secondary and unspecified malignant neoplasm of lymph nodes site unspecified","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.0","display_name":"Secondary malignant neoplasm of lung","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.1","display_name":"Secondary malignant neoplasm of mediastinum","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.2","display_name":"Secondary malignant neoplasm of pleura","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.3","display_name":"Secondary malignant neoplasm of other respiratory organs","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.4","display_name":"Secondary malignant neoplasm of small intestine including duodenum","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.5","display_name":"Secondary malignant neoplasm of large intestine and rectum","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.6","display_name":"Secondary malignant neoplasm of retroperitoneum and peritoneum","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.7","display_name":"Malignant neoplasm of liver secondary","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"197.8","display_name":"Secondary malignant neoplasm of other digestive organs and spleen","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.0","display_name":"Secondary malignant neoplasm of kidney","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.1","display_name":"Secondary malignant neoplasm of other urinary organs","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.2","display_name":"Secondary malignant neoplasm of skin","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.3","display_name":"Secondary malignant neoplasm of brain and spinal cord","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.4","display_name":"Secondary malignant neoplasm of other parts of nervous system","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.5","display_name":"Secondary malignant neoplasm of bone and bone marrow","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.6","display_name":"Secondary malignant neoplasm of ovary","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.7","display_name":"Secondary malignant neoplasm of adrenal gland","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.81","display_name":"Secondary malignant neoplasm of breast","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.82","display_name":"Secondary malignant neoplasm of genital organs","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"198.89","display_name":"Secondary malignant neoplasm of other specified sites","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"199.0","display_name":"Disseminated malignant neoplasm","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"204.00","display_name":"Acute lymphoid leukemia without mention of having achieved remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"204.01","display_name":"Acute lymphoid leukemia in remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"204.02","display_name":"Acute lymphoid leukemia in relapse","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"205.00","display_name":"Acute myeloid leukemia without mention of having achieved remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"205.01","display_name":"Acute myeloid leukemia in remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"205.02","display_name":"Acute myeloid leukemia in relapse","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"206.00","display_name":"Acute monocytic leukemia without mention of having achieved remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"206.01","display_name":"Acute monocytic leukemia in remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"206.02","display_name":"Acute monocytic leukemia in relapse","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"207.00","display_name":"Acute erythremia and erythroleukemia without mention of having achieved remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"207.01","display_name":"Acute erythremia and erythroleukemia in remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"207.02","display_name":"Acute erythremia and erythroleukemia in relapse","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"208.00","display_name":"Acute leukemia of unspecified cell type without mention of having achieved remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"208.01","display_name":"Acute leukemia of unspecified cell type in remission","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"208.02","display_name":"Acute leukemia of unspecified cell type in relapse","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.70","display_name":"Secondary neuroendocrine tumor unspecified site","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.71","display_name":"Secondary neuroendocrine tumor of distant lymph nodes","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.72","display_name":"Secondary neuroendocrine tumor of liver","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.73","display_name":"Secondary neuroendocrine tumor of bone","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.74","display_name":"Secondary neuroendocrine tumor of peritoneum","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.75","display_name":"Secondary merkel cell carcinoma","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"},{"code_system_name":"2.16.840.1.113883.6.103","code":"209.79","display_name":"Secondary neuroendocrine tumor of other sites","code_system":"2.16.840.1.113883.6.103","code_system_version":"0.1"}],"rule_hash":"33735625423A8A6D","patient":{"first_name":"LAURA","last_name":"CHRISTIE","middle_name":null,"dob":"05/06/1948","gender":"FEMALE","org_id":407},"patient_uuid":"069c8315-630d-467f-bff0-023692eac02a","model_run":"Final"},"annotations":[{"flaggedForReview":true,"changed":true,"result":"reject","rejectReason":"Invalid Date of Service","comment":"Grinder Flag for Review","page":"4"}]}    		
    		
#============================================================== NEW REJECT ==========================================================================================    				


DATA = 	{ \
			"opportunity": \
			{ \
			"model_year": opportunity.get("model_year"), \
			"hash": opportunity.get("hash"), \
			"scorables": \
			[ \
			{ \
			"mimeType": scorable.get("mimeType"), \
			"document_title": scorable.get("document_title"), \
			"code": \
			{ \
			"code_system_name": scorable.get("code_system_name"), \
			"code":"V12_7", \
			"display_name": scorable.get("display_name"), \
			"code_system": scorable.get("code_system"), \
			"code_system_version": scorable.get("code_system_version") \
			}, \
			"end":1394582400000, \
			"start":1394582400000, \
			"conditionSet":"Metastatic Cancer and Acute Leukemia", \
			"patient_org_id":"407", \
			"patient_id":"069c8315-630d-467f-bff0-023692eac02a", \
			"source_type":"document", \
			"document_uuid":"7400d7d4-c62d-4c41-aae8-07f2c62b418c", \
			"elements": \
			[ \
			{ \
			"event.sourceType":"NARRATIVE", \
			"evidence.appliedDateExtraction":"false", \
			"event.bucketType":"dictionary.v0.1", \
			"evidence.hasMention":"YES", \
			"evidence.junkiness":"0.8735", \
			"index":"4.0000", \
			"event.bucketName":"dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10", \
			"title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf", \
			"snippet":"metastatic disease", \
			"evidence.extractionType":"ocrText", \
			"event.editType":"ACTIVE", \
			"evidence.snippet":"metastatic disease", \
			"evidence.predictionConfidence":"1.0000", \
			"evidence.title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf", \
			"condition":"Metastatic Cancer and Acute Leukemia", \
			"event.$batchId":"407_eventSubmission_031215015448", \
			"evidence.f2fConfidence":"0.9831", \
			"evidence.mentions":"metastatic disease", \
			"evidence.patternsFile":"negation_triggers_20140211.txt", \
			"event.totalPages":"5.0000", \
			"fact":"APXCAT-V12_7", \
			"evidence.face2face":"true" \
			},{ \
			"event.sourceType":"NARRATIVE", \
			"evidence.appliedDateExtraction":"false", \
			"event.bucketType":"dictionary.v0.1", \
			"evidence.hasMention":"YES", \
			"evidence.junkiness":"0.8735", \
			"index":"4.0000", \
			"event.bucketName":"dictionary.v0.1.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10", \
			"title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf", \
			"snippet":"metastatic disease","evidence.extractionType":"ocrText","event.editType":"ACTIVE","evidence.snippet":"metastatic disease","evidence.predictionConfidence":"1.0000", \
			"evidence.title":"History and Physical - CHRISTIE LAURA - MR#0896051 -  - Doc#82071891-82071891.pdf", \
			"condition":"Metastatic Cancer and Acute Leukemia","event.$batchId":"407_eventSubmission_031115224051","evidence.f2fConfidence":"0.9831","evidence.mentions":"metastatic disease", \
			"evidence.patternsFile":"negation_triggers_20140211.txt","event.totalPages":"5.0000","fact":"APXCAT-V12_7","evidence.face2face":"true" \
			}], \
			"source_id":"7400d7d4-c62d-4c41-aae8-07f2c62b418c", \
			"date_of_service":"03/12/2014", \
			"id":8319631, \
			"page":"4", \
			"list_position":0 \
			}], \
			"hcc_description":"Metastatic Cancer and Acute Leukemia", \
			"payment_year":"2015", \
			"patient_id":"069c8315-630d-467f-bff0-023692eac02a", \
			"project":"CP_c0810d74-bae7-466e-a200-51175a38ddd9", \
			"hcc":"7", \
			"get_id":"62414a4b-6b3c-495e-a45c-32c28a92dc15", \
			"label_set_version":"V12", \
			"suggested_codes": \
			[ \
			{"code_system_name":"2.16.840.1.113883.6.103","code":"196.0","display_name":"Secondary and unspecified malignant neoplasm of lymph nodes of head face and neck","code_system":"2.16.840.1.113883.6.103", \
			"code_system_version":"0.1" \
			} \
			], \
			"rule_hash":"33735625423A8A6D", \
			"patient":{"first_name":"LAURA","last_name":"CHRISTIE","middle_name":None,"dob":"05/06/1948","gender":"FEMALE","org_id":407}, \
			"patient_uuid":"069c8315-630d-467f-bff0-023692eac02a", \
			"model_run":"Final" \
			}, \
			"annotations": \
			[{ \
			"flaggedForReview":True, \
			"changed":True, \
			"result":"reject", \
			"rejectReason":"Invalid Date of Service", \
			"comment":"Grinder Flag for Review", \
			"page":"4" \
			}]}    		
    		

			
#============================================================== BLANK NEW REJECT ==========================================================================================

{
    "opportunity": {
        "model_year": "string",
        "hash": "string",
        "scorables": [
            {
                "mimeType": "string",
                "document_title": "string",
                "code": {
                    "code_system_name": "string",
                    "code": "string",
                    "display_name": "string",
                    "code_system": "string",
                    "code_system_version": "string"
                },
                "end": "string",
                "start": "string",
                "conditionSet": "string",
                "patient_org_id": "string",
                "patient_id": "string",
                "source_type": "string",
                "document_uuid": "string",
                "elements": "string",
                "source_id": "string",
                "date_of_service": "string",
                "id": "string",
                "page": "string",
                "list_position": "string"
            }
        ],
        "hcc_description": "string",
        "payment_year": "string",
        "patient_id": "string",
        "project": "string",
        "hcc": "string",
        "get_id": "string",
        "label_set_version": "string",
        "suggested_codes": "string",
        "rule_hash": "string",
        "patient": "string",
        "patient_uuid": "string",
        "model_run": "thing"
    },
    "annotations": [
        {
            "flaggedForReview": "string",
            "changed": "string",
            "result": "string",
            "encounterType": "string",
            "icd": {
                "code_system_name": "sys name",
                "code": "code",
                "display_name": "string",
                "code_system": "string",
                "code_system_version": "string"
            },
            "provider": "string",
            "dateOfService": "string",
            "page": "string",
            "comment": "Grinder Flag for Review"
        }
    ]
}

			
#============================================================== NEW REJECT ==========================================================================================		
  
    DATA = { \
			"opportunity": \
			{ \
			"model_year": opportunity.get("model_year"), \
			"hash": opportunity.get("hash"), \
			"scorables": \
			[{ \
			"mimeType": scorable.get("mimeType"), \
			"document_title": scorable.get("document_title"), \
			"code": \
			{ \
			"code_system_name": scorable.get("code_system_name"), \
			"code": scorable.get("code"), \
			"display_name": scorable.get("display_name"), \
			"code_system": scorable.get("code_system"), \
			"code_system_version": scorable.get("code_system_version") \
			}, \
			"end": scorable.get("end"), \
			"start": scorable.get("start"), \
			"conditionSet": scorable.get("conditionSet"), \
			"patient_org_id": scorable.get("patient_org_id"), \
			"patient_id": scorable.get("patient_id"), \
			"source_type": scorable.get("source_type"), \
			"document_uuid": scorable.get("document_uuid"), \
			"elements": scorable.get("elements"), \
			"source_id": scorable.get("source_id"), \
			"date_of_service": scorable.get("date_of_service"), \
			"id": scorable.get("id"), \
			"page": scorable.get("page"), \
			"list_position": str(doc_no_current) \
			}], \
			"hcc_description": opportunity.get("hcc_description"), \
			"payment_year": opportunity.get("payment_year"), \
			"patient_id": opportunity.get("patient_id"), \
			"project": opportunity.get("project"), \
			"hcc": opportunity.get("hcc"), \
			"get_id": opportunity.get("get_id"), \
			"label_set_version": opportunity.get("label_set_version"), \
			"suggested_codes": opportunity.get("suggested_codes"), \
			"rule_hash": opportunity.get("rule_hash"), \
			"patient": opportunity.get("patient"), \
			"patient_uuid": opportunity.get("patient_uuid"), \
			"model_run": opportunity.get("model_run") \
			}, \
			"annotations": \
			[{ \
			"flaggedForReview": True, \
			"changed": True, \
			"result": "reject", \
			"rejectReason": "Invalid Date of Service", \
			"comment": "Grinder Flag for Review Comment", \
			"page": scorable.get("page") \
			}]}		

#============================================================== OLD SKIP ==========================================================================================	
    DATA = 	{ \
    		"user_id": USERNAME, \
    		"timestamp": str(1000 * int(time.time())), \
    		"result": "skipped", \
    		"date_of_service": scorable.get("date_of_service"), \
    		"payment_year": str(opportunity.get("payment_year")), \
    		"orig_date_of_service": scorable.get("date_of_service"), \
    		"opportunity_hash": opportunity.get("hash"), \
    		"rule_hash": opportunity.get("rule_hash"), \
    		"get_id": str(opportunity.get("get_id")), \
    		"patient_uuid": opportunity.get("patient_uuid"), \
    		"hcc[code]": str(opportunity.get("hcc")), \
    		"hcc[model_run]": opportunity.get("model_run"), \
    		"hcc[model_year]": str(opportunity.get("model_year")), \
    		"hcc[description]": opportunity.get("hcc_description") + " (stressTest)", \
    		"hcc[label_set_version]": opportunity.get("label_set_version"), \
    		"hcc[mapping_version]": str(opportunity.get("model_year")) + " " + opportunity.get("model_run"), \
    		"hcc[code_system]": str(opportunity.get("model_year")) + "PYFinal", \
    		"finding_id": str(finding_id), \
    		"document_uuid": scorable.get("document_uuid"), \
    		"patient_org_id": str(scorable.get("patient_org_id")), \
    		"list_position": str(doc_no_current), \
    		"list_length": str(doc_no_max), \
    		"document_date": scorable.get("date_of_service"), \
    		"snippets": str(scorable.get("snippets")), \
    		"predicted_code[code_system_name]": "The stressTest", \
    		"predicted_code[code]": "The stressTest", \
    		"predicted_code[display_name]": "The stressTest", \
    		"predicted_code[code_system]": "The stressTest", \
    		"predicted_code[code_system_version]": "The stressTest", \
    		"page_load_time": str(1000 * int(time.time())), \
    		"document_load_time": str(1000 * int(time.time())) \
    		}
			
			
#============================================================== NEW SKIP ==========================================================================================	


    DATA = { \
			"opportunity": \
			{ \
			"model_year": opportunity.get("model_year"), \
			"hash": opportunity.get("hash"), \
			"scorables": \
			[ \
			{ \
			"mimeType": scorable.get("mimeType"), \
			"document_title": scorable.get("document_title"), \
			"code": \
			{ \
			"code_system_name": scorable.get("code_system_name"), \
			"code": scorable.get("code"), \
			"display_name": scorable.get("display_name"), \
			"code_system": scorable.get("code_system"), \
			"code_system_version": scorable.get("code_system_version") \
			}, \
			"end": scorable.get("end"), \
			"start": scorable.get("start"), \
			"conditionSet": scorable.get("conditionSet"), \
			"patient_org_id": scorable.get("patient_org_id"), \
			"patient_id": scorable.get("patient_id"), \
			"source_type": scorable.get("source_type"), \
			"document_uuid": scorable.get("document_uuid"), \
			"elements": scorable.get("elements"), \
			"source_id": scorable.get("source_id"), \
			"date_of_service": scorable.get("date_of_service"), \
			"id": scorable.get("id"), \
			"page": scorable.get("page") \
			}], \
			"hcc_description": opportunity.get("hcc_description"), \
			"payment_year": opportunity.get("payment_year"), \
			"patient_id": opportunity.get("patient_id"), \
			"project": opportunity.get("project"), \
			"hcc": opportunity.get("hcc"), \
			"get_id": opportunity.get("get_id"), \
			"label_set_version": opportunity.get("label_set_version"), \
			"suggested_codes": opportunity.get("suggested_codes"), \
			"rule_hash": opportunity.get("rule_hash"), \
			"patient": opportunity.get("patient"), \
			"patient_uuid": opportunity.get("patient_uuid"), \
			"model_run": opportunity.get("model_run") \
			}, \
			"annotations": \
			[{ \
			"changed": True, \
			"result": "skipped", \
			"flaggedForReview": False \
			}]}

		