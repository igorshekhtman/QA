import pycurl
#res = Response()
bufu = io.BytesIO()
response = cStringIO.StringIO()
curl = pycurl.Curl()
#curl.setopt(curl.URL, "https://hcc-opprouter-stg.apixio.net:8443/ctrl/data/f7fb88f0-5104-4469-9d9a-3ef91be27254/reload")
curl.setopt(curl.URL, "https://hcc-opprouter-stg.apixio.com:8443/ctrl/data/f7fb88f0-5104-4469-9d9a-3ef91be27254/reload")
curl.setopt(curl.WRITEFUNCTION, bufu.write)
curl.setopt(curl.VERBOSE, True)
curl.setopt(curl.SSL_VERIFYHOST, 0)
curl.setopt(curl.SSL_VERIFYPEER, 1)
curl.setopt(curl.POST, 1)
curl.setopt(curl.SSLCERTTYPE, "PEM")
curl.setopt(curl.SSLKEYTYPE, "PEM")
curl.setopt(curl.CAPATH, "/etc/pki/tls/certs/")
curl.setopt(curl.SSLCERT, "/mnt/automation/secrets/apixio.hcc-opprouter-stg.apixio.com.pem")
print ("Executing curl.perform command ...")
curl.perform()
