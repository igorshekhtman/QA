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
from time import gmtime, strftime, localtime
import calendar
import mmap
import hashlib


# MAIN FUNCTION CALLER ####################################################################################################

os.system('clear')


def countdown(x, i):

	if x[i] == 'firstfolder':
		print ("done x=%s"%x[i])
	else:
		start = len(x[i])-3
		#print start
		#print x[i][start:]
		if x[i][start:] == 'txt':
			print ("file name    = %s" % x[i])
		else:	
			print ("folder name  = %s" % x[i])
		countdown(x, i-1)

x=['firstfolder', 'firstfile.txt', 'secondfolder', 'secondfile.txt', 'thirdfolder']	
countdown(x, 4)
			

