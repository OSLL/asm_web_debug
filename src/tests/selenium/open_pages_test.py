#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from selenium import webdriver

from basic_test import BasicTest

class OpenPagesTest(BasicTest):

    def test_open_slash(self):
        self.driver.get(self.getUrl('/'))
        code_id = self.get_code_id_from_current_url()
        assert code_id, 'No code_id in URL for new code(page)'
        assert "Web ASM" in self.driver.title, "No 'Web ASM' in title"

    def test_open_code(self):
        self.open_code_page()
        code_id = self.get_code_id_from_current_url()
        assert code_id == self.CODE_ID, 'New code_id != test.CODE_ID'
        assert "Web ASM" in self.driver.title, "No 'Web ASM' in title"