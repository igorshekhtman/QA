#=========================================================================================
#====================================== validate.py ======================================
#=========================================================================================
#
# PROGRAM:         validate.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    05-Nov-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#			This program will read in data from Apixio's hcc-code-mappings.js as well as 
#			well as CMS's icd_9 and icd_10 code mappings.  Will identify differences 
#			beween them and specific missing/extra codes in each.  
#			
#			Will generate json file in output folder.
#
#			Will generate HTML report file.
#
#			Will allow for user to correct or match codes between CMS's and Apixio's
#			code-mappings files.
#
# NOTES / COMMENTS:  python2.7 validate.py
#
#=========================================================================================
#
import json
import csv
from pprint import pprint
import time
import datetime
import csv
import random
import re
import sys, os
import smtplib
from time import gmtime, strftime, localtime
#=========================================================================================
#====================== GLOBAL VARIABLE ASSIGNMENT =======================================
#=========================================================================================
APIXIO_SOURCE_FOLDER = "apixio_source_files/"
CMS_SOURCE_FOLDER = "cms_source_files/"
OUTPUT_DIFF_FOLDER = "output_json/"
OUTPUT_REPORT_FOLDER = "output_html_report/"
OUTPUT_APIXIO_MAPINGS_FOLDER = "output_mapings/"
#=========================================================================================
#====================== FUNCTIONS ========================================================
#=========================================================================================
def loadApixioHccToIcd():

	code_mappings = json.load(open(APIXIO_SOURCE_FOLDER+"hcc-code-mappings.js"))
	apixio_hcc_to_icd = {}

	for code_mapping in code_mappings:
		if (code_mapping["fromCodingSystem"] == "2.16.840.1.113883.6.90"): # if this is ICD-10
			hcc_key = code_mapping["labelSet"] + "-" + code_mapping["hcc"] # key value by labelSet and HCC
			codes = apixio_hcc_to_icd[hcc_key] if hcc_key in apixio_hcc_to_icd else {"icd9s":[],"icd10s":[]}
			codes["icd10s"].append(code_mapping["fromCode"])
			apixio_hcc_to_icd[hcc_key] = codes
	
		if (code_mapping["fromCodingSystem"] == "2.16.840.1.113883.6.103"): # if this is ICD-9
			hcc_key = code_mapping["labelSet"] + "-" + code_mapping["hcc"] # key value by labelSet and HCC
			codes = apixio_hcc_to_icd[hcc_key] if hcc_key in apixio_hcc_to_icd else {"icd9s":[],"icd10s":[]}
			codes["icd9s"].append(code_mapping["fromCode"])
			apixio_hcc_to_icd[hcc_key] = codes

	return (apixio_hcc_to_icd)
#=========================================================================================	
def loadCmsHccToIcd():

	cms_hcc_to_icd = {}
	
	# ICD9 Codes
	with open(CMS_SOURCE_FOLDER+"icd9_mappings.csv", "rb") as csvfile:
		hccreader = csv.reader(csvfile, delimiter=",", quotechar='"')
		for icd9_mapping in hccreader:
			icd9_code = icd9_mapping[0].strip()         # DIAGNOSIS CODE
			desc = icd9_mapping[1].strip()              # SHORT DESCRIPTION
			hcc_category_2013 = icd9_mapping[2].strip() # 2013 CMS-HCC Model Category
			hcc_category_pace = icd9_mapping[3].strip() # CMS-HCC PACE/ESRD Model Category
			hcc_category_2014 = icd9_mapping[4].strip() # 2014 CMS-HCC Model Category
			hcc_category_rx = icd9_mapping[5].strip()   # RxHCC Model Category
			hcc_model_2013 = icd9_mapping[6].strip()    # 2013 CMS-HCC Model for 2014 Payment Year
			hcc_model_pace = icd9_mapping[7].strip()    # CMS-HCC PACE/ESRD Model for 2014 Payment Year
			hcc_model_2014 = icd9_mapping[8].strip()    # 2014 CMS-HCC Model for 2014 Payment Year
			hcc_model_rx = icd9_mapping[9].strip()      # RxHCC Model for 2014 Payment Year
			hcc_keys = []
			if hcc_model_2013 == "Yes":
				hcc_keys.append("V12-" + hcc_category_2013)
			if hcc_model_2014 == "Yes":
				hcc_keys.append("V22-" + hcc_category_2014)
			for key in hcc_keys:
				mapping = cms_hcc_to_icd[key] if key in cms_hcc_to_icd else {"icd9s":set(),"icd10s":set()}
				mapping["icd9s"].add(icd9_code)
				cms_hcc_to_icd[key] = mapping

	# ICD10 Codes
	with open(CMS_SOURCE_FOLDER+"icd10_mappings.csv", "rb") as csvfile:
		hccreader = csv.reader(csvfile, delimiter=",", quotechar='"')
		for icd10_mapping in hccreader:
			icd10_code = icd10_mapping[0].strip()         # Diagnosis Code
			desc = icd10_mapping[1].strip()               # Description
			hcc_category_v21 = icd10_mapping[2].strip()   # CMS-HCC PACE/ESRD Model Category V21
			hcc_category_v22 = icd10_mapping[3].strip()   # CMS-HCC Model Category V22
			hcc_category_v05 = icd10_mapping[4].strip()   # RxHCC Model Category V05 (clinically revised model implemented in 2016)
			hcc_model_v21 = icd10_mapping[5].strip()      # CMS-HCC PACE/ESRD Model for 2016 Payment Year
			hcc_model_v22 = icd10_mapping[6].strip()      # CMS-HCC Model for 2016 Payment Year
			hcc_model_v05 = icd10_mapping[7].strip()      # RxHCC Model for 2016 Payment Year
        	hcc_keys = []
        	if hcc_model_v22 == "Yes":
        		hcc_keys.append("V22-" + hcc_category_v22)
        	for key in hcc_keys:
        		mapping = cms_hcc_to_icd[key] if key in cms_hcc_to_icd else {"icd9s":set(),"icd10s":set()}
        		mapping["icd10s"].add(icd10_code)
        		cms_hcc_to_icd[key] = mapping

	return (cms_hcc_to_icd)	
