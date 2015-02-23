email="root@api.apixio.com"
passw="thePassword"

token=$(curl -v --data email=$email --data password="$passw" "http://localhost:8076/auths?int=true" | cut -c11-49)

echo "Token is:  $token"

#curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/rule/assignments

echo "#########"
echo "/aclop"
curl -v --request POST \
  --header "Authorization: Apixio ${token}" \
  --header "Content-Type: application/json" \
  --data-binary '{"name":"CanReview","description":"Can Review Things"}' \
  http://localhost:8076/aclop
echo ""; echo ""

echo "#########"
echo "/groups"
curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/groups
echo ""; echo ""

echo "#########"
echo "/groups?type=System:Role"
curl -v --header "Authorization: Apixio ${token}" "http://localhost:8076/groups?type=System:Role"
echo ""; echo ""

echo "#########"
echo "/groups/{root}/members"
curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/groups/G_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/members
echo ""; echo ""

echo "#########"
echo "/perms/{sub}/{op}/{obj}"
curl -v --header "Authorization: Apixio ${token}" http://localhost:8076/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC
echo ""; echo ""

echo "#########"
echo "/perms/{sub}/{op}/{obj}"
curl -v --request PUT --header "Authorization: Apixio ${token}" http://localhost:8076/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC
echo ""; echo ""

echo "#########"
echo "/perms/{sub}/{op}/{obj}"
curl -v --request DELETE --header "Authorization: Apixio ${token}" http://localhost:8076/perms/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview/IHC
echo ""; echo ""

echo "#########"
echo "/grants/{sub}/{op}"
curl -v --request PUT \
  --header "Authorization: Apixio ${token}" \
  --header "Content-Type: application/json" \
  --data-binary '{"subject":{"type":"All"}, "object":{"type":"All"}}' \
  http://localhost:8076/grants/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview
echo ""; echo ""

echo "#########"
echo "/grants/{sub}/{op}"
curl -v --request DELETE \
  --header "Authorization: Apixio ${token}" \
  --header "Content-Type: application/json" \
  http://localhost:8076/grants/U_970a22c2-cdd3-4e51-a53a-da20d82fb4b9/CanReview
echo ""; echo ""

