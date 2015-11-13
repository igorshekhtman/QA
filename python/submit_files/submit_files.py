####################################################################################################
#
# PROGRAM: 	submit_files.py
# AUTHOR:  	Igor Shekhtman ishekhtman@apixio.com
# DATE:    	2011.01.01 Initial Version
#
#
# PURPOSE:
#          	Purpose of this program is to push set of documents together with Catalog files to the 
#			Doc-Receiver. Catalog files are generated based on specific document types being uploaded. 
#		   
# INITIAL SET OF FEATURES:
#			* Support to upload PDF as well as TXT document types
#			* Patient First, Last name auto generation
#			* Upload of multiple documents to a single or multiple patients
#
#
# SAMPLE CALL:
#		   python2.7 submit_files.py
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

# ============================ INITIALIZING GLOBAL VARIABLES VALUES ==============================================

#USERNAME="apxdemot0216"
USERNAME="protest01"

#PASSWORD="Hadoop.4522"
PASSWORD="apixio.123"

#HOST="https://testdr.apixio.com:8443"
HOST="https://dr-stg.apixio.com"

#DIR="/mnt/testdata/SanityTwentyDocuments/Documents"
#DIR="/mnt/testdata/10_20_30_49_50_51_100_200_300Mb_PDFs/docs"
#DIR="/mnt/testdata/FiveSmallPDFDocuments/Documents"
DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

BATCH=strftime("%d%m%Y%H%M%S", gmtime())

UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH)

TOKEN_URL="%s/auth/token/" % (HOST)

PATIENT_ID=uuid.uuid1()

DOCUMENTCOUNTER = 0
NUMBEROFDOCUMENTS = 0
PATIENTCOUNTER = 0

# =================================================================================================================



def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)


os.system('clear')

print ("USERNAME: ",USERNAME)
print ("PASSWORD: ",PASSWORD)
print ("HOST: ",HOST)
print ("DIR: ",DIR)
print ("BATCH: ",BATCH)



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
	
buf = io.BytesIO()
data = {'username':USERNAME, 'password':PASSWORD}
post = urllib.urlencode(data)
getUserData()
obj=json.loads(buf.getvalue())	
TOKEN=obj["token"]
# print (obj)

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

# ========================================================================= Assign Values =======================================================
FILES = os.listdir(DIR)
PREV_PAT_UUID = PATIENT_ID

#FILE = FILES[4]

# print (FILES)
# print ('Processing files in: ', DIR);

print ("\nUploading documents ...")

# if (NUMBEROFDOCUMENTS > 0):
# elif:
# for FILE in FILES:
#for DOCUMENTCOUNTER in range(NUMBEROFDOCUMENTS):

print "===================================================================================================================="
print "Document #\tOrgID:\t\tDocument UUID:\t\t\t\t\tPatient UUID:"
print "===================================================================================================================="

for FILE in FILES:		
		DOCUMENTCOUNTER += 1

		ORGANIZATION=obj["organization"]
		ORG_ID=obj["org_id"]
		CODE=obj["code"]
		USER_ID=obj["user_id"]
		S3_BUCKET=obj["s3_bucket"]
		ROLES=obj["roles"]
		TRACE_COLFAM=obj["trace_colFam"]
		DOCUMENT_ID=uuid.uuid1()
		# Comment our next line to upload all documents to single patient
		PATIENT_ID=uuid.uuid1()
				
		if PATIENT_ID != PREV_PAT_UUID:
			PATIENTCOUNTER += 1
			PATIENT_FIRST_NAME=("F_%s" % (uuid.uuid1()))
			PATIENT_MIDDLE_NAME="MiddleName"
			PATIENT_LAST_NAME=("L_%s" % (uuid.uuid1()))
		else:
			PATIENT_FIRST_NAME="FirstName"
			PATIENT_MIDDLE_NAME="MiddleName"
			PATIENT_LAST_NAME="LastName"	
	
		PREV_PAT_UUID=PATIENT_ID
		
		PATIENT_ID_AA="PATIENT_ID_1"
		PATIENT_FIRST_NAME=("F_%s" % (uuid.uuid1()))
		PATIENT_MIDDLE_NAME="MiddleName"
		PATIENT_LAST_NAME=("L_%s" % (uuid.uuid1()))
		PATIENT_DOB="19670809"
		PATIENT_GENDER="M"
		ORGANIZATION="ORGANIZATION_VALUE"
		PRACTICE_NAME="PRACTICE_NAME_VALUE"
		FILE_LOCATION=("%s" % (FILE))
		
		FILE_FORMAT_TEMP=FILE.split(".")
		FILE_FORMAT=FILE_FORMAT_TEMP[len(FILE_FORMAT_TEMP)-1].upper()
		if FILE_FORMAT == "PDF":
			MIME_TYPE="""application/pdf"""
		else:
			MIME_TYPE="""text/plain"""
		
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

		# print (obju)
		#print ("Document UUID: %s" % (UUID));
		print ("%s\t\t%s\t\t%s\t\t%s"%(DOCUMENTCOUNTER, ORGGID, UUID, PATIENT_ID))

		#print (CATALOG_FILE)
		#print (FILE_FORMAT_TEMP)
		#print (FILE_FORMAT)
		#print (MIME_TYPE)
		#quit()


# ========================================================== Finish by closing batch ======================================================================================
print "===================================================================================================================="	
print ("Total number of documents uploaded: %s" % (DOCUMENTCOUNTER))
print ("Total number of patients uploaded: %s" % (PATIENTCOUNTER if PATIENTCOUNTER>0 else 1))
print "===================================================================================================================="
print ("Closing Batch ...\n")
import cStringIO
import pycurl
CLOSE_URL="%s/receiver/batch/%s/status/flush?submit=true" % (HOST, BATCH)
bufc = io.BytesIO()
response = cStringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, CLOSE_URL)
c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
c.setopt(c.WRITEFUNCTION, bufc.write)
c.perform()
objc=json.loads(bufc.getvalue())
# print (objc)
print ("Batch Closed, Upload Completed ...\n\n")
# =========================================================================================================================================================================









