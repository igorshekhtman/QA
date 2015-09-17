__author__ = 'ha'


import apxapi

def login(env):
  if env == apxapi.STG or env == apxapi.ENG:
    s = apxapi.APXSession("ishekhtman@apixio.com", "apixio.123", environment=env)
  elif env == apxapi.PRD or env == apxapi.ESPRD:
    s = apxapi.APXSession("ishekhtman@apixio.com", "apixio.123", environment=env)
  else:
    raise "error with login"

  return s