from mod_python import apache

def handler(req):
    req.content_type = 'text/plain'
    req.write("Hello World!")
	print (req.form)
    return apache.OK