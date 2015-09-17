__author__ = 'ha'


def get_apxapi():
  import imp
  f, filename, description = imp.find_module('apxapi', ['.'])
  apxapi = imp.load_module('apxapi', f, filename, description)
  return apxapi


def login(env):
  apxapi = get_apxapi()
  if env == apxapi.STG or env == apxapi.ENG:
    s = apxapi.APXSession("{STG USERNAME}", "{STG PASSWD}", environment=env)
  elif env == apxapi.PRD or env == apxapi.ESPRD:
    s = apxapi.APXSession("{PRD USERNAME}", "{PRD PASSWD}", environment=env)
  else:
    raise "error with login"

  return s