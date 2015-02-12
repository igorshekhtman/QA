import json
import csv
import datetime
from pprint import pprint as pprint_fn

def dist(d):
  r = {}
  for x in d:
    r[x] = r.get(x, 0) + 1
  return r

avg = lambda x: sum(x)/float(len(x)) if x else 0.0
stddev = lambda x, m: (sum([(v-m)**2 for v in x]) / float(len(x)-1))**0.5 if len(x) > 1 else 0.0

pp = lambda x: pprint_fn(x, width=200)

sget = lambda x, y: x.get(y, {})

def scol(d, k, v):
  if k in d:
    d[k].append(v)
  else:
    d[k] = [v]

ttime = lambda x: int(x['unixtime'])

tmdate = lambda x: (ttime(x)/(1000.0*60*60*24))+25569

tevent = lambda x: sget(sget(x, 'app'), 'hcc').get('event_name')
terror = lambda x: sget(sget(x, 'app'), 'hcc').get('error_name')
tfrontend = lambda x: sget(sget(sget(x, 'app'), 'hcc'), 'frontend').get(tevent(x), sget(sget(sget(x, 'app'), 'hcc'), 'frontend').get(terror(x)))
thcc = lambda x: sget(tfrontend(x), 'hcc').get('code')
tpatient = lambda x: tfrontend(x).get('patient_uuid', sget(tfrontend(x), 'scorable').get('patient_uuid'))
torg = lambda x: tfrontend(x).get('patient_org_id', tfrontend(x).get('org_id'))
tcoderorg = lambda x: sget(sget(x, 'app'), 'app_user_info').get('coding_org_name', sget(sget(x, 'app'), 'app_user_info').get('org_name'))
tsession = lambda x: sget(sget(x, 'app'), 'app_user_info').get('session')
tfinding = lambda x: tfrontend(x).get('finding_id', sget(tfrontend(x), 'scorable').get('finding_id'))
topp = lambda x: tfrontend(x).get('get_id', sget(tfrontend(x), 'scorable').get('get_id'))
tclick = lambda x: tevent(x) is not None and ('_click' in tevent(x) or tevent(x) == 'document_loaded')
tcoder = lambda x: sget(sget(x, 'app'), 'app_user_info').get('user', tfrontend(x).get('user_name'))
treport = lambda x: tfrontend(x).get('from_report')
tview = lambda x: tfrontend(x).get('fragment')
tcduration = lambda x: (ttime(x[-1]) - ttime(x[0])) / (60 * 60 * 1000.0)
notnone = lambda x: x is not None
tcfindings = lambda x: filter(notnone, map(tfinding, x))
tcpatients = lambda x: filter(notnone, map(tpatient, x))
tcevents = lambda x: filter(notnone, map(tevent, x))
tcvalid = lambda x: len(set(tcevents(x)) & set(['accept_finding', 'reject_finding', 'accept_submit', 'reject_submit'])) > 0
tcpatient = lambda x: filter(lambda x: notnone(x) and x != '', map(tpatient, x))[0]
tcmaxduration = lambda x: max([tcduration(e) for e in zip(x[:-1], x[1:])]) if len(x) > 1 else 0.0

def tcorg(x):
  res = filter(lambda x: notnone(x) and x != '', map(torg, x))
  return res[0] if res else ''

tcopps = lambda x: filter(notnone, map(topp, x))
tcannotations = lambda x: filter(notnone, map(tfinding, filter(lambda x: tevent(x) in ('accept_finding', 'reject_finding'), x)))

def loadmappings(f, s=0, e=9999999999999):
  oppfs, forgs, corgs = {}, {}, {}
  with open(f, 'r') as fp:
    for x in fp:
      try:
        if x[0] == '{' and x[-1] == '\n':
          d = json.loads(x)
          if 'unixtime' in d and ttime(d) >= e:
            break
          if 'unixtime' in d and ttime(d) >= s:
            if tfrontend(d) is not None and tfinding(d) is not None and topp(d) is not None and topp(d) != '':
              oppfs[topp(d)] = tfinding(d)
            if tfrontend(d) is not None and tfinding(d) is not None and torg(d) is not None and torg(d) != '':
              forgs[tfinding(d)] = str(torg(d))
            if tfrontend(d) is not None and tcoder(d) is not None and tcoderorg(d) is not None and tcoderorg(d) != '':
              corgs[tcoder(d)] = tcoderorg(d)
      except KeyboardInterrupt:
        raise
      except:
        pass
  return oppfs, forgs, corgs
  
