	DATA = { 
  "subject": { 
      "uri": str(patientID), 
      "type": "patient" 
  }, 
  "fact": { 
      "code": { 
          "code": "36201", 
          "codeSystem": "2.16.840.1.113883.6.103", 
          "codeSystemVersion": "9", 
          "displayName": "36201" 
      }, 
      "time": { 
          "startTime": "2014-01-02T00:00:00-0800", 
          "endTime": "2014-12-30T00:00:00-0800" 
      } 
  }, 
  "source": { 
      "uri": str(documentID), 
      "type": "document" 
  }, 
  "evidence": { 
      "inferred": False, 
      "source": { 
          "uri": "casper", 
          "type": "jromero@apexcodemine.com" 
      }, 
      "attributes": { 
          "pageNumber": str(page), 
          "totalPages": "4" 
      } 
  }, 
  "attributes": {
      "sourceType": "NARRATIVE", 
      "SOURCE_TYPE": "NARRATIVE", 
      "totalPages": "4", 
      "$orgId": "488",
      "bucketName": "maxentModel.v0.0.5a.ex6d_big_idf_LDADateExtract20150820_MT20151105" 
  } 
}


old bucket names:
#old bucket-names for V5s is maxentModel.v0.0.5a.ex6d_big_idf_BRDREC20141028_RETRAIN_2014_10
#old bucket-name for dictionary is dictionary.v0.1.ex6d_big_idf_LDADateExtract20150820_MT20151105


new bucket names:
#new bucket-names for V5s is maxentModel.v0.0.5a.ex6d_big_idf_LDADateExtract20150820_MT20151105
#new bucket-name for dictionary is dictionary.v0.1.ex6d_big_idf_LDADateExtract20150820_MT20151105

