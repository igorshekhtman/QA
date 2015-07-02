#[2/23/15, 4:10:54 PM] Alex Aitken - Apixio Ops: 54.193.248.3
#[2/23/15, 4:10:56 PM] Alex Aitken - Apixio Ops: external
#[2/23/15, 4:11:26 PM] Alex Aitken - Apixio Ops: 10.226.24.132
#[2/23/15, 4:11:29 PM] Alex Aitken - Apixio Ops: internal
#http://useraccount-stg.apixio.com


#email="root@api.apixio.com"
#passw="thePassword"

email="ishekhtman@apixio.com"
passw="apixio.123"
url="https://useraccount-stg.apixio.com:7076"


#token=$(curl -v --data email=$email --data password="$passw" "http://localhost:8076/auths?int=true" | cut -c11-49)
token=$(curl -v --data email=$email --data password="$passw" ${url}"/auths?int=false" | cut -c11-49)

echo "Token is:  $token"

read -p "Press key to continue ... " test

#curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/rule/assignments

echo "#########"
echo "/aclop"
#curl -v --request POST \
#  --header "Authorization: Apixio ${token}" \
#  --header "Content-Type: application/json" \
#  --data-binary '{"name":"CanReview","description":"Can Review Things"}' \
#  http://localhost:8076/aclop
curl -v --request POST --header "Authorization: Apixio ${token}" --header "Content-Type: application/json" --data-binary '{"name":"CanReview","description":"Can Review Things"}' ${url}/aclop  
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/groups"
#curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/groups
curl -v --header "Authorization: Apixio ${token}" ${url}"/groups"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/groups?type=System:Role"
#curl -v --header "Authorization: Apixio ${token}" "http://localhost:8076/groups?type=System:Role"
curl -v --header "Authorization: Apixio ${token}" ${url}"/groups?type=System:Role"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/groups/{root}/members"
#curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/groups/G_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/members
curl -v --header "Authorization: Apixio ${token}" ${url}"/G_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/members"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/perms/{sub}/{op}/{obj}"
#curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC
curl -v --header "Authorization: Apixio ${token}" ${url}"/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/perms/{sub}/{op}/{obj}"
#curl -v --request PUT --header "Authorization: Apixio ${token}" http://localhost:8076/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC
curl -v --request PUT --header "Authorization: Apixio ${token}" ${url}"/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/perms/{sub}/{op}/{obj}"
#curl -v --request DELETE --header "Authorization: Apixio ${token}" http://localhost:8076/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC
curl -v --request DELETE --header "Authorization: Apixio ${token}" ${url}"/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/grants/{sub}/{op}"
#curl -v --request PUT \
#  --header "Authorization: Apixio ${token}" \
#  --header "Content-Type: application/json" \
#  --data-binary '{"subject":{"type":"All"}, "object":{"type":"All"}}' \
#  http://localhost:8076/grants/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview
curl -v --request PUT \
  --header "Authorization: Apixio ${token}" \
  --header "Content-Type: application/json" \
  --data-binary '{"subject":{"type":"All"}, "object":{"type":"All"}}' \
  ${url}"/grants/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview"
echo ""; echo ""
read -p "Press key to continue ... " test

echo "#########"
echo "/grants/{sub}/{op}"
#curl -v --request DELETE \
#  --header "Authorization: Apixio ${token}" \
#  --header "Content-Type: application/json" \
#  http://localhost:8076/grants/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview
curl -v --request DELETE \
  --header "Authorization: Apixio ${token}" \
  --header "Content-Type: application/json" \
  ${url}"/grants/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview"
echo ""; echo ""
read -p "Press key to continue ... " test

