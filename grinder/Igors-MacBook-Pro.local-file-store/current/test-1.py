from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest, HTTPPluginControl
from HTTPClient import Cookie, CookieModule, CookiePolicyHandler, NVPair
from org.json.simple import JSONObject, JSONValue
import time

HOST_DOMAIN = 'hccstage.apixio.com'
HOST_URL = 'https://%s' % HOST_DOMAIN
USERNAME = 'root@api.apixio.com'
PASSWORD = 'thePassword'
MAX_OPPS = 2

def create_request(test, headers=None):
    request = HTTPRequest()
    if headers:
        request.headers = headers
    test.record(request)
    return request

def get_csrf_token(thread_context):
    cookies = CookieModule.listAllCookies(thread_context)
    csrftoken = ''
    for cookie in cookies:
        if cookie.getName() == 'csrftoken':
            csrftoken = cookie.getValue()
    return csrftoken

class TestRunner:
    def __call__(self):
        print "Starting HCC Front End Test - Igor"
        thread_context = HTTPPluginControl.getThreadHTTPClientContext()
	control = HTTPPluginControl.getConnectionDefaults()
	control.setFollowRedirects(1)

        print "Connecting to host... - Igor"
        create_request(Test(10000, 'Connect to host')).GET(HOST_URL + '/')

        print "Detecting login page... - Igor"
        create_request(Test(20000, 'Get login page')).GET(HOST_URL + '/account/login/?next=/')
	
        # Create login request. Referer appears to be necessary
        login = create_request(Test(30000, 'Log in user'),[
            NVPair('Referer', HOST_URL + '/account/login/?next=/'),
        ])

        print "Logging in to HCC Front End... - Igor"
        response = login.POST(HOST_URL + '/account/login/?next=/', (
            NVPair('csrfmiddlewaretoken', get_csrf_token(thread_context)),
            NVPair('username', USERNAME),
            NVPair('password', PASSWORD),))

	print "Beginning Get Opportunity Loop - Igor"
	for x in range(0, MAX_OPPS):    
            print "Getting a coding opportunity - Igor"
	    testCode = 30000 + (100 * x)
	    response = create_request(Test(testCode, 'Get coding opportunity')).GET(HOST_URL + '/api/coding-opportunity/')
            opportunity = JSONValue.parse(response.getText())
            patient_uuid = opportunity.get("patient_uuid")
            print "patient: " + patient_uuid
            
	    scorables = opportunity.get("scorables")
	    counter = 0
	    opp_index = 0
	    num_opps = len(scorables)
	    for scorable in scorables:
	        opp_index += 1
		counter += 1
                document_uuid = scorable.get("document_uuid")
	        print "downloading document: " + document_uuid
                doc_request = create_request(Test(testCode + counter, 'Get scorable document'),[
                    NVPair('Referer', HOST_URL + '/'),
		    NVPair('Host', HOST_DOMAIN),
                ])

		# Get the document just to see how long it takes and to ensure we can
                response = doc_request.GET(HOST_URL + '/api/document/' + document_uuid)
	        
		counter += 1

		#annotation time!
		if (opp_index % 2 == 0):
		    accept_opportunity(opportunity, scorable, testCode + counter, opp_index, num_opps)
		else:
		    reject_opportunity(opportunity, scorable, testCode + counter, opp_index, num_opps)
		
        print "Ending HCC Front End Test... - Igor"