def loaddata(f, s=0, e=9999999999999):
  res = []
  with open(f, 'r') as fp:
    for x in fp:
      if x[0] == '{' and x[-1] == '\n':
        d = json.loads(x)
        if 'unixtime' in d and ttime(d) >= e:
          break
        if 'unixtime' in d and ttime(d) >= s:
            res.append(d)
  return sorted(res, key=lambda x: ttime(x))
    

kcodersession = lambda x: (tcoder(x), tsession(x))
kcodersessionopp = lambda x: (tcoder(x), tsession(x), topp(x))
kcodersessionoof = lambda x: (tcoder(x), tsession(x), topp(x) if topp(x) != '' else tfinding(x))
kcodersessionfind = lambda x: (tcoder(x), tsession(x), tfinding(x))
scoder = lambda x: x[0]
aduration = lambda x: tcduration(x)
asumtime = lambda x: sum([v[1] for v in x])
fnone = lambda k: k[0] == '' or None in k

def groupByKey(data, keyfn=kcodersession, filterfn=fnone):
  r = {}
  for x in data:
    k = keyfn(x)
    if not filterfn(k):
      scol(r, k, x)
  return r

def groupByKeySeq(data, keyfn=kcodersession, seqfn=scoder, filterfn=fnone):
  r = {}
  ids = {}
  seq = {}
  for x in data:
    k = keyfn(x)
    #print '%s, %s, %s, %s, %s' % (str(k), str(filterfn(k)), str(seqfn(k)), str(seq.get(seqfn(k))), str(ids.get(k)))
    if not filterfn(k):
      if seqfn(k) in seq and seq[seqfn(k)] == k:
        r[ids[k]].append(x)
      else:
        seq[seqfn(k)] = k
        ids[k] = k + (ids.get(k, (0,))[-1] + 1,)
        r[ids[k]] = [x]
  return r

def reduceByKey(data, key_fn=lambda x: x, val_fn=lambda x: x):
  res = {}
  for k,v in data.items():
    res[key_fn(k)] = res.get(key_fn(k), 0.0) + val_fn(v)
  return res

def annotateTime(data, gp=150*1000, bw=600*1000, tfn=lambda x:  (x / (60 * 60 * 1000.0))):
  res = []
  for x1, x2 in zip(data[:-1], data[1:]):
    diff = ttime(x2) - ttime(x1)
    dur = tfn(diff) if diff < bw else tfn(gp)
    res.append((x1, dur))
  res.append((data[-1], 0.0))
  return res
  
def annotateBreaks(data, bw=600*1000):
  res = []
  for x1, x2 in zip(data[:-1], data[1:]):
    res.append((x1, (ttime(x2) - ttime(x1)) > bw))
  res.append((data[-1], False))
  return res

def eventStats(data):
  """return: {event: (len, total_hours, mean_minutes, std_minutes, num_outside_2d)}"""
  dataat = dict([(k, annotateTime(v, 0, 10*60*60*1000.0)) for k, v in data.items()])
  dataat_e = {}
  for x in [x for v in dataat.values() for x in v]:
    scol(dataat_e, tevent(x[0]), x[1]*60*60)
  stats_e = {}
  for k, v in dataat_e.items():
    l, m, s = len(v), avg(v), stddev(v, avg(v))
    stats_e[k] = (l, sum(v)/(60*60), m/60.0, s/60.0, len([x for x in v if x < (m - 2*s) or x > (m + 2*s)]))
  return stats_e

pstats = lambda x: pp(sorted([(k, v, int((v[2]+2*v[3])*60.0*1000)) for k, v in x.items()], key=lambda x: x[2], reverse=True))

def coderOrgs(data):
  res = {}
  for x in data:
    c = tcoder(x)
    co = tcoderorg(x)
    if c is not None and co is not None and c and co:
      res[c] = co
  return res


