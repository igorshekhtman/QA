__author__ = 'ishekhtman'

import stress
import collections
import sys
import requests

doc = {"mimeType": "application/pdf", "document_title": "Consults", "elements": [{"start": 1402943268000, "code": {"codeSystemVersion": "2.0", "code": "V12_8", "displayName": "lung cancer", "codeSystem": "APXCAT"}, "end": 1402943268000, "index": 26}, {"start": 1402943268000, "code": {"codeSystemVersion": "2.0", "code": "V12_8", "displayName": "primary lung cancer", "codeSystem": "APXCAT"}, "end": 1402943268000, "index": 28}], "sourceType": "document", "sourceId": "be07100f-9975-4692-aa3a-228ab159d266", "total_pages": "35", "patient_org_id": "372", "summary": [{"rejects": 0, "totalNonSkip": 0, "totalActions": 0, "accepts": 0, "skips": 0, "user": "total", "lastResult": "none", "earliest": -62167219200000, "lastFlag": "false", "latest": -62167219200000}], "doc_date": "06/16/2014", "documentInfo": {"sortOrdinal": 0}, "pages": "26, 28"}

options=collections.OrderedDict()
options['rep_type'] = 'Stress Test'
options['usr'] = sys.argv[1] if len(sys.argv) > 1 else "mmgenergyes@apixio.net"
options['env'] = sys.argv[2] if len(sys.argv) > 2 else "Development"
options['pwd'] = 'apixio.123'
options['env_hosts'] = stress.getEnvHosts(options['env'])
options['max_opps'] = sys.argv[3] if len(sys.argv) > 3 else 1
options['max_docs'] = sys.argv[4] if len(sys.argv) > 4 else 1
options['max_doc_pages'] = sys.argv[5] if len(sys.argv) > 5 else 1
options['max_ret'] = sys.argv[6] if len(sys.argv) > 6 else 2
options['coding_delay_time'] = sys.argv[7] if len(sys.argv) > 7 else 0
accept = sys.argv[8] if len(sys.argv) > 8 else 45
reject = sys.argv[9] if len(sys.argv) > 9 else 45
skip = sys.argv[10] if len(sys.argv) > 10 else 10
options['action_weights'] = {'view':0,'accept':accept,'reject':reject,'skip':skip}
options['dos'] = sys.argv[11] if len(sys.argv) > 11 else "04/04/2014"
options['report_recepients'] = sys.argv[12] if len(sys.argv) > 12 else "ishekhtman@apixio.com"

stress.defineGlobals()
cookies = stress.loginHCC(options)
dpurl = options['env_hosts']['hcchost']+"document_page/"
i=1
document_uuid='be07100f-9975-4692-aa3a-228ab159d266'
#document_uuid='218bb7bb-f855-4a6a-80fb-b3347c4a33cd'
DATA={}
HEADERS = {'Cookie': 'csrftoken='+cookies["csrftoken"]+'; sessionid='+cookies["jsessionid"]+'; ApxToken='+cookies["ApxToken"]}

response = requests.get(dpurl + document_uuid + "/" + str(i), cookies=cookies, data=DATA, headers=HEADERS)
print response.status_code
