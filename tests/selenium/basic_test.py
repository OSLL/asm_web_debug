#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import unittest

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager


class BasicTest(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    CODE_ID = 'test-compile-code'
    ARCHS = ['x86_64', 'ARM','AVR']

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
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.delete_all_cookies()
        self.login_as_test_user()

    def tearDown(self):
        body = self.driver.find_element_by_tag_name('body')
        jsError = body.get_attribute('JSError')
        self.assertIsNone(jsError)
        self.driver.close()

    def login_as_test_user(self):
        self.driver.get(self.getUrl("/login"))
        self.driver.execute_script(f"""
            document.getElementById("username").value = "test_username";
            document.getElementById("password").value = "test_password";
            document.querySelector("form").submit();
        """)
        time.sleep(1.0)

    def open_code_page(self, code_id=None):
        code_url = self.getUrl(f'/{code_id if code_id else self.CODE_ID}')
        self.driver.get(code_url)

    def get_code_id_from_current_url(self):
        _, _, code_id = self.driver.current_url.rpartition('/')
        return code_id

    def set_code(self, code):
        # send code to textarea
        self.driver.execute_script(f"""
            element = document.querySelector('.CodeMirror');
            element.CodeMirror.setValue(`{code}`);
        """)
