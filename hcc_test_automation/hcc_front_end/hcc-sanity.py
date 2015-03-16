#!/usr/bin/env python
import os, sys, re
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class hcc_sanity(unittest.TestCase) :

    @classmethod
    def setUpClass(cls) :
        if 'DISPLAY' not in os.environ :
            os.environ['DISPLAY'] = ':1'
        cls.driver = webdriver.Firefox()

#-----------------------------------------------------------------------------------------

    def login(self) :
        self.driver.get('https://hccstage2.apixio.com/account/login/')
        username_form = self.driver.find_element_by_name("username")
        password_form = self.driver.find_element_by_name("password")
        username_form.send_keys(self.username)
        password_form.send_keys(self.password)
        username_form.submit()

#-----------------------------------------------------------------------------------------

    def setUp(self) :
        """
        sets up the firefox by logging in with a known username and password.
        """
        self.username = "sanitytest001@apixio.net"
        self.password = "apixio.123"
        self.login()
        
#-----------------------------------------------------------------------------------------
        
    def test_code_and_accept_opportunities(self) :
    
        #self.driver.get("https://hccstage2.apixio.com/#/opportunity") # go to the coding opp page
		
        for i in range (0,1):
        	self.driver.get("https://hccstage2.apixio.com/#/opportunity") # go to the coding opp page
        	first_document_link = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.ng-binding")))
        	first_document_link.click()
        	#accept_button = self.driver.find_element(By.CSS_SELECTOR, "div.btn.btn-success")
        	accept_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.btn.btn-success")))
        	accept_button.click()
        
        	icd_code_select_field = Select(self.driver.find_element_by_name("icd"))
        	#icd_code_select_field.select_by_index(5)
        	icd_code_select_field.select_by_visible_text("V45.11 - Renal dialysis status")
        
        	provider_name_field = self.driver.find_element_by_name("providerName")
        	provider_name_field.send_keys("Dr. Feel Good")
        
        	date_field = self.driver.find_element_by_name("dateOfService")
        	date_field.send_keys("03-04-2015")
        
        	provider_type_select_field = Select(self.driver.find_element_by_name("encounterType"))
        	provider_type_select_field.select_by_visible_text("Hospital Outpatient Setting") 
               
        
        	#done_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.btn.btn-success")))
        	#done_button = self.driver.find_element(By.CSS_SELECTOR, "input.btn.btn-success")
        	#done_button.click()
        	#name = "acceptForm"
        
        	accept_form = self.driver.find_element_by_name("acceptForm")
        	accept_form.submit()
        
        
        	next_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.btn.btn-success")))
        	next_button.click()
    
        
        
        	#flag_for_review_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.btn.btn-default.input-group-addon")))
        	#accept_button.click()
        	#<div class="btn btn-default input-group-addon open"
        
        	#flag_for_review_field = self.driver.find_element_by_class_name("btn btn-default input-group-addon open")     
        	#flag_for_review_field.send_keys("Dr. Feel Good testing flag field")
        
  
    		#next_button = self.driver.find_element(By.CSS_SELECTOR, "span.btn.btn-default")
    		#self.driver.implicitly_wait(6)
    		#next_button.click()
    		#self.driver.implicitly_wait(6)
    		#alert = self.driver.switch_to_alert()
    		#self.driver.implicitly_wait(6)
    		#cancel_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-success")
    		#cancel_button.click()	

#-----------------------------------------------------------------------------------------

    #def test_reporting_should_have_limited_pagination_603(self) :
    
    #    self.driver.get("https://hccstage2.apixio.com/#/qa") # go to the qa-workflow
        
    #    self.driver.implicitly_wait(3)
    #    pagination_controls = self.driver.find_elements_by_css_selector(".pagination > li")
    #    self.assertGreater(len(pagination_controls),2)
    #    self.assertLess(len(pagination_controls), 13)

    @classmethod
    def tearDownClass(cls) :
        cls.driver.quit()
