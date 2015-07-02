email="ishekhtman@apixio.com"
passw="apixio.123"
authhost="https://useraccount-stg.apixio.com:7076"
tokehost="https://useraccount-stg.apixio.com:7075"
pipehost="http://coordinator-stg.apixio.com:8066"

token=$(curl -v --data email=$email --data password="$passw" ${authhost}/auths | cut -c11-49)
echo "External token is:  $token"

itoken=$(curl -v --request POST --header "Authorization: Apixio ${token}" "${tokehost}/tokens" | cut -c11-49)

echo "Internal token is:  $itoken"


echo "#########"
echo "/pipeline/datasource/387/keys"
curl -v --request GET --header "Authorization: Apixio ${itoken}" "${pipehost}/pipeline/datasource/371/keys?filter=patientUUID"
echo ""; echo ""

