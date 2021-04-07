#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from selenium import webdriver
import time


class BasicTest(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    CODE_ID = 'test-compile-code'
    ARCHS = ['x86', 'arm', 'avr']

    def __init__(self, methodName='runTest', param=None):
        super(BasicTest, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_class, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_class)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_class(name, param=param))
        return suite
    
    def getUrl(self, relativePath):
        return self.param + relativePath

    def setUp(self):
        self.driver = webdriver.Firefox()#Chrome()
        self.driver.delete_all_cookies()

    def tearDown(self):
        body = self.driver.find_element_by_tag_name('body')
        jsError = body.get_attribute('JSError')
        self.assertIsNone(jsError)
        self.driver.close()

    def open_code_page(self, code_id=None):
        code_url = self.getUrl(f'/{code_id if code_id else self.CODE_ID}')
        self.driver.get(code_url)

    def get_code_id_from_current_url(self):
        _, _, code_id = self.driver.current_url.rpartition('/')
        return code_id