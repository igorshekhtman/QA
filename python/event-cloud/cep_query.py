
try:
  import readline
  import requests
  import sys
  import tabulate
except:
  print 'Missing some libraries: `pip install requests tabulate`'
  raise

class CEPException(Exception):
  pass

def output(data):
  columns = sorted(reduce(lambda x, y: set(x) | set(y), [set(x.keys()) for x in data]))
  odata = [[x.split('_')[-1] for x in columns]]
  for row in data:
    odata.append([row.get(x) if type(row.get(x)) != float else '%.2f' % row.get(x) for x in columns])
  print tabulate.tabulate(odata, headers='firstrow', missingval='')

def query(stmt, url=None):
  url = url if url is not None else URL
  r = requests.get(url, params={'statement': stmt})
  if r.status_code != 200:
    raise CEPException(r.text)
  j = r.json()
  if len(j) == 0:
    raise CEPException('JSON length 0')
  return j

################################### HCC ########################################
def date_hcc(args):
  output(query('select current_timestamp.format() current_date from AllUserSessions limit 1'))
  
def esper_error_count_hcc(args):
  output(query('select count(*) count from AllEsperErrors limit 1'))

def all_counts_hcc(args):
  if len(args) == 0:
    output(query('select * from CurrentTotals'))
  else:
    output(query('select * from CurrentTotals where interval = %s' % (args[0],)))

def counts_by_name_hcc(args):
  if len(args) == 1:
    output(query("select * from CurrentTotals where name = '%s'" % (args[0],)))
  elif len(args) == 2:
    output(query("select * from CurrentTotals where name = '%s' and interval = %s" % (args[0],args[1])))

def counts_by_gkvalue_hcc(args):
  if len(args) == 1:
    output(query("select * from CurrentTotals where gkvalue = '%s'" % (args[0],)))
  elif len(args) == 2:
    output(query("select * from CurrentTotals where gkvalue = '%s' and interval = %s" % (args[0],args[1])))

def orgs_hcc(args):
  output(query("select distinct(gkvalue) a_orgId, cast(max(time), long).format() b_lasttime from HistoricalTotals where gkey = 'org' and gkvalue != '' group by gkvalue order by max(time)"))

def org_stats_hour_hcc(args):
  output(query("select * from CurrentTotals where interval = 1 and ((gkey = 'org' and gkvalue = '%s') or (gkey = 'org_wtype' and gkvalue like '%s%%'))" % (args[0],args[0])))

def org_history_by_name_hcc(args):
  output(query("select * from HistoricalTotals where name = '%s' and ((gkey = 'org' and gkvalue = '%s') or (gkey = 'org_wtype' and gkvalue like '%s%%'))" % (args[1],args[0],args[0])))

def coders_currently_logged_in_hcc(args):
  output(query("select distinct(coderId) a_coder, count(*) b_events, lastever(activityType) c_lastaction, (current_timestamp - max(time)) / (60 * 1000.0) d_timesince, (max(time) - min(time)) / (60 * 1000.0) e_duration from CurrentUserSession group by coderId having lastever(activityType) != 'logout' and (current_timestamp - max(time)) - (max(time) - min(time)) < (20 * 60 * 60 * 1000)"))

def coders_currently_working_hcc(args):
  output(query("select distinct(coderId) a_coder, count(*) b_events, lastever(activityType) c_lastaction, (current_timestamp - max(time)) / (60 * 1000.0) d_timesince, firstever(orgId, orgId != '') e_org, firstever(oppId, oppId != '') f_opp, lastever(findingId, findingId != '') g_finding, firstever(hccv(*), hccv(*) != ',') h_hccInfo, (max(time) - min(time)) / (60 * 1000.0) i_duration from CurrentWorkSession group by coderId"))
  
def all_projects_hcc(args):
  output(query("select projectName a_projectName, orgId b_orgId, orgName c_orgName, budget d_budget, rafpt e_RAFtarget, starttime.format() f_start, endtime.format() g_end, state h_state from AllProjects"))

