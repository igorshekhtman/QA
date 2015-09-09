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

USERNAME="prot1440527370697"

PASSWORD="apixio.123"

HOST="https://dr-stg.apixio.com"

DIR="/mnt/testdata/SanityTwentyDocuments/Documents"

BATCH=strftime("%d%m%Y%H%M%S", gmtime())

UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH)

TOKEN_URL="%s/auth/token/" % (HOST)

DOCUMENTCOUNTER=0
NUMBEROFDOCUMENTS=0

# =================================================================================================================



def test(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)


os.system('clear');

print ("USERNAME: ",USERNAME);
print ("PASSWORD: ",PASSWORD);
print ("HOST: ",HOST);
print ("DIR: ",DIR);
print ("BATCH: ",BATCH);



def getUserData():
	TOKEN_URL="%s/auth/token/" % (HOST);
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
TOTAL_DOCS = len(FILES)
patlist = open('patlist', 'w')


print ("Uploading total of %d documents ...\n" % TOTAL_DOCS)	
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
		PATIENT_ID=uuid.uuid1()
		patlist.write(str(PATIENT_ID)+"\n")
		PATIENT_ID_AA="PATIENT_ID_1"
		PATIENT_FIRST_NAME=("Firstname_%s" % (DOCUMENTCOUNTER))
		PATIENT_MIDDLE_NAME=("Middlename_%s" % (DOCUMENTCOUNTER))
		PATIENT_LAST_NAME=("Lastname_%s" % (DOCUMENTCOUNTER))
		PATIENT_DOB="19880706"
		PATIENT_GENDER="M"
		ORGANIZATION="ORGANIZATION_VALUE"
		PRACTICE_NAME="PRACTICE_NAME_VALUE"
		FILE_LOCATION=("%s" % (FILE))
		FILE_FORMAT_TEMP=FILE.split(".")
		FILE_FORMAT=FILE_FORMAT_TEMP[1].upper()
		DOCUMENT_TYPE="DOCUMENT_TYPE_VALUE"
		CREATION_DATE="2014-06-12T10:00:47-07:00"
		MODIFIED_DATE="2014-06-12T10:00:47-07:00"
		DESCRIPTION=("%s" % (FILE))
		METATAGS="METATAGS_VALUE"
		MIME_TYPE="""text/plain"""
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
		#print CATALOG_FILE
		#quit()						
		
		# ============================== Uploading Data =================================================================================================================
		UPLOAD_URL="%s/receiver/batch/%s/document/upload" % (HOST, BATCH);
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
		# print (obju)
		print ("Document %d out of %d \t\t Document UUID: %s" % (DOCUMENTCOUNTER, TOTAL_DOCS, UUID));

		#print (TOKEN), (ORGANIZATION), (ORG_ID), (CODE), (USER_ID), (S3_BUCKET), (ROLES), (TRACE_COLFAM), (DOCUMENT_ID)
		#print (PATIENT_ID), (PATIENT_ID_AA), (PATIENT_FIRST_NAME), (PATIENT_LAST_NAME), (PATIENT_MIDDLE_NAME), (PATIENT_DOB), (PATIENT_GENDER), (ORGANIZATION)
		#print (PRACTICE_NAME), (FILE_LOCATION), (FILE_FORMAT), (DOCUMENT_TYPE), (CREATION_DATE), (MODIFIED_DATE), (DESCRIPTION), (METATAGS), (SOURCE_SYSTEM)
		#print (TOKEN_URL), (UPLOAD_URL)
		#print (" ")
		#print (CATALOG_FILE)
		#print (" ")

# ========================================================== Finish by closing batch ======================================================================================
patlist.close()
print (" ")	
print ("TOTAL NUMBER OF DOCUMENTS UPLOADED: %s" % (DOCUMENTCOUNTER));
print (" ")
print ("Closing Batch ...")
import cStringIO
import pycurl
CLOSE_URL="%s/receiver/batch/%s/status/flush?submit=true" % (HOST, BATCH);
bufc = io.BytesIO()
response = cStringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, CLOSE_URL)
c.setopt(c.HTTPPOST, [("token", str(TOKEN))])
c.setopt(c.WRITEFUNCTION, bufc.write)
c.perform()
objc=json.loads(bufc.getvalue())
# print (objc)
print (" ")
print ("Batch Closed, Upload Completed ...")

print ("================================================================================")
print ("* USERNAME               = %s" % USERNAME)
print ("* PASSWORD:              = %s" % PASSWORD)
print ("* HOST:                  = %s" % HOST)
print ("* SOURCE FOLDER          = %s" % DIR)
print ("* TOTAL DOCS UPLOADED    = %d" % DOCUMENTCOUNTER)
print ("* TOTAL DOCS EXPECTED    = %d" % TOTAL_DOCS)
print ("================================================================================")
# =========================================================================================================================================================================









