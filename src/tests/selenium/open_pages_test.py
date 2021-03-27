#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from selenium import webdriver

from basic_test import BasicTest

class OpenPagesTest(BasicTest):

    def test_open_slash(self):
        self.driver.get(self.getUrl('/'))
        assert "Web ASM" in self.driver.title
