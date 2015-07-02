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

print (hash("Igor"))

print (hash("igor"))

print (hash("igorr"))


#def rhash(n):
#  return ((0x0000FFFF & n)<<16) + ((0xFFFF0000 & n)>>16)
  
#print (rhash("Igor"))  

secret_random_value = "asdfasdfasdfasdf"

hasher = hashlib.sha1()
hasher.update(secret_random_value)
hasher.update('Igor')
print hasher.hexdigest()