def accept_opportunity(opportunity, scorable, testname, opp_index, num_opps):
    finding_id = scorable.get("id")   
    print "making accept annotation for scorable: " + str(finding_id)
    annotation = create_request(Test(testname, 'Annotate Finding'))   
    response = annotation.POST(HOST_URL+ '/api/annotate/' + str(finding_id) + '/', (
	NVPair('user_id', USERNAME),
	NVPair('timestamp',str(1000 * int(time.time()))),
	NVPair('result','accept'),
	NVPair('comment',''),
	NVPair('date_of_service',scorable.get("date_of_service")),
	NVPair('flag_for_review','false'),
        NVPair('icd9[code_system_name]',
		opportunity.get("suggested_codes")[0].get("[code_system_name")),
	NVPair('icd9[code]',
		opportunity.get("suggested_codes")[0].get("[code")),
	NVPair('icd9[display_name]',
		opportunity.get("suggested_codes")[0].get("[display_name")),
	NVPair('icd9[code_system]',
		opportunity.get("suggested_codes")[0].get("[code_system")),
	NVPair('icd9[code_system_version]',
		opportunity.get("suggested_codes")[0].get("[code_system_version")),
	NVPair('provider[name]','ABESAMIS, WILFREDO R., M.D.'),
	NVPair('provider[id]','1992754832'),
	NVPair('provider[type]','Hospital Inpatient Setting: Other Diagnosis'),
	NVPair('payment_year',str(opportunity.get("payment_year"))),
	NVPair('org_id',str(scorable.get("org_id"))),
	NVPair('orig_date_of_service',scorable.get("date_of_service")),
	NVPair('opportunity_hash',opportunity.get("hash")),
	NVPair('rule_hash',opportunity.get("rule_hash")),
	NVPair('get_id',str(opportunity.get("get_id"))),
	NVPair('patient_uuid',opportunity.get("patient_uuid")),
	NVPair('hcc[code]',str(opportunity.get("hcc"))),
	NVPair('hcc[model_run]',opportunity.get("model_run")),
	NVPair('hcc[model_year]',str(opportunity.get("model_year"))),
	NVPair('hcc[description]',opportunity.get("hcc_description")),
	NVPair('hcc[label_set_version]',opportunity.get("label_set_version")),
	NVPair('hcc[mapping_version]',str(opportunity.get("model_year")) + " " + opportunity.get("model_run")),
	NVPair('hcc[code_system]',str(opportunity.get("model_year")) + 'PYFinal'),
	NVPair('finding_id',str(finding_id)),
	NVPair('document_uuid', scorable.get("document_uuid")),
	NVPair('list_position',str(opp_index)),
	NVPair('list_length',str(num_opps)),
	NVPair('document_date',scorable.get("date_of_service")),
	NVPair('snippets',str(scorable.get("snippets"))),
	NVPair('page_load_time',str(1000 * int(time.time()))),))  

def reject_opportunity(opportunity, scorable, testname, opp_index, num_opps):
    finding_id = scorable.get("id")   
    print "making reject annotation for scorable: " + str(finding_id)
    annotation = create_request(Test(testname, 'Annotate Finding'))   
    response = annotation.POST(HOST_URL+ '/api/annotate/' + str(finding_id) + '/', (
	NVPair('user_id', USERNAME),
	NVPair('timestamp',str(1000 * int(time.time()))),
	NVPair('result','reject'),
	NVPair('reject_reason','Additional documentation needed to Accept the document for this HCC'),
	NVPair('comment',''),
	NVPair('date_of_service',scorable.get("date_of_service")),
	NVPair('flag_for_review','false'),
	NVPair('payment_year',str(opportunity.get("payment_year"))),
	NVPair('org_id',str(scorable.get("org_id"))),
	NVPair('orig_date_of_service',scorable.get("date_of_service")),
	NVPair('opportunity_hash',opportunity.get("hash")),
	NVPair('rule_hash',opportunity.get("rule_hash")),
	NVPair('get_id',str(opportunity.get("get_id"))),
	NVPair('patient_uuid',opportunity.get("patient_uuid")),
	NVPair('hcc[code]',str(opportunity.get("hcc"))),
	NVPair('hcc[model_run]',opportunity.get("model_run")),
	NVPair('hcc[model_year]',str(opportunity.get("model_year"))),
	NVPair('hcc[description]',opportunity.get("hcc_description")),
	NVPair('hcc[label_set_version]',opportunity.get("label_set_version")),
	NVPair('hcc[mapping_version]',str(opportunity.get("model_year")) + " " + opportunity.get("model_run")),
	NVPair('hcc[code_system]',str(opportunity.get("model_year")) + 'PYFinal'),
	NVPair('finding_id',str(finding_id)),
	NVPair('document_uuid', scorable.get("document_uuid")),
	NVPair('list_position',str(opp_index)),
	NVPair('list_length',str(num_opps)),
	NVPair('document_date',scorable.get("date_of_service")),
	NVPair('snippets',str(scorable.get("snippets"))),
	NVPair('predicted_code[code_system_name]',
		scorable.get("code").get("[code_system_name")),
	NVPair('predicted_code[code]',
		scorable.get("code").get("[code")),
	NVPair('predicted_code[display_name]',
		scorable.get("code").get("[display_name")),
	NVPair('predicted_code[code_system]',
		scorable.get("code").get("[code_system")),
	NVPair('predicted_code[code_system_version]',
		scorable.get("code").get("[code_system_version")),
	NVPair('page_load_time',str(1000 * int(time.time()))),))   


