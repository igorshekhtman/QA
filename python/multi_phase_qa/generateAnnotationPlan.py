__author__ = 'Ha Pham'

import json

from util import get_apxapi, login
apxapi = get_apxapi()

from AnnotationPlanTemplate import PLANS_OPPS_WITH_ONE_FINDING, PLANS_OPPS_WITH_TWO_FINDINGS

from elasticsearch import Elasticsearch
es = Elasticsearch(['http://elasticsearch-stg2.apixio.com:9200'])

def bundle(s, proj):
  cmpmsvc = s.cmpmsvc
  resp = cmpmsvc.bundle(proj, batch_id='')
  return resp


def prepareAnnotationPlan(es_index):
  plans = {"1": PLANS_OPPS_WITH_ONE_FINDING, "2": PLANS_OPPS_WITH_TWO_FINDINGS}
  res = es.search(index=es_index, doc_type="opportunity", body={"query":{"match_all":{}},
    "_source":["_id", "findings.sourceId", "findings.annotations", "findings.elements"],
    "from": 0,
    "size": 700
  })

  # nFindings histogram for Opportunity
  hist = {}
  opps = {}
  for opp in res['hits']['hits']:
    if 'findings' in opp['_source']:
      nFindings = str(len(opp["_source"]["findings"]))
      if nFindings in hist.keys():
        hist[nFindings] += 1
        opps[nFindings].append(opp)
      else:
        hist[nFindings] = 1
        opps[nFindings] = [opp]

  oppsDistribution = {}
  for k in hist.keys():
    if k in plans.keys():
      (div,mod) = divmod(hist[k], len(plans[k]))

      # prune mod Opps
      count = 0
      bulk_delete_body = ""
      for o in res['hits']['hits']:
        if 'findings' in o['_source'] and len(o["_source"]["findings"]) == int(k) and count < mod:
          count += 1
          bulk_delete_body += """{"delete": {"_index": \"""" + es_index + """\", "_type": "opportunity","_id": \""""+ o["_id"] + """\"}}\n"""
      if bulk_delete_body != "":
        es.bulk(bulk_delete_body, index=es_index, doc_type="opportunity", refresh=True)

      print "# of opps: " + str(hist[k])
      print "# of plans: " + str(len(plans[k]))
      print "# of opps per annotation plan: " + str(div)
      oppsDistribution[k] = div

  # create annotation plan
  annotation_plans = []
  for k in oppsDistribution.keys():
    for (plan, plan_idx) in zip(plans[k], range(len(plans[k]))):
      annotation_plan = {'state': plan['state']}
      for opp in opps[k][plan_idx * oppsDistribution[k] : (plan_idx+1)*oppsDistribution[k]-1]:
        annotation_plan['id'] = opp['_id']
        annotation_plan['steps'] = []
        for step in plan['steps']:
          findingId = opp['_source']['findings'][step[0]]['sourceId']
          annotation_plan['steps'].append({"findingId":findingId, "action": step[1]})

        annotation_plans.append(annotation_plan)


  # write annotation plan to file
  f = open(es_index + '-annotation-plan.json','w')
  f.write(json.dumps(annotation_plans))
  f.close()


def deleteOppsWithMoreThanOneFinding(es_index):
  res = es.search(index=es_index, doc_type="opportunity", body={
    "query":{"match_all":{}},
    "_source":["_id", "findings.sourceId", "findings.annotations", "findings.elements"],
    "from": 0,
    "size": 170
  })

  # only keep opp with nFindings=1
  # we'll deal with Opps with more than 1 finding later
  bulk_delete_body = ""
  for opp in res['hits']['hits']:
    if 'findings' in opp['_source'] and len(opp["_source"]["findings"]) != 1:
      bulk_delete_body += """{"delete": {"_index": \"""" + es_index + """\", "_type": "opportunity","_id": \""""+ opp["_id"] + """\"}}\n"""

  es.bulk(bulk_delete_body, index=es_index, doc_type="opportunity", refresh=True)


if __name__ == '__main__':

  # environment and cred
  env = apxapi.ENG
  #env = apxapi.STG
  #env = apxapi.PRD
  #env = apxapi.ESPRD

  # get a valid session
  session = login(env)

  # bundle
  if False:
    #proj = 'CP_84cffb11-bbda-41ae-a0ec-0e9693f9459c'  # this is in ENG - "Healthnow Staging Verification"
    #proj = 'CP_a3efeecd-8483-4436-b90f-0a83590580af'  # this is in PRD - "Wellpoint UAT"
    proj = 'projectID: CP_fc5161b6-0647-41e4-8f15-ef7218c9c1fa'  # this is in STG/ENG - org-372
    bundle(session, proj)

  # prune data
  if False:
    deleteOppsWithMoreThanOneFinding("org-372")

  # generate annotation plan
  if False:
    prepareAnnotationPlan("org-372")





  print "eof"



