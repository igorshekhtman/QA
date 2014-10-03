import htmlmaker as htmlGenerator
import dynamicPython as pythonGenerator
import fileinput
import os.path
from mod_python import apache

#this method will be called when the user clicks ok in the gui w/ all info filled in
def addChart(title, env, cat, type1, type2, type3, days, query1, query2, query3, dataloc, yaxis, charttype):
	print("Chart being added . . .")
	
	types = [type1,type2,type3]
	query = [query1,query2,query3]
	
	types = filter(None, types)
	query = filter(None, query)
	print(types)
	print(query)
	#generates the new html file for the new chart
	print("adding html for new chart")
	htmlGenerator.generateHTML(env, dataloc)
	# runs python script to execute queries and generate JSON for new chart.
	print("running hive query for new chart")
	pythonGenerator.executeMethods(env, cat, types, days, query, dataloc, yaxis, charttype)
	#add link to new desired chart to frame2.html
	print("updating frame2.html")
	updateHTML(env, dataloc, title)
	#add call of executeMethods to callAll.py
	print("updating callAll.py")
	updateCallAll(env, cat, types, days, query, dataloc, yaxis, charttype)
	#return "done."
	
	
def updateCallAll(env, cat, types, days, query, dataloc, yaxis, charttype):
	filename = '/var/www/html/py/callAll.py'
  	#completeName = os.path.join("py/",filename)
 	
	for line in fileinput.input(filename, inplace=1):
		if line.startswith('#DO NOT DELETE comment used for updating queries.#'):
			print ("""QUERIES["%s"] = %s""" % (dataloc, query))
		if line.startswith('#DO NOT DELETE comment used for updating method calls.#'):
			print ("""script.executeMethods("%s", "%s", %s, %s, %s, "%s", "%s", "%s")""" % (env, cat, types, days, "QUERIES[\"" + dataloc +  "\"]", dataloc, yaxis, charttype))
		print line,

		
def updateHTML(env, dataloc, title):
	filename = '/var/www/html/frame2.html'
  	#completeName = os.path.join("../",filename)
	for line in fileinput.input(filename, inplace=1):
		if line.startswith('<!-- This is a comment for updating purposes DO NOT REMOVE -->'):
			print """<a href="html/%s.%s.html" target="frame3">%s: %s</a><br>""" % (env, dataloc, env, title)
		print line,


def email(req, title, env, cat, type1, days, query1, dataloc, yaxis, charttype):
	cat = cat.replace("-", "_")
	query1 = query1.replace("-", "_")
	addChart(title, env, cat, type1, "", "", days, query1, "", "", dataloc, yaxis, charttype)
	
	return "Thanks for waiting, your chart has been generated!"

