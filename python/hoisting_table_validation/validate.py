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
BKP_APIXIO_SOURCE_FOLDER = "bkp_apixio_source_files/"
BKP_CMS_SOURCE_FOLDER = "bkp_cms_source_files/"
OUTPUT_DIFF_FOLDER = "output_json/"
OUTPUT_REPORT_FOLDER = "output_html_report/"
OUTPUT_APIXIO_MAPINGS_FOLDER = "output_mapings/"
ICD9_CODING_SYSTEM = "2.16.840.1.113883.6.103"
ICD10_CODING_SYSTEM = "2.16.840.1.113883.6.90"
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

	missing = [hcc for hcc in cms if hcc not in apixio]
	extra = [hcc for hcc in apixio if hcc not in cms]

	# list the HCCs that are present in the CMS model but not in Apixio Code Mappings
	print "* List of missing HCCs from Apixio Code Mappings:            %s" % (missing if len(missing) > 0 else "None")
	# list the HCCs that are present in the Apixio model but not in HCC model
	print "* List of extra HCCs in Apixio Code Mappings:                %s" % (extra if len(extra) > 0 else "None")
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
def backupOriginalMappingsFile():
	os.system("cp "+ APIXIO_SOURCE_FOLDER + "* " + BKP_APIXIO_SOURCE_FOLDER)
	os.system("cp "+ CMS_SOURCE_FOLDER + "* " + BKP_CMS_SOURCE_FOLDER)
	return ()
#=========================================================================================	
def addMissingCodesToApixioMappings(mappings, coding_system, hcc, code, cms):

# description - "Human immunodeficiency virus [HIV] disease"
# fromCode - 042
# hcc - 1
# labelSet - V12
# fromCodingSystemVersion - ""
# fromCodingSystem - "2.16.840.1.113883.6.103"
	

	from_cofing_system_version = ""
	label_set, hcc = hcc.split("-")

	if coding_system == ICD9_CODING_SYSTEM:
		with open(CMS_SOURCE_FOLDER+"icd9_mappings.csv", "rb") as csvfile:
			hccreader = csv.reader(csvfile, delimiter=",", quotechar='"')
			for icd9_mapping in hccreader:
				icd9_code = icd9_mapping[0].strip()         # Diagnosis Code
				desc = icd9_mapping[1].strip()              # Description
				if icd9_code == code:
					description = desc
	elif coding_system == ICD10_CODING_SYSTEM:		
		with open(CMS_SOURCE_FOLDER+"icd10_mappings.csv", "rb") as csvfile:
			hccreader = csv.reader(csvfile, delimiter=",", quotechar='"')
			for icd10_mapping in hccreader:
				icd10_code = icd10_mapping[0].strip()         # Diagnosis Code
				desc = icd10_mapping[1].strip()               # Description
				if icd10_code == code:
					description = desc

	print "***************************************************************************************************************"
	print "* description:                                               %s" % description
	print "* fromCode:                                                  %s" % code
	print "* hcc:                                                       %s" % hcc
	print "* labelSet:                                                  %s" % label_set
	print "* fromCodingSystemVersion:                                   %s" % from_cofing_system_version
	print "* fromCodingSystem:                                          %s" % coding_system
	print "***************************************************************************************************************"
	print "* Appending ... "
	
	
	mapping = { "description" : description, \
				"fromCode" : code, \
				"hcc" : hcc, \
				"labelSet" : label_set, \
				"fromCodingSystemVersion" : from_cofing_system_version, \
				"fromCodingSystem" : coding_system }
	
	
	mappings.append(mapping)			
			
	return (mappings)
#=========================================================================================	
def removeExtraCodesFromApixioMappings(mappings, coding_system, hcc, code):

# description - "Human immunodeficiency virus [HIV] disease"
# fromCode - 042
# hcc - 1
# labelSet - V12
# fromCodingSystemVersion - ""
# fromCodingSystem - "2.16.840.1.113883.6.103"

	for mapping in mappings:
		if (mapping["fromCodingSystem"] == coding_system): # ICD10 or ICD9
			hcc_key = mapping["labelSet"] + "-" + mapping["hcc"] # key value by labelSet and HCC
			if hcc_key == hcc:	
				if code == mapping["fromCode"]:
					#print code
					#print mappings.index(mapping)
					mappings.pop(mappings.index(mapping))
	
	return (mappings)
#=========================================================================================	
def saveMappingsFile(mappings):
	#save apixio into a json file: hcc-code-mappings.js in OUTPUT_APIXIO_MAPINGS_FOLDER
	
	with open(OUTPUT_APIXIO_MAPINGS_FOLDER+"hcc-code-mappings.js", "w") as outfile:
		json.dump(mappings, outfile)
		
	return()				
