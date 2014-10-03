import htmlmaker.py as htmlGenerator
import dynamicPython.py as pythonGenerator
import fileinput
import os.path

#this method will be called when the user clicks ok in the gui w/ all info filled in
def addChart(env, cat, type1, type2, type3, days, query1, query2, query3, dataloc, yaxis, charttype):
	print("Chart being added . . .")
	types = []
	types.append(type1)
	types.append(type2)
	types.append(type3)
	query = []
	query.append(query1)
	query.append(query2)
	query.append(query3)
	for t in types:
		if (t == None):
			types.remove(t)
	for q in query:
		if (q == None):
			query.remove(q)
	print(types)
	print(query)
	#add title to frame2.html
	#
	#add link to new desired chart to frame2.html
	updateHTML(env, dataloc)
	#generates the new html file for the new chart
	htmlGenerator.generateHTML(env, dataloc)
	# runs python script to execute queries and generate JSON for new chart.
	pythonGenerator.executeMethods(env, cat, types, days, query, dataloc, yaxis, charttype)
	#add call of executeMethods to callAll.py
	updateCallAll(env, cat, types, days, query, dataloc, yaxis, charttype)
	
	
def updateCallAll(env, cat, types, days, query, dataloc, yaxis, charttype):
	filename = env + '.' + dataloc + '.py'
  	completeName = os.path.join("py/",filename)
 	
	for line in fileinput.input(completeName, inplace=1):
		if line.startswith('#DO NOT DELETE comment used for updating queries.#'):
			print ("""QUERIES["%s"] = %s""" % (dataloc, query))
		if line.startswith('#DO NOT DELETE comment used for updating method calls.#'):
			print ("""script.executeMethods("%s", "%s", %s, %s, %s, "%s", "%s", "%s")""" % (env, cat, types, days, "QUERIES[\"" + dataloc +  "\"]", dataloc, yaxis, charttype))
		print line,

	
		
def updateHTML(env, dataloc):
	for line in fileinput.input('frame2.html', inplace=1):
		if line.startswith('<!-- This is a comment for updating purposes DO NOT REMOVE -->'):
			print """<a href="html/%s.%s.html" target="frame3">%s: %s</a><br>""" % (env, dataloc, env, dataloc)
		print line,

addChart(env, cat, type1, type2, type3, days, query1, query2, query3, dataloc, yaxis, charttype)