patient_org_map = {'10000328': 'Highmark', '10000291': 'HCP of Nevada', '10000331': 'UAM', '10000330': 'Wellcare', '10000318': 'Cambia', '10000263': 'CCHCA', '10000334': 'Health Net', '10000337': 'Network Health HCC', '10000336': 'NTSP', '10000327': 'Well Point', '10000278': 'Hill Physicians', '10000320': 'Health Net', '10000332': 'Health Plus', '10000340': 'Healthnow', '10000284': 'RMC', '10000342': 'Brown Toland HCC'}

def outputCSOV(f, cso, co, forgs, oppfs):
  columns = ['Start_Date', 'End_Date', 'Coder', 'Coding_Org', 'Session', 'OppOrFindId', 'Patient', 'Patient_Org', 'Duration', 'Num_Events', 'Num_Unique_Findings', 'Timestamp']
  mapping = lambda k, v: (tmdate(v[0]), tmdate(v[-1]),
                          k[0], co[k[0]],
                          k[1], k[2], tcpatient(v), patient_org_map.get(forgs.get(k[2], forgs.get(oppfs.get(k[2]))), forgs.get(k[2], forgs.get(oppfs.get(k[2]), ''))),
                          tcduration(v), len(v), len(set(tcfindings(v))), ttime(v[-1]))
  with open(f, 'wb') as fp:
    w = csv.writer(fp)
    w.writerow(columns)
    for k, v in cso.items():
      w.writerow(map(str, mapping(k, v)))

def outputCS(f, cs, co):
  columns = ['Start_Date', 'End_Date', 'Coder', 'Coding_Org', 'Session', 'Duration', 'Num_Events', 'Num_Unique_Findings', 'Num_Unique_Patients', 'Timestamp']
  mapping = lambda k, v: (tmdate(v[0]), tmdate(v[-1]), k[0], co[k[0]], k[1], tcduration(v), len(v), len(set(tcfindings(v))), len(set(tcpatients(v))), ttime(v[-1]))
  with open(f, 'wb') as fp:
    w = csv.writer(fp)
    w.writerow(columns)
    for k, v in cs.items():
      w.writerow(map(str, mapping(k, v)))

aug114 = 1406851200000
sep114 = 1409529600000
oct114 = 1412121600000
nov114 = 1414800000000
dec114 = 1417392000000
jan115 = 1420070400000
datafile = '/home/slydon/data/aug_nov/sorted_hcc_agg_uniq_logs.json'

pst_adj = lambda x: x + (7 * 60 * 60 * 1000)
pdt_adj = lambda x: x + (8 * 60 * 60 * 1000)

pvbd = lambda data, desired: '\n'.join(['%5.2f' % x[1] for x in sorted([(k, v) for k, v in data.items() if k in desired])])
pvbdwc = lambda data, desired: '\n'.join(['%s,%5.2f' % x for x in sorted([(k, v) for k, v in data.items() if k in desired])])
#print '\n'.join(['%5.2f' % x[1] for x in sorted([(k, v) for k, v in _c.reduceByKey(csofov, _c.scoder, lambda x: 1).items() if ('aeaallc' in k or 'codemine' in k) and 'carlyn' not in k])])

def runit(s, e, df, sf, of, mappings=None):
  data = loaddata(df, s, e)
  oppfs, forgs, corgs = mappings if mappings is not None else loadmappings(df, s, e)
  cs = groupByKeySeq(data, kcodersession, scoder, fnone)
  csov = dict([(k, v) for k, v in groupByKeySeq(data, kcodersessionoof, scoder, fnone).items() if tcvalid(v)])
  outputCS(sf, cs, corgs)
  outputCSOV(of, csov, corgs, forgs, oppfs)


if __name__ == '__main__':
  sff = '/home/slydon/data/aug_nov/%s_coder_hours_by_session.csv'
  off = '/home/slydon/data/aug_nov/%s_coder_hours_by_opp.csv'
  mappings = loadmappings(datafile)

  runit(aug114, sep114, datafile, sff % ('aug',), off % ('aug',), mappings)
  runit(sep114, oct114, datafile, sff % ('sep',), off % ('sep',), mappings)
  runit(oct114, nov114, datafile, sff % ('oct',), off % ('oct',), mappings)
  runit(nov114, dec114, datafile, sff % ('nov',), off % ('nov',), mappings)
