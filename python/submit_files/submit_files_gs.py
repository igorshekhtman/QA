####################################################################################################
#
# PROGRAM: 	submit_files_gs.py (Submit Files Gold Standard)
# AUTHOR:  	Igor Shekhtman ishekhtman@apixio.com
# DATE:    	10/12/2015 Initial Version
#
#
# PURPOSE:
#          	Purpose of this program is to push set of documents together with Catalog files to the 
#			Doc-Receiver. Catalog files are generated based on specific document types being uploaded. 
#			Patient UUIDs and Document UUIDs are retrieved from provided imported GS_FNAME - csv file.
#		   
# INITIAL SET OF FEATURES:
#			* Support to upload PDF as well as TXT document types
#			* Patient First, Last name auto generation via Patient UUID
#			* Upload of multiple documents to a single or multiple patients
#
#
# SAMPLE CALL:
#		   python2.7 submit_files_gs.py
#
# REQUIRED and OPTIONAL PARAMETERS:
#			None
#
#
# SETUP:
#          	* Assumes Staging and/or Production Doc-Receiver is available
#          	* Assumes a Python 2.7 environment is available
#          	* Production QA server (qa.apixio.com) is available
#			* /mnt/automation/python/submit_files folder edit "submit_files.py" to change
#			paramaters are required for your specific upload job
#
# USAGE:	
#
####################################################################################################
#
# EDITED:		November 13th, 2015
# EDITED BY:	Igor Shekhtman ishekhtman@apixio.com
# PURPOSE:		Added formatted version of uploaded documents and patients as upload, while displaying
#				overall progress of the upload.
#				Resolved issue with multiple dots in source document names, which were used to identify
#				mime-type as well as document-type.
#
####################################################################################################
#
# EDITED:		December 14th, 2015
# EDITED BY:	Igor Shekhtman ishekhtman@apixio.com
# PURPOSE:		Added list of files to be uploaded.  This will prevent uploading hidden files and other
#				file types located in the upload folder at the time. New function filterFilesList(files) 
#				was introduced to accomplish this.
#
####################################################################################################

import os
import time
import datetime
import sys
import subprocess
from time import gmtime, strftime
import pycurl
import io
import urllib
import urllib2
import urlparse
import json
import re
import smtplib
import string
import uuid
import cStringIO
import csv

#============================ INITIALIZING GLOBAL VARIABLES VALUES ==============================================

USERNAME="goldstd01"

PASSWORD="apixio.123"

HOST="https://dr-stg.apixio.com"

#DIR = "testpdf"
DIR = "/Volumes/eng/GoldStandard"

GS_FNAME ="gold_standart_data_2015_Dec.csv"

BATCH=strftime("%d%m%Y%H%M%S", gmtime())

UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH)

ALLOW_EXT=["PDF", "TXT", "JPG", "GIF"]

TOKEN_URL="%s/auth/token/" % (HOST)

PATIENT_ID_AA="PATIENT_ID_1"

PATIENT_ID=uuid.uuid1()

DOCUMENTCOUNTER = 0
NUMBEROFDOCUMENTS = 0
PATIENTCOUNTER = 0

DIVLINE = "="*120

#=================================================================================================================
#=================================== Helper Functions ============================================================
#=================================================================================================================
def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)
    return()
#=================================================================================================================
def getUserData():
	TOKEN_URL="%s/auth/token/" % (HOST)
	c = pycurl.Curl()
	c.setopt(pycurl.URL, TOKEN_URL)
	c.setopt(pycurl.HTTPHEADER, [
	'Accept: application/json',
	'Content-Type: application/x-www-form-urlencoded'        
	])
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.POSTFIELDS, post)
	c.setopt(pycurl.WRITEFUNCTION, buf.write)
	c.setopt(pycurl.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 1)
	# c.setopt(pycurl.DEBUGFUNCTION, test)
	c.perform()
	return()
