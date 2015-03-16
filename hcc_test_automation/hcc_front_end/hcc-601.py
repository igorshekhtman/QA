#!/usr/bin/env python
import os, sys, re
import unittest

from selenium import webdriver

class hcc_601(unittest.TestCase) :

    @classmethod
    def setUpClass(cls) :
        if 'DISPLAY' not in os.environ :
            os.environ['DISPLAY'] = ':1'
        cls.driver = webdriver.Firefox()


    def login(self) :
        self.driver.get('https://hccstage2.apixio.com/account/login/')
        username_form = self.driver.find_element_by_name("username")
        password_form = self.driver.find_element_by_name("password")

        username_form.send_keys(self.username)
        password_form.send_keys(self.password)
        
        username_form.submit()

    def setUp(self) :
        """
        sets up the firefox by logging in with a known username and password.
        """
        self.username = "sanitytest001@apixio.net"
        self.password = "apixio.123"

        self.login()


    def test_reporting_should_have_limited_pagination_601(self) :
        self.driver.get("https://hccstage2.apixio.com/#/qa") # go to the qa-workflow
        
        self.driver.implicitly_wait(3)
        pagination_controls = self.driver.find_elements_by_css_selector(".pagination > li")
        self.assertGreater(len(pagination_controls),2)
        self.assertLess(len(pagination_controls), 13)

    @classmethod
    def tearDownClass(cls) :
        cls.driver.quit()
