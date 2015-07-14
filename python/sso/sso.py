#=========================================================================================
#======================================= sso.py ==========================================
#=========================================================================================
#
# PROGRAM:         sso.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    13-Jul-2015
# INITIAL VERSION: 1.0.0
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
#=========================================================================================
class TestingSSO(object):

	def __init__(self):
		self.tangerine = "This is a test"

	def apple(self):
		print "This is only a TEST"
        
        
	def getExtTok(self, user, pw): 	
		self.response = requests.post("https://useraccount-stg.apixio.com:7076/auths", \
			data={'email': user, 'password': pw}, headers={})
		self.statuscode = self.response.status_code
		if self.response.status_code < 400:
			self.etoken = self.response.json().get("token")
			self.expiration = self.response.json().get("passwordExpiresIn")
		else:
			self.userjson = {"error": "Fatal error occured, external token could not be obtained"}	
	
		
	def getIntTok(self, extok): 	
		self.response = requests.post("https://tokenizer-stg.apixio.com:7075/tokens", \
			data={}, headers={'Authorization': 'Apixio ' + extok})
		self.statuscode = self.response.status_code
		if self.response.status_code < 400:
			self.itoken = self.response.json().get("token")
		else:
			self.userjson = {"error": "Fatal error occured, internal token could not be obtained"}	
			

	def getInfoForForgetLink(self, forget_link):
		print ""
		print "getting Info for Forget Password Link "+forget_link
		user_accounts="https://useraccount-stg.apixio.com:7076/"
		response=requests.post(user_accounts+"verifications/"+forget_link+"/forgot")
		if response.status_code < 400:
			print "Succeeded in getting forget link info:"
			print response.json();
			print ""
			return response.json()
		else:
			print "Failed To Get Forget Link Info" 
			print response.status_code	

			
	def getPolicy(self, intok):
		print ""
		print "Getting /users/me/policy with token " + internalToken
		user_accounts="https://useraccount-stg.apixio.com:7076/users/me/passpolicy"
  		HEADERS = {'Authorization': 'Apixio ' + intok}
		response = requests.get(user_accounts,headers=HEADERS)
		if response.status_code < 400:
			print "Got Policy for user:"
			print response.json()
			print ""
		else:
			print "Error getting user policy"
			print response.status_code			
		

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================

os.system('clear')
extoken = TestingSSO()
intoken = TestingSSO()
extoken.getExtTok("ishekhtman@apixio.com", "apixio.123")
intoken.getIntTok(extoken.etoken)
print ("====================================================================")
print ("* STATUS CODE             %s" % extoken.statuscode)
print ("* EXTERNAL TOKEN          %s" % extoken.etoken) 
print ("* EXPIRES IN              %s" % extoken.expiration)
print ("* STATUS CODE             %s" % intoken.statuscode)
print ("* INTERNAL TOKEN          %s" % intoken.itoken) 
print ("====================================================================")
linkInfo = TestingSSO().getInfoForForgetLink("V_cd5764d7-c981-457f-a8e2-1e9e45cc88b3")
print linkInfo
internalToken = TestingSSO().getIntTok(linkInfo.get("token"))
getPolicy(intoken.itoken)
 
    