#=================================================================================================================
def uploadData():
	UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH);
	c = pycurl.Curl()
	c.setopt(pycurl.URL, UPLOAD_URL)
	c.setopt(pycurl.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/x-www-form-urlencoded'])
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.POSTFIELDS, post)
	c.setopt(pycurl.WRITEFUNCTION, buf.write)
	c.setopt(pycurl.VERBOSE, True)
	c.setopt(c.SSL_VERIFYPEER, 0)
	c.setopt(pycurl.DEBUGFUNCTION, test)
	c.setopt(c.HTTPPOST, [("document", (c.FORM_FILE, "%s%s" % (DIR, FILE))), ("catalog", (c.FORM_FILE, "%s" % (CATALOG_FILE))) ])
	c.perform()	
	return()
#=================================================================================================================
def loadGoldStandardData():
	global GS_LIST
	
	with open(GS_FNAME, 'rb') as f:
		reader = csv.reader(f)
		GS_LIST = map(tuple, reader)
	
	return GS_LIST	
#=================================================================================================================    	
def filterFilesList(files):
	nFiles = []
	for file in files:
		fft=file.split(".")
		ff=fft[len(fft)-1].upper()
		if ff in ALLOW_EXT:
			nFiles.append(file)
	
	return(nFiles)
#================================================================================================================= 
os.system('clear')

print ("USERNAME: ",USERNAME)
print ("PASSWORD: ",PASSWORD)
print ("HOST: ",HOST)
print ("DIR: ",DIR)
print ("BATCH: ",BATCH)
	
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()
obj=json.loads(buf.getvalue())	
TOKEN=obj["token"]

FILES = os.listdir(DIR)
FILES = filterFilesList(FILES)
TOTDOCS = len(FILES)

print ("\nUploading documents ...")
print DIVLINE
print "* USERNAME                 = %s" % USERNAME
print "* PASSWORD                 = %s" % PASSWORD
print "* DOC RECEIVER HOST URL    = %s" % HOST
print "* DOC SOURCE FOLDER        = %s" % DIR
print "* GS MATCHING FILE NAME    = %s" % GS_FNAME
print "* PRIMARY ASSIGN AUTHORITY = %s" % PATIENT_ID_AA
print "* EXTENSIONS TO UPLOAD     = %s" % ", ".join(ALLOW_EXT)
print "* TOTAL # OF DOCS          = %s" % TOTDOCS
print DIVLINE
user_response = raw_input("Enter 'P' to Proceed or 'Q' to Quit: ")
if user_response.upper() == "Q":
	print "exiting ..."
	quit()
else:
	print "proceeding ..."


print DIVLINE
print "OrgID:     Format:    Document UUID:                         Patient UUID:                             Document #:"
print DIVLINE

#========================= MAIN LOOP =====================================================


