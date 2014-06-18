#! /bin/sh

export TZ=America/Los_Angeles

TIMESTAMP=$(date +'%s')
DATESTAMP=$(date +'%m/%d/%y %r')

USERNAME=apxdemot0176;
PASSWORD=Hadoop.4522;
HOST=https://testdr.apixio.com:8443;
DIR=/mnt/testdata/SanityTwentyDocuments/Documents;
BATCH=$(date +'%d');

echo "Authenticating..."
TOKEN=$(curl -s -k -d username=$USERNAME -d password=$PASSWORD "$HOST/auth/token/" | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["token"]');
echo "Got Token:" $TOKEN;

FILES=$DIR/*.*
echo "Processing files in: "$FILES;
for FILE in $FILES
do
	echo "Processing file: "$FILE
	DOCUMENT_ID=$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_ID=$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_ID_AA='RANDOM_UUID';
	PATIENT_FIRST_NAME=FIRST_$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_MIDDLE_NAME='';
	PATIENT_LAST_NAME=LAST_$(python  -c 'import uuid; print uuid.uuid1()');
	PATIENT_DOB='19290809';
	PATIENT_GENDER='M';
	ORGANIZATION='ORGANIZATION_VALUE';
	PRACTICE_NAME='PRACTICE_NAME_VALUE';
	FILE_LOCATION=$FILE;
	FILE_FORMAT=$(echo "$FILE" | awk -F . '{print $NF}' | tr '[:lower:]' '[:upper:]');
	DOCUMENT_TYPE='DOCUMENT_TYPE_VALUE';
	CREATION_DATE='2010-05-11T10:00:47-07:00';
	MODIFIED_DATE='2010-05-11T10:00:47-07:00';
	DESCRIPTION=$FILE;
	METATAGS='METATAGS_VALUE';
	SOURCE_SYSTEM='SOURCE_SYSTEM_VALUE';

	CATALOG_FILE='<ApxCatalog><CatalogEntry><Version>V0.9</Version><DocumentId>'$DOCUMENT_ID'</DocumentId><Patient><PatientId><Id>'$PATIENT_ID'</Id><AssignAuthority>'$PATIENT_ID_AA'</AssignAuthority></PatientId><PatientFirstName>'$PATIENT_FIRST_NAME'</PatientFirstName><PatientMiddleName>'$PATIENT_MIDDLE_NAME'</PatientMiddleName><PatientLastName>'$PATIENT_LAST_NAME'</PatientLastName><PatientDOB>'$PATIENT_DOB'</PatientDOB><PatientGender>'$PATIENT_GENDER'</PatientGender></Patient><Organization>'$ORGANIZATION'</Organization><PracticeName>'$PRACTICE_NAME'</PracticeName><FileLocation>'$FILE_LOCATION'</FileLocation><FileFormat>'$FILE_FORMAT'</FileFormat><DocumentType>'$DOCUMENT_TYPE'</DocumentType><CreationDate>'$CREATION_DATE'</CreationDate><ModifiedDate>'$MODIFIED_DATE'</ModifiedDate><Description>'$DESCRIPTION'</Description><MetaTags>'$METATAGS'</MetaTags><SourceSystem>'$SOURCE_SYSTEM'</SourceSystem><MimeType /></CatalogEntry></ApxCatalog>';
	echo "Uploading..."
	UUID=$(echo $CATALOG_FILE | curl  -k --form document=@"$FILE" --form catalog=@- --form token=$TOKEN "$HOST/receiver/batch/$BATCH/document/upload" | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["uuid"]');
	echo "Uploaded Successfully. Document UUID: "$UUID;
done
echo "Closing Batch"
curl -s -k -X POST --form token=$TOKEN "$HOST/receiver/batch/$BATCH/status/flush?submit=true"
echo "Batch closed"
sleep 7m