#=========================================================================================
def resolveDifferences(apixio, cms, differences):
	# add or delete ICD codes from hcc-code-mappings.js depending on the difference file
	# write new, revised file to an output folder

	#print "* Total number of differences:                               %s" % (len(differences) if len(differences) > 0 else "None")
	mappings = json.load(open(APIXIO_SOURCE_FOLDER+"hcc-code-mappings.js"))
	
	for hcc in differences:
		micd9codes = differences[hcc]['icd9s_not_in_apixio']
		if len(micd9codes) > 0:
			for code in micd9codes:
				mappings = addMissingCodesToApixioMappings(mappings, ICD9_CODING_SYSTEM, hcc, code, cms)
		micd10codes = differences[hcc]['icd10s_not_in_apixio']
		if len(micd10codes) > 0:
			for code in micd10codes:
				mappings = addMissingCodesToApixioMappings(mappings, ICD10_CODING_SYSTEM, hcc, code, cms)
		eicd9codes = differences[hcc]['icd9s_not_in_cms']
		if len(eicd9codes) > 0:
			for code in eicd9codes:
				mappings = removeExtraCodesFromApixioMappings(mappings, ICD9_CODING_SYSTEM, hcc, code)
		eicd10codes = differences[hcc]['icd10s_not_in_cms']
		if len(eicd10codes) > 0:
			for code in eicd10codes:
				mappings = removeExtraCodesFromApixioMappings(mappings, ICD10_CODING_SYSTEM, hcc, code)
				
		print "---------------------------------------------------------------------------------------------------------------"
		print "* Label Set Version - HCC:                                   %s" % hcc
		print "* Missing ICD-9 codes from Apixio code mapping table:        %s" % (json.dumps(micd9codes) if len(micd9codes) > 0 else "None")
		print "* Missing ICD-10 codes from Apixio code mapping table:       %s" % (json.dumps(micd10codes) if len(micd10codes) > 0 else "None")
		print "* Extra ICD-9 codes in Apixio code mapping table:            %s" % (json.dumps(eicd9codes) if len(eicd9codes) > 0 else "None")
		print "* Extra ICD-10 codes in Apixio code mapping table:           %s" % (json.dumps(eicd10codes) if len(eicd10codes) > 0 else "None")
		print "---------------------------------------------------------------------------------------------------------------"
		#print "\n"
		
	print "* Total number of differences:                               %s" % (len(differences) if len(differences) > 0 else "None")
	saveMappingsFile(mappings)
	return()
#=========================================================================================	
def endValidationMessage():
	print ("\n===============================================================================================================")	
	print ("==================================== End of Hosting Table Validation ==========================================")
	print ("===============================================================================================================")
	return()	

#=========================================================================================

def mainMenu():
	os.system('clear')
	print "---------------------------------------------------------------------------------------------------------------"
	apixio_hcc_to_icd = loadApixioHccToIcd();
	print "* Length of apixio_hcc_to_icd list:                          %d"%len(apixio_hcc_to_icd);
	cms_hcc_to_icd = loadCmsHccToIcd();
	print "* Length of cms_hcc_to_icd list:                             %d"%len(cms_hcc_to_icd);
	missing_Hccs = findMissingHccs(apixio_hcc_to_icd, cms_hcc_to_icd);
	hcc_diff = obtainDifference(apixio_hcc_to_icd, cms_hcc_to_icd);
	print "---------------------------------------------------------------------------------------------------------------"
	print "R. Resolve differences "
	print "B. Backup original files"
	print "V. Validate"
	print "3. No option"
	print "4. No option"
	print "5. No option"
	print "6. No option"
	print "7. No option"
	print "8. No option"
	print "9. No option"
	print "---------------------------------------------------------------------------------------------------------------"
	input_string = raw_input("Update string: 370,false,5 or just enter Q to Quit: ")
	if input_string.upper() != "Q":
		validation = validateUpdateString(input_string)
		if validation.upper() == "SUCCESS":
			updateOrgConfig(input_string)
		else:
			print (validation)
			#quit()
			raw_input("Press Enter to continue...")
	return(input_string)

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

while True:
	mainMenu()
	print("Select specific option or 'Q' to Quit: ")
	n = mainMenu()
	if n.upper() == 'Q':
		endValidationMessage()
		break
	if n == 'R':
		resolveDifferences(apixio_hcc_to_icd, cms_hcc_to_icd, hcc_diff)
	if n == 'B':
		backupOriginalMappingsFile()
	if n == 'V':
		obtainDifference(apixio_hcc_to_icd, cms_hcc_to_icd)				
	else:
		mainMenu()
	mainMenu()	



#print "---------------------------------------------------------------------------------------------------------------"
#apixio_hcc_to_icd = loadApixioHccToIcd();
#print "* Length of apixio_hcc_to_icd list:                          %d"%len(apixio_hcc_to_icd);

#cms_hcc_to_icd = loadCmsHccToIcd();
#print "* Length of cms_hcc_to_icd list:                             %d"%len(cms_hcc_to_icd);

#missing_Hccs = findMissingHccs(apixio_hcc_to_icd, cms_hcc_to_icd);

#hcc_diff = obtainDifference(apixio_hcc_to_icd, cms_hcc_to_icd);

#backupOriginalMappingsFile();

#resolveDifferences(apixio_hcc_to_icd, cms_hcc_to_icd, hcc_diff);
#print "---------------------------------------------------------------------------------------------------------------"

#endValidationMessage();

#=========================================================================================