for FILE in FILES:

		FILE_FORMAT_TEMP=FILE.split(".")
		FILE_FORMAT=FILE_FORMAT_TEMP[len(FILE_FORMAT_TEMP)-1].upper()
		if FILE_FORMAT == "PDF":
			MIME_TYPE="""application/pdf"""
		elif FILE_FORMAT == "XML":
			MIME_TYPE="""application/xml"""
		else:
			MIME_TYPE="""text/plain"""


		DOCUMENT_ID = FILE.split(".")[0]
		
		PATIENT_ID = uuid.uuid1()
		for i in range (0, len(GS_LIST)):
			if str(DOCUMENT_ID) in GS_LIST[i]:
				PATIENT_ID = GS_LIST[i][13]	

		DOCUMENTCOUNTER += 1

		ORGANIZATION=obj["organization"]
		ORG_ID=obj["org_id"]
		CODE=obj["code"]
		USER_ID=obj["user_id"]
		S3_BUCKET=obj["s3_bucket"]
		ROLES=obj["roles"]
		TRACE_COLFAM=obj["trace_colFam"]

				
		PATIENTCOUNTER += 1
		
		PATIENT_FIRST_NAME=("F_%s" % (PATIENT_ID))
		PATIENT_LAST_NAME=("L_%s" % (PATIENT_ID))	
	
		PATIENT_MIDDLE_NAME="MiddleName"
		PATIENT_DOB="19670809"
		PATIENT_GENDER="M"
		ORGANIZATION="ORGANIZATION_VALUE"
		PRACTICE_NAME="PRACTICE_NAME_VALUE"
		FILE_LOCATION=("%s" % (FILE))
		
		
		
		DOCUMENT_TYPE="DOCUMENT_TYPE_VALUE"
		CREATION_DATE="2014-04-04T10:00:47-07:00"
		MODIFIED_DATE="2014-04-04T10:00:47-07:00"
		DESCRIPTION=("%s" % (FILE))
		METATAGS="METATAGS_VALUE"
		SOURCE_SYSTEM="SOURCE_SYSTEM_VALUE"
		TOKEN_URL="%s/auth/token/" % (HOST)
		UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH)
		
		CATALOG_FILE=("	<ApxCatalog> \
						<CatalogEntry> \
						<Version>V0.9</Version> \
						<DocumentId>%s</DocumentId> \
						<Patient><PatientId><Id>%s</Id> \
						<AssignAuthority>%s</AssignAuthority></PatientId> \
						<PatientFirstName>%s</PatientFirstName> \
						<PatientMiddleName>%s</PatientMiddleName> \
						<PatientLastName>%s</PatientLastName> \
						<PatientDOB>%s</PatientDOB> \
						<PatientGender>%s</PatientGender></Patient> \
						<Organization>%s</Organization> \
						<PracticeName>%s</PracticeName> \
						<FileLocation>%s</FileLocation> \
						<FileFormat>%s</FileFormat> \
						<DocumentType>%s</DocumentType> \
						<CreationDate>%s</CreationDate> \
						<ModifiedDate>%s</ModifiedDate> \
						<Description>%s</Description> \
						<MetaTags>%s</MetaTags> \
						<SourceSystem>%s</SourceSystem> \
						<MimeType>%s</MimeType> \
						</CatalogEntry> \
						</ApxCatalog>" % ( \
						DOCUMENT_ID, PATIENT_ID, PATIENT_ID_AA, PATIENT_FIRST_NAME, PATIENT_MIDDLE_NAME, \
						PATIENT_LAST_NAME, PATIENT_DOB, PATIENT_GENDER, ORGANIZATION, PRACTICE_NAME, \
						FILE_LOCATION, FILE_FORMAT, DOCUMENT_TYPE, CREATION_DATE, MODIFIED_DATE, \
						DESCRIPTION, METATAGS, SOURCE_SYSTEM, MIME_TYPE \
						))
		
		# ============================== Uploading Data =================================================================================================================
		UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH)
		bufu = io.BytesIO()
		response = cStringIO.StringIO()
		c = pycurl.Curl()
		c.setopt(c.URL, UPLOAD_URL)
		c.setopt(c.HTTPPOST, [("token", str(TOKEN)),("document", (pycurl.FORM_FILE, DIR+"/"+FILE)),("catalog", (c.FORM_CONTENTS, str(CATALOG_FILE)))])
		c.setopt(c.WRITEFUNCTION, bufu.write)
		c.perform()	
		# ================================================================================================================================================================
		obju=json.loads(bufu.getvalue())	
		UUID=obju["uuid"]
		ORGGID=obju["orgid"]

		print ORGGID.ljust(10), FILE_FORMAT.ljust(10), str(UUID).ljust(38), str(PATIENT_ID).ljust(38), str(DOCUMENTCOUNTER).rjust(5), "of "+str(TOTDOCS).ljust(5)

# ========================================================== Finish by closing batch ======================================================================================
print DIVLINE	
print ("Total number of documents uploaded: %s" % (DOCUMENTCOUNTER))
print ("Total number of patients uploaded: %s" % (PATIENTCOUNTER if PATIENTCOUNTER>0 else 1))
print DIVLINE
print ("Closing Batch ...\n")

CLOSE_URL="%s/receiver/batch/%s/status/flush?submit=true" % (HOST, BATCH)
bufc = io.BytesIO()
response = cStringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, CLOSE_URL)
c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
c.setopt(c.WRITEFUNCTION, bufc.write)
c.perform()
objc=json.loads(bufc.getvalue())
print ("Batch Closed, Upload Completed ...\n\n")
# =========================================================================================================================================================================









