__author__ = 'ha'

from time import time
import cql

from util import get_apxapi
apxapi = get_apxapi()


def getSequenceStoreCfName(session, org_id):
  r = session.useraccounts.get_customer("O_00000000-0000-0000-0000-000000000%s"%org_id)
  result = r.json()['properties']['sequence_store_datastore_folder'] # store457
  print result
  return result


def truncateCf():
  con = cql.connect('10.1.2.91', 9160, "apixio", cql_version='3.0.0')
  print ("Connected!")
  cursor = con.cursor()
  CQLString = "TRUNCATE store457;"
  #cursor.execute(CQLString)
  pass


def generate_events(session, org_id):
  # -------- get patient keys -------
  r = session.pipelineadmin.patient_keys(org_id, addPrefix="true")
  if r.text == '':
    r = session.pipelineadmin.list_keys(org_id, filterType="patientUUID")

  keys = [k.lstrip('pat_') for k in r.text.split('\n')]


  # -------- submit extraction batch -------
  # ---- (this is a small org so all patients can be sent in one job) --
  operation = "eventGeneration"
  batch = org_id + "_" + operation + "_" + str(int(time()))
  r = session.pipelineadmin.submit_job(org_id, operation, batch, keys)
  # r.status_code should be 200

if __name__ == '__main__':
  env = apxapi.ENG
  s = apxapi.APXSession("hpham@apixio.com", environment=env)
