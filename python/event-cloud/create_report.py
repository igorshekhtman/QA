
import csv
import json
import requests
import sys
from datetime import datetime

QUERY_URL = 'http://54.177.153.168:8075/event/query'

tmdate = lambda x: (x/(1000.0*60*60*24))+25569

pom = {'10000263': 'CCHCA',
       '10000278': 'Hill Physicians',
       '10000279': 'Production Test Org',
       '10000284': 'RMC',
       '10000291': 'HealthCare Partners',
       '10000318': 'Cambia',
       '10000320': 'Health Net',
       '10000327': 'Well Point',
       '10000328': 'Highmark',
       '10000330': 'Wellcare',
       '10000331': 'UAM',
       '10000332': 'Health Plus',
       '10000334': 'Health Net',
       '10000336': 'NTSP',
       '10000337': 'Network Health HCC',
       '10000340': 'Healthnow',
       '10000342': 'Brown Toland HCC',
       '10000343': 'Hometown Health',
       '10000344': 'Scripps'}

com = {'UO_57f103ca-2f51-4bde-a7ef-2159c6f7ab6c': 'Apixo data QA',
       'UO_19b1bd49-ffc5-4e7d-9dd4-2d7d00056983': 'Aviacode',
       'UO_0df8c4c5-07f9-4a3f-b767-7dc40af1b587': 'AE & Associates',
       'UO_b9149f29-a062-4f83-8e85-c68e5b8b8b48': 'Apex Codemine',
       'UO_eedd3201-13e4-4837-a9e4-a1227dd800f9': 'Codebusters',
       'UO_ba0e1b58-2e51-420f-b0a4-6bd8b518a8a9': 'Apex Codemine',
       'UO_8f5a9a9b-7e8e-4c1f-9702-21f927ed284d': 'CCHCA',
       'UO_1a62aa58-6c4b-478d-b9c5-2d523724b22e': 'Grinder'}

def datestamp():
  return  datetime.now().strftime("%m%d%Y")

def userdata(start, end):
  stmt = "select * from AllUserSessions where time >= %d and time < %d" % (start, end)
  r = requests.get(QUERY_URL, params=[('statement', stmt)])
  if r.status_code != 200: raise Exception(r.text)
  return r.json()

def workdata(start, end):
  stmt = "select * from AllWorkSessions where time >= %d and time < %d and result in ('accept', 'reject')" % (start, end)
  r = requests.get(QUERY_URL, params=[('statement', stmt)])
  if r.status_code != 200: raise Exception(r.text)
  return r.json()

def generate_work_report(start, end, prefix):
  columns = ['Start_Date', 'End_Date', 'Coder', 'Coding_Org', 'Session', 'OppOrFindId', 'QA', 'Patient', 'Patient_Org', 'Duration', 'Num_Events', 'Num_Unique_Findings', 'Timestamp']
  mapping = lambda x: (tmdate(x['time']-x['duration']), tmdate(x['time']), x['coderId'], com.get(x['coderOrg'], x['coderOrg']), x['session'], x['id'], x['qa'], x['patientId'], pom.get(x['orgId'], x['orgId']), x['duration']/(60*60*1000.0), x['actions'], x['findings'], x['time'])
  fname = '%s_work_%s.csv' % (prefix, datestamp())
  with open(fname, 'w') as fp:
    w = csv.writer(fp)
    w.writerow(columns)
    for x in workdata(start, end):
      if pom.get(x['orgId']) is None:
        print 'WARN: %s not mapped' % (x['orgId'],)
      if com.get(x['coderOrg']) is None:
        print 'WARN: %s is not mapped' % (x['coderOrg'],)
      w.writerow(mapping(x))
  return fname

def generate_session_report(start, end, prefix):
  columns = ['Start_Date', 'End_Date', 'Coder', 'Coding_Org', 'Session', 'Duration', 'Num_Events', 'Timestamp']
  mapping = lambda x: (tmdate(x['time']-x['duration']), tmdate(x['time']), x['coderId'], com.get(x['coderOrg'], x['coderOrg']), x['session'], x['duration']/(60*60*1000.0), x['actions'], x['time'])
  fname = '%s_session_%s.csv' % (prefix, datestamp())
  with open(fname, 'w') as fp:
    w = csv.writer(fp)
    w.writerow(columns)
    for x in userdata(start, end):
      w.writerow(mapping(x))
  return fname

if __name__ == '__main__':
  if len(sys.argv) != 5:
    print 'Usage: %s <start_ts> <end_ts> <prefix> <work|session>' % (sys.argv[0],)
    raise SystemExit
  if sys.argv[4] == 'work':
    print generate_work_report(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
  elif sys.argv[4] == 'session':
    print generate_session_report(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
  else:
    print 'Usage: %s <start_ts> <end_ts> <prefix> <work|session>' % (sys.argv[0],)
    raise SystemExit
