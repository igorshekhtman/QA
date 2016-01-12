__author__ = 'ishekhtman'
########################################################################################################################
#
# PROGRAM: claims_data_subtraction.py
# AUTHOR:  Igor Shekhtman ishekhtman@apixio.com
# DATE:    Jan. 12, 2015 - Initial Version
#
# REVISIONS:
# AUTHOR: Igor Shekhtman ishekhtman@apixio.com
# DATE: Jan. 12, 2015
# SPECIFICS: None
#
# PURPOSE:
#          This program should be executed via Python 2.6 and is meant for testing Bundler Claims Data Subtraction mechanism:
#          * 1st Pass Project creation
#          * 2nd Pass Project creation
#          * Number of Opportunities generated by the Bundler verification
#          * 2nd Pass Project creation
#          * Number of Opportunities generation by the Bundler verification
#
# SETUP:
#          * Assumes a HCC environment is available
#          * Assumes a Python 2.6 environment is available
#          * From QA server (qa.apixio.com) /mnt/automation/python/stress_test folder enter "python2.7 claims_data_subtraction.py"
#
# USAGE:   * Test Results will be printed on Console screen as well as mailed via QA report
#
########################################################################################################################
import os,sys,time
import collections
import authentication
import elasticsearch

#=======================================================================================================================
def getEnvHosts(env):
  if env.lower()[0] == 's':
    hcchost = 'https://hcc-stg.apixio.com/'
    ssohost = 'https://accounts-stg.apixio.com'
    uahost = 'https://useraccount-stg.apixio.com'
    uaport = ':7076'
    caller = 'hcc_stg'
  elif env.lower()[0] == 'd':
    hcchost = 'https://hccdev.apixio.com/'
    ssohost = 'https://accounts-dev.apixio.com'
    uahost = 'https://useraccount-dev.apixio.com'
    uaport = ':7076'
    caller = 'hcc_dev'
  elif env.lower()[0] == 'e':
    hcchost = 'https://hcceng.apixio.com/'
    ssohost = 'https://accounts-eng.apixio.com'
    uahost = 'https://useraccount-eng.apixio.com'
    uaport = ':7076'
    caller = 'hcc_eng'
  return {'hcchost':hcchost, \
          'ssohost':ssohost, \
          'uahost':uahost, \
          'uaport':uaport, \
          'caller':caller}
#=======================================================================================================================
#==================================================== MAIN PROGRAM =====================================================
#=======================================================================================================================
def Main():
  global options
  os.system('clear')
  start_time=time.time()

  options=collections.OrderedDict()
  options['rep_type'] = 'Claims Data Bundling Test'
  options['usr'] = sys.argv[1] if len(sys.argv) > 1 else "mmgenergyes@apixio.net"
  options['env'] = sys.argv[2] if len(sys.argv) > 2 else "Development"
  options['pwd'] = 'apixio.123'
  options['env_hosts'] = getEnvHosts(options['env'])
  options['report_recepients'] = sys.argv[12] if len(sys.argv) > 12 else "ishekhtman@apixio.com"



  cookies = authentication.loginHCC(options)
  BODY = {
"query": {
      "bool": {
        "must": [
          {
            "terms": {
              "project": ["CP_926086b3-350c-4cbb-911a-898820823b4d"]
            }
          }
        ]
      }
    },
    "from": 0,
    "size": 1
}
  es = elasticsearch.Elasticsearch('http://elasticsearch-stg.apixio.com:9200')
  es.index(index='org-506', doc_type='opportunity', id='_search', body=BODY)
  resp = es.get(index='org-506', doc_type='opportunity', id='_search')['hits']
  print resp['total']




if __name__ == "__main__":
  Main()
#=======================================================================================================================