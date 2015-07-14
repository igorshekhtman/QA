#=========================================================================================
#======================================= sso.py ==========================================
#=========================================================================================
#
# PROGRAM:         token.py
# AUTHOR:          Igor Shekhtman ishekhtman@apixio.com
# DATE CREATED:    13-Jul-2015
# INITIAL VERSION: 1.0.0
#
#=========================================================================================
import requests
import sys, os
import json
#=========================================================================================

class TokenManager(object):

	def __init__(self):
		self.external_token_url="https://useraccount-stg.apixio.com:7076/auths"
		self.tokenizer_url = "https://tokenizer-stg.apixio.com:7075/tokens"

	def getExternalToken(self, user, pw): 	
		self.response = requests.post(self.external_token_url ,\
			data={'email': user, 'password': pw}, headers={})
		self.external_token_status_code = self.response.status_code
		if self.response.status_code < 400:
			self.etoken = self.response.json().get("token")
			self.expiration = self.response.json().get("passwordExpiresIn")
		else:
			raise Exception('{"error": "Fatal error occured, external token could not be obtained"}')
	
		
	def getInternalToken(self, extok): 	
		self.response = requests.post(self.tokenizer_url, \
			data={}, headers={'Authorization': 'Apixio ' + extok})
		self.internal_token_status_code = self.response.status_code
		if self.response.status_code < 400:
			self.itoken = self.response.json().get("token")
		else:
			raise Exception('{"error": "Fatal error occured, internal token could not be obtained"}')

				

#=========================================================================================
#====================== MAIN PROGRAM BODY ================================================
#=========================================================================================
if __name__=='__main__':
	os.system('clear')
	tokenManager = TokenManager()
	tokenManager.getExternalToken("ishekhtman@apixio.com", "apixio.123")
	tokenManager.getInternalToken(tokenManager.etoken)
	print ("====================================================================")
	print ("* STATUS CODE             %s" % tokenManager.external_token_status_code)
	print ("* EXTERNAL TOKEN          %s" % tokenManager.etoken) 
	print ("* EXPIRES IN              %s" % tokenManager.expiration)
	print ("* STATUS CODE             %s" % tokenManager.internal_token_status_code)
	print ("* INTERNAL TOKEN          %s" % tokenManager.itoken) 
	print ("====================================================================")
 
    