#!/usr/bin/env python
import os, sys, re
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException  


class hcc_sanity(unittest.TestCase) :

    @classmethod
    def setUpClass(cls) :
        if 'DISPLAY' not in os.environ :
            os.environ['DISPLAY'] = ':1'
        cls.driver = webdriver.Firefox()
        #cls.driver = webdriver.Chrome()

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
        
    def check_exists_by_xpath(xpath) :
        try:
            webdriver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True        
        
#-----------------------------------------------------------------------------------------
        
    def test_code_and_accept_ten_opportunities(self) :
    
        self.driver.get("https://hccstage2.apixio.com/#/opportunity") # go to the coding opp page
		
        for i in range (0,10):
        	first_document_link = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.ng-binding")))
        	first_document_link.click()

        	accept_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.btn.btn-success")))
        	accept_button.click()
        
        	icd_code_select_field = Select(self.driver.find_element_by_name("icd"))
        	icd_code_select_field.select_by_index(1)
        	#icd_code_select_field.select_by_visible_text("V45.11 - Renal dialysis status")
        
        	provider_name_field = self.driver.find_element_by_name("providerName")
        	provider_name_field.send_keys("Dr. Feel Good")
        
        	date_field = self.driver.find_element_by_name("dateOfService")
        	date_field.send_keys("03-04-2015")
        
        	provider_type_select_field = Select(self.driver.find_element_by_name("encounterType"))
        	provider_type_select_field.select_by_visible_text("Hospital Outpatient Setting") 
               
    		#found_on_page_field = self.driver.find_element_by_name("page")
    		found_on_page_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "page")))
    		found_on_page_field.send_keys("1")
    
    		flag_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//form/div/div[3]/div[2]/div/div/div[1]/span")))
    		flag_button.click()
    		
    		flag_comment_accept_flag = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//form/div/div[3]/div[2]/div/div/input")))
    		flag_comment_accept_flag.send_keys("Sanity Test Accept Comment")
    		   
        	accept_form = self.driver.find_element_by_name("acceptForm")
        	accept_form.submit()
                
        	next_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.btn.btn-success")))
        	next_button.click()
        	
#-----------------------------------------------------------------------------------------

    def test_code_and_reject_ten_opportunities(self) :
    	self.driver.get("https://hccstage2.apixio.com/#/opportunity") # go to the coding opp page
    		
        for i in range (0,10):
        	#first_document_link = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.ng-binding")))
        	first_document_link = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[1]/td[2]")))
        	tot_docs = 1
        	
        	#check if 2nd document is present
        	try:
        		second_document_link = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[2]/td[2]")))
        	except NoSuchElementException:
        		tot_docs = 1
        	except TimeoutException:
        		tot_docs = 1	
        	else:
        		tot_docs = 2	
        		
   	        	        	
        	print ("Loop number: %s, Total number of documents found: %s" % (i, tot_docs))

        	
        	if tot_docs > 1:
        		WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[2]/td[2]"))).click()
        	else:
        		WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[1]/td[2]"))).click()
        			
        	

        	#reject_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.btn.btn-primary")))
        	reject_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "html/body/div[1]/div[2]/ui-view/div/div[4]/div[1]/div[2]/div")))
        	reject_button.click()
        	     	
        	reject_reason_select_field = Select(self.driver.find_element_by_xpath("//form/div/div[1]/div/select"))
        	reject_reason_select_field.select_by_index(1)
        	
        	flag_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//form/div/div[2]/div/div/div[1]/span")))
    		flag_button.click()
        	
        	flag_comment_reject_flag = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//form/div/div[2]/div/div/input")))
    		flag_comment_reject_flag.send_keys("Sanity Test Reject Comment")
        	
        	done_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//form/div/div[3]/input")))
        	done_button.click()
        	    
        	next_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//ui-view/div/div/div/div[2]/span")))
        	next_button.click()
        	
        	if tot_docs > 1:
        		alert = self.driver.switch_to_alert()
        		skip_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "html/body/div[3]/div/div/div[2]/div/div/button[2]")))
        		skip_button.click()
        	
    
#-----------------------------------------------------------------------------------------

    @classmethod
    def tearDownClass(cls) :
        cls.driver.quit()
