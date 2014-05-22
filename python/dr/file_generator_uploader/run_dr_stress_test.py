#import pyhs2
import os
import subprocess
import multiprocessing
import time
import thread
import threading
import datetime
import sys
import subprocess
from time import gmtime, strftime
#import pycurl
import io
import urllib
import urllib2
import urlparse
import json
import re
import smtplib
import string
import uuid
import cStringIO
os.system('clear')

#
#================================== INITIALIZING AND ASSIGN GLOBAL VARIABLES ============================================================================
#
THREADS = 10
DOCUMENTS = 10
USERNAME = "apxdemot0271"
ORGID = "291"
ENVIRONMENT = "Staging"

#
#========================================================================================================================================================
#




#
#================================== OBTAINING TEST LIMITATION PARAMATER =================================================================================
#
ENVIRONMENT = raw_input("Enter test environment (default "+str(ENVIRONMENT)+"): ")
if ENVIRONMENT == "":
	ENVIRONMENT = "Staging"
print ("Selected test environment: %s\n") % (ENVIRONMENT)
USERNAME = raw_input("Enter user name (default "+str(USERNAME)+"): ")
if USERNAME == "":
	USERNAME = "apxdemot0271"
print ("Selected user name: %s\n") % (USERNAME)
ORGID = raw_input("Enter org ID (default "+str(ORGID)+"): ")
if ORGID == "":
	ORGID = "291"
print ("Selected org ID: %s\n") % (ORGID)

try:
	THREADS = int(raw_input("Enter number of threads (default "+str(THREADS)+"): "))
except ValueError:
	print ("That was not a number. Assigning default value of 1")
print ("Total number of threads: %s\n") % (THREADS)

try:
	DOCUMENTS = int(raw_input("Enter number of documents (default "+str(DOCUMENTS)+"): "))
except ValueError:
	print ("That was not a number. Assigning default value of 10")
print ("Total number of documents: %s\n") % (DOCUMENTS)
#
#================================== EXECUTING DOC RECEIVER STRESS TEST ==================================================================================
#


	
def upload():

	subprocess.call("python2.6 file_generator_uploader.py", shell=True)
    #data = urllib2.urlopen("http://www.google.com/").read()
	print "python2.6 file_generator_uploader.py"	
	
	

threads = []

for n in range(10):
    thread = threading.Thread(target=upload)
    thread.start()

    threads.append(thread)

# to wait until all three functions are finished

print "Waiting..."

for thread in threads:
    thread.join()

print "Complete."
		
#for i in range(0, THREADS):
#		subprocess.call("python2.6 file_generator_uploader.py", shell=True)
#print ("Total number of concurrent threads: %s") % (i+1)
		
#
#================================== END =================================================================================================================
#