#=========================================================================================
def findMissingHccs(apixio, cms):

	# list the HCCs that are present in the CMS model but not in Apixio Code Mappings
	print [hcc for hcc in cms_hcc_to_icd if hcc not in apixio_hcc_to_icd]
	
	# list the HCCs that are present in the Apixio model but not in HCC model
	print [hcc for hcc in apixio_hcc_to_icd if hcc not in cms_hcc_to_icd]

	return ()
#=========================================================================================	
def obtainDifference(apixio, cms):
	hcc_diff = {}
	# check if Apixio and CMS agree on the ICD codes used for a particular HCC
	for hcc in cms:
		icd9s_not_in_apixio = [icd for icd in cms[hcc]['icd9s'] if icd not in apixio[hcc]['icd9s']]
		icd10s_not_in_apixio = [icd for icd in cms[hcc]['icd10s'] if icd not in apixio[hcc]['icd10s']]
		icd9s_not_in_cms = [icd for icd in apixio[hcc]['icd9s'] if icd not in cms[hcc]['icd9s']]
		icd10s_not_in_cms = [icd for icd in apixio[hcc]['icd10s'] if icd not in cms[hcc]['icd10s']]
		
		if len(icd9s_not_in_apixio) > 0 or len(icd10s_not_in_apixio) > 0 or len(icd9s_not_in_cms) > 0 or len(icd10s_not_in_cms) > 0:
			hcc_diff[hcc] = {'icd9s_not_in_apixio':icd9s_not_in_apixio, \
				'icd10s_not_in_apixio':icd10s_not_in_apixio, \
				'icd9s_not_in_cms':icd9s_not_in_cms, \
				'icd10s_not_in_cms':icd10s_not_in_cms}
				
	with open(OUTPUT_DIFF_FOLDER+"hoisting_analysis_diff.json","w") as diff:
		pprint(json.dumps(hcc_diff), diff)
		#pprint(hcc_diff)

	return (hcc_diff)	
#=========================================================================================
def resolveDifferences(apixio, cms, differences):
	# add or delete ICD codes from hcc-code-mappings.js depending on the difference file
	# write new, revised file to an output folder
	#OUTPUT_APIXIO_MAPINGS_FOLDER
	#code_mappings = json.load(open(APIXIO_SOURCE_FOLDER+"hcc-code-mappings.js"))

	print ("Total number of differences: %d" % len(differences))
	#jdifferences = json.dumps(differences)
	for diff in differences:
		print diff
		
		
	print ("Total number of differences: %d" % len(differences))
	return()	
		
#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

apixio_hcc_to_icd = loadApixioHccToIcd();

cms_hcc_to_icd = loadCmsHccToIcd();

missing_Hccs = findMissingHccs(apixio_hcc_to_icd, cms_hcc_to_icd);

hcc_diff = obtainDifference(apixio_hcc_to_icd, cms_hcc_to_icd);

resolveDifferences(apixio_hcc_to_icd, cms_hcc_to_icd, hcc_diff);


print ("\n=================================================================================")	
print ("=========================== End of Hosting Table Validation =====================")
print ("=================================================================================")
#=========================================================================================