def projects_hcc(args):
  output(query("select projectName a_projectName, orgId b_orgId, orgName c_orgName, budget d_budget, rafpt e_RAFtarget, starttime.format() f_start, endtime.format() g_end, state h_state from AllProjects where state = 'ongoing' and starttime > (current_timestamp - (60L * 24 * 60 * 60 * 1000))"))

################################### PIPELINE ########################################
def date_pipeline(args):
  output(query('select current_timestamp.format() current_date from AllBatchState limit 1'))
  
def esper_error_count_pipeline(args):
  output(query('select count(*) count from AllEsperErrors limit 1'))

def batches_pipeline(args):
  output(query("select batchId a_batchId, firstever(numDocs, stateName='PersistMapped') b_docs, cast(min(starttime), long).format() c_start, cast(max(lasttime), long).format() d_last from AllBatchState group by batchId order by max(lasttime) desc"))

def batch_info_pipeline(args):
  output(query("select stateName a_state, occurences b_count, successes c_successes, errors d_errors, numDocs e_docs, numPatients f_patients, numEvents g_events, duration h_duration, starttime.format() i_start, lasttime.format() j_last from AllBatchState where batchId = '%s' order by j_last" % (args[0],)))

def batch_info2_pipeline(args):
  output(query("select stateName a_state, successes b_successes, errors c_errors, numDocs d_docs, docsWE e_docsWithE, numPatients f_patients, patientsWE g_patientsWithE, numEvents h_events, v5Events i_v5, dictEvents j_dict, claimEvents k_claims, duration l_duration, starttime.format() m_start, lasttime.format() n_last from AllBatchState where batchId = '%s' order by n_last" % (args[0],)))

def batch_all_info_pipeline(args):
  output(query("select * from AllBatchState where batchId = '%s'" % (args[0],)))

def docs_in_batch_pipeline(args):
  output(query("select distinct(docId) docId from AllDocumentState where batchId = '%s' limit %s" % tuple(args)))

def doc_info_pipeline(args):
  output(query("select stateName a_state, occurences b_count, successes c_successes, errors d_errors, type e_type, size f_size, pages ff_pages, patientId g_patId, numEvents h_events, duration i_duration from AllDocumentState where docId = '%s'" % (args[0],)))

def doc_props_pipeline(args):
  output(query("select srcId a_src, batchId b_batch, type c_type, size d_size, pages e_pages, patientId f_patId, numEvents g_events from AllDocumentState where docId = '%s'" % (args[0],)))

def doc_all_info_pipeline(args):
  output(query("select * from AllDocumentState where docId = '%s'" % (args[0],)))

def shell_hcc(args):
  shell()

def shell_pipeline(args):
  shell()

def shell():
  try:
    while True:
      inp = raw_input("$ ")
      if len(inp) > 0:
        try:
          output(query(inp))
        except CEPException, e:
          print e
  except EOFError:
    print

def set_url(host):
  global URL
  URL = 'http://%s/event/query' % host

if __name__ == '__main__':
  g = globals()
  if len(sys.argv) < 4:
    print 'Usage: %s <host> hcc|pipeline <function_name> [arg1] [arg2] ... [argN]' % sys.argv[0]
    print 'Available:'
    fns = []
    for k in g.keys():
      if k.endswith('_hcc'):
        fns.append('hcc ....... %s' % '_'.join(k.split('_')[:-1]))
      elif k.endswith('_pipeline'):
        fns.append('pipeline .. %s' % '_'.join(k.split('_')[:-1]))
    if len(sys.argv) == 3:
      fns = filter(lambda x: x.startswith(sys.argv[2]), fns)
    print '\n'.join(sorted(fns))
    raise SystemExit
    
  set_url(sys.argv[1])
  fn = g['%s_%s' % (sys.argv[3], sys.argv[2])]  
  fn(sys.argv[4:])