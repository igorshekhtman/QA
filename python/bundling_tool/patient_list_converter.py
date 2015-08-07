#=========================================================================================
#====================== patient_list_converter.py ========================================
#=========================================================================================
#
# PROGRAM:         patient_list_converter.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    30-Jul-2015
# INITIAL VERSION: 1.0.0
#
# PURPOSE:
#          This program should be executed via Python2.7 for Bundle specific data set:
#
# NOTES / COMMENTS:  python2.7 bundle.py staging projectID
#
#
#
#
# COVERED TEST CASES:
#
#
# SETUP:
#          * Assumes Meta ACLs and HCC environments are available
#		   * Assumes that Python2.7 is available 
#
# USAGE:
#          * Convert list of patients to comma-separated list of strings
#
# MISC: 
#
#=========================================================================================
import requests
import time
import datetime
import csv
import operator
import random
import re
import sys, os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from time import gmtime, strftime, localtime
import calendar
import mmap
import token
#=========================================================================================
#============= Initialization of the UserAccountsConfig file =============================
#=========================================================================================
CSV_CONFIG_FILE_PATH = "/mnt/automation/python/bundling_tool/"
CSV_CONFIG_FILE_NAME = "bundle.csv"
VERSION = "1.0.3"

DEBUG_MODE=bool(0)
REPORT = ""
REPORT_TYPE = "User Accounts Regression Test"
SENDER="donotreply@apixio.com"
CUR_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
START_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
TIME_START=time.time()
END_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
DURATION_TIME=strftime("%m/%d/%Y %H:%M:%S", gmtime())
DAY=strftime("%d", gmtime())
MONTH=strftime("%m", gmtime())
MONTH_FMN=strftime("%B", gmtime())
YEAR=strftime("%Y", gmtime())
CURDAY=strftime("%d", gmtime())
CURMONTH=strftime("%m", gmtime())
CURYEAR=strftime("%Y", gmtime())

PASSED_STAT="<table width='100%%'><tr><td bgcolor='#00A303' align='center'><font size='3' color='white'><b>STATUS - PASSED</b></font></td></tr></table>"
FAILED_STAT="<table width='100%%'><tr><td bgcolor='#DF1000' align='center'><font size='3' color='white'><b>STATUS - FAILED</b></font></td></tr></table>"
SUBHDR="<br><table width='100%%'><tr><td bgcolor='#4E4E4E' align='left'><font size='3' color='white'><b>&nbsp;&nbsp; %s</b></font></td></tr></table>"

#=========================================================================================
#================== Global variable declaration, initialization ==========================
#=========================================================================================
#
# Author: Igor Shekhtman ishekhtman@apixio.com
#
# Creation Date: 23-Oct-2014
#
# Description: Global configuration variables are read from "CSV_CONFIG_FILE_NAME" 
# defined above which is located in "CSV_CONFIG_FILE_PATH".  All values are read into 
# a "result" dictionary, which is later parsed one row at a time, filling values for 
# each of the global variables.
#
#=========================================================================================

INPUT_FILE = "MMG_372_01f8d7fb-ae83-48a9-82da-5d7f5e199c45"
OUTPUT_FILE = "output_"+INPUT_FILE

def ReadConvertWriteFile(in_filename, out_filename):
	#result={ }
	result=""
	csvfile_in = open(in_filename, 'rb')
	csvfile_out = open(out_filename, 'w')
	reader = csv.reader(csvfile_in, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
	for row in reader:
		result = result + "\t\t\"" + row[0] + "\"" + ",\n"
		csvfile_out.write("\t\t\"" + row[0] + "\"" + ",\n")
	print result
	csvfile_in.close()
	csvfile_out.close()
	return (result)    	

#=========================================================================================


	
	
	

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')

ReadConvertWriteFile(INPUT_FILE, OUTPUT_FILE)

print "Done ..."	

#=========================================